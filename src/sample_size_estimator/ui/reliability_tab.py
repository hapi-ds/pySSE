"""Reliability life testing UI tab for Streamlit application."""

import logging
from datetime import datetime
from pathlib import Path

import streamlit as st

from ..calculations.reliability_calcs import calculate_reliability, celsius_to_kelvin
from ..config import get_settings
from ..logger import log_calculation
from ..models import CalculationReport, ReliabilityInput
from ..reports import generate_calculation_report
from ..validation import get_engine_validation_info


def render_reliability_tab(logger: logging.Logger) -> None:
    """
    Render the reliability life testing tab.

    Args:
        logger: Application logger instance
    """
    st.header("Reliability Life Testing")

    # Help section
    with st.expander("ℹ️ How to use this module", expanded=False):
        st.markdown("""
        **Reliability life testing** determines how long to test products to demonstrate reliability.

        This module calculates:
        1. **Test Duration**: Required test time for zero-failure demonstration
        2. **Acceleration Factor**: How much faster products fail at elevated test conditions

        **Key Concepts**:
        - **Zero-Failure Demonstration**: Testing with no failures to prove reliability
        - **Arrhenius Equation**: Models temperature acceleration of failure mechanisms
        - **Activation Energy**: Material property determining temperature sensitivity

        **Use Cases**:
        - Planning reliability demonstration tests
        - Accelerated life testing at elevated temperatures
        - Estimating field life from test results
        """)

    # Input section
    st.subheader("Input Parameters")

    # Basic parameters
    col1, col2, col3 = st.columns(3)

    with col1:
        confidence = st.number_input(
            "Confidence Level (%)",
            min_value=0.1,
            max_value=99.9,
            value=95.0,
            step=0.1,
            help="Confidence in the reliability demonstration"
        )

    with col2:
        reliability = st.number_input(
            "Reliability (%)",
            min_value=0.1,
            max_value=99.9,
            value=90.0,
            step=0.1,
            help="Target reliability level to demonstrate"
        )

    with col3:
        failures = st.number_input(
            "Number of Failures",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            help="Expected number of failures during test (typically 0)"
        )

    # Acceleration factor section (optional)
    st.divider()
    st.subheader("Acceleration Factor (Optional)")

    use_acceleration = st.checkbox(
        "Calculate acceleration factor for elevated temperature testing",
        value=False,
        help="Enable this to calculate how much faster failures occur at test temperature"
    )

    activation_energy = None
    use_temperature = None
    test_temperature = None

    if use_acceleration:
        st.markdown("""
        **Arrhenius Acceleration**: Products fail faster at higher temperatures.
        The acceleration factor tells you how much faster.
        """)

        col1, col2 = st.columns(2)

        with col1:
            activation_energy = st.number_input(
                "Activation Energy (eV)",
                min_value=0.01,
                max_value=5.0,
                value=0.7,
                step=0.01,
                format="%.2f",
                help="Material property (typical range: 0.3-1.5 eV for electronics)"
            )

        with col2:
            temp_unit = st.radio(
                "Temperature Unit",
                options=["Celsius", "Kelvin"],
                horizontal=True
            )

        col1, col2 = st.columns(2)

        with col1:
            if temp_unit == "Celsius":
                use_temp_c = st.number_input(
                    "Use Temperature (°C)",
                    min_value=-273.0,
                    max_value=500.0,
                    value=25.0,
                    step=1.0,
                    help="Normal operating temperature"
                )
                use_temperature = celsius_to_kelvin(use_temp_c)
                st.caption(f"= {use_temperature:.2f} K")
            else:
                use_temperature = st.number_input(
                    "Use Temperature (K)",
                    min_value=0.1,
                    max_value=773.0,
                    value=298.15,
                    step=1.0,
                    help="Normal operating temperature in Kelvin"
                )

        with col2:
            if temp_unit == "Celsius":
                test_temp_c = st.number_input(
                    "Test Temperature (°C)",
                    min_value=-273.0,
                    max_value=500.0,
                    value=85.0,
                    step=1.0,
                    help="Elevated test temperature (must be > use temperature)"
                )
                test_temperature = celsius_to_kelvin(test_temp_c)
                st.caption(f"= {test_temperature:.2f} K")
            else:
                test_temperature = st.number_input(
                    "Test Temperature (K)",
                    min_value=0.1,
                    max_value=773.0,
                    value=358.15,
                    step=1.0,
                    help="Elevated test temperature in Kelvin (must be > use temperature)"
                )

        # Validate temperatures
        if test_temperature is not None and use_temperature is not None and test_temperature <= use_temperature:
            st.error("❌ Test temperature must be greater than use temperature")

    # Calculate button
    if st.button("Calculate Test Duration", type="primary"):
        try:
            # Validate temperatures if acceleration is used
            if use_acceleration and test_temperature is not None and use_temperature is not None and test_temperature <= use_temperature:
                st.error("❌ Test temperature must be greater than use temperature")
                return

            # Create input model
            input_data = ReliabilityInput(
                confidence=confidence,
                reliability=reliability,
                failures=failures,
                activation_energy=activation_energy,
                use_temperature=use_temperature,
                test_temperature=test_temperature
            )

            # Perform calculation
            result = calculate_reliability(input_data)

            # Log calculation
            log_calculation(
                logger,
                "reliability",
                input_data.model_dump(),
                result.model_dump()
            )

            # Store result in session state
            st.session_state['reliability_result'] = result
            st.session_state['reliability_input'] = input_data

        except Exception as e:
            st.error(f"❌ Calculation error: {str(e)}")
            logger.error(f"Reliability calculation failed: {str(e)}", exc_info=True)

    # Display results
    if 'reliability_result' in st.session_state:
        st.divider()
        st.subheader("Results")

        result = st.session_state['reliability_result']
        input_data = st.session_state['reliability_input']

        # Test duration
        st.markdown("**Test Duration**")
        st.success(f"✅ **Required Test Duration: {result.test_duration:.2f} units**")

        st.info(f"""
        **Method**: {result.method}

        This value is proportional to the chi-squared distribution and represents the
        required test duration or number of test units needed.
        """)

        # Acceleration factor (if calculated)
        if result.acceleration_factor is not None:
            st.divider()
            st.markdown("**Acceleration Factor**")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Acceleration Factor", f"{result.acceleration_factor:.2f}x")

            with col2:
                equivalent_time = result.test_duration / result.acceleration_factor
                st.metric("Equivalent Field Time", f"{equivalent_time:.2f} units")

            st.success(f"""
            ✅ **Interpretation**: Testing at {input_data.test_temperature:.2f} K accelerates failures
            by {result.acceleration_factor:.2f}x compared to use conditions at {input_data.use_temperature:.2f} K.

            Testing for {result.test_duration:.2f} units at test temperature is equivalent to
            {equivalent_time:.2f} units at use temperature.
            """)

            # Additional guidance
            st.info("""
            **Practical Application**:
            - If test duration is in hours, multiply by acceleration factor to get equivalent field hours
            - If test duration is in cycles, multiply by acceleration factor to get equivalent field cycles
            - Higher activation energy = more temperature sensitivity = higher acceleration
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
                    module="reliability",
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
                output_path = output_dir / f"reliability_report_{timestamp_str}.pdf"

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
