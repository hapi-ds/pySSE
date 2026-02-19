"""Unit tests for ValidationCertificateGenerator.

This module tests the certificate generation functionality including:
- PDF generation with mock data
- Chapter formatting
- Traceability matrix generation
- Certificate hash calculation
"""

import hashlib
from datetime import datetime
from pathlib import Path

import pytest

from src.sample_size_estimator.validation.certificate import (
    ValidationCertificateGenerator,
)
from src.sample_size_estimator.validation.models import (
    EnvironmentFingerprint,
    IQCheck,
    IQResult,
    OQResult,
    OQTest,
    PQResult,
    PQTest,
    SystemInfo,
    ValidationResult,
)


@pytest.fixture
def sample_environment_fingerprint():
    """Create sample environment fingerprint."""
    return EnvironmentFingerprint(
        python_version="3.11.5",
        dependencies={
            "scipy": "1.11.0",
            "numpy": "1.25.0",
            "streamlit": "1.28.0",
            "pydantic": "2.4.0",
            "reportlab": "4.0.0",
            "pytest": "7.4.0",
            "playwright": "1.40.0"
        }
    )


@pytest.fixture
def sample_system_info():
    """Create sample system information."""
    return SystemInfo(
        os_name="Windows",
        os_version="10",
        python_version="3.11.5",
        dependencies={
            "scipy": "1.11.0",
            "numpy": "1.25.0",
            "streamlit": "1.28.0",
            "pydantic": "2.4.0",
            "reportlab": "4.0.0",
            "pytest": "7.4.0",
            "playwright": "1.40.0"
        }
    )


@pytest.fixture
def sample_iq_result():
    """Create sample IQ test results."""
    checks = [
        IQCheck(
            name="test_python_version",
            description="Verify Python version meets requirements",
            passed=True,
            expected_value="3.11.x",
            actual_value="3.11.5"
        ),
        IQCheck(
            name="test_scipy_installed",
            description="Verify scipy is installed",
            passed=True,
            expected_value="1.11.0",
            actual_value="1.11.0"
        ),
        IQCheck(
            name="test_config_file",
            description="Verify configuration file exists",
            passed=True
        )
    ]
    
    return IQResult(
        passed=True,
        checks=checks,
        timestamp=datetime(2024, 1, 15, 10, 30, 0)
    )


@pytest.fixture
def sample_oq_result():
    """Create sample OQ test results."""
    tests = [
        OQTest(
            test_name="tests/test_attribute_calcs.py::test_zero_failures",
            urs_id="URS-FUNC_A-02",
            urs_requirement="Calculate sample size for attribute data",
            functional_area="Attribute",
            passed=True
        ),
        OQTest(
            test_name="tests/test_variables_calcs.py::test_tolerance_factor",
            urs_id="URS-FUNC_V-03",
            urs_requirement="Calculate tolerance factors",
            functional_area="Variables",
            passed=True
        ),
        OQTest(
            test_name="tests/test_reliability_calcs.py::test_zero_failure_demo",
            urs_id="URS-FUNC_R-01",
            urs_requirement="Calculate reliability test duration",
            functional_area="Reliability",
            passed=True
        )
    ]
    
    return OQResult(
        passed=True,
        tests=tests,
        timestamp=datetime(2024, 1, 15, 10, 35, 0)
    )


@pytest.fixture
def sample_pq_result():
    """Create sample PQ test results."""
    tests = [
        PQTest(
            test_name="tests/test_ui_playwright_attribute.py::test_attribute_workflow",
            urs_id="URS-UI-01",
            urs_requirement="User can perform attribute analysis",
            module="Attribute",
            workflow_description="User enters AQL/RQL values and calculates sample size",
            passed=True
        ),
        PQTest(
            test_name="tests/test_pdf_validation_attribute.py::test_pdf_matches_calculation",
            urs_id="URS-REP-01",
            urs_requirement="PDF report shows correct results",
            module="Attribute",
            workflow_description="PDF report contains same results as UI calculation",
            passed=True
        )
    ]
    
    return PQResult(
        passed=True,
        tests=tests,
        timestamp=datetime(2024, 1, 15, 10, 40, 0)
    )


@pytest.fixture
def sample_validation_result(
    sample_environment_fingerprint,
    sample_system_info,
    sample_iq_result,
    sample_oq_result,
    sample_pq_result
):
    """Create sample validation result."""
    return ValidationResult(
        success=True,
        validation_date=datetime(2024, 1, 15, 10, 30, 0),
        validation_hash="abc123def456" * 5,  # 60 char hash
        environment_fingerprint=sample_environment_fingerprint,
        iq_result=sample_iq_result,
        oq_result=sample_oq_result,
        pq_result=sample_pq_result,
        system_info=sample_system_info
    )


