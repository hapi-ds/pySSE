"""Variables data analysis UI tab for Streamlit application."""

import logging
from datetime import datetime
from pathlib import Path

import streamlit as st

from ..calculations.variables_calcs import calculate_variables
from ..config import get_settings
from ..logger import log_calculation
from ..models import CalculationReport, VariablesInput
from ..reports import generate_calculation_report
from ..validation import get_engine_validation_info


def render_variables_tab(logger: logging.Logger) -> None:
    """
    Render the variables data analysis tab.

    Args:
        logger: Application logger instance
    """
    st.header("Variables Data Analysis (Normal Distribution)")

    # Help section
    with st.expander("ℹ️ How to use this module", expanded=False):
        st.markdown("""
        **Variables data** involves continuous measurements (length, weight, temperature, etc.).

        Use this module to:
        - Calculate tolerance factors for normally distributed data
        - Determine tolerance limits that contain a specified proportion of the population
        - Compare tolerance limits against specification limits
        - Calculate process performance index (Ppk)

        **Key Concepts**:
        - **Tolerance Factor (k)**: Statistical multiplier used to calculate tolerance limits
        - **Tolerance Limits**: Statistical bounds containing a specified proportion of the population
        - **Specification Limits**: Engineering requirements (LSL/USL)
        - **Ppk**: Process capability index comparing variation to specifications
        """)

    # Input section
    st.subheader("Input Parameters")

    # Statistical parameters
    col1, col2, col3 = st.columns(3)

    with col1:
        confidence = st.number_input(
            "Confidence Level (%)",
            min_value=0.1,
            max_value=99.9,
            value=95.0,
            step=0.1,
            help="Confidence that tolerance limits contain the specified proportion"
        )

    with col2:
        reliability = st.number_input(
            "Reliability/Coverage (%)",
            min_value=0.1,
            max_value=99.9,
            value=90.0,
            step=0.1,
            help="Proportion of population contained within tolerance limits"
        )

    with col3:
        sample_size = st.number_input(
            "Sample Size (n)",
            min_value=2,
            max_value=10000,
            value=30,
            step=1,
            help="Number of measurements in your sample"
        )

    # Sample statistics
    st.markdown("**Sample Statistics**")
    col1, col2 = st.columns(2)

    with col1:
        sample_mean = st.number_input(
            "Sample Mean (μ)",
            value=100.0,
            format="%.6f",
            help="Average of your measurements"
        )

    with col2:
        sample_std = st.number_input(
            "Sample Standard Deviation (σ)",
            min_value=0.000001,
            value=5.0,
            format="%.6f",
            help="Standard deviation of your measurements (must be positive)"
        )

    # Sided selection
    sided = st.radio(
        "Tolerance Limit Type",
        options=["two", "one"],
        format_func=lambda x: "Two-sided (both upper and lower limits)" if x == "two" else "One-sided (upper limit only)",
        help="Choose whether you need both limits or just an upper limit"
    )

    # Specification limits (optional)
    st.markdown("**Specification Limits (Optional)**")
    st.markdown("*Provide specification limits to compare against tolerance limits and calculate Ppk*")

    use_spec_limits = st.checkbox("Include specification limits", value=False)

    lsl = None
    usl = None

    if use_spec_limits:
        col1, col2 = st.columns(2)

        with col1:
            lsl_input = st.number_input(
                "Lower Specification Limit (LSL)",
                value=85.0,
                format="%.6f",
                help="Minimum acceptable value"
            )
            lsl = lsl_input

        with col2:
            usl_input = st.number_input(
                "Upper Specification Limit (USL)",
                value=115.0,
                format="%.6f",
                help="Maximum acceptable value"
            )
            usl = usl_input

        # Validate LSL < USL
        if lsl >= usl:
            st.error("❌ LSL must be less than USL")

    # Calculate button
    if st.button("Calculate Tolerance Limits", type="primary"):
        try:
            # Validate LSL < USL if both provided
            if lsl is not None and usl is not None and lsl >= usl:
                st.error("❌ Lower Specification Limit must be less than Upper Specification Limit")
                return

            # Create input model
            input_data = VariablesInput(
                confidence=confidence,
                reliability=reliability,
                sample_size=sample_size,
                sample_mean=sample_mean,
                sample_std=sample_std,
                lsl=lsl,
                usl=usl,
                sided=sided
            )

            # Perform calculation
            result = calculate_variables(input_data)

            # Log calculation
            log_calculation(
                logger,
                "variables",
                input_data.model_dump(),
                result.model_dump()
            )

            # Store result in session state
            st.session_state['variables_result'] = result
            st.session_state['variables_input'] = input_data

        except Exception as e:
            st.error(f"❌ Calculation error: {str(e)}")
            logger.error(f"Variables calculation failed: {str(e)}", exc_info=True)

    # Display results
    if 'variables_result' in st.session_state:
        st.divider()
        st.subheader("Results")

        result = st.session_state['variables_result']
        input_data = st.session_state['variables_input']

        # Tolerance factor and limits
        st.markdown("**Tolerance Analysis**")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tolerance Factor (k)", f"{result.tolerance_factor:.4f}")
        with col2:
            if result.lower_tolerance_limit is not None:
                st.metric("Lower Tolerance Limit", f"{result.lower_tolerance_limit:.4f}")
            else:
                st.metric("Lower Tolerance Limit", "N/A")
        with col3:
            if result.upper_tolerance_limit is not None:
                st.metric("Upper Tolerance Limit", f"{result.upper_tolerance_limit:.4f}")
            else:
                st.metric("Upper Tolerance Limit", "N/A")

        # Specification comparison (if applicable)
        if result.pass_fail is not None:
            st.divider()
            st.markdown("**Specification Comparison**")

            if result.pass_fail == "PASS":
                st.success(f"✅ **Result: {result.pass_fail}**")
                st.markdown("Tolerance limits are within specification limits.")
            else:
                st.error(f"❌ **Result: {result.pass_fail}**")
                st.markdown("Tolerance limits exceed specification limits.")

            col1, col2, col3 = st.columns(3)

            with col1:
                if result.ppk is not None:
                    st.metric("Process Performance (Ppk)", f"{result.ppk:.2f}")
                    if result.ppk >= 1.33:
                        st.success("Excellent capability")
                    elif result.ppk >= 1.0:
                        st.warning("Adequate capability")
                    else:
                        st.error("Poor capability")

            with col2:
                if result.margin_lower is not None:
                    st.metric("Margin to LSL", f"{result.margin_lower:.4f}")
                    if result.margin_lower < 0:
                        st.error("Below LSL")

            with col3:
                if result.margin_upper is not None:
                    st.metric("Margin to USL", f"{result.margin_upper:.4f}")
                    if result.margin_upper < 0:
                        st.error("Above USL")

        # Interpretation
        st.info(f"""
        **Interpretation**: With {input_data.confidence}% confidence, {input_data.reliability}% of the population
        falls within the calculated tolerance limits based on a sample of {input_data.sample_size} measurements.
        """)

        # Report generation
        st.divider()
        if st.button("📄 Generate PDF Report"):
            try:
                settings = get_settings()

                # Get validation info
                validation_info = get_engine_validation_info(
                    settings.calculations_file,
                    settings.validated_hash
                )

                # Prepare report data
                results_dict = result.model_dump()

                report = CalculationReport(
                    timestamp=datetime.now(),
                    module="variables",
                    inputs=input_data.model_dump(),
                    results=results_dict,
                    engine_hash=validation_info["current_hash"],
                    validated_state=validation_info["is_validated"],
                    app_version=settings.app_version
                )

                # Generate PDF
                output_dir = Path(settings.report_output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)

                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = output_dir / f"variables_report_{timestamp_str}.pdf"

                generate_calculation_report(report, str(output_path))

                # Provide download
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Report",
                        data=f.read(),
                        file_name=output_path.name,
                        mime="application/pdf"
                    )

                st.success("✅ Report generated successfully!")

            except Exception as e:
                st.error(f"❌ Report generation failed: {str(e)}")
                logger.error(f"Report generation failed: {str(e)}", exc_info=True)
