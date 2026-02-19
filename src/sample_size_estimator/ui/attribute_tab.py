"""Attribute data analysis UI tab for Streamlit application."""

import logging
from datetime import datetime
from pathlib import Path

import streamlit as st

from ..calculations.attribute_calcs import calculate_attribute
from ..config import get_settings
from ..logger import log_calculation
from ..models import (
    AttributeInput,
    AttributeResult,
    CalculationReport,
    SensitivityResult,
)
from ..reports import generate_calculation_report
from ..validation import get_engine_validation_info


def render_attribute_tab(logger: logging.Logger) -> None:
    """
    Render the attribute data analysis tab.

    Args:
        logger: Application logger instance
    """
    st.header("Attribute Data Analysis (Binomial)")

    # Help section
    with st.expander("ℹ️ How to use this module", expanded=False):
        st.markdown("""
        **Attribute data** involves binary outcomes (pass/fail, conforming/non-conforming).

        Use this module to calculate the minimum sample size needed to demonstrate
        a specified reliability level with a given confidence.

        - **Confidence Level**: The probability that your conclusion is correct (typically 95%)
        - **Reliability**: The proportion of conforming items in the population (e.g., 90% means 90% pass rate)
        - **Allowable Failures**: Maximum number of failures permitted in the sample
          - Leave empty for sensitivity analysis (calculates for c=0, 1, 2, 3)
          - Set to 0 for Success Run Theorem (zero failures allowed)
          - Set to >0 for binomial calculation with failures
        """)

    # Input section
    st.subheader("Input Parameters")

    col1, col2 = st.columns(2)

    with col1:
        confidence = st.number_input(
            "Confidence Level (%)",
            min_value=0.1,
            max_value=99.9,
            value=95.0,
            step=0.1,
            help="The probability that the population reliability is at least the specified value"
        )

    with col2:
        reliability = st.number_input(
            "Reliability (%)",
            min_value=0.1,
            max_value=99.9,
            value=90.0,
            step=0.1,
            help="The proportion of conforming items in the population"
        )

    # Allowable failures input with special handling for sensitivity analysis
    st.markdown("**Allowable Failures**")
    use_sensitivity = st.checkbox(
        "Perform sensitivity analysis (calculate for c=0, 1, 2, 3)",
        value=True,
        help="Check this to see sample sizes for multiple failure scenarios"
    )

    allowable_failures = None
    if not use_sensitivity:
        allowable_failures = st.number_input(
            "Number of allowable failures (c)",
            min_value=0,
            max_value=100,
            value=0,
            step=1,
            help="Maximum number of failures permitted while still demonstrating required reliability"
        )

    # Calculate button
    if st.button("Calculate Sample Size", type="primary"):
        try:
            # Create input model
            input_data = AttributeInput(
                confidence=confidence,
                reliability=reliability,
                allowable_failures=allowable_failures
            )

            # Perform calculation
            result = calculate_attribute(input_data)

            # Log calculation
            log_calculation(
                logger,
                "attribute",
                input_data.model_dump(),
                result.model_dump() if isinstance(result, AttributeResult) else {"results": [r.model_dump() for r in result.results]}
            )

            # Store result in session state
            st.session_state['attribute_result'] = result
            st.session_state['attribute_input'] = input_data

        except Exception as e:
            st.error(f"❌ Calculation error: {str(e)}")
            logger.error(f"Attribute calculation failed: {str(e)}", exc_info=True)

    # Display results
    if 'attribute_result' in st.session_state:
        st.divider()
        st.subheader("Results")

        result = st.session_state['attribute_result']

        # Check if result has 'results' attribute (SensitivityResult) or 'sample_size' (AttributeResult)
        if isinstance(result, SensitivityResult) or (hasattr(result, 'results') and not hasattr(result, 'sample_size')):
            # Display sensitivity analysis table
            st.markdown("**Sensitivity Analysis Results**")
            st.markdown("Sample sizes for different allowable failure scenarios:")

            # Create table data
            table_data = []
            for r in result.results:
                table_data.append({
                    "Allowable Failures (c)": r.allowable_failures,
                    "Required Sample Size (n)": r.sample_size,
                    "Method": r.method.replace("_", " ").title()
                })

            st.table(table_data)

            # Interpretation
            st.info(f"""
            **Interpretation**: With {result.results[0].confidence}% confidence and {result.results[0].reliability}% reliability:
            - Zero failures requires n = {result.results[0].sample_size}
            - One failure allowed requires n = {result.results[1].sample_size}
            - Two failures allowed requires n = {result.results[2].sample_size}
            - Three failures allowed requires n = {result.results[3].sample_size}
            """)

        else:
            # Display single result
            st.success(f"✅ **Required Sample Size: {result.sample_size}**")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Confidence Level", f"{result.confidence}%")
            with col2:
                st.metric("Reliability", f"{result.reliability}%")
            with col3:
                st.metric("Allowable Failures", result.allowable_failures)

            st.info(f"""
            **Method**: {result.method.replace("_", " ").title()}

            **Interpretation**: To demonstrate {result.reliability}% reliability with {result.confidence}% confidence,
            you need to test {result.sample_size} units with no more than {result.allowable_failures} failure(s).
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
                input_data = st.session_state['attribute_input']

                if isinstance(result, SensitivityResult) or (hasattr(result, 'results') and not hasattr(result, 'sample_size')):
                    results_dict = {
                        "sensitivity_analysis": [
                            {
                                "allowable_failures": r.allowable_failures,
                                "sample_size": r.sample_size,
                                "method": r.method
                            }
                            for r in result.results
                        ]
                    }
                else:
                    results_dict = {
                        "sample_size": result.sample_size,
                        "allowable_failures": result.allowable_failures,
                        "method": result.method
                    }

                report = CalculationReport(
                    timestamp=datetime.now(),
                    module="attribute",
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
                output_path = output_dir / f"attribute_report_{timestamp_str}.pdf"

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