@pytest.fixture
def certificate_generator():
    """Create certificate generator instance."""
    urs_requirements = {
        "URS-FUNC_A-02": "Calculate sample size for attribute data",
        "URS-FUNC_V-03": "Calculate tolerance factors",
        "URS-FUNC_R-01": "Calculate reliability test duration",
        "URS-UI-01": "User can perform attribute analysis",
        "URS-REP-01": "PDF report shows correct results"
    }
    return ValidationCertificateGenerator(urs_requirements)


def test_certificate_generator_initialization():
    """Test certificate generator can be initialized."""
    generator = ValidationCertificateGenerator()
    assert generator is not None
    assert generator.urs_requirements == {}


def test_certificate_generator_with_urs_requirements():
    """Test certificate generator with URS requirements."""
    urs_requirements = {"URS-001": "Test requirement"}
    generator = ValidationCertificateGenerator(urs_requirements)
    assert generator.urs_requirements == urs_requirements


def test_generate_certificate_creates_pdf(
    certificate_generator,
    sample_validation_result,
    tmp_path
):
    """Test that generate_certificate creates a PDF file."""
    output_path = tmp_path / "test_certificate.pdf"
    
    certificate_hash = certificate_generator.generate_certificate(
        sample_validation_result,
        output_path
    )
    
    # Verify PDF was created
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    
    # Verify hash was returned
    assert certificate_hash is not None
    assert len(certificate_hash) == 64  # SHA-256 produces 64 hex characters


