"""Validation orchestration module.

This module provides the ValidationOrchestrator class for executing the complete
IQ/OQ/PQ validation workflow, including test execution, result parsing, and
state management.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

from .certificate import ValidationCertificateGenerator
from .models import (
    EnvironmentFingerprint,
    IQCheck,
    IQResult,
    OQResult,
    OQTest,
    PQResult,
    PQTest,
    SystemInfo,
    ValidationConfig,
    ValidationResult,
)
from .state_manager import ValidationStateManager


class ValidationOrchestrator:
    """Orchestrates the complete validation workflow including IQ/OQ/PQ phases.
    
    This class:
    - Executes IQ/OQ/PQ tests in sequence using pytest
    - Parses pytest JSON output to extract test results
    - Extracts URS markers from test metadata
    - Provides progress callback support for UI updates
    - Manages subprocess execution for test runs
    - Stops workflow if any phase fails
    - Generates validation certificate PDF
    - Returns ValidationResult with complete test results
    
    Validates: Requirements 6.1-6.5, 7.1-7.7, 8.1-8.8, 9.1-9.7
    """

    def __init__(self, certificate_output_dir: Path | None = None):
        """Initialize the validation orchestrator.
        
        Args:
            certificate_output_dir: Directory for certificate output.
                                   Defaults to 'reports' if not specified.
        """
        self.certificate_output_dir = certificate_output_dir or Path("reports")
        self.certificate_generator = ValidationCertificateGenerator()

    def execute_validation_workflow(
            self,
            progress_callback: Callable[[str, float], None] | None = None,
            generate_certificate: bool = True
        ) -> ValidationResult:
            """Execute complete IQ/OQ/PQ validation workflow.

            This method:
            1. Executes IQ tests first
            2. If IQ passes, executes OQ tests
            3. If OQ passes, executes PQ tests
            4. Stops workflow if any phase fails
            5. Calls progress_callback with phase name and progress percentage (0.0-1.0)
            6. Generates validation certificate if requested
            7. Returns ValidationResult with all test results

            Args:
                progress_callback: Optional callback for progress updates
                                  (phase_name, progress_percentage as float 0.0-1.0)
                generate_certificate: Whether to generate certificate PDF (default: True)

            Returns:
                ValidationResult with overall status and detailed results

            Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5
            """
            if progress_callback:
                progress_callback("Starting validation", 0.0)

            # Execute IQ tests
            if progress_callback:
                progress_callback("IQ", 0.10)

            iq_result = self.execute_iq_tests()

            if progress_callback:
                progress_callback("IQ", 0.33)

            # Stop if IQ fails
            if not iq_result.passed:
                return self._create_failed_result(
                    iq_result=iq_result,
                    oq_result=None,
                    pq_result=None
                )

            # Execute OQ tests
            if progress_callback:
                progress_callback("OQ", 0.40)

            oq_result = self.execute_oq_tests()

            if progress_callback:
                progress_callback("OQ", 0.66)

            # Stop if OQ fails
            if not oq_result.passed:
                return self._create_failed_result(
                    iq_result=iq_result,
                    oq_result=oq_result,
                    pq_result=None
                )

            # Execute PQ tests
            if progress_callback:
                progress_callback("PQ", 0.70)

            pq_result = self.execute_pq_tests()

            if progress_callback:
                progress_callback("PQ", 0.90)

            # Create final result
            result = self._create_result(
                success=pq_result.passed,
                iq_result=iq_result,
                oq_result=oq_result,
                pq_result=pq_result
            )

            # Generate certificate if requested (regardless of pass/fail)
            if generate_certificate:
                if progress_callback:
                    progress_callback("Generating certificate", 0.95)

                try:
                    # Generate certificate with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cert_filename = f"validation_certificate_{timestamp}.pdf"
                    cert_path = self.certificate_output_dir / cert_filename

                    # Generate certificate
                    cert_hash = self.certificate_generator.generate_certificate(
                        result,
                        cert_path
                    )

                    # Update result with certificate info
                    result.certificate_path = cert_path
                    result.certificate_hash = cert_hash

                    # Also save as "latest" for easy access
                    latest_path = self.certificate_output_dir / "validation_certificate_latest.pdf"
                    cert_hash_latest = self.certificate_generator.generate_certificate(
                        result,
                        latest_path
                    )

                except Exception as e:
                    # Log error but don't fail validation
                    print(f"Warning: Failed to generate certificate: {e}")

            if progress_callback:
                progress_callback("Complete", 1.0)

            return result


    def execute_iq_tests(self) -> IQResult:
        """Execute Installation Qualification tests.
        
        This method:
        1. Runs pytest with -m iq marker
        2. Uses --json-report to get structured output
        3. Parses test results to extract IQ checks
        4. Maps test results to IQCheck objects
        
        Returns:
            IQResult with test results and status
        
        Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
        """
        # Run pytest with IQ marker
        result = self._run_pytest_with_marker("iq")
        
        # Parse results
        checks = self._parse_iq_results(result)
        
        # Determine overall pass/fail
        passed = all(check.passed for check in checks)
        
        return IQResult(
            passed=passed,
            checks=checks,
            timestamp=datetime.now()
        )

    def execute_oq_tests(self) -> OQResult:
        """Execute Operational Qualification tests.
        
        This method:
        1. Runs pytest with -m oq marker
        2. Uses --json-report to get structured output
        3. Parses test results to extract OQ tests
        4. Extracts URS markers from test metadata
        5. Maps tests to functional areas
        
        Returns:
            OQResult with test results and URS traceability
        
        Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8
        """
        # Run pytest with OQ marker
        result = self._run_pytest_with_marker("oq")
        
        # Parse results
        tests = self._parse_oq_results(result)
        
        # Determine overall pass/fail
        passed = all(test.passed for test in tests)
        
        return OQResult(
            passed=passed,
            tests=tests,
            timestamp=datetime.now()
        )

    def execute_pq_tests(self) -> PQResult:
        """Execute Performance Qualification tests.
        
        This method:
        1. Runs pytest with -m pq marker
        2. Uses --json-report to get structured output
        3. Parses test results to extract PQ tests
        4. Extracts URS markers from test metadata
        5. Maps tests to analysis modules
        
        Returns:
            PQResult with UI test results and URS traceability
        
        Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7
        """
        # Run pytest with PQ marker
        result = self._run_pytest_with_marker("pq")
        
        # Parse results
        tests = self._parse_pq_results(result)
        
        # Determine overall pass/fail
        passed = all(test.passed for test in tests)
        
        return PQResult(
            passed=passed,
            tests=tests,
            timestamp=datetime.now()
        )

    def _run_pytest_with_marker(self, marker: str) -> dict:
        """Run pytest with specified marker and return parsed results.
        
        Args:
            marker: Pytest marker to filter tests (iq, oq, or pq)
        
        Returns:
            Dictionary containing parsed pytest results
        
        Raises:
            RuntimeError: If pytest execution fails
        """
        try:
            # Run pytest with marker and verbose output
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "-m",
                marker,
                "-v",
                "--tb=short"
            ]
            
            # Set timeout based on marker (PQ tests take much longer due to Playwright)
            timeout = 600 if marker == "pq" else 300  # 10 minutes for PQ, 5 for IQ/OQ
            
            # Execute pytest
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Parse output to extract test results
            report = self._parse_pytest_output(process.stdout, process.stderr, process.returncode)
            return report
        
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Pytest execution timed out for marker: {marker}")
        
        except Exception as e:
            raise RuntimeError(f"Failed to run pytest with marker {marker}: {str(e)}")

    def _parse_pytest_output(self, stdout: str, stderr: str, returncode: int) -> dict:
        """Parse pytest verbose output to extract test results.
        
        Args:
            stdout: Pytest stdout
            stderr: Pytest stderr
            returncode: Pytest return code
        
        Returns:
            Dictionary with tests list
        """
        tests = []
        
        # Parse test results from output
        lines = stdout.split("\n")
        
        for line in lines:
            # Look for test result lines in verbose format
            # Format: tests/test_file.py::test_name PASSED
            # or: tests/test_file.py::TestClass::test_name FAILED
            if "::" in line and any(status in line for status in ["PASSED", "FAILED", "SKIPPED", "ERROR"]):
                # Extract nodeid (everything before the status)
                parts = line.split()
                if len(parts) >= 2:
                    nodeid = parts[0]
                    
                    # Determine outcome
                    if "PASSED" in line:
                        outcome = "passed"
                    elif "FAILED" in line:
                        outcome = "failed"
                    elif "SKIPPED" in line:
                        outcome = "skipped"
                    else:
                        outcome = "error"
                    
                    # Extract URS markers from source file
                    urs_markers = self._extract_urs_from_source(nodeid)
                    
                    test_dict = {
                        "nodeid": nodeid,
                        "outcome": outcome,
                        "urs_markers": urs_markers,
                        "call": {
                            "longrepr": ""
                        }
                    }
                    
                    tests.append(test_dict)
        
        return {"tests": tests}

    def _parse_iq_results(self, report: dict) -> list[IQCheck]:
        """Parse IQ test results from pytest JSON report.
        
        Args:
            report: Pytest JSON report dictionary
        
        Returns:
            List of IQCheck objects
        """
        checks = []
        
        # Get tests from report
        tests = report.get("tests", [])
        
        for test in tests:
            # Extract test information
            test_name = test.get("nodeid", "Unknown test").split("::")[-1]
            outcome = test.get("outcome", "failed")
            
            # Extract description from docstring if available
            description = self._extract_test_description(test)
            
            # Create IQCheck
            check = IQCheck(
                name=test_name,
                description=description,
                passed=(outcome == "passed"),
                expected_value=None,
                actual_value=None,
                failure_reason=self._extract_failure_reason(test) if outcome != "passed" else None
            )
            
            checks.append(check)
        
        return checks

    def _parse_oq_results(self, report: dict) -> list[OQTest]:
        """Parse OQ test results from pytest JSON report.
        
        Args:
            report: Pytest JSON report dictionary
        
        Returns:
            List of OQTest objects
        """
        tests = []
        
        # Get tests from report
        test_results = report.get("tests", [])
        
        for test in test_results:
            # Extract test information
            test_name = test.get("nodeid", "Unknown test")
            outcome = test.get("outcome", "failed")
            
            # Extract URS markers
            urs_ids = self._extract_urs_markers(test)
            urs_id = urs_ids[0] if urs_ids else "URS-UNKNOWN"
            
            # Determine functional area from test path
            functional_area = self._determine_functional_area(test_name)
            
            # Create OQTest
            oq_test = OQTest(
                test_name=test_name,
                urs_id=urs_id,
                urs_requirement=f"Requirement {urs_id}",
                functional_area=functional_area,
                passed=(outcome == "passed"),
                failure_reason=self._extract_failure_reason(test) if outcome != "passed" else None
            )
            
            tests.append(oq_test)
        
        return tests

    def _parse_pq_results(self, report: dict) -> list[PQTest]:
        """Parse PQ test results from pytest JSON report.
        
        Args:
            report: Pytest JSON report dictionary
        
        Returns:
            List of PQTest objects
        """
        tests = []
        
        # Get tests from report
        test_results = report.get("tests", [])
        
        for test in test_results:
            # Extract test information
            test_name = test.get("nodeid", "Unknown test")
            outcome = test.get("outcome", "failed")
            
            # Extract URS markers
            urs_ids = self._extract_urs_markers(test)
            urs_id = urs_ids[0] if urs_ids else "URS-UNKNOWN"
            
            # Determine module from test path
            module = self._determine_module(test_name)
            
            # Create PQTest
            pq_test = PQTest(
                test_name=test_name,
                urs_id=urs_id,
                urs_requirement=f"Requirement {urs_id}",
                module=module,
                workflow_description=self._extract_test_description(test),
                passed=(outcome == "passed"),
                failure_reason=self._extract_failure_reason(test) if outcome != "passed" else None
            )
            
            tests.append(pq_test)
        
        return tests

    def _extract_urs_markers(self, test: dict) -> list[str]:
        """Extract URS markers from test metadata or source file.
        
        Args:
            test: Test dictionary from pytest report
        
        Returns:
            List of URS marker strings
        """
        # Check if markers were already extracted during parsing
        if "urs_markers" in test and test["urs_markers"]:
            return test["urs_markers"]
        
        # Otherwise extract from source
        nodeid = test.get("nodeid", "")
        return self._extract_urs_from_source(nodeid)

    def _extract_urs_from_source(self, nodeid: str) -> list[str]:
        """Extract URS markers from test source file.
        
        Args:
            nodeid: Test node ID (e.g., tests/test_file.py::TestClass::test_method)
        
        Returns:
            List of URS marker strings
        """
        import re
        
        urs_markers = []
        
        try:
            # Extract file path from nodeid
            if "::" in nodeid:
                file_path = nodeid.split("::")[0]
                test_name = nodeid.split("::")[-1]
                
                # Read test file
                with open(file_path, "r") as f:
                    content = f.read()
                
                # Find URS markers near the test function
                # Look for @pytest.mark.urs("URS-XXX") decorators
                pattern = r'@pytest\.mark\.urs\(["\']([^"\']+)["\']\)'
                matches = re.findall(pattern, content)
                
                if matches:
                    urs_markers.extend(matches)
        
        except Exception:
            # If we can't read the file, return empty list
            pass
        
        return urs_markers

    def _extract_test_description(self, test: dict) -> str:
        """Extract test description from test metadata.
        
        Args:
            test: Test dictionary from pytest JSON report
        
        Returns:
            Test description string
        """
        # Try to get docstring
        docstring = test.get("call", {}).get("longrepr", "")
        
        if docstring:
            return docstring
        
        # Fallback to test name
        return test.get("nodeid", "No description")

    def _extract_failure_reason(self, test: dict) -> str:
        """Extract failure reason from test metadata.
        
        Args:
            test: Test dictionary from pytest JSON report
        
        Returns:
            Failure reason string
        """
        # Get failure information from call
        call = test.get("call", {})
        longrepr = call.get("longrepr", "")
        
        if longrepr:
            # Extract first line of error message
            if isinstance(longrepr, str):
                lines = longrepr.split("\n")
                return lines[0] if lines else "Unknown failure"
        
        return "Test failed"

    def _determine_functional_area(self, test_name: str) -> str:
        """Determine functional area from test name.
        
        Args:
            test_name: Test node ID
        
        Returns:
            Functional area name
        """
        test_name_lower = test_name.lower()
        
        if "attribute" in test_name_lower:
            return "Attribute"
        elif "variable" in test_name_lower:
            return "Variables"
        elif "non_normal" in test_name_lower or "nonnormal" in test_name_lower:
            return "Non-Normal"
        elif "reliability" in test_name_lower:
            return "Reliability"
        else:
            return "General"

    def _determine_module(self, test_name: str) -> str:
        """Determine analysis module from test name.
        
        Args:
            test_name: Test node ID
        
        Returns:
            Module name
        """
        # Same logic as functional area for now
        return self._determine_functional_area(test_name)

    def _create_result(
        self,
        success: bool,
        iq_result: IQResult,
        oq_result: OQResult,
        pq_result: PQResult
    ) -> ValidationResult:
        """Create ValidationResult from test results.
        
        Args:
            success: Overall validation success
            iq_result: IQ test results
            oq_result: OQ test results
            pq_result: PQ test results
        
        Returns:
            ValidationResult object
        """
        # Create state manager to get hash and environment
        config = ValidationConfig()
        state_manager = ValidationStateManager(config)
        
        validation_hash = state_manager.calculate_validation_hash()
        environment_fingerprint = state_manager.get_environment_fingerprint()
        
        # Get system info
        system_info = self._get_system_info(environment_fingerprint)
        
        return ValidationResult(
            success=success,
            validation_date=datetime.now(),
            validation_hash=validation_hash,
            environment_fingerprint=environment_fingerprint,
            iq_result=iq_result,
            oq_result=oq_result,
            pq_result=pq_result,
            system_info=system_info,
            certificate_path=None,
            certificate_hash=None
        )

    def _create_failed_result(
        self,
        iq_result: IQResult,
        oq_result: OQResult | None,
        pq_result: PQResult | None
    ) -> ValidationResult:
        """Create ValidationResult for failed validation.
        
        Args:
            iq_result: IQ test results
            oq_result: OQ test results (or None if not executed)
            pq_result: PQ test results (or None if not executed)
        
        Returns:
            ValidationResult object with success=False
        """
        # Create state manager to get hash and environment
        config = ValidationConfig()
        state_manager = ValidationStateManager(config)
        
        validation_hash = state_manager.calculate_validation_hash()
        environment_fingerprint = state_manager.get_environment_fingerprint()
        
        # Get system info
        system_info = self._get_system_info(environment_fingerprint)
        
        # Create empty results for phases that didn't run
        if oq_result is None:
            oq_result = OQResult(
                passed=False,
                tests=[],
                timestamp=datetime.now()
            )
        
        if pq_result is None:
            pq_result = PQResult(
                passed=False,
                tests=[],
                timestamp=datetime.now()
            )
        
        return ValidationResult(
            success=False,
            validation_date=datetime.now(),
            validation_hash=validation_hash,
            environment_fingerprint=environment_fingerprint,
            iq_result=iq_result,
            oq_result=oq_result,
            pq_result=pq_result,
            system_info=system_info,
            certificate_path=None,
            certificate_hash=None
        )

    def _get_system_info(self, environment_fingerprint: EnvironmentFingerprint) -> SystemInfo:
        """Get system information for validation certificate.
        
        Args:
            environment_fingerprint: Environment fingerprint
        
        Returns:
            SystemInfo object
        """
        import platform
        
        return SystemInfo(
            os_name=platform.system(),
            os_version=platform.release(),
            python_version=environment_fingerprint.python_version,
            dependencies=environment_fingerprint.dependencies
        )
