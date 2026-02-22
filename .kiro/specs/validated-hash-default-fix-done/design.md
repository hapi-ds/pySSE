# Validated Hash Default Fix - Bugfix Design

## Overview

The test `test_app_settings_defaults` fails because Pydantic Settings automatically loads environment variables from the `.env` file when `AppSettings()` is instantiated, even in test contexts. The test expects `validated_hash` to have its default value (None), but instead receives the hash value from `.env`. This is a test isolation issue where the test environment is not properly isolated from production configuration.

The fix requires modifying the test to prevent Pydantic Settings from loading the `.env` file, allowing it to use only the default values defined in the class. This ensures the test validates default behavior without interference from environment configuration.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when `AppSettings()` is instantiated in `test_app_settings_defaults` and loads from `.env` instead of using defaults
- **Property (P)**: The desired behavior - `AppSettings()` in the test should return default values without loading from `.env`
- **Preservation**: Existing behavior where `AppSettings()` loads from `.env` in production and other test contexts must remain unchanged
- **AppSettings**: The Pydantic Settings class in `src/sample_size_estimator/config.py` that manages application configuration
- **model_config**: The Pydantic Settings configuration that controls `.env` file loading behavior
- **SettingsConfigDict**: Pydantic Settings configuration object with `env_file` parameter

## Bug Details

### Fault Condition

The bug manifests when `test_app_settings_defaults` instantiates `AppSettings()` to verify default values. Pydantic Settings automatically loads the `.env` file due to the `model_config` setting `env_file=".env"`, causing `validated_hash` to receive the production value instead of the default None.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type TestContext
  OUTPUT: boolean
  
  RETURN input.test_name == "test_app_settings_defaults"
         AND input.instantiation_method == "AppSettings()"
         AND AppSettings.model_config.env_file == ".env"
         AND ".env" file exists with VALIDATED_HASH set
         AND input.expected_value == None
         AND input.actual_value == hash_from_env_file
END FUNCTION
```

### Examples

- **Test Context**: `test_app_settings_defaults` calls `AppSettings()` expecting `validated_hash=None`, but receives `validated_hash="a4826d4db0e60972182dada4617a3c12cbff54167676b7a1a5d7e55c43482e1e"` from `.env`
- **Assertion Failure**: `assert settings.validated_hash in (None, "")` fails because the actual value is the hash string from `.env`
- **Production Context**: `get_settings()` in `app.py` correctly loads `validated_hash` from `.env` - this behavior must be preserved
- **Edge Case**: If `.env` file doesn't exist, the test would pass (but this is not the desired fix)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Production code must continue to load `validated_hash` from `.env` file when `AppSettings()` is instantiated
- The `get_settings()` singleton function must continue to return settings loaded from environment variables and `.env`
- The test `test_app_settings_custom_values` must continue to work with `monkeypatch.setenv()` to override settings
- All other tests that rely on environment configuration must continue to function correctly
- The `model_config` with `env_file=".env"` must remain in the `AppSettings` class for production use

**Scope:**
All contexts that do NOT involve testing default values should be completely unaffected by this fix. This includes:
- Production application startup and configuration loading
- Other test cases that intentionally use environment variables
- The singleton pattern in `get_settings()`
- Any code that depends on `.env` file loading

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause is:

1. **Pydantic Settings Auto-Loading**: The `AppSettings` class has `model_config = SettingsConfigDict(env_file=".env", ...)` which automatically loads the `.env` file on instantiation
   - This is correct behavior for production
   - But it interferes with testing default values

2. **Test Lacks Isolation**: The test `test_app_settings_defaults` does not prevent `.env` file loading
   - It calls `AppSettings()` directly without overriding the configuration
   - Pydantic Settings loads `.env` by default, overriding the None default for `validated_hash`

3. **No Test-Specific Configuration**: There is no mechanism to instantiate `AppSettings` without `.env` loading
   - Pydantic Settings provides `_env_file=None` parameter to disable `.env` loading
   - The test does not use this parameter

4. **Ambiguous Test Intent**: The test comment says "validated_hash can be None or empty string depending on .env file"
   - This suggests the test was written to accommodate `.env` loading
   - But the assertion `assert settings.validated_hash in (None, "")` expects default values only
   - The test intent is to verify defaults, not to verify `.env` loading

## Correctness Properties

Property 1: Fault Condition - Default Values Without Environment Loading

_For any_ test context where `test_app_settings_defaults` instantiates `AppSettings`, the test SHALL receive default values (validated_hash=None) without loading from the `.env` file, allowing proper verification of default configuration.

**Validates: Requirements 2.1, 2.2**

Property 2: Preservation - Environment Loading in Production

_For any_ context that is NOT the `test_app_settings_defaults` test (production code, other tests, singleton pattern), `AppSettings` SHALL continue to load configuration from the `.env` file exactly as before, preserving all existing environment-based configuration behavior.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `tests/test_config.py`

**Function**: `test_app_settings_defaults`

**Specific Changes**:
1. **Disable .env Loading**: Pass `_env_file=None` parameter to `AppSettings()` constructor
   - This tells Pydantic Settings to skip `.env` file loading
   - Environment variables can still be loaded, but not from the file
   - This isolates the test to verify only default values

2. **Update Test Comment**: Remove the ambiguous comment about "depending on .env file"
   - The test should clearly state it's testing defaults without environment loading
   - This clarifies the test intent for future maintainers

3. **Verify Assertion**: Keep the assertion `assert settings.validated_hash in (None, "")` 
   - With `_env_file=None`, this will correctly verify the default value
   - The `in (None, "")` handles both None and empty string as valid defaults

**Implementation**:
```python
def test_app_settings_defaults():
    """Test that AppSettings has correct default values without loading .env file."""
    # Disable .env file loading to test pure defaults
    settings = AppSettings(_env_file=None)
    
    assert settings.app_title == "Sample Size Estimator"
    assert settings.app_version == "0.1.0"
    assert settings.log_level == "INFO"
    assert settings.log_file == "logs/app.log"
    assert settings.log_format == "json"
    assert settings.validated_hash in (None, "")
    assert settings.calculations_file == "src/sample_size_estimator/calculations/__init__.py"
    assert settings.report_output_dir == "reports"
    assert settings.report_author == "Sample Size Estimator System"
    assert settings.default_confidence == 95.0
    assert settings.default_reliability == 90.0
