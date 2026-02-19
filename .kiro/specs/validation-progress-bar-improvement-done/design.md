# Design Document: Validation Progress Bar Improvement

## Overview

This design improves the validation progress bar in the Streamlit side-panel by using Streamlit's `st.empty()` container pattern to enable in-place updates. The current implementation creates new progress bars on each update, resulting in a cluttered UI. The improved design maintains references to UI containers and updates them in place, providing a clean, professional progress display.

The key insight is that Streamlit's `st.empty()` creates a placeholder that can be repeatedly updated with new content, allowing us to replace the progress bar and text without creating new UI elements.

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         app.py                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  run_validation()                                      │  │
│  │    - Creates ValidationOrchestrator                    │  │
│  │    - Creates progress_callback closure                 │  │
│  │    - Calls execute_validation_workflow()               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              ValidationOrchestrator                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  execute_validation_workflow(progress_callback)        │  │
│  │    - Calls progress_callback("IQ", 0.10)               │  │
│  │    - Calls progress_callback("IQ", 0.33)               │  │
│  │    - Calls progress_callback("OQ", 0.40)               │  │
│  │    - Calls progress_callback("OQ", 0.66)               │  │
│  │    - Calls progress_callback("PQ", 0.70)               │  │
│  │    - Calls progress_callback("PQ", 0.90)               │  │
│  │    - Calls progress_callback("Complete", 1.00)         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ invokes
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   ValidationUI                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  render_validation_progress(phase, percentage)         │  │
│  │    - Updates text_placeholder with phase label         │  │
│  │    - Updates progress_placeholder with progress bar    │  │
│  │    - Maintains state across calls                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### State Management

The ValidationUI class will maintain instance variables to store references to Streamlit placeholders:
- `_progress_text_placeholder`: Stores the `st.empty()` container for phase text
- `_progress_bar_placeholder`: Stores the `st.empty()` container for the progress bar
- `_current_phase`: Tracks the current phase to detect transitions

## Components and Interfaces

### ValidationUI Class Modifications

```python
class ValidationUI:
    """UI components for validation system display."""
    
    def __init__(self):
        """Initialize ValidationUI with placeholder references."""
        self._progress_text_placeholder = None
        self._progress_bar_placeholder = None
        self._current_phase = None
    
    def render_validation_progress(
        self,
        phase: str,
        percentage: float
    ) -> None:
        """Render validation progress indicator with phase and percentage.
        
        This method creates placeholders on first call and reuses them
        for subsequent updates, ensuring a single progress bar that
        updates in place.
        
        Args:
            phase: Current validation phase (e.g., "IQ", "OQ", "PQ")
            percentage: Progress percentage (0.0 to 1.0)
        
        Validates: Requirements 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 4.2
        """
        # Create placeholders on first call
        if self._progress_text_placeholder is None:
            self._progress_text_placeholder = st.empty()
        if self._progress_bar_placeholder is None:
            self._progress_bar_placeholder = st.empty()
        
        # Detect phase transitions
        if self._current_phase != phase:
            self._current_phase = phase
            # Reset progress bar to 0 for new phase
            percentage = 0.0
        
        # Update text placeholder with phase label
        phase_label = self._format_phase_label(phase)
        self._progress_text_placeholder.text(phase_label)
        
        # Update progress bar placeholder
        self._progress_bar_placeholder.progress(percentage)
    
    def _format_phase_label(self, phase: str) -> str:
        """Format phase name into user-friendly label.
        
        Args:
            phase: Phase name from orchestrator
        
        Returns:
            Formatted label string
        
        Validates: Requirements 2.1, 2.4
        """
        phase_labels = {
            "Starting validation": "Starting validation...",
            "IQ": "Running IQ tests...",
            "OQ": "Running OQ tests...",
            "PQ": "Running PQ tests...",
            "Generating certificate": "Generating certificate...",
            "Complete": "Validation complete!"
        }
        return phase_labels.get(phase, f"Running {phase}...")
    
    def clear_validation_progress(self) -> None:
        """Clear progress bar and text after validation completes or fails.
        
        Validates: Requirements 1.4, 6.2, 6.4
        """
        if self._progress_text_placeholder is not None:
            self._progress_text_placeholder.empty()
            self._progress_text_placeholder = None
        
        if self._progress_bar_placeholder is not None:
            self._progress_bar_placeholder.empty()
            self._progress_bar_placeholder = None
        
        self._current_phase = None
```

### Progress Callback in app.py

The progress callback closure in `app.py` will be modified to use the ValidationUI instance:

