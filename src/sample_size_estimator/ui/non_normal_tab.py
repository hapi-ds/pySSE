"""Non-normal data analysis UI tab for Streamlit application."""

import logging

import numpy as np
import streamlit as st

from ..calculations.non_normal_calcs import (
    apply_transformation,
    calculate_wilks_limits,
    detect_outliers,
    generate_qq_plot,
    test_normality,
)
from ..logger import log_calculation


def render_non_normal_tab(logger: logging.Logger) -> None:
    """
    Render the non-normal data analysis tab.

    Args:
        logger: Application logger instance
    """
    st.header("Non-Normal Distribution Analysis")

    # Help section
    with st.expander("ℹ️ How to use this module", expanded=False):
        st.markdown("""
        **Non-normal data** doesn't follow a bell curve distribution.

        This module helps you:
        1. **Detect outliers** using the IQR method
        2. **Test normality** using Shapiro-Wilk and Anderson-Darling tests
        3. **Visualize normality** with Q-Q plots
        4. **Transform data** to achieve normality (Box-Cox, log, square root)
        5. **Use non-parametric methods** when transformations fail (Wilks' method)

        **Workflow**:
        - Enter your data
        - Check for outliers
        - Test normality
        - If non-normal, try transformations
        - If transformations fail, use Wilks' method
        """)

    # Data input section
    st.subheader("Data Input")

    data_input_method = st.radio(
        "Choose input method",
        options=["Manual Entry", "Paste Values"],
        help="Enter data manually or paste from spreadsheet"
    )

    data = None

    if data_input_method == "Manual Entry":
        data_str = st.text_area(
            "Enter data values (one per line or comma-separated)",
            value="10.2, 10.5, 10.1, 10.8, 10.3, 10.6, 10.4, 10.7, 10.2, 10.5",
            height=150,
            help="Enter numerical values separated by commas or newlines"
        )
    else:
        data_str = st.text_area(
            "Paste data values",
            value="",
            height=150,
            help="Paste values from Excel or other sources"
        )

    # Parse data
    if data_str:
        try:
            # Try to parse as comma or newline separated
            data_str_clean = data_str.replace('\n', ',').replace('\t', ',')
            data = [float(x.strip()) for x in data_str_clean.split(',') if x.strip()]

            if len(data) < 3:
                st.warning("⚠️ Please enter at least 3 data points")
                data = None
            else:
                st.success(f"✅ Loaded {len(data)} data points")

                # Show basic statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Count", len(data))
                with col2:
                    st.metric("Mean", f"{np.mean(data):.4f}")
                with col3:
                    st.metric("Std Dev", f"{np.std(data, ddof=1):.4f}")
                with col4:
                    st.metric("Range", f"{np.min(data):.4f} - {np.max(data):.4f}")

        except ValueError:
            st.error("❌ Invalid data format. Please enter numerical values only.")
            data = None

    if data is None:
        st.info("👆 Please enter data to begin analysis")
        return

    # Outlier detection section
    st.divider()
    st.subheader("1. Outlier Detection")

    if st.button("Detect Outliers", key="detect_outliers"):
        try:
            outlier_values, outlier_indices = detect_outliers(data)

            st.session_state['outliers'] = {
                'values': outlier_values,
                'indices': outlier_indices,
                'count': len(outlier_values)
            }

            log_calculation(
                logger,
                "outlier_detection",
                {"data_count": len(data)},
                {"outlier_count": len(outlier_values), "outliers": outlier_values}
            )

        except Exception as e:
            st.error(f"❌ Outlier detection failed: {str(e)}")
            logger.error(f"Outlier detection failed: {str(e)}", exc_info=True)

    if 'outliers' in st.session_state:
        outliers = st.session_state['outliers']

        if outliers['count'] == 0:
            st.success("✅ No outliers detected")
        else:
            st.warning(f"⚠️ Detected {outliers['count']} outlier(s)")
            st.write("Outlier values:", outliers['values'])
            st.info("Note: Outliers are flagged but not removed. Consider investigating these values.")

    # Normality testing section
    st.divider()
    st.subheader("2. Normality Testing")

    if st.button("Test Normality", key="test_normality"):
        try:
            normality_result = test_normality(data)

            st.session_state['normality_result'] = normality_result

            log_calculation(
                logger,
                "normality_test",
                {"data_count": len(data)},
                normality_result.model_dump()
            )

        except Exception as e:
            st.error(f"❌ Normality testing failed: {str(e)}")
            logger.error(f"Normality testing failed: {str(e)}", exc_info=True)

    if 'normality_result' in st.session_state:
        result = st.session_state['normality_result']

        if result.is_normal:
            st.success("✅ Data appears to be normally distributed")
        else:
            st.warning("⚠️ Data does not appear to be normally distributed")

        st.markdown("**Test Results:**")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Shapiro-Wilk Test**")
            st.write(f"Statistic: {result.shapiro_wilk_statistic:.6f}")
            st.write(f"P-value: {result.shapiro_wilk_pvalue:.6f}")
            if result.shapiro_wilk_pvalue > 0.05:
                st.success("✅ Passes (p > 0.05)")
            else:
                st.error("❌ Fails (p ≤ 0.05)")

        with col2:
            st.markdown("**Anderson-Darling Test**")
            st.write(f"Statistic: {result.anderson_darling_statistic:.6f}")
            st.write(f"Critical value (5%): {result.anderson_darling_critical_values[2]:.6f}")
            if result.anderson_darling_statistic < result.anderson_darling_critical_values[2]:
                st.success("✅ Passes")
            else:
                st.error("❌ Fails")

        st.info(result.interpretation)

    # Q-Q Plot section
    st.divider()
    st.subheader("3. Q-Q Plot Visualization")

    if st.button("Generate Q-Q Plot", key="generate_qq"):
        try:
            fig = generate_qq_plot(data)
            st.session_state['qq_plot'] = fig

        except Exception as e:
            st.error(f"❌ Q-Q plot generation failed: {str(e)}")
            logger.error(f"Q-Q plot generation failed: {str(e)}", exc_info=True)

    if 'qq_plot' in st.session_state:
        st.pyplot(st.session_state['qq_plot'])
        st.info("Points close to the diagonal line indicate normality. Deviations suggest non-normality.")

    # Transformation section
    st.divider()
    st.subheader("4. Data Transformation")

    transformation_method = st.selectbox(
        "Select transformation method",
        options=["boxcox", "log", "sqrt"],
        format_func=lambda x: {
            "boxcox": "Box-Cox (automatic lambda optimization)",
            "log": "Natural Logarithm",
            "sqrt": "Square Root"
        }[x],
        help="Choose a transformation to attempt achieving normality"
    )

    if st.button("Apply Transformation", key="apply_transform"):
        try:
            transformation_result = apply_transformation(data, transformation_method)

            st.session_state['transformation_result'] = transformation_result
            st.session_state['original_data'] = data

            log_calculation(
                logger,
                "transformation",
                {"method": transformation_method, "data_count": len(data)},
                {
                    "lambda": transformation_result.lambda_param,
                    "normality_after": transformation_result.normality_after.model_dump()
                }
            )

        except ValueError as e:
            st.error(f"❌ Transformation failed: {str(e)}")
            st.info("Tip: Log and Box-Cox require all positive values. Square root requires non-negative values.")
        except Exception as e:
            st.error(f"❌ Transformation failed: {str(e)}")
            logger.error(f"Transformation failed: {str(e)}", exc_info=True)

    if 'transformation_result' in st.session_state:
        trans_result = st.session_state['transformation_result']

        st.markdown(f"**Transformation: {trans_result.method.upper()}**")

        if trans_result.lambda_param is not None:
            st.write(f"Optimal lambda parameter: {trans_result.lambda_param:.4f}")

        # Show normality after transformation
        st.markdown("**Normality After Transformation:**")

        if trans_result.normality_after.is_normal:
            st.success("✅ Transformed data is normally distributed!")
        else:
            st.warning("⚠️ Transformed data is still not normally distributed")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"Shapiro-Wilk p-value: {trans_result.normality_after.shapiro_wilk_pvalue:.6f}")
        with col2:
            st.write(f"Anderson-Darling statistic: {trans_result.normality_after.anderson_darling_statistic:.6f}")

        # Show transformed data statistics
        st.markdown("**Transformed Data Statistics:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mean", f"{np.mean(trans_result.transformed_data):.4f}")
        with col2:
            st.metric("Std Dev", f"{np.std(trans_result.transformed_data, ddof=1):.4f}")
        with col3:
            st.metric("Range", f"{np.min(trans_result.transformed_data):.4f} - {np.max(trans_result.transformed_data):.4f}")

        st.info("""
        **Next Steps**: If transformation achieved normality, you can use parametric methods
        on the transformed data. Remember to back-transform results to original units.
        """)

    # Wilks' method section
    st.divider()
    st.subheader("5. Non-Parametric Method (Wilks)")

    st.markdown("""
    If transformations fail to achieve normality, use Wilks' non-parametric method.
    This method uses the minimum and maximum of the sample as tolerance limits.
    """)

    col1, col2 = st.columns(2)

    with col1:
        wilks_confidence = st.number_input(
            "Confidence Level (%)",
            min_value=0.1,
            max_value=99.9,
            value=95.0,
            step=0.1,
            key="wilks_conf"
        )

    with col2:
        wilks_reliability = st.number_input(
            "Reliability/Coverage (%)",
            min_value=0.1,
            max_value=99.9,
            value=90.0,
            step=0.1,
            key="wilks_rel"
        )

    if st.button("Calculate Wilks' Limits", key="calc_wilks"):
        try:
            lower_limit, upper_limit = calculate_wilks_limits(
                data,
                wilks_confidence,
                wilks_reliability
            )

            st.session_state['wilks_result'] = {
                'lower': lower_limit,
                'upper': upper_limit
            }

            log_calculation(
                logger,
                "wilks_method",
                {"confidence": wilks_confidence, "reliability": wilks_reliability, "data_count": len(data)},
                {"lower_limit": lower_limit, "upper_limit": upper_limit}
            )

        except Exception as e:
            st.error(f"❌ Wilks' calculation failed: {str(e)}")
            logger.error(f"Wilks' calculation failed: {str(e)}", exc_info=True)

    if 'wilks_result' in st.session_state:
        wilks = st.session_state['wilks_result']

        st.success("✅ Wilks' Limits Calculated")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Lower Limit", f"{wilks['lower']:.4f}")
        with col2:
            st.metric("Upper Limit", f"{wilks['upper']:.4f}")

        st.warning("""
        **Note**: Wilks' method is conservative and requires larger sample sizes than parametric methods.
        The limits are simply the minimum and maximum of your sample.
        """)
