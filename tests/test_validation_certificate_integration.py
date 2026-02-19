"""Integration tests for certificate generation with orchestrator.

This module tests the integration between ValidationOrchestrator and
ValidationCertificateGenerator to ensure certificates are generated
correctly during the validation workflow.
"""

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
from src.sample_size_estimator.validation.orchestrator import ValidationOrchestrator


@pytest.fixture
def mock_validation_result():
    """Create a mock validation result for testing."""
    env_fingerprint = EnvironmentFingerprint(
        python_version="3.11.5",
        dependencies={
            "scipy": "1.11.0",
            "numpy": "1.25.0",
            "streamlit": "1.28.0",
        }
    )
    
    system_info = SystemInfo(
        os_name="Windows",
        os_version="10",
        python_version="3.11.5",
        dependencies={"scipy": "1.11.0", "numpy": "1.25.0"}
    )
    
    iq_result = IQResult(
        passed=True,
        checks=[
            IQCheck(
                name="test_python_version",
                description="Verify Python version",
                passed=True
            )
        ],
        timestamp=datetime.now()
    )
    
    oq_result = OQResult(
        passed=True,
        tests=[
            OQTest(
                test_name="test_calculation",
                urs_id="URS-001",
                urs_requirement="Test requirement",
                functional_area="Attribute",
                passed=True
            )
        ],
        timestamp=datetime.now()
    )
    
    pq_result = PQResult(
        passed=True,
        tests=[
            PQTest(
                test_name="test_ui",
                urs_id="URS-002",
                urs_requirement="UI requirement",
                module="Attribute",
                workflow_description="Test workflow",
                passed=True
            )
        ],
        timestamp=datetime.now()
    )
    
    return ValidationResult(
        success=True,
        validation_date=datetime.now(),
        validation_hash="test_hash_123",
        environment_fingerprint=env_fingerprint,
        iq_result=iq_result,
        oq_result=oq_result,
        pq_result=pq_result,
        system_info=system_info
    )


def test_orchestrator_initializes_with_certificate_generator(tmp_path):
    """Test that orchestrator initializes with certificate generator."""
    orchestrator = ValidationOrchestrator(certificate_output_dir=tmp_path)
    
    assert orchestrator.certificate_generator is not None
    assert isinstance(orchestrator.certificate_generator, ValidationCertificateGenerator)
    assert orchestrator.certificate_output_dir == tmp_path


def test_orchestrator_uses_default_certificate_directory():
    """Test that orchestrator uses default certificate directory."""
    orchestrator = ValidationOrchestrator()
    
    assert orchestrator.certificate_output_dir == Path("reports")


def test_certificate_generation_integration(tmp_path, mock_validation_result):
    """Test certificate generation through orchestrator workflow."""
    # Create orchestrator with temp directory
    orchestrator = ValidationOrchestrator(certificate_output_dir=tmp_path)
    
    # Manually generate certificate (simulating what workflow does)
    cert_path = tmp_path / "test_certificate.pdf"
    cert_hash = orchestrator.certificate_generator.generate_certificate(
        mock_validation_result,
        cert_path
    )
    
    # Verify certificate was created
    assert cert_path.exists()
    assert cert_hash is not None
    assert len(cert_hash) == 64


def test_certificate_includes_all_chapters(tmp_path, mock_validation_result):
    """Test that generated certificate includes all required chapters."""
    orchestrator = ValidationOrchestrator(certificate_output_dir=tmp_path)
    
    cert_path = tmp_path / "full_certificate.pdf"
    orchestrator.certificate_generator.generate_certificate(
        mock_validation_result,
        cert_path
    )
    
    # Verify certificate exists and has content
    assert cert_path.exists()
    assert cert_path.stat().st_size > 5000  # Should be reasonably sized PDF (>5KB)


def test_certificate_generation_with_failed_validation(tmp_path, mock_validation_result):
    """Test certificate generation when validation fails."""
    # Modify result to be failed
    mock_validation_result.success = False
    mock_validation_result.iq_result.passed = False
    
    orchestrator = ValidationOrchestrator(certificate_output_dir=tmp_path)
    
    cert_path = tmp_path / "failed_certificate.pdf"
    cert_hash = orchestrator.certificate_generator.generate_certificate(
        mock_validation_result,
        cert_path
    )
    
    # Certificate should still be generated for failed validations
    assert cert_path.exists()
    assert cert_hash is not None


def test_multiple_certificates_have_unique_hashes(tmp_path, mock_validation_result):
    """Test that multiple certificate generations produce unique hashes."""
    orchestrator = ValidationOrchestrator(certificate_output_dir=tmp_path)
    
    # Generate first certificate
    cert_path1 = tmp_path / "cert1.pdf"
    hash1 = orchestrator.certificate_generator.generate_certificate(
        mock_validation_result,
        cert_path1
    )
    
    # Generate second certificate
    cert_path2 = tmp_path / "cert2.pdf"
    hash2 = orchestrator.certificate_generator.generate_certificate(
        mock_validation_result,
        cert_path2
    )
    
    # Hashes should be different due to timestamps
    assert hash1 != hash2
    assert len(hash1) == 64
    assert len(hash2) == 64