```

**Alternative Approach** (if `_env_file=None` doesn't work):
Use `monkeypatch` to temporarily remove the `.env` file or set environment variables to empty values. However, this is more complex and less explicit than using Pydantic's built-in parameter.

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Run the existing `test_app_settings_defaults` test on UNFIXED code to observe the failure. Then create a diagnostic test that explicitly checks whether `.env` is being loaded.

**Test Cases**:
1. **Current Test Failure**: Run `uv run pytest tests/test_config.py::test_app_settings_defaults -v` (will fail on unfixed code)
2. **Diagnostic Test**: Create a test that instantiates `AppSettings()` and checks if `validated_hash` matches the `.env` value (will pass on unfixed code, confirming `.env` is loaded)
3. **Isolation Test**: Create a test that instantiates `AppSettings(_env_file=None)` and checks if `validated_hash` is None (will pass, confirming the fix approach works)
4. **Environment Variable Test**: Verify that `_env_file=None` still allows environment variables to be loaded (not from file)

**Expected Counterexamples**:
- `test_app_settings_defaults` fails with: `AssertionError: assert 'a4826d4db0e60972182dada4617a3c12cbff54167676b7a1a5d7e55c43482e1e' in (None, '')`
- Diagnostic test confirms `validated_hash` equals the value from `.env` file
- Possible causes: `.env` file loading is enabled by default, test lacks isolation

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL test_context WHERE isBugCondition(test_context) DO
  settings := AppSettings(_env_file=None)
  ASSERT settings.validated_hash IN (None, "")
  ASSERT all_other_defaults_are_correct(settings)
END FOR
```

**Test Plan**: After applying the fix, run `test_app_settings_defaults` and verify it passes. Also verify that the test correctly validates all default values.

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL context WHERE NOT isBugCondition(context) DO
  ASSERT AppSettings_original(context) = AppSettings_fixed(context)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for production instantiation and other tests, then write tests to verify this behavior continues after the fix.

**Test Cases**:
1. **Production Loading Preservation**: Verify that `AppSettings()` (without `_env_file=None`) still loads from `.env` in production contexts
2. **Singleton Preservation**: Verify that `get_settings()` continues to work correctly and loads from `.env`
3. **Custom Values Preservation**: Verify that `test_app_settings_custom_values` with `monkeypatch.setenv()` continues to work
4. **Other Tests Preservation**: Run the full test suite to ensure no other tests are affected by the change

### Unit Tests

- Test that `AppSettings(_env_file=None)` returns default values without loading `.env`
- Test that `AppSettings()` (without parameter) still loads from `.env` 
- Test that all default values are correct when `.env` is not loaded
- Test edge case where `.env` file doesn't exist (should work the same as `_env_file=None`)

### Property-Based Tests

- Generate random environment configurations and verify that `AppSettings()` loads them correctly (preservation)
- Generate random default value checks and verify that `AppSettings(_env_file=None)` returns defaults (fix checking)
- Test that mixing environment variables and `_env_file=None` works correctly (env vars should still be loaded)

### Integration Tests

- Run the full test suite to ensure no regressions
- Verify that the Streamlit application still loads configuration correctly from `.env`
- Test that validation workflow still accesses `validated_hash` from settings
- Verify that logging configuration is still loaded from `.env`
