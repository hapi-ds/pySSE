# Validated Hash History

This document tracks the history of validated hashes for the Sample Size Estimator calculation engine.

## Purpose

The validated hash is a SHA-256 cryptographic hash of all calculation module files. It ensures that the calculation engine has not been modified since validation testing. Any change to the calculation code will result in a different hash, triggering an "UNVERIFIED CHANGE" warning in calculation reports.

## Hash History

### Version 0.1.0 - Initial Validation

**Date:** 2026-02-18  
**Validated Hash:** `a4826d4db0e60972182dada4617a3c12cbff54167676b7a1a5d7e55c43482e1e`

**Validation Details:**
- Test Suite: 246 tests executed
- Test Results: All tests PASSED
- Validation Certificate: `reports/validation_certificate_20260218_144033.pdf`
- Python Version: 3.13.5
- Operating System: Windows 11

**Calculation Modules Included:**
- `src/sample_size_estimator/calculations/__init__.py`
- `src/sample_size_estimator/calculations/attribute_calcs.py`
- `src/sample_size_estimator/calculations/variables_calcs.py`
- `src/sample_size_estimator/calculations/non_normal_calcs.py`
- `src/sample_size_estimator/calculations/reliability_calcs.py`

**Changes Since Last Version:** Initial validation - no previous version

**Approved By:** Automated Test System  
**Quality Review:** Pending

---

## Hash Update Instructions

When updating the validated hash after revalidation:

1. Add a new section above with the format:
   ```markdown
   ### Version X.Y.Z - Description
   
   **Date:** YYYY-MM-DD
   **Validated Hash:** `<64-character-hash>`
   
   **Validation Details:**
   - Test Suite: XXX tests executed
   - Test Results: All tests PASSED/FAILED
   - Validation Certificate: `reports/validation_certificate_YYYYMMDD_HHMMSS.pdf`
   - Python Version: X.Y.Z
   - Operating System: OS Name
   
   **Changes Since Last Version:** Brief description of changes
   
   **Approved By:** Name/System
   **Quality Review:** Status
   ```

2. Update the `.env.example` file with the new hash
3. Update the `.env` file (if used) with the new hash
4. Store the validation certificate in quality records
5. Commit changes to version control

## Verification

To verify the current hash matches the validated hash:

```bash
# Generate a calculation report from the application
# Check the "Validation Information" section
# It should show "VALIDATED STATE: YES"
```

If the validation state shows "NO - UNVERIFIED CHANGE", the calculation code has been modified since the last validation and revalidation is required.

## Related Documentation

- [Validation Protocol](VALIDATION_PROTOCOL.md) - Complete validation procedures
- [README.md](../README.md) - Quick start and validation overview
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development and testing guidelines