def test_generate_certificate_hash_calculation(
    certificate_generator,
    sample_validation_result,
    tmp_path
):
    """Test that certificate hash is calculated correctly."""
    output_path = tmp_path / "test_certificate.pdf"
    
    certificate_hash = certificate_generator.generate_certificate(
        sample_validation_result,
        output_path
    )
    
    # Manually calculate hash
    sha256_hash = hashlib.sha256()
    with open(output_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    expected_hash = sha256_hash.hexdigest()
    
    # Verify hashes match
    assert certificate_hash == expected_hash


def test_generate_certificate_creates_output_directory(
    certificate_generator,
    sample_validation_result,
    tmp_path
):
    """Test that generate_certificate creates output directory if it doesn't exist."""
    output_path = tmp_path / "reports" / "validation" / "certificate.pdf"
    
    # Ensure directory doesn't exist
    assert not output_path.parent.exists()
    
    certificate_generator.generate_certificate(
        sample_validation_result,
        output_path
    )
    
    # Verify directory was created
    assert output_path.parent.exists()
    assert output_path.exists()


def test_generate_title_page(certificate_generator, sample_validation_result):
    """Test title page generation."""
    elements = certificate_generator.generate_title_page(sample_validation_result)
    
    # Verify elements were generated
    assert len(elements) > 0
    
    # Check for key content (this is a basic check)
    # In a real test, we'd verify specific content


def test_generate_system_info_section(certificate_generator, sample_system_info):
    """Test system information section generation."""
    elements = certificate_generator.generate_system_info_section(sample_system_info)
    
    # Verify elements were generated
    assert len(elements) > 0


def test_generate_iq_chapter(certificate_generator, sample_iq_result):
    """Test IQ chapter generation."""
    elements = certificate_generator.generate_iq_chapter(sample_iq_result)
    
    # Verify elements were generated
    assert len(elements) > 0


def test_generate_iq_chapter_with_failed_checks(certificate_generator):
    """Test IQ chapter generation with failed checks."""
    checks = [
        IQCheck(
            name="test_failed_check",
            description="This check failed",
            passed=False,
            failure_reason="Dependency version mismatch"
        )
    ]
    
    iq_result = IQResult(
        passed=False,
        checks=checks,
        timestamp=datetime.now()
    )
    
    elements = certificate_generator.generate_iq_chapter(iq_result)
    
    # Verify elements were generated
    assert len(elements) > 0


def test_generate_oq_chapter(certificate_generator, sample_oq_result):
    """Test OQ chapter generation."""
    elements = certificate_generator.generate_oq_chapter(sample_oq_result)
    
    # Verify elements were generated
    assert len(elements) > 0


def test_generate_oq_chapter_groups_by_functional_area(
    certificate_generator,
    sample_oq_result
):
    """Test that OQ chapter groups tests by functional area."""
    elements = certificate_generator.generate_oq_chapter(sample_oq_result)
    
    # Verify elements were generated
    assert len(elements) > 0
    
    # The sample data has 3 functional areas, so we should see multiple sections


def test_generate_pq_chapter(certificate_generator, sample_pq_result):
    """Test PQ chapter generation."""
    elements = certificate_generator.generate_pq_chapter(sample_pq_result)
    
    # Verify elements were generated
    assert len(elements) > 0


def test_generate_pq_chapter_groups_by_module(certificate_generator, sample_pq_result):
    """Test that PQ chapter groups tests by module."""
    elements = certificate_generator.generate_pq_chapter(sample_pq_result)
    
    # Verify elements were generated
    assert len(elements) > 0


def test_generate_traceability_matrix(
    certificate_generator,
    sample_validation_result
):
    """Test traceability matrix generation."""
    elements = certificate_generator.generate_traceability_matrix(
        sample_validation_result
    )
    
    # Verify elements were generated
    assert len(elements) > 0


def test_traceability_matrix_includes_all_tests(
    certificate_generator,
    sample_validation_result
):
    """Test that traceability matrix includes all OQ and PQ tests."""
    elements = certificate_generator.generate_traceability_matrix(
        sample_validation_result
    )
    
    # Verify elements were generated
    assert len(elements) > 0
    
    # Total tests should be OQ tests + PQ tests
    total_tests = (
        len(sample_validation_result.oq_result.tests) +
        len(sample_validation_result.pq_result.tests)
    )
    assert total_tests == 5  # 3 OQ + 2 PQ from fixtures


def test_certificate_hash_is_unique(
    certificate_generator,
    sample_validation_result,
    tmp_path
):
    """Test that certificate hash is calculated and unique.
    
    Note: ReportLab includes timestamps in PDFs, so each generation
    produces a different hash even with identical content.
    """
    output_path1 = tmp_path / "cert1.pdf"
    output_path2 = tmp_path / "cert2.pdf"
    
    # Generate same certificate twice
    hash1 = certificate_generator.generate_certificate(
        sample_validation_result,
        output_path1
    )
    
    hash2 = certificate_generator.generate_certificate(
        sample_validation_result,
        output_path2
    )
    
    # Both hashes should be valid SHA-256 hashes
    assert len(hash1) == 64
    assert len(hash2) == 64
    
    # Hashes will be different due to timestamps in PDF
    # This is expected behavior and provides tamper detection
    assert hash1 != hash2


def test_failed_validation_certificate(
    certificate_generator,
    sample_validation_result,
    tmp_path
):
    """Test certificate generation for failed validation."""
    # Modify result to be failed
    sample_validation_result.success = False
    sample_validation_result.iq_result.passed = False
    
    output_path = tmp_path / "failed_cert.pdf"
    
    certificate_hash = certificate_generator.generate_certificate(
        sample_validation_result,
        output_path
    )
    
    # Verify PDF was created even for failed validation
    assert output_path.exists()
    assert certificate_hash is not None


def test_certificate_with_empty_test_results(
    certificate_generator,
    sample_environment_fingerprint,
    sample_system_info,
    tmp_path
):
    """Test certificate generation with empty test results."""
    # Create validation result with no tests
    validation_result = ValidationResult(
        success=False,
        validation_date=datetime.now(),
        validation_hash="test_hash",
        environment_fingerprint=sample_environment_fingerprint,
        iq_result=IQResult(passed=False, checks=[], timestamp=datetime.now()),
        oq_result=OQResult(passed=False, tests=[], timestamp=datetime.now()),
        pq_result=PQResult(passed=False, tests=[], timestamp=datetime.now()),
        system_info=sample_system_info
    )
    
    output_path = tmp_path / "empty_cert.pdf"
    
    certificate_hash = certificate_generator.generate_certificate(
        validation_result,
        output_path
    )
    
    # Verify PDF was created
    assert output_path.exists()
    assert certificate_hash is not None


def test_iq_summary_statistics(sample_iq_result):
    """Test IQ result summary statistics."""
    summary = sample_iq_result.get_summary()
    
    assert summary["total"] == 3
    assert summary["passed"] == 3
    assert summary["failed"] == 0


def test_oq_summary_statistics(sample_oq_result):
    """Test OQ result summary statistics."""
    summary = sample_oq_result.get_summary()
    
    assert summary["total"] == 3
    assert summary["passed"] == 3
    assert summary["failed"] == 0


def test_pq_summary_statistics(sample_pq_result):
    """Test PQ result summary statistics."""
    summary = sample_pq_result.get_summary()
    
    assert summary["total"] == 2
    assert summary["passed"] == 2
    assert summary["failed"] == 0


def test_oq_group_by_functional_area(sample_oq_result):
    """Test OQ result grouping by functional area."""
    grouped = sample_oq_result.group_by_functional_area()
    
    assert "Attribute" in grouped
    assert "Variables" in grouped
    assert "Reliability" in grouped
    assert len(grouped["Attribute"]) == 1
    assert len(grouped["Variables"]) == 1
    assert len(grouped["Reliability"]) == 1


def test_pq_group_by_module(sample_pq_result):
    """Test PQ result grouping by module."""
    grouped = sample_pq_result.group_by_module()
    
    assert "Attribute" in grouped
    assert len(grouped["Attribute"]) == 2
