# PDF Table Line Breaks Bugfix Design

## Overview

This bugfix addresses text overflow in PDF table cells by replacing plain string rendering with ReportLab Paragraph flowables. Currently, when table cell content exceeds column width, text overflows cell boundaries and overlaps adjacent cells, making reports unreadable. The fix will wrap all table cell content in Paragraph objects, enabling automatic text wrapping within cell boundaries while preserving all existing table styling, colors, and formatting.

The fix targets two files:
- `src/sample_size_estimator/reports.py` - Calculation reports and simple validation certificates
- `src/sample_size_estimator/validation/certificate.py` - Comprehensive validation certificates with IQ/OQ/PQ chapters

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when table cell content length exceeds the allocated column width
- **Property (P)**: The desired behavior when cell content is long - text should wrap within cell boundaries using Paragraph flowables
- **Preservation**: Existing table styling (colors, fonts, padding, alignment, conditional coloring) and PDF layout that must remain unchanged
- **Paragraph flowable**: ReportLab's text container that automatically handles line wrapping and formatting
- **Table cell**: Individual data cell in a ReportLab Table object
- **Column width**: The fixed width allocated to each table column (measured in inches)
- **Text overflow**: When rendered text extends beyond its container boundaries

## Bug Details

### Fault Condition

The bug manifests when table cell content (strings) exceeds the allocated column width. The ReportLab Table class renders plain strings without wrapping, causing text to overflow cell boundaries and overlap with adjacent cells or extend beyond the page margin.

**Formal Specification:**
```
FUNCTION isBugCondition(cell_content, column_width, font_size)
  INPUT: 
    cell_content of type string
    column_width of type float (in points)
    font_size of type int
  OUTPUT: boolean
  
  RETURN estimatedTextWidth(cell_content, font_size) > column_width
         AND cell_content is rendered as plain string
         AND NOT wrapped in Paragraph flowable
END FUNCTION
```

### Examples

- **Calculation Report - Long Input Parameter**: Input parameter name "Maximum Allowable Failure Rate for Statistical Significance Testing" in a 2-inch column overflows and overlaps with the value column
- **Validation Certificate - Long Test Name**: Test name "test_acceptance_sampling_calculation_with_extreme_confidence_level_requirements" in a 2-inch column overflows into adjacent columns
- **Dependency Table - Long Package Name**: Package name "sample-size-estimator-validation-framework" with version "1.2.3.4567890" overflows the 2-inch column
- **OQ Chapter - Long Failure Reason**: Failure reason "Expected sample size 150 but got 148 due to rounding differences in binomial coefficient calculation" overflows the 2.3-inch column
- **Edge Case - Short Text**: Text "PASS" in any column width renders correctly (no wrapping needed, should continue working)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Table styling (grid lines, background colors, padding, alignment) must continue to render exactly as before
- Conditional coloring for PASS/FAIL status cells must continue to apply green/red colors correctly
- Font specifications (Helvetica, Helvetica-Bold, font sizes) must remain unchanged
- Table column widths must remain at their current values
- PDF page layout and page breaks must continue to work correctly
- Multi-page reports must continue to flow across pages properly
- Validation certificate SHA-256 hashes will change (expected due to content changes), but hash calculation logic must remain unchanged

**Scope:**
All table cells that contain short text fitting within column width should be completely unaffected by this fix. This includes:
- Status indicators ("PASS", "FAIL", "PASSED", "FAILED")
- Short labels and headers
- Numeric values and dates
- URS IDs and phase indicators
- Any text where estimatedTextWidth < column_width

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause is:

1. **Plain String Rendering**: All table cells use plain Python strings instead of Paragraph flowables
   - In `reports.py`: Lines 60, 76, 103-108, 127-131, 147, 260-265, 280-285
   - In `certificate.py`: Lines 177-180, 234-237, 268-271, 330-340, 400-410, 470-480, 580-590
   - ReportLab's Table class renders plain strings without any wrapping logic

