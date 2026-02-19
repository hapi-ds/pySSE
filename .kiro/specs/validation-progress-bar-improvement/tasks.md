# Implementation Plan: Validation Progress Bar Improvement

## Overview

This implementation improves the validation progress bar in the Streamlit side-panel by using `st.empty()` placeholders to enable in-place updates. The changes are focused on the ValidationUI class and the progress callback in app.py, with comprehensive testing to ensure correctness.

## Tasks

- [ ] 1. Update ValidationUI class with placeholder-based progress rendering
  - [x] 1.1 Add `__init__` method to ValidationUI class
    - Initialize instance variables: `_progress_text_placeholder`, `_progress_bar_placeholder`, `_current_phase`
    - Set all to None initially
    - _Requirements: 1.1, 1.3_

  - [x] 1.2 Modify `render_validation_progress` method to use placeholders
    - Create `st.empty()` placeholders on first call (when None)
    - Detect phase transitions by comparing with `_current_phase`
    - Update text placeholder with formatted phase label
    - Update progress bar placeholder with percentage
    - Add error handling for invalid inputs (clamp percentage, handle None phase)
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.3, 3.1, 3.2, 4.2_

  - [x] 1.3 Add `_format_phase_label` helper method
    - Create dictionary mapping phase names to user-friendly labels
    - Handle known phases: "Starting validation", "IQ", "OQ", "PQ", "Generating certificate", "Complete"
    - Return formatted label with fallback for unknown phases
    - _Requirements: 2.1, 2.4, 7.3_

  - [x] 1.4 Add `clear_validation_progress` method
    - Call `.empty()` on text placeholder if not None
    - Call `.empty()` on progress bar placeholder if not None
    - Reset all instance variables to None
    - _Requirements: 1.4, 6.2, 6.4_

- [ ] 2. Update app.py to clear progress after validation
  - [x] 2.1 Add progress clearing after successful validation
    - Call `validation_ui.clear_validation_progress()` after displaying success message
    - _Requirements: 1.4_

  - [x] 2.2 Add progress clearing after failed validation
    - Call `validation_ui.clear_validation_progress()` in exception handler
    - Call `validation_ui.clear_validation_progress()` after displaying failure message
    - _Requirements: 6.2, 6.4_

- [ ] 3. Checkpoint - Manual testing of progress bar behavior
  - Run validation workflow and verify single progress bar updates in place
  - Verify phase labels display correctly for each phase
  - Verify progress bar clears after completion
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Write unit tests for ValidationUI progress methods
  - [x] 4.1 Test placeholder creation on first call
    - Verify placeholders are None before first call
    - Verify placeholders are created after first call
    - _Requirements: 1.1, 1.3_

  - [x] 4.2 Test placeholder reuse across multiple calls
    - Call render_validation_progress multiple times
    - Verify placeholder references remain the same
    - _Requirements: 1.2, 1.3_

  - [x] 4.3 Test phase label formatting for known phases
    - Test "IQ" → "Running IQ tests..."
    - Test "OQ" → "Running OQ tests..."
    - Test "PQ" → "Running PQ tests..."
    - Test "Complete" → "Validation complete!"
    - Test unknown phase → "Running {phase}..."
    - _Requirements: 2.1, 7.3_

  - [x] 4.4 Test phase transition detection
    - Call with phase "IQ", verify _current_phase is "IQ"
    - Call with phase "OQ", verify _current_phase is "OQ"
    - _Requirements: 2.3_

  - [x] 4.5 Test clear_validation_progress method
    - Create placeholders by calling render_validation_progress
    - Call clear_validation_progress
    - Verify all instance variables are None
    - _Requirements: 1.4, 6.4_

  - [x] 4.6 Test error handling for invalid percentage values
    - Test percentage < 0.0 is clamped to 0.0
    - Test percentage > 1.0 is clamped to 1.0
    - _Requirements: 3.2_

  - [x] 4.7 Test error handling for None or empty phase
    - Test None phase is handled gracefully
    - Test empty string phase is handled gracefully
    - _Requirements: 7.3_

- [ ]* 5. Write property-based tests for correctness properties
  - [ ]* 5.1 Write property test for phase label formatting
    - **Property 1: Phase label formatting**
    - **Validates: Requirements 2.1, 7.3**
    - Use Hypothesis to generate random phase name strings
    - Verify _format_phase_label always returns non-empty string
    - Run minimum 100 iterations

  - [ ]* 5.2 Write property test for phase transition detection
    - **Property 2: Phase transition detection**
    - **Validates: Requirements 2.3**
    - Use Hypothesis to generate two different phase names and percentages
    - Verify _current_phase updates when phase changes
    - Run minimum 100 iterations

  - [ ]* 5.3 Write property test for valid percentage range handling
    - **Property 3: Valid percentage range handling**
    - **Validates: Requirements 3.2**
    - Use Hypothesis to generate phase names and percentages in [0.0, 1.0]
    - Verify render_validation_progress completes without exception
    - Run minimum 100 iterations

- [ ] 6. Final checkpoint - Ensure all tests pass
  - Run all unit tests: `uv run pytest tests/test_validation_ui_progress.py -q`
  - Run all property tests: `uv run pytest tests/test_validation_ui_progress.py -k property -q`
  - Verify no regressions in existing validation tests
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- The implementation maintains backward compatibility with existing orchestrator code
- No changes required to ValidationOrchestrator class
