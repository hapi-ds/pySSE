#!/usr/bin/env python3
"""Command-line validation script for Sample Size Estimator.

This script executes the complete IQ/OQ/PQ validation workflow from the command line,
generates a validation certificate, and updates the validation state.

Usage:
    python scripts/validate.py [--output-dir DIR] [--expiry-days DAYS]

Examples:
    python scripts/validate.py
    python scripts/validate.py --output-dir ./validation_reports
    python scripts/validate.py --expiry-days 180
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sample_size_estimator.validation import (
    ValidationConfig,
    ValidationOrchestrator,
    ValidationPersistence,
    ValidationState,
)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Run IQ/OQ/PQ validation workflow for Sample Size Estimator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --output-dir ./validation_reports
  %(prog)s --expiry-days 180

Exit Codes:
  0 - Validation successful
  1 - Validation failed (tests did not pass)
  2 - Error during validation execution
        """
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory for validation certificate output (default: from config)"
    )

    parser.add_argument(
        "--expiry-days",
        type=int,
        default=None,
        help="Number of days until validation expires (default: from config)"
    )

    return parser.parse_args()


def progress_callback(phase: str, percentage: float) -> None:
    """Display progress to console.

    Args:
        phase: Current validation phase (IQ, OQ, or PQ).
        percentage: Progress percentage (0.0 to 1.0).
    """
    bar_length = 40
    filled_length = int(bar_length * percentage)
    bar = "=" * filled_length + "-" * (bar_length - filled_length)
    print(f"\r{phase} Tests: [{bar}] {int(percentage * 100)}%", end="", flush=True)


def main() -> int:
    """Main entry point for validation script.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    args = parse_arguments()

    print("=" * 70)
    print("Sample Size Estimator - Validation Workflow")
    print("=" * 70)
    print()

    try:
        # Initialize validation configuration
        config = ValidationConfig()

        # Override config with command-line arguments if provided
        if args.output_dir:
            config.certificate_output_dir = Path(args.output_dir)
        if args.expiry_days:
            config.validation_expiry_days = args.expiry_days

        print(f"Configuration:")
        print(f"  Output Directory: {config.certificate_output_dir}")
        print(f"  Expiry Days: {config.validation_expiry_days}")
        print(f"  Persistence Directory: {config.persistence_dir}")
        print()

        # Create output directory if it doesn't exist
        config.certificate_output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize orchestrator and persistence
        orchestrator = ValidationOrchestrator(config.certificate_output_dir)
        persistence = ValidationPersistence(config.persistence_dir)

        print("Starting validation workflow...")
        print()

        # Execute validation workflow with progress callback
        result = orchestrator.execute_validation_workflow(
            progress_callback=progress_callback
        )

        print()  # New line after progress bar
        print()

        # Display results
        if result.success:
            print("[SUCCESS] VALIDATION SUCCESSFUL")
            print()
            print("Results:")
            print(f"  IQ Tests: {'PASSED' if result.iq_result.passed else 'FAILED'} "
                  f"({result.iq_result.get_summary()['passed']}/{result.iq_result.get_summary()['total']})")
            print(f"  OQ Tests: {'PASSED' if result.oq_result.passed else 'FAILED'} "
                  f"({result.oq_result.get_summary()['passed']}/{result.oq_result.get_summary()['total']})")
            print(f"  PQ Tests: {'PASSED' if result.pq_result.passed else 'FAILED'} "
                  f"({result.pq_result.get_summary()['passed']}/{result.pq_result.get_summary()['total']})")
            print()
            print(f"Validation Hash: {result.validation_hash}")
            print(f"Validation Date: {result.validation_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Expiry Date: {(result.validation_date + timedelta(days=config.validation_expiry_days)).strftime('%Y-%m-%d')}")
            print()

            if result.certificate_path:
                print(f"Certificate: {result.certificate_path}")
                print(f"Certificate Hash: {result.certificate_hash}")
                print()

            # Save validation state
            expiry_date = result.validation_date + timedelta(days=config.validation_expiry_days)
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
            persistence.save_validation_state(validation_state)

            print("Validation state saved successfully.")
            print()
            print("=" * 70)

            return 0

        else:
            print("[FAILED] VALIDATION FAILED")
            print()
            print("Results:")
            print(f"  IQ Tests: {'PASSED' if result.iq_result.passed else 'FAILED'} "
                  f"({result.iq_result.get_summary()['passed']}/{result.iq_result.get_summary()['total']})")
            print(f"  OQ Tests: {'PASSED' if result.oq_result.passed else 'FAILED'} "
                  f"({result.oq_result.get_summary()['passed']}/{result.oq_result.get_summary()['total']})")
            print(f"  PQ Tests: {'PASSED' if result.pq_result.passed else 'FAILED'} "
                  f"({result.pq_result.get_summary()['passed']}/{result.pq_result.get_summary()['total']})")
            print()

            # Display failure details
            if not result.iq_result.passed:
                print("IQ Failures:")
                for check in result.iq_result.checks:
                    if not check.passed:
                        print(f"  - {check.name}: {check.failure_reason}")
                print()

            if not result.oq_result.passed:
                print("OQ Failures:")
                for test in result.oq_result.tests:
                    if not test.passed:
                        print(f"  - {test.test_name}: {test.failure_reason}")
                print()

            if not result.pq_result.passed:
                print("PQ Failures:")
                for test in result.pq_result.tests:
                    if not test.passed:
                        print(f"  - {test.test_name}: {test.failure_reason}")
                print()

            print("=" * 70)

            return 1

    except KeyboardInterrupt:
        print()
        print()
        print("Validation interrupted by user.")
        return 2

    except Exception as e:
        print()
        print()
        print(f"[ERROR] {str(e)}")
        print()
        print("Validation workflow failed due to an error.")
        print("Please check the logs for more details.")
        print()
        print("=" * 70)
        return 2


if __name__ == "__main__":
    sys.exit(main())