2. **No Text Wrapping Configuration**: Tables are created with fixed column widths but no wrapping mechanism
   - Column widths are specified (e.g., `colWidths=[2 * inch, 4 * inch]`)
   - No Paragraph flowables are used to enable wrapping within those widths

3. **Missing Style Configuration**: Paragraph styles exist but are only used for headings, not table cells
   - `getSampleStyleSheet()` provides 'Normal' style suitable for table cells
   - This style is never applied to table cell content

## Correctness Properties

Property 1: Fault Condition - Text Wrapping in Long Cells

_For any_ table cell where the content length exceeds the column width (isBugCondition returns true), the fixed code SHALL wrap the text using a Paragraph flowable with the 'Normal' style, ensuring all text remains within cell boundaries and no text overlaps with adjacent cells.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

Property 2: Preservation - Table Styling and Short Text

_For any_ table cell where the content length does NOT exceed the column width (isBugCondition returns false), the fixed code SHALL produce exactly the same visual output as the original code, preserving all styling, colors, fonts, alignment, and rendering behavior.

**Validates: Requirements 3.1, 3.2, 3.3, 3.5, 3.6**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File 1**: `src/sample_size_estimator/reports.py`

**Function**: `generate_calculation_report`

**Specific Changes**:
1. **Import Paragraph**: Already imported, no change needed

2. **Create helper function**: Add a `_wrap_text()` helper function at module level to wrap strings in Paragraph flowables
   - Takes string and style as parameters
   - Returns Paragraph object
   - Handles None values gracefully

3. **Wrap metadata table cells**: Convert metadata_data list items to use Paragraph flowables
   - Line 60: Wrap date/time, module, and version values

4. **Wrap input parameters table cells**: Convert input_data list items to use Paragraph flowables
   - Line 76: Wrap parameter names and values

5. **Wrap sensitivity analysis table cells**: Convert sensitivity_data list items to use Paragraph flowables
   - Lines 103-108: Wrap allowable failures, sample size, and method values

6. **Wrap results table cells**: Convert results_data list items to use Paragraph flowables
   - Lines 127-131: Wrap result names and values

7. **Wrap validation table cells**: Convert validation_data list items to use Paragraph flowables
   - Line 147: Wrap engine hash and validation status

**Function**: `generate_validation_certificate`

**Specific Changes**:
1. **Wrap execution info table cells**: Convert exec_data list items to use Paragraph flowables
   - Lines 260-265: Wrap test date, tester, OS, and Python version

2. **Wrap URS results table cells**: Convert urs_data list items to use Paragraph flowables
   - Lines 280-285: Wrap URS ID, test name, and status

3. **Wrap summary table cells**: Convert summary_data list items to use Paragraph flowables
   - Lines 300-305: Wrap overall status and validated hash

**File 2**: `src/sample_size_estimator/validation/certificate.py`

**Class**: `ValidationCertificateGenerator`

**Specific Changes**:
1. **Add helper method**: Add `_wrap_text()` instance method to wrap strings in Paragraph flowables
   - Similar to reports.py helper but as instance method
   - Uses self.styles['Normal'] by default

2. **Wrap title page table cells**: Convert cert_data list items to use Paragraph flowables
   - Lines 177-180: Wrap validation date, hash, and expiry date

3. **Wrap system info table cells**: Convert os_data and dep_data list items to use Paragraph flowables
   - Lines 234-237: Wrap OS name, version, Python version
   - Lines 268-271: Wrap package names and versions

4. **Wrap IQ chapter table cells**: Convert iq_data list items to use Paragraph flowables
   - Lines 330-340: Wrap check name, description, status, and details

5. **Wrap OQ chapter table cells**: Convert oq_data list items to use Paragraph flowables
   - Lines 400-410: Wrap test name, URS ID, status, and failure reason

6. **Wrap PQ chapter table cells**: Convert pq_data list items to use Paragraph flowables
   - Lines 470-480: Wrap test name, URS ID, workflow description, and status

