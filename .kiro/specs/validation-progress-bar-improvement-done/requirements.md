# Requirements Document

## Introduction

This feature improves the validation progress bar display in the Streamlit side-panel during IQ/OQ/PQ validation workflows. Currently, the progress bar creates multiple new UI elements at fixed intervals, which appears unprofessional and confusing to users. The improved implementation will display a single progress bar that updates in place, with clear phase labels and smooth transitions between validation phases.

## Glossary

- **Progress_Bar**: The visual UI component that displays validation progress as a percentage
- **Phase**: One of the three validation stages (IQ, OQ, or PQ)
- **Orchestrator**: The ValidationOrchestrator class that executes the validation workflow
- **UI_Component**: The ValidationUI class that renders Streamlit UI elements
- **Progress_Callback**: A function passed to the orchestrator that receives phase name and percentage updates

## Requirements

### Requirement 1: Single Progress Bar Display

**User Story:** As a user running validation, I want to see a single progress bar that updates in place, so that the UI remains clean and professional.

#### Acceptance Criteria

1. WHEN the validation workflow starts, THE Progress_Bar SHALL be created once and reused for all updates
2. WHEN progress updates are received, THE Progress_Bar SHALL update its value without creating new UI elements
3. THE UI_Component SHALL maintain a reference to the Progress_Bar across multiple update calls
4. WHEN validation completes, THE Progress_Bar SHALL display 100% before being removed

### Requirement 2: Phase-Based Progress Display

**User Story:** As a user, I want to see which validation phase is currently running, so that I understand what the system is doing.

#### Acceptance Criteria

1. WHEN each phase begins, THE UI_Component SHALL display a clear phase label (e.g., "Running IQ tests...", "Running OQ tests...", "Running PQ tests...")
2. WHEN a phase completes, THE Progress_Bar SHALL show 100% for that phase
3. WHEN transitioning to a new phase, THE Progress_Bar SHALL reset to 0% and display the new phase label
4. THE UI_Component SHALL display phase labels above the Progress_Bar

### Requirement 3: Smooth Progress Updates

**User Story:** As a user, I want the progress bar to update smoothly, so that I can see the validation is actively running.

#### Acceptance Criteria

1. WHEN the Orchestrator calls the Progress_Callback, THE UI_Component SHALL update the Progress_Bar immediately
2. THE Progress_Bar SHALL display percentage values between 0.0 and 1.0 (or 0% to 100%)
3. WHEN multiple updates occur in sequence, THE Progress_Bar SHALL reflect each update without flickering
4. THE UI_Component SHALL handle rapid progress updates without performance degradation

### Requirement 4: Progress Callback Integration

**User Story:** As a developer, I want the progress callback to work seamlessly with Streamlit's rendering model, so that updates are displayed correctly.

#### Acceptance Criteria

1. WHEN the Progress_Callback is invoked, THE UI_Component SHALL receive the phase name and percentage
2. THE UI_Component SHALL use Streamlit container or placeholder mechanisms to enable in-place updates
3. WHEN validation runs outside the main Streamlit flow, THE Progress_Bar SHALL still update correctly
4. THE UI_Component SHALL handle edge cases where progress_callback is None

### Requirement 5: Phase Transition Handling

**User Story:** As a user, I want clear visual feedback when validation moves from one phase to another, so that I can track overall progress.

#### Acceptance Criteria

1. WHEN IQ phase completes, THE Progress_Bar SHALL show 100% before transitioning to OQ
2. WHEN OQ phase completes, THE Progress_Bar SHALL show 100% before transitioning to PQ
3. WHEN PQ phase completes, THE Progress_Bar SHALL show 100% before displaying completion message
4. THE UI_Component SHALL provide a brief visual indication (e.g., 0.5 second pause) at phase transitions

### Requirement 6: Error State Handling

**User Story:** As a user, I want to see appropriate feedback if validation fails during a phase, so that I understand what went wrong.

#### Acceptance Criteria

1. IF a phase fails, THEN THE UI_Component SHALL display an error message with the phase name
2. WHEN validation fails, THE Progress_Bar SHALL remain at its last position
3. THE UI_Component SHALL distinguish between in-progress, completed, and failed states
4. WHEN an error occurs, THE UI_Component SHALL clear the Progress_Bar and display error details

### Requirement 7: Backward Compatibility

**User Story:** As a developer, I want the improved progress bar to work with the existing orchestrator code, so that minimal changes are required.

#### Acceptance Criteria

1. THE UI_Component SHALL accept the same progress_callback signature (phase: str, percentage: float)
2. THE Orchestrator SHALL continue calling progress_callback with phase names ("IQ", "OQ", "PQ", "Starting validation", "Complete", "Generating certificate")
3. THE UI_Component SHALL handle all existing phase names without modification to the Orchestrator
4. WHEN progress_callback is None, THE Orchestrator SHALL continue to function without errors
