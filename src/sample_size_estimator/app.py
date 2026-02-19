"""Main Streamlit application for Sample Size Estimator."""


import streamlit as st

from .config import get_settings
from .logger import setup_logger
from .ui.attribute_tab import render_attribute_tab
from .ui.non_normal_tab import render_non_normal_tab
from .ui.reliability_tab import render_reliability_tab
from .ui.variables_tab import render_variables_tab
from .validation import (
    ValidationConfig,
    ValidationOrchestrator,
    ValidationPersistence,
    ValidationStateManager,
    ValidationUI,
)


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

    # Initialize validation system components
    validation_config = ValidationConfig()
    state_manager = ValidationStateManager(validation_config)
    persistence = ValidationPersistence(validation_config.persistence_dir)
    validation_ui = ValidationUI()

    # Check validation status on startup
    persisted_state = persistence.load_validation_state()
    validation_status = state_manager.check_validation_status(persisted_state)
    logger.info(f"Validation status: {validation_status.get_status_text()}")

    # Application header
    st.title(f"📊 {settings.app_title}")
    st.markdown(f"**Version {settings.app_version}**")

    # Display non-validated banner if not validated
    if not validation_status.is_validated:
        validation_ui.render_non_validated_banner()

    # Display expiry warnings if applicable
    if validation_status.days_until_expiry is not None:
        for threshold in validation_config.reminder_thresholds:
            if validation_status.days_until_expiry <= threshold:
                validation_ui.render_expiry_warning(
                    validation_status.days_until_expiry,
                    threshold
                )
                break

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


    # Main help section
    with st.expander("Risk-Based Statistical Strategies for Medical Device Verification and Validation", expanded=False):
        st.markdown("""
        ## Introduction: Why We Can't Just Test 30 Units Anymore

        The days of picking arbitrary sample sizes are gone. Regulators—the FDA, EU notified bodies—now require a documented,
        statistically valid rationale for every test protocol we write. That means sample size can't be a guess. It has to be
        calculated based on your specific risk profile.
        
        This shift isn't just bureaucratic. It makes sense: we're trying to prove device safety, and that proof needs to be
        mathematically sound. The regulations are clear: 21 CFR 820.250(b) and ISO 13485:2016 both mandate statistical techniques
        with documented rationale for sampling plans.
        
        The reality is, sample size depends on three things:
        - **How severe is a failure?** (Risk from ISO 14971)
        - **How confident do we need to be?** (Confidence level)
        - **What percentage of devices must work?** (Reliability)
        
        Link those three, do the math, and you get your sample size. That's the story regulators want to see in your Design
        Verification Plan.
        
        ## The Problem With Old Heuristics
        
        We used to lean on the "rule of 30"—test 30 units because the t-distribution approximates normal at n≥30. That's true,
        but it's answering the wrong question. It's about the average performance. In design verification, you care about the
        extremes—the worst-case units. That's a different statistical problem entirely.
        
        ## Building Your Statistical Policy: Risk Drives Sample Size
        
        Start with ISO 14971. Map your hazards to severity levels, then define what confidence and reliability you actually need:

        | Risk Level | Severity | Required Confidence | Required Reliability |
        |------------|----------|---------------------|---------------------|
        | **Critical** | Catastrophic (death, permanent injury) | 95% | 99.0% - 99.9% |
        | **High** | Serious (life-threatening) | 95% | 99.0% |
        | **Medium** | Moderate (medical intervention needed) | 95% | 95.0% |
        | **Low** | Minor (temporary, no medical care) | 95% | 90.0% |
        | **Negligible** | Inconvenience only | 90% | 80.0% |

        That's your policy. It's your "valid rationale." Document it, stick to it, and you've got defensible sample sizes.

        ## Confidence vs. Reliability: Get This Right

        **Reliability (R)**: The percentage of devices in production that actually meet spec. 99% reliability = 99 out of 100
        devices work as intended.

        **Confidence (C)**: How sure you are about that claim. You're testing a sample, not everything, so there's always
        uncertainty. 95% confidence means if you repeated the test 100 times, you'd get the right answer 95 times.

        Regulators basically expect 95% confidence as a floor for safety-critical testing. Reliability is what scales with
        risk—catastrophic failures demand 99.9%, while minor issues might only need 90%.

        ## Use Variable Data When Possible

        Statistical power matters. Here's the hierarchy:

        1. **Variable data (parametric)**: Measure actual values (dimension, force, output). Best sample size efficiency.
        2. **Variable data (non-parametric)**: Measurements that don't fit normal distribution. Still good.
        3. **Attribute data**: Pass/fail only. Requires the largest sample sizes.

        Pro tip: Define specs in variable terms instead of binary pass/fail. You'll dramatically reduce your sample
        size and get better insight into design margins.

        ## The Takeaway

        Your sample size isn't a preference—it's a calculated answer to a quantified risk question. Start
        with the risk assessment, define your confidence and reliability targets, then calculate. Document it all.
        That's what regulators are actually looking for: the mathematical connection between "this could harm someone"
        and "we tested this many units."
        """)


    # Sidebar information
    with st.sidebar:
        st.header("ℹ️ Information")

        # Validation section
        st.markdown("### Validation Status")
        validation_ui.render_validation_metrics_dashboard(validation_status)

        # Validation button with callback
        def run_validation() -> None:
            """Run validation workflow."""
            logger.info("Starting validation workflow from UI")
            orchestrator = ValidationOrchestrator(validation_config.certificate_output_dir)

            with st.spinner("Running validation..."):
                # Progress callback
                def progress_callback(phase: str, percentage: float) -> None:
                    validation_ui.render_validation_progress(phase, percentage)

                try:
                    result = orchestrator.execute_validation_workflow(
                        progress_callback=progress_callback
                    )

                    # Create validation state object (for both success and failure)
                    from datetime import timedelta
                    from .validation import ValidationState
                    
                    expiry_date = result.validation_date + timedelta(
                        days=validation_config.validation_expiry_days
                    )
                    
                    validation_state = ValidationState(
                        validation_date=result.validation_date,
                        validation_hash=result.validation_hash,
                        environment_fingerprint=result.environment_fingerprint,
                        iq_status="PASS" if result.iq_result.passed else "FAIL",
                        oq_status="PASS" if result.oq_result.passed else "FAIL",
                        pq_status="PASS" if result.pq_result.passed else "FAIL",
                        expiry_date=expiry_date,
                        certificate_hash=result.certificate_hash
                    )
                    
                    # Save validation state (both success and failure)
                    persistence.save_validation_state(validation_state)
                    
                    # Force Streamlit to rerun to reload validation status
                    st.rerun()

                    if result.success:
                        validation_ui.render_validation_result(
                            True,
                            "✅ Validation completed successfully!"
                        )
                        
                        # Clear progress display after successful validation
                        validation_ui.clear_validation_progress()
                        
                        logger.info("Validation workflow completed successfully")
                    else:
                        # Clear progress display after failed validation
                        validation_ui.clear_validation_progress()
                        
                        validation_ui.render_validation_result(
                            False,
                            "❌ Validation failed. Please review the errors."
                        )
                        logger.error("Validation workflow failed")

                except Exception as e:
                    # Clear progress display on error
                    validation_ui.clear_validation_progress()
                    
                    validation_ui.render_validation_result(
                        False,
                        f"❌ Validation error: {str(e)}"
                    )
                    logger.error(f"Validation workflow error: {e}")

        validation_ui.render_validation_button(validation_status, on_click=run_validation)

        # Certificate access
        latest_state = persistence.load_validation_state()
        if latest_state and latest_state.certificate_hash:
            cert_path = validation_config.certificate_output_dir / "validation_certificate.pdf"
            if cert_path.exists():
                validation_ui.render_certificate_access(
                    str(cert_path),
                    latest_state.validation_date
                )

        st.divider()

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
