"""Integration tests for Sample Size Estimator.

This module provides end-to-end integration tests that verify:
- Complete workflows for each calculation module
- Report generation with real calculations
- Validation state verification
- Cross-module interactions

Requirements: REQ-24 (Operational Qualification Test Suite)
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import os


# ============================================================================
# Attribute Module Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.attribute
@pytest.mark.urs("URS-FUNC_A-01", "URS-FUNC_A-02", "URS-FUNC_A-03")
class TestAttributeModuleIntegration:
    """Integration tests for attribute calculations end-to-end workflow."""
    
    def test_attribute_zero_failures_complete_workflow(self):
        """Test complete workflow: input validation → calculation → result.
        
        Validates: Requirements 1.1, 1.2, 1.3
        """
        from sample_size_estimator.models import AttributeInput
        from sample_size_estimator.calculations.attribute_calcs import calculate_attribute
        
        # Create valid input
        input_data = AttributeInput(
            confidence=95.0,
            reliability=90.0,
            allowable_failures=0
        )
        
        # Execute calculation
        result = calculate_attribute(input_data)
        
        # Verify result structure and values
        assert hasattr(result, 'sample_size')
        assert hasattr(result, 'allowable_failures')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'reliability')
        assert hasattr(result, 'method')
        
        assert result.sample_size == 29  # Known value for C=95%, R=90%
        assert result.allowable_failures == 0
        assert result.confidence == 95.0
        assert result.reliability == 90.0
        assert result.method == "success_run"
    
    def test_attribute_with_failures_complete_workflow(self):
        """Test complete workflow with allowable failures.
        
        Validates: Requirements 2.1, 2.2, 2.3, 2.4
        """
        from sample_size_estimator.models import AttributeInput
        from sample_size_estimator.calculations.attribute_calcs import calculate_attribute
        
        # Create input with failures
        input_data = AttributeInput(
            confidence=95.0,
            reliability=90.0,
            allowable_failures=2
        )
        
        # Execute calculation
        result = calculate_attribute(input_data)
        
        # Verify result
        assert result.sample_size == 61  # Known value for C=95%, R=90%, c=2
        assert result.allowable_failures == 2
        assert result.method == "binomial"
    
    def test_attribute_sensitivity_analysis_workflow(self):
        """Test sensitivity analysis workflow.
        
        Validates: Requirements 3.1, 3.2, 3.4
        """
        from sample_size_estimator.models import AttributeInput
        from sample_size_estimator.calculations.attribute_calcs import calculate_attribute
        
        # Create input without specifying failures
        input_data = AttributeInput(
            confidence=95.0,
            reliability=90.0,
            allowable_failures=None
        )
        
        # Execute calculation
        result = calculate_attribute(input_data)
        
        # Verify sensitivity result structure
        assert hasattr(result, 'results')
        assert len(result.results) == 4
        
        # Verify each result has correct c value
        for i, res in enumerate(result.results):
            assert res.allowable_failures == i
            assert res.confidence == 95.0
            assert res.reliability == 90.0
            assert res.sample_size > 0
        
        # Verify sample sizes are increasing
        sample_sizes = [res.sample_size for res in result.results]
        assert sample_sizes == sorted(sample_sizes)


# ============================================================================
# Variables Module Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.variables
@pytest.mark.urs("URS-FUNC_V-01", "URS-FUNC_V-02", "URS-FUNC_V-03")
class TestVariablesModuleIntegration:
    """Integration tests for variables calculations end-to-end workflow."""
    
    def test_variables_complete_workflow_with_spec_limits(self):
        """Test complete workflow with specification limits.
        
        Validates: Requirements 4, 5, 6, 7
        """
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        # Create input with spec limits
        input_data = VariablesInput(
            confidence=95.0,
            reliability=90.0,
            sample_size=30,
            sample_mean=10.0,
            sample_std=1.0,
            lsl=7.0,
            usl=13.0,
            sided="two"
        )
        
        # Execute calculation
        result = calculate_variables(input_data)
        
        # Verify all components calculated
        assert result.tolerance_factor > 0
        assert result.lower_tolerance_limit is not None
        assert result.upper_tolerance_limit is not None
        assert result.ppk is not None
        assert result.pass_fail in ["PASS", "FAIL"]
        assert result.margin_lower is not None
        assert result.margin_upper is not None
        
        # Verify Ppk calculation (known value)
        assert abs(result.ppk - 1.0) < 0.01
        
        # Verify tolerance limits are within spec limits (should PASS)
        assert result.lower_tolerance_limit >= input_data.lsl
        assert result.upper_tolerance_limit <= input_data.usl
        assert result.pass_fail == "PASS"
    
    def test_variables_one_sided_workflow(self):
        """Test one-sided tolerance limit workflow.
        
        Validates: Requirements 4.1, 5.3
        """
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        # Create one-sided input
        input_data = VariablesInput(
            confidence=95.0,
            reliability=90.0,
            sample_size=30,
            sample_mean=10.0,
            sample_std=1.0,
            usl=15.0,
            sided="one"
        )
        
        # Execute calculation
        result = calculate_variables(input_data)
        
        # Verify one-sided results
        assert result.tolerance_factor > 0
        assert result.lower_tolerance_limit is None  # One-sided upper only
        assert result.upper_tolerance_limit is not None
        assert result.upper_tolerance_limit > input_data.sample_mean
    
    def test_variables_fail_scenario(self):
        """Test scenario where tolerance limits exceed spec limits.
        
        Validates: Requirements 6.3
        """
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        # Create input with tight spec limits that will fail
        input_data = VariablesInput(
            confidence=95.0,
            reliability=90.0,
            sample_size=10,  # Small sample = large tolerance factor
            sample_mean=10.0,
            sample_std=2.0,  # Large std dev
            lsl=9.0,  # Very tight limits
            usl=11.0,
            sided="two"
        )
        
        # Execute calculation
        result = calculate_variables(input_data)
        
        # Should fail due to tight limits
        assert result.pass_fail == "FAIL"
        assert (result.margin_lower < 0) or (result.margin_upper < 0)


# ============================================================================
# Non-Normal Module Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.non_normal
@pytest.mark.urs("URS-FUNC_N-01", "URS-FUNC_N-02", "URS-FUNC_N-03")
class TestNonNormalModuleIntegration:
    """Integration tests for non-normal calculations end-to-end workflow."""
    
    def test_complete_normality_assessment_workflow(self):
        """Test complete workflow: outlier detection → normality testing.
        
        Validates: Requirements 8, 9
        """
        from sample_size_estimator.calculations.non_normal_calcs import (
            detect_outliers,
            test_normality
        )
        import numpy as np
        
        # Create dataset with outliers
        np.random.seed(42)
        normal_data = np.random.normal(10, 2, 50).tolist()
        data_with_outliers = normal_data + [50.0, 60.0]  # Add clear outliers
        
        # Step 1: Detect outliers
        outlier_values, outlier_indices = detect_outliers(data_with_outliers)
        
        # Verify outliers detected
        assert len(outlier_values) >= 2
        assert 50.0 in outlier_values or 60.0 in outlier_values
        
        # Step 2: Test normality on original data
        normality_result = test_normality(data_with_outliers)
        
        # Verify normality test structure
        assert hasattr(normality_result, 'shapiro_wilk_statistic')
        assert hasattr(normality_result, 'shapiro_wilk_pvalue')
        assert hasattr(normality_result, 'anderson_darling_statistic')
        assert hasattr(normality_result, 'anderson_darling_critical_values')
        assert hasattr(normality_result, 'is_normal')
        assert hasattr(normality_result, 'interpretation')
        
        # With outliers, data may fail normality
        assert isinstance(normality_result.is_normal, bool)
        assert len(normality_result.interpretation) > 0
    
    def test_transformation_workflow(self):
        """Test complete transformation workflow.
        
        Validates: Requirements 11, 12, 13
        """
        from sample_size_estimator.calculations.non_normal_calcs import (
            apply_transformation,
            back_transform_log
        )
        import numpy as np
        
        # Create positive data suitable for log transformation
        np.random.seed(42)
        data = np.random.exponential(scale=2.0, size=50).tolist()
        
        # Apply log transformation
        transform_result = apply_transformation(data, "log")
        
        # Verify transformation result structure
        assert transform_result.method == "log"
        assert len(transform_result.transformed_data) == len(data)
        assert transform_result.normality_after is not None
        
        # Verify back-transformation works
        original_value = data[0]
        transformed_value = transform_result.transformed_data[0]
        back_transformed = back_transform_log(transformed_value)
        
        assert abs(back_transformed - original_value) < 1e-9
    
    def test_boxcox_transformation_workflow(self):
        """Test Box-Cox transformation with lambda optimization.
        
        Validates: Requirements 11.1, 11.4, 13.2
        """
        from sample_size_estimator.calculations.non_normal_calcs import (
            apply_transformation,
            back_transform_boxcox
        )
        import numpy as np
        
        # Create positive data
        np.random.seed(42)
        data = np.random.uniform(1.0, 100.0, 50).tolist()
        
        # Apply Box-Cox transformation
        transform_result = apply_transformation(data, "boxcox")
        
        # Verify lambda parameter calculated
        assert transform_result.method == "boxcox"
        assert transform_result.lambda_param is not None
        assert len(transform_result.transformed_data) == len(data)
        
        # Verify back-transformation
        original_value = data[0]
        transformed_value = transform_result.transformed_data[0]
        back_transformed = back_transform_boxcox(
            transformed_value,
            transform_result.lambda_param
        )
        
        assert abs(back_transformed - original_value) < 1e-6
    
    def test_wilks_nonparametric_workflow(self):
        """Test Wilks' non-parametric method workflow.
        
        Validates: Requirements 14.2
        """
        from sample_size_estimator.calculations.non_normal_calcs import (
            calculate_wilks_limits
        )
        
        # Create dataset
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        
        # Calculate Wilks' limits
        lower, upper = calculate_wilks_limits(data, 95.0, 90.0)
        
        # Verify limits are min/max
        assert lower == min(data)
        assert upper == max(data)


# ============================================================================
# Reliability Module Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.reliability
@pytest.mark.urs("URS-FUNC_R-01", "URS-FUNC_R-02")
class TestReliabilityModuleIntegration:
    """Integration tests for reliability calculations end-to-end workflow."""
    
    def test_zero_failure_demonstration_workflow(self):
        """Test zero-failure demonstration workflow.
        
        Validates: Requirements 15.1, 15.2
        """
        from sample_size_estimator.models import ReliabilityInput
        from sample_size_estimator.calculations.reliability_calcs import (
            calculate_reliability
        )
        
        # Create input for zero-failure test
        input_data = ReliabilityInput(
            confidence=95.0,
            reliability=90.0,
            failures=0
        )
        
        # Execute calculation
        result = calculate_reliability(input_data)
        
        # Verify result structure
        assert result.test_duration > 0
        assert result.acceleration_factor is None  # No AF inputs provided
        assert "zero-failure" in result.method.lower()
        
        # Verify chi-squared value is reasonable (should be ~5.991 for 95% confidence)
        assert abs(result.test_duration - 5.991) < 0.01
    
    def test_acceleration_factor_workflow(self):
        """Test complete workflow with acceleration factor.
        
        Validates: Requirements 15, 16
        """
        from sample_size_estimator.models import ReliabilityInput
        from sample_size_estimator.calculations.reliability_calcs import (
            calculate_reliability
        )
        
        # Create input with acceleration parameters
        input_data = ReliabilityInput(
            confidence=95.0,
            reliability=90.0,
            failures=0,
            activation_energy=0.7,
            use_temperature=298.15,  # 25°C
            test_temperature=358.15  # 85°C
        )
        
        # Execute calculation
        result = calculate_reliability(input_data)
        
        # Verify both duration and AF calculated
        assert result.test_duration > 0
        assert result.acceleration_factor is not None
        assert result.acceleration_factor > 1.0  # Higher temp = acceleration
        assert "arrhenius" in result.method.lower()
        
        # Verify AF is reasonable for these parameters (60°C difference)
        # Ea=0.7eV, T_use=298K, T_test=358K gives AF ≈ 96
        assert 90.0 < result.acceleration_factor < 100.0
    
    def test_temperature_validation_workflow(self):
        """Test that temperature validation works in workflow.
        
        Validates: Requirements 16.4
        """
        from sample_size_estimator.models import ReliabilityInput
        from sample_size_estimator.calculations.reliability_calcs import (
            calculate_acceleration_factor
        )
        
        # Test that test temp must be > use temp
        with pytest.raises(ValueError, match="greater than use temperature"):
            calculate_acceleration_factor(
                activation_energy=0.7,
                use_temperature=358.15,  # Higher
                test_temperature=298.15  # Lower - should fail
            )


# ============================================================================
# Report Generation Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.reports
@pytest.mark.urs("URS-VAL-01", "URS-VAL-02")
class TestReportGenerationIntegration:
    """Integration tests for report generation with real calculations."""
    
    def test_attribute_calculation_report_generation(self):
        """Test generating report from attribute calculation.
        
        Validates: Requirements 20, 21
        """
        from sample_size_estimator.models import AttributeInput, CalculationReport
        from sample_size_estimator.calculations.attribute_calcs import calculate_attribute
        from sample_size_estimator.reports import generate_calculation_report
        from sample_size_estimator.validation import calculate_file_hash
        
        # Perform calculation
        input_data = AttributeInput(
            confidence=95.0,
            reliability=90.0,
            allowable_failures=0
        )
        result = calculate_attribute(input_data)
        
        # Calculate engine hash
        engine_file = "src/sample_size_estimator/calculations/__init__.py"
        if os.path.exists(engine_file):
            engine_hash = calculate_file_hash(engine_file)
        else:
            engine_hash = "test_hash_123"
        
        # Create report data
        report_data = CalculationReport(
            timestamp=datetime.now(),
            module="attribute",
            inputs=input_data.model_dump(),
            results=result.model_dump(),
            engine_hash=engine_hash,
            validated_state=False,  # No validated hash set
            app_version="1.0.0"
        )
        
        # Generate report
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_report.pdf")
            generated_path = generate_calculation_report(report_data, output_path)
            
            # Verify report created
            assert os.path.exists(generated_path)
            assert os.path.getsize(generated_path) > 0
    
    def test_variables_calculation_report_generation(self):
        """Test generating report from variables calculation.
        
        Validates: Requirements 20, 21
        """
        from sample_size_estimator.models import VariablesInput, CalculationReport
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        from sample_size_estimator.reports import generate_calculation_report
        
        # Perform calculation
        input_data = VariablesInput(
            confidence=95.0,
            reliability=90.0,
            sample_size=30,
            sample_mean=10.0,
            sample_std=1.0,
            lsl=7.0,
            usl=13.0,
            sided="two"
        )
        result = calculate_variables(input_data)
        
        # Create report data
        report_data = CalculationReport(
            timestamp=datetime.now(),
            module="variables",
            inputs=input_data.model_dump(),
            results=result.model_dump(),
            engine_hash="test_hash_456",
            validated_state=True,  # Simulating validated state
            app_version="1.0.0"
        )
        
        # Generate report
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_variables_report.pdf")
            generated_path = generate_calculation_report(report_data, output_path)
            
            # Verify report created
            assert os.path.exists(generated_path)
            assert os.path.getsize(generated_path) > 0


# ============================================================================
# Validation State Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.validation
@pytest.mark.urs("URS-VAL-03")
class TestValidationStateIntegration:
    """Integration tests for validation state verification."""
    
    def test_validation_state_workflow(self):
        """Test complete validation state verification workflow.
        
        Validates: Requirements 21.1, 21.3, 21.4, 21.5
        """
        from sample_size_estimator.validation import (
            calculate_file_hash,
            verify_validation_state,
            get_engine_validation_info
        )
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write("# Test calculation engine\n")
            f.write("def test_function():\n")
            f.write("    return 42\n")
            test_file = f.name
        
        try:
            # Calculate hash
            hash1 = calculate_file_hash(test_file)
            assert len(hash1) == 64  # SHA-256 produces 64 hex characters
            
            # Calculate again - should be deterministic
            hash2 = calculate_file_hash(test_file)
            assert hash1 == hash2
            
            # Test validation with matching hash
            is_valid, message = verify_validation_state(hash1, hash1)
            assert is_valid is True
            assert "YES" in message
            
            # Test validation with non-matching hash
            is_valid, message = verify_validation_state(hash1, "different_hash")
            assert is_valid is False
            assert "UNVERIFIED CHANGE" in message
            
            # Test validation with no validated hash
            is_valid, message = verify_validation_state(hash1, None)
            assert is_valid is False
            assert "No validated hash" in message
            
            # Test complete validation info
            validation_info = get_engine_validation_info(test_file, hash1)
            assert validation_info['current_hash'] == hash1
            assert validation_info['validated_hash'] == hash1
            assert validation_info['is_validated'] is True
            
        finally:
            # Cleanup
            os.unlink(test_file)
    
    def test_validation_state_in_report(self):
        """Test that validation state is correctly included in reports.
        
        Validates: Requirements 20.6, 21.2
        """
        from sample_size_estimator.models import CalculationReport
        from sample_size_estimator.reports import generate_calculation_report
        
        # Create report with validated state
        report_data_validated = CalculationReport(
            timestamp=datetime.now(),
            module="attribute",
            inputs={"confidence": 95.0, "reliability": 90.0},
            results={"sample_size": 29},
            engine_hash="abc123",
            validated_state=True,
            app_version="1.0.0"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "validated_report.pdf")
            generate_calculation_report(report_data_validated, output_path)
            assert os.path.exists(output_path)
            
            # Create report with unvalidated state
            report_data_unvalidated = CalculationReport(
                timestamp=datetime.now(),
                module="attribute",
                inputs={"confidence": 95.0, "reliability": 90.0},
                results={"sample_size": 29},
                engine_hash="abc123",
                validated_state=False,
                app_version="1.0.0"
            )
            
            output_path2 = os.path.join(tmpdir, "unvalidated_report.pdf")
            generate_calculation_report(report_data_unvalidated, output_path2)
            assert os.path.exists(output_path2)


# ============================================================================
# Cross-Module Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
class TestCrossModuleIntegration:
    """Integration tests that span multiple modules."""
    
    def test_complete_application_workflow(self):
        """Test a complete workflow using multiple modules.
        
        This simulates a user performing multiple calculations in sequence.
        """
        from sample_size_estimator.models import (
            AttributeInput,
            VariablesInput,
            CalculationReport
        )
        from sample_size_estimator.calculations.attribute_calcs import calculate_attribute
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        from sample_size_estimator.reports import generate_calculation_report
        
        # Step 1: Attribute calculation
        attr_input = AttributeInput(
            confidence=95.0,
            reliability=90.0,
            allowable_failures=None  # Sensitivity analysis
        )
        attr_result = calculate_attribute(attr_input)
        assert len(attr_result.results) == 4
        
        # Step 2: Variables calculation
        var_input = VariablesInput(
            confidence=95.0,
            reliability=90.0,
            sample_size=30,
            sample_mean=10.0,
            sample_std=1.0,
            lsl=7.0,
            usl=13.0,
            sided="two"
        )
        var_result = calculate_variables(var_input)
        assert var_result.ppk is not None
        
        # Step 3: Generate reports for both
        with tempfile.TemporaryDirectory() as tmpdir:
            # Attribute report
            attr_report = CalculationReport(
                timestamp=datetime.now(),
                module="attribute",
                inputs=attr_input.model_dump(),
                results={"results": [r.model_dump() for r in attr_result.results]},
                engine_hash="test_hash",
                validated_state=False,
                app_version="1.0.0"
            )
            attr_report_path = os.path.join(tmpdir, "attr_report.pdf")
            generate_calculation_report(attr_report, attr_report_path)
            assert os.path.exists(attr_report_path)
            
            # Variables report
            var_report = CalculationReport(
                timestamp=datetime.now(),
                module="variables",
                inputs=var_input.model_dump(),
                results=var_result.model_dump(),
                engine_hash="test_hash",
                validated_state=False,
                app_version="1.0.0"
            )
            var_report_path = os.path.join(tmpdir, "var_report.pdf")
            generate_calculation_report(var_report, var_report_path)
            assert os.path.exists(var_report_path)
    
    def test_error_handling_across_modules(self):
        """Test that errors are properly handled across module boundaries."""
        from sample_size_estimator.models import VariablesInput
        from pydantic import ValidationError
        
        # Test that invalid input is caught at model level
        with pytest.raises(ValidationError):
            VariablesInput(
                confidence=150.0,  # Invalid - > 100
                reliability=90.0,
                sample_size=30,
                sample_mean=10.0,
                sample_std=1.0,
                sided="two"
            )
        
        # Test that LSL > USL is caught
        with pytest.raises(ValidationError):
            VariablesInput(
                confidence=95.0,
                reliability=90.0,
                sample_size=30,
                sample_mean=10.0,
                sample_std=1.0,
                lsl=15.0,  # Greater than USL
                usl=10.0,
                sided="two"
            )