```python
def run_validation() -> None:
    """Run validation workflow."""
    logger.info("Starting validation workflow from UI")
    orchestrator = ValidationOrchestrator(validation_config.certificate_output_dir)

    with st.spinner("Running validation..."):
        # Progress callback using ValidationUI instance
        def progress_callback(phase: str, percentage: float) -> None:
            validation_ui.render_validation_progress(phase, percentage)

        try:
            result = orchestrator.execute_validation_workflow(
                progress_callback=progress_callback
            )

            # Clear progress display after completion
            validation_ui.clear_validation_progress()

            if result.success:
                # ... existing success handling ...
            else:
                # ... existing failure handling ...

        except Exception as e:
            # Clear progress display on error
            validation_ui.clear_validation_progress()
            # ... existing error handling ...
```

## Data Models

No new data models are required. The existing interfaces remain unchanged:

- `progress_callback: Callable[[str, float], None]` - Signature remains the same
- Phase names: "Starting validation", "IQ", "OQ", "PQ", "Generating certificate", "Complete"
- Percentage: float value between 0.0 and 1.0

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing the acceptance criteria, most requirements focus on UI behavior, timing, and visual presentation that are difficult to test programmatically in Streamlit. The testable properties are:

- Phase label formatting (2.1, 7.3) - Can be combined into one property about label generation
- Phase transition detection (2.3) - Property about resetting progress on phase changes
- Percentage range handling (3.2) - Property about accepting valid percentage values

These properties are independent and provide unique validation value.

### Correctness Properties

Property 1: Phase label formatting
*For any* phase name string, the `_format_phase_label` method should return a non-empty string containing descriptive text about the phase
**Validates: Requirements 2.1, 7.3**

Property 2: Phase transition detection
*For any* sequence of calls to `render_validation_progress`, when the phase name changes between consecutive calls, the progress should reset to 0.0 for the new phase
**Validates: Requirements 2.3**

Property 3: Valid percentage range handling
*For any* percentage value between 0.0 and 1.0 (inclusive), calling `render_validation_progress` should complete without raising an exception
**Validates: Requirements 3.2**

## Error Handling

### Error Scenarios

1. **Invalid percentage values**: If percentage < 0.0 or > 1.0, clamp to valid range (0.0-1.0)
2. **None phase name**: Treat as empty string and format as "Running ..."
3. **Streamlit context errors**: If placeholders fail to create, log warning and continue
4. **Placeholder update failures**: Catch exceptions during update and log errors

### Error Handling Strategy

```python
def render_validation_progress(
    self,
    phase: str,
    percentage: float
) -> None:
    """Render validation progress with error handling."""
    try:
        # Clamp percentage to valid range
        percentage = max(0.0, min(1.0, percentage))
        
        # Handle None or empty phase
        if not phase:
            phase = "Unknown"
        
        # Create placeholders on first call
        if self._progress_text_placeholder is None:
            self._progress_text_placeholder = st.empty()
        if self._progress_bar_placeholder is None:
            self._progress_bar_placeholder = st.empty()
        
        # Detect phase transitions
        if self._current_phase != phase:
            self._current_phase = phase
        
        # Update UI elements
        phase_label = self._format_phase_label(phase)
        self._progress_text_placeholder.text(phase_label)
        self._progress_bar_placeholder.progress(percentage)
        
    except Exception as e:
        # Log error but don't crash the validation workflow
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating progress bar: {e}")
```

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and integration with Streamlit
- **Property tests**: Verify universal properties across all inputs

### Unit Testing

Unit tests will focus on:

1. **Placeholder creation**: Verify placeholders are created on first call
2. **Placeholder reuse**: Verify same placeholders are used across multiple calls
3. **Phase label formatting**: Test specific phase names produce expected labels
4. **Phase transition behavior**: Test progress resets when phase changes
5. **Completion behavior**: Test clear_validation_progress removes placeholders
6. **Error handling**: Test invalid inputs are handled gracefully
7. **Integration**: Test with mock Streamlit context

Example unit tests:

