"""
PDF report generation module.

This module provides functions to generate PDF reports for user calculations
and validation certificates.
"""

from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import CalculationReport


def generate_calculation_report(
    report_data: CalculationReport,
    output_path: str
) -> str:
    """
    Generate PDF report for user calculation.

    Args:
        report_data: Complete calculation report data
        output_path: Path to save PDF file

    Returns:
        Path to generated PDF file
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30
    )
    story.append(Paragraph(
        "Sample Size Estimator - Calculation Report",
        title_style
    ))
    story.append(Spacer(1, 0.2 * inch))

    # Metadata section
    story.append(Paragraph("<b>Report Information</b>", styles['Heading2']))
    metadata_data = [
        ["Date/Time:", report_data.timestamp.strftime("%Y-%m-%d %H:%M:%S")],
        ["Module:", report_data.module.capitalize()],
        ["Application Version:", report_data.app_version]
    ]
    metadata_table = Table(metadata_data, colWidths=[2 * inch, 4 * inch])
    metadata_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 0.3 * inch))

    # Input parameters section
    story.append(Paragraph("<b>Input Parameters</b>", styles['Heading2']))
    input_data = [[k, str(v)] for k, v in report_data.inputs.items()]
    input_table = Table(input_data, colWidths=[2 * inch, 4 * inch])
    input_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(input_table)
    story.append(Spacer(1, 0.3 * inch))

    # Results section
    story.append(Paragraph("<b>Calculated Results</b>", styles['Heading2']))

    # Check if this is a sensitivity analysis result
    if "sensitivity_analysis" in report_data.results:
        story.append(Paragraph(
            "Sensitivity Analysis: Sample sizes for different allowable failure scenarios",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.1 * inch))

        # Create table with headers
        sensitivity_data = [["Allowable Failures (c)", "Required Sample Size (n)", "Method"]]
        for result in report_data.results["sensitivity_analysis"]:
            sensitivity_data.append([
                str(result["allowable_failures"]),
                str(result["sample_size"]),
                result["method"].replace("_", " ").title()
            ])

        sensitivity_table = Table(sensitivity_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
        sensitivity_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(sensitivity_table)
    else:
        # Standard results table for non-sensitivity analysis
        results_data = [[k, str(v)] for k, v in report_data.results.items()]
        results_table = Table(results_data, colWidths=[2 * inch, 4 * inch])
        results_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(results_table)

    story.append(Spacer(1, 0.3 * inch))

    # Validation section
    story.append(Paragraph("<b>Validation Information</b>", styles['Heading2']))
    validation_color = colors.green if report_data.validated_state else colors.red
    validation_status = "VALIDATED" if report_data.validated_state else "NOT VALIDATED"
    validation_data = [
        ["Engine Hash:", report_data.engine_hash],
        ["Validation Status:", validation_status]
    ]
    validation_table = Table(validation_data, colWidths=[2 * inch, 4 * inch])
    validation_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (1, 1), (1, 1), validation_color),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(validation_table)

    # Add disclaimer if not validated
    if not report_data.validated_state:
        story.append(Spacer(1, 0.2 * inch))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.red,
            borderColor=colors.red,
            borderWidth=1,
            borderPadding=10,
            spaceAfter=10
        )
        story.append(Paragraph(
            "<b>DISCLAIMER:</b> This calculation was performed using a non-validated "
            "version of the Sample Size Estimator. Results should not be used for "
            "regulatory submissions without proper validation. Please run the validation "
            "workflow to ensure calculation accuracy and compliance.",
            disclaimer_style
        ))

    # Build PDF
    doc.build(story)

    return output_path


def generate_validation_certificate(
    test_results: dict[str, Any],
    output_path: str
) -> str:
    """
    Generate validation certificate PDF from test suite results.

    Args:
        test_results: Dictionary containing test execution results
        output_path: Path to save PDF file

    Returns:
        Path to generated PDF file

    Expected test_results structure:
    {
        "test_date": datetime,
        "tester": str,
        "system_info": {"os": str, "python_version": str, "dependencies": dict},
        "urs_results": [{"urs_id": str, "status": "PASS"|"FAIL", "test_name": str}],
        "validated_hash": str,
        "all_passed": bool
    }
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30
    )
    story.append(Paragraph("Validation Certificate", title_style))
    story.append(Paragraph(
        "Sample Size Estimator Application",
        styles['Heading2']
    ))
    story.append(Spacer(1, 0.3 * inch))

    # Test execution info
    story.append(Paragraph(
        "<b>Test Execution Information</b>",
        styles['Heading2']
    ))
    exec_data = [
        ["Test Date:", test_results["test_date"].strftime("%Y-%m-%d %H:%M:%S")],
        ["Tester:", test_results["tester"]],
        ["Operating System:", test_results["system_info"]["os"]],
        ["Python Version:", test_results["system_info"]["python_version"]]
    ]
    exec_table = Table(exec_data, colWidths=[2 * inch, 4 * inch])
    exec_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 0.3 * inch))

    # URS test results
    story.append(Paragraph(
        "<b>URS Requirement Test Results</b>",
        styles['Heading2']
    ))
    urs_data = [["URS ID", "Test Name", "Status"]]
    for result in test_results["urs_results"]:
        urs_data.append([
            result["urs_id"],
            result["test_name"],
            result["status"]
        ])

    urs_table = Table(urs_data, colWidths=[1.5 * inch, 3 * inch, 1 * inch])

    # Build table style with conditional coloring
    table_style = [
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]

    # Add color coding for PASS/FAIL
    for i, result in enumerate(test_results["urs_results"], start=1):
        if result["status"] == "PASS":
            table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.green))
        else:
            table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.red))

    urs_table.setStyle(TableStyle(table_style))
    story.append(urs_table)
    story.append(Spacer(1, 0.3 * inch))

    # Validation summary
    story.append(Paragraph("<b>Validation Summary</b>", styles['Heading2']))
    overall_status = "PASSED" if test_results["all_passed"] else "FAILED"
    status_color = colors.green if test_results["all_passed"] else colors.red
    summary_data = [
        ["Overall Status:", overall_status],
        ["Validated Hash:", test_results["validated_hash"]]
    ]
    summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (1, 0), (1, 0), status_color),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)

    # Build PDF
    doc.build(story)

    return output_path
