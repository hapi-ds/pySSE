"""Main Streamlit application for Sample Size Estimator."""


import streamlit as st

from .config import get_settings
from .logger import setup_logger
from .ui.attribute_tab import render_attribute_tab
from .ui.non_normal_tab import render_non_normal_tab
from .ui.reliability_tab import render_reliability_tab
from .ui.variables_tab import render_variables_tab


def main() -> None:
    """Main application entry point."""

    # Load settings
    settings = get_settings()

    # Set up page configuration
    st.set_page_config(
        page_title=settings.app_title,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize logger
    logger = setup_logger(
        name="sample_size_estimator",
        log_file=settings.log_file,
        log_level=settings.log_level,
        log_format=settings.log_format
    )

    # Log app initialization
    logger.info("Application started")

    # Application header
    st.title(f"📊 {settings.app_title}")
    st.markdown(f"**Version {settings.app_version}**")

    # Main help section
    with st.expander("📖 About This Application", expanded=False):
        st.markdown("""
        ## Sample Size Estimator

        A validated statistical tool for medical device design verification and process validation.

        ### Purpose
        This application helps quality engineers and statisticians determine statistically valid
        sample sizes and analyze measurement data for regulatory compliance per ISO/TR 80002-2.

        ### Modules

        **1. Attribute Data (Binomial)**
        - Calculate sample sizes for pass/fail testing
        - Success Run Theorem (zero failures)
        - Binomial calculations (with allowable failures)
        - Sensitivity analysis

        **2. Variables Data (Normal)**
        - Tolerance factor calculations
        - Tolerance limit determination
        - Process capability (Ppk)
        - Specification limit comparison

        **3. Non-Normal Distribution**
        - Outlier detection (IQR method)
        - Normality testing (Shapiro-Wilk, Anderson-Darling)
        - Q-Q plots for visualization
        - Data transformations (Box-Cox, log, square root)
        - Non-parametric methods (Wilks)

        **4. Reliability Life Testing**
        - Zero-failure demonstration
        - Test duration calculation
        - Arrhenius acceleration factors
        - Accelerated life testing

        ### Features
        - ✅ Validated calculation engine with hash verification
        - ✅ PDF report generation with audit trail
        - ✅ Comprehensive logging for regulatory compliance
        - ✅ Property-based testing for correctness
        - ✅ User-friendly interface with contextual help

        ### Getting Started
        1. Select the appropriate tab for your analysis type
        2. Enter your parameters (hover over labels for help)
        3. Click the calculate button
        4. Review results and generate PDF reports as needed

        ### Validation State
        This application maintains a validated state through cryptographic hash verification.
        All generated reports include the validation status of the calculation engine.
        """)

    # Sidebar information
    with st.sidebar:
        st.header("ℹ️ Information")

        st.markdown("### Quick Guide")
        st.markdown("""
        **Choose your analysis type:**

        🔢 **Attribute** - Binary outcomes (pass/fail)

        📏 **Variables** - Continuous measurements

        📊 **Non-Normal** - Data transformations

        ⏱️ **Reliability** - Life testing
        """)

        st.divider()

        st.markdown("### Configuration")
        st.info(f"""
        **Log Level**: {settings.log_level}

        **Report Directory**: {settings.report_output_dir}

        **Validation**: {'Enabled' if settings.validated_hash else 'Not configured'}
        """)

        st.divider()

        st.markdown("### Support")
        st.markdown("""
        For questions or issues:
        - Review the help sections in each tab
        - Check the comprehensive user guide
        - Consult the validation protocol
        """)

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔢 Attribute (Binomial)",
        "📏 Variables (Normal)",
        "📊 Non-Normal Distribution",
        "⏱️ Reliability"
    ])

    # Render each tab
    with tab1:
        render_attribute_tab(logger)

    with tab2:
        render_variables_tab(logger)

    with tab3:
        render_non_normal_tab(logger)

    with tab4:
        render_reliability_tab(logger)

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    Sample Size Estimator | Validated Statistical Analysis Tool<br>
    For medical device design verification and process validation
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