```python
def test_placeholder_creation_on_first_call():
    """Test that placeholders are created on first call."""
    ui = ValidationUI()
    assert ui._progress_text_placeholder is None
    assert ui._progress_bar_placeholder is None
    
    ui.render_validation_progress("IQ", 0.5)
    
    assert ui._progress_text_placeholder is not None
    assert ui._progress_bar_placeholder is not None

def test_phase_label_formatting():
    """Test specific phase names produce expected labels."""
    ui = ValidationUI()
    
    assert ui._format_phase_label("IQ") == "Running IQ tests..."
    assert ui._format_phase_label("OQ") == "Running OQ tests..."
    assert ui._format_phase_label("PQ") == "Running PQ tests..."
    assert ui._format_phase_label("Complete") == "Validation complete!"

def test_phase_transition_resets_progress():
    """Test that changing phase resets progress tracking."""
    ui = ValidationUI()
    
    ui.render_validation_progress("IQ", 0.5)
    assert ui._current_phase == "IQ"
    
    ui.render_validation_progress("OQ", 0.3)
    assert ui._current_phase == "OQ"
```

### Property-Based Testing

Property-based tests will use Hypothesis (Python's PBT library) to verify universal properties:

**Configuration**: Each property test will run minimum 100 iterations

**Property Test 1: Phase label formatting**
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_phase_label_always_returns_string(phase_name):
    """Feature: validation-progress-bar-improvement, Property 1: 
    For any phase name string, _format_phase_label returns non-empty string"""
    ui = ValidationUI()
    result = ui._format_phase_label(phase_name)
    assert isinstance(result, str)
    assert len(result) > 0
```

**Property Test 2: Phase transition detection**
```python
@given(st.text(), st.floats(0.0, 1.0), st.text(), st.floats(0.0, 1.0))
def test_phase_change_updates_current_phase(phase1, pct1, phase2, pct2):
    """Feature: validation-progress-bar-improvement, Property 2:
    For any sequence of calls, phase changes update current phase"""
    assume(phase1 != phase2)  # Only test actual phase changes
    
    ui = ValidationUI()
    ui.render_validation_progress(phase1, pct1)
    assert ui._current_phase == phase1
    
    ui.render_validation_progress(phase2, pct2)
    assert ui._current_phase == phase2
```

**Property Test 3: Valid percentage range handling**
```python
@given(st.text(), st.floats(0.0, 1.0))
def test_valid_percentage_range_accepted(phase, percentage):
    """Feature: validation-progress-bar-improvement, Property 3:
    For any percentage in [0.0, 1.0], render_validation_progress succeeds"""
    ui = ValidationUI()
    # Should not raise exception
    ui.render_validation_progress(phase, percentage)
```

### Testing Limitations

Due to Streamlit's execution model, some aspects cannot be easily tested:

- **Visual appearance**: Cannot verify actual UI rendering without browser automation
- **In-place updates**: Cannot verify that new UI elements aren't created (requires Streamlit internals)
- **Timing and smoothness**: Cannot test visual smoothness programmatically

These aspects will be verified through manual testing and user acceptance testing.

## Implementation Notes

### Streamlit Execution Model

Streamlit reruns the entire script on each interaction, which means:

1. The ValidationUI instance in the sidebar is recreated on each rerun
2. Placeholder references are lost between reruns
3. Progress updates only work within a single execution context (inside `with st.spinner()`)

This is acceptable because validation runs within a single execution context and completes before the next rerun.

### Alternative Approaches Considered

1. **Session state for placeholders**: Store placeholder references in `st.session_state`
   - Rejected: Adds complexity and isn't necessary for single-execution workflows

2. **Custom Streamlit component**: Build a React-based progress component
   - Rejected: Overkill for this use case, adds maintenance burden

3. **Status container pattern**: Use `st.status()` context manager
   - Rejected: Less flexible for showing percentage progress

### Performance Considerations

- Placeholder updates are lightweight operations in Streamlit
- No performance concerns for typical validation workflows (3-5 minutes)
- Progress updates every few seconds are sufficient for user feedback

## Migration Plan

### Changes Required

1. **ValidationUI class** (`src/sample_size_estimator/validation/ui.py`):
   - Add `__init__` method with placeholder instance variables
   - Modify `render_validation_progress` to use placeholders
   - Add `_format_phase_label` helper method
   - Add `clear_validation_progress` method

2. **app.py** (`src/sample_size_estimator/app.py`):
   - Add `validation_ui.clear_validation_progress()` calls after validation completes or fails

3. **Tests** (new file `tests/test_validation_ui_progress.py`):
   - Add unit tests for progress bar behavior
   - Add property-based tests for correctness properties

### Backward Compatibility

- The `render_validation_progress(phase, percentage)` signature remains unchanged
- The orchestrator requires no modifications
- Existing progress callback code continues to work

### Rollout Strategy

1. Implement changes to ValidationUI class
2. Add unit tests and verify behavior
3. Update app.py to clear progress on completion/error
4. Manual testing of validation workflow
5. Deploy to production

No feature flag needed - changes are low risk and fully backward compatible.