7. **Wrap traceability matrix table cells**: Convert trace_data list items to use Paragraph flowables
   - Lines 580-590: Wrap URS ID, test name, phase, and status

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code by generating PDFs with long text and observing overflow, then verify the fix works correctly and preserves existing behavior.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Create test cases that generate PDFs with intentionally long text in various table cells. Manually inspect the generated PDFs to observe text overflow. Run these tests on the UNFIXED code to confirm the bug exists and understand its manifestation.

**Test Cases**:
1. **Long Input Parameter Test**: Generate calculation report with input parameter name exceeding 100 characters (will show overflow on unfixed code)
2. **Long Test Name Test**: Generate validation certificate with test name exceeding 80 characters (will show overflow on unfixed code)
3. **Long Failure Reason Test**: Generate OQ chapter with failure reason exceeding 150 characters (will show overflow on unfixed code)
4. **Long Package Name Test**: Generate system info section with package name exceeding 50 characters (will show overflow on unfixed code)
5. **Multiple Long Cells Test**: Generate table row with multiple cells containing long text (will show overlapping on unfixed code)

**Expected Counterexamples**:
- Text extends beyond cell boundaries and overlaps adjacent cells
- Text may extend beyond page margins
- Multiple long cells in same row create unreadable overlapping text
- Possible causes: plain string rendering, no Paragraph wrapping, fixed column widths without wrapping

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL table_cell WHERE isBugCondition(table_cell.content, table_cell.column_width, table_cell.font_size) DO
  pdf := generate_pdf_with_fixed_code(table_cell)
  ASSERT text_is_wrapped_within_cell_boundaries(pdf, table_cell)
  ASSERT no_text_overlaps_adjacent_cells(pdf, table_cell)
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL table_cell WHERE NOT isBugCondition(table_cell.content, table_cell.column_width, table_cell.font_size) DO
  pdf_original := generate_pdf_with_original_code(table_cell)
  pdf_fixed := generate_pdf_with_fixed_code(table_cell)
  ASSERT visual_appearance_identical(pdf_original, pdf_fixed, table_cell)
  ASSERT styling_preserved(pdf_fixed, table_cell)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain (short text, medium text, various table types)
- It catches edge cases that manual unit tests might miss (empty strings, single characters, exact boundary cases)
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for short text cells, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Short Text Preservation**: Observe that "PASS", "FAIL", dates, and short labels render correctly on unfixed code, then write test to verify this continues after fix
2. **Table Styling Preservation**: Observe that grid lines, background colors, padding, and alignment work correctly on unfixed code, then write test to verify this continues after fix
3. **Conditional Coloring Preservation**: Observe that PASS/FAIL cells are colored green/red correctly on unfixed code, then write test to verify this continues after fix
4. **Font Styling Preservation**: Observe that bold headers and regular text render correctly on unfixed code, then write test to verify this continues after fix

### Unit Tests

- Test `_wrap_text()` helper function with various input types (strings, None, empty strings)
- Test PDF generation with long text in each table type (metadata, input parameters, results, validation info)
- Test PDF generation with short text to verify no regression
- Test edge cases (empty tables, single-cell tables, tables with mixed long/short content)
- Test that Paragraph objects are created with correct style ('Normal')

### Property-Based Tests

- Generate random strings of varying lengths (0-500 characters) and verify wrapping behavior
- Generate random table configurations (different column counts, widths) and verify text fits within cells
- Generate random combinations of long and short text in same table and verify no overlapping
- Test across all table types in both files (calculation reports, validation certificates, IQ/OQ/PQ chapters)

### Integration Tests

- Generate complete calculation report with realistic long input parameters and verify readability
- Generate complete validation certificate with realistic long test names and failure reasons and verify readability
- Generate multi-page reports with long text and verify page breaks work correctly
- Verify that validation certificate hashes change (expected) but hash calculation logic works correctly
- Test visual inspection: manually review generated PDFs to confirm text wrapping looks professional
