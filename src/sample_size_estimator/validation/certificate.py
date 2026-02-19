"""Validation certificate generation module.

This module provides the ValidationCertificateGenerator class for generating
comprehensive validation certificate PDFs with IQ/OQ/PQ chapters, URS traceability,
and tamper detection.
"""

import hashlib
import platform
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .models import IQResult, OQResult, PQResult, ValidationResult


class ValidationCertificateGenerator:
    """Generates validation certificate PDFs with IQ/OQ/PQ chapters.
    
    This class:
    - Generates comprehensive validation certificate PDFs
    - Includes title page with validation date and status
    - Includes system information section
    - Includes separate chapters for IQ, OQ, and PQ results
    - Includes URS traceability matrix
    - Calculates certificate SHA-256 hash for tamper detection
    
    Validates: Requirements 10.1-10.8, 11.1-11.6, 12.1-12.6, 13.1-13.6, 14.1-14.5, 26.1, 26.2
    """

    def __init__(self, urs_requirements: dict[str, str] | None = None):
        """Initialize with URS requirements mapping.
        
        Args:
            urs_requirements: Mapping of URS IDs to requirement text.
                            If None, uses generic requirement text.
        """
        self.urs_requirements = urs_requirements or {}
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self) -> None:
        """Set up custom paragraph styles for the certificate."""
        # Title style
        self.title_style = ParagraphStyle(
            'CertificateTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Chapter heading style
        self.chapter_style = ParagraphStyle(
            'ChapterHeading',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=20,
            spaceBefore=20
        )
        
        # Section heading style
        self.section_style = ParagraphStyle(
            'SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )

    def generate_certificate(
        self,
        validation_result: ValidationResult,
        output_path: Path
    ) -> str:
        """Generate complete validation certificate PDF.
        
        This method:
        1. Creates PDF document with title page
        2. Adds system information section
        3. Adds IQ chapter with installation verification details
        4. Adds OQ chapter with calculation verification details
        5. Adds PQ chapter with UI verification details
        6. Adds URS traceability matrix
        7. Calculates and returns certificate SHA-256 hash
        
        Args:
            validation_result: Complete validation results
            output_path: Path for output PDF file
        
        Returns:
            SHA-256 hash of generated certificate
        
        Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        
        # Generate all sections
        story.extend(self.generate_title_page(validation_result))
        story.append(PageBreak())
        
        story.extend(self.generate_system_info_section(validation_result.system_info))
        story.append(PageBreak())
        
        story.extend(self.generate_iq_chapter(validation_result.iq_result))
        story.append(PageBreak())
        
        story.extend(self.generate_oq_chapter(validation_result.oq_result))
        story.append(PageBreak())
        
        story.extend(self.generate_pq_chapter(validation_result.pq_result))
        story.append(PageBreak())
        
        story.extend(self.generate_traceability_matrix(validation_result))
        
        # Build PDF
        doc.build(story)
        
        # Calculate certificate hash
        certificate_hash = self._calculate_certificate_hash(output_path)
        
        return certificate_hash

    def generate_title_page(self, validation_result: ValidationResult) -> list:
        """Generate certificate title page.
        
        Args:
            validation_result: Validation results
        
        Returns:
            List of flowable elements for the title page
        
        Validates: Requirements 10.2
        """
        elements = []
        
        # Title
        elements.append(Spacer(1, 1.5 * inch))
        elements.append(Paragraph(
            "VALIDATION CERTIFICATE",
            self.title_style
        ))
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(
            "Sample Size Estimator Application",
            self.styles['Heading2']
        ))
        elements.append(Spacer(1, 0.5 * inch))
        
        # Validation status
        status_text = "PASSED" if validation_result.success else "FAILED"
        status_color = colors.green if validation_result.success else colors.red
        
        status_style = ParagraphStyle(
            'StatusStyle',
            parent=self.styles['Normal'],
            fontSize=20,
            textColor=status_color,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph(f"Status: {status_text}", status_style))
        elements.append(Spacer(1, 0.5 * inch))
        
        # Certificate information
        cert_data = [
            ["Validation Date:", validation_result.validation_date.strftime("%Y-%m-%d %H:%M:%S")],
            ["Validation Hash:", validation_result.validation_hash[:16] + "..."],
            ["Expiry Date:", "365 days from validation date"],
        ]
        
        cert_table = Table(cert_data, colWidths=[2.5 * inch, 3.5 * inch])
        cert_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(cert_table)
        
        return elements

    def generate_system_info_section(self, system_info) -> list:
        """Generate system information section.
        
        Args:
            system_info: System information object
        
        Returns:
            List of flowable elements for system information
        
        Validates: Requirements 10.3
        """
        elements = []
        
        # Section heading
        elements.append(Paragraph("System Information", self.chapter_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Operating system information
        elements.append(Paragraph("Operating System", self.section_style))
        os_data = [
            ["OS Name:", system_info.os_name],
            ["OS Version:", system_info.os_version],
            ["Python Version:", system_info.python_version],
        ]
        
        os_table = Table(os_data, colWidths=[2 * inch, 4 * inch])
        os_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(os_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Dependencies
        elements.append(Paragraph("Key Dependencies", self.section_style))
        
        dep_data = [["Package", "Version"]]
        for package, version in sorted(system_info.dependencies.items()):
            dep_data.append([package, version])
        
        dep_table = Table(dep_data, colWidths=[2 * inch, 2 * inch])
        dep_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(dep_table)
        
        return elements

    def generate_iq_chapter(self, iq_result: IQResult) -> list:
        """Generate IQ chapter with installation verification details.
        
        Args:
            iq_result: IQ test results
        
        Returns:
            List of flowable elements for IQ chapter
        
        Validates: Requirements 10.4, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
        """
        elements = []
        
        # Chapter heading
        elements.append(Paragraph(
            "Chapter 1: Installation Qualification (IQ)",
            self.chapter_style
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Summary
        summary = iq_result.get_summary()
        status_text = "PASSED" if iq_result.passed else "FAILED"
        status_color = colors.green if iq_result.passed else colors.red
        
        elements.append(Paragraph(
            f"<b>Overall Status:</b> <font color='{status_color.hexval()}'>{status_text}</font>",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>Total Checks:</b> {summary['total']} | "
            f"<b>Passed:</b> {summary['passed']} | "
            f"<b>Failed:</b> {summary['failed']}",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>Execution Time:</b> {iq_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.3 * inch))
        
        # IQ checks table
        elements.append(Paragraph("Installation Verification Details", self.section_style))
        
        iq_data = [["Check Name", "Description", "Status", "Details"]]
        
        for check in iq_result.checks:
            status_text = "PASS" if check.passed else "FAIL"
            details = ""
            
            if check.expected_value and check.actual_value:
                details = f"Expected: {check.expected_value}\nActual: {check.actual_value}"
            elif check.failure_reason:
                details = check.failure_reason
            
            iq_data.append([
                check.name,
                check.description,
                status_text,
                details
            ])
        
        iq_table = Table(iq_data, colWidths=[1.5 * inch, 2 * inch, 0.8 * inch, 2 * inch])
        
        # Build table style with conditional coloring
        table_style = [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]
        
        # Add color coding for PASS/FAIL
        for i, check in enumerate(iq_result.checks, start=1):
            if check.passed:
                table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.green))
            else:
                table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.red))
        
        iq_table.setStyle(TableStyle(table_style))
        elements.append(iq_table)
        
        return elements

    def generate_oq_chapter(self, oq_result: OQResult) -> list:
        """Generate OQ chapter with calculation verification details.
        
        Args:
            oq_result: OQ test results
        
        Returns:
            List of flowable elements for OQ chapter
        
        Validates: Requirements 10.5, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6
        """
        elements = []
        
        # Chapter heading
        elements.append(Paragraph(
            "Chapter 2: Operational Qualification (OQ)",
            self.chapter_style
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Summary
        summary = oq_result.get_summary()
        status_text = "PASSED" if oq_result.passed else "FAILED"
        status_color = colors.green if oq_result.passed else colors.red
        
        elements.append(Paragraph(
            f"<b>Overall Status:</b> <font color='{status_color.hexval()}'>{status_text}</font>",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>Total Tests:</b> {summary['total']} | "
            f"<b>Passed:</b> {summary['passed']} | "
            f"<b>Failed:</b> {summary['failed']}",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>Execution Time:</b> {oq_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Group tests by functional area
        grouped_tests = oq_result.group_by_functional_area()
        
        for area, tests in sorted(grouped_tests.items()):
            elements.append(Paragraph(f"Functional Area: {area}", self.section_style))
            
            oq_data = [["Test Name", "URS ID", "Status", "Failure Reason"]]
            
            for test in tests:
                status_text = "PASS" if test.passed else "FAIL"
                failure_reason = test.failure_reason or ""
                
                oq_data.append([
                    test.test_name.split("::")[-1],  # Just the test function name
                    test.urs_id,
                    status_text,
                    failure_reason
                ])
            
            oq_table = Table(oq_data, colWidths=[2 * inch, 1.2 * inch, 0.8 * inch, 2.3 * inch])
            
            # Build table style with conditional coloring
            table_style = [
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]
            
            # Add color coding for PASS/FAIL
            for i, test in enumerate(tests, start=1):
                if test.passed:
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.green))
                else:
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.red))
            
            oq_table.setStyle(TableStyle(table_style))
            elements.append(oq_table)
            elements.append(Spacer(1, 0.2 * inch))
        
        return elements

    def generate_pq_chapter(self, pq_result: PQResult) -> list:
        """Generate PQ chapter with UI verification details.
        
        Args:
            pq_result: PQ test results
        
        Returns:
            List of flowable elements for PQ chapter
        
        Validates: Requirements 10.6, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6
        """
        elements = []
        
        # Chapter heading
        elements.append(Paragraph(
            "Chapter 3: Performance Qualification (PQ)",
            self.chapter_style
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Summary
        summary = pq_result.get_summary()
        status_text = "PASSED" if pq_result.passed else "FAILED"
        status_color = colors.green if pq_result.passed else colors.red
        
        elements.append(Paragraph(
            f"<b>Overall Status:</b> <font color='{status_color.hexval()}'>{status_text}</font>",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>Total Tests:</b> {summary['total']} | "
            f"<b>Passed:</b> {summary['passed']} | "
            f"<b>Failed:</b> {summary['failed']}",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>Execution Time:</b> {pq_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Group tests by module
        grouped_tests = pq_result.group_by_module()
        
        for module, tests in sorted(grouped_tests.items()):
            elements.append(Paragraph(f"Analysis Module: {module}", self.section_style))
            
            pq_data = [["Test Name", "URS ID", "Workflow", "Status"]]
            
            for test in tests:
                status_text = "PASS" if test.passed else "FAIL"
                
                pq_data.append([
                    test.test_name.split("::")[-1],  # Just the test function name
                    test.urs_id,
                    test.workflow_description[:50] + "..." if len(test.workflow_description) > 50 else test.workflow_description,
                    status_text
                ])
            
            pq_table = Table(pq_data, colWidths=[1.8 * inch, 1.2 * inch, 2.3 * inch, 0.8 * inch])
            
            # Build table style with conditional coloring
            table_style = [
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]
            
            # Add color coding for PASS/FAIL
            for i, test in enumerate(tests, start=1):
                if test.passed:
                    table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.green))
                else:
                    table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.red))
            
            pq_table.setStyle(TableStyle(table_style))
            elements.append(pq_table)
            elements.append(Spacer(1, 0.2 * inch))
        
        return elements

    def generate_traceability_matrix(self, validation_result: ValidationResult) -> list:
        """Generate URS traceability matrix.
        
        Args:
            validation_result: Complete validation results
        
        Returns:
            List of flowable elements for traceability matrix
        
        Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5
        """
        elements = []
        
        # Chapter heading
        elements.append(Paragraph(
            "URS Traceability Matrix",
            self.chapter_style
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        elements.append(Paragraph(
            "This matrix shows the mapping between User Requirements Specification (URS) "
            "requirements and validation tests, demonstrating complete traceability.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Collect all tests with URS IDs
        all_tests = []
        
        # Add OQ tests
        for test in validation_result.oq_result.tests:
            all_tests.append({
                "urs_id": test.urs_id,
                "test_name": test.test_name.split("::")[-1],
                "phase": "OQ",
                "status": "PASS" if test.passed else "FAIL"
            })
        
        # Add PQ tests
        for test in validation_result.pq_result.tests:
            all_tests.append({
                "urs_id": test.urs_id,
                "test_name": test.test_name.split("::")[-1],
                "phase": "PQ",
                "status": "PASS" if test.passed else "FAIL"
            })
        
        # Sort by URS ID
        all_tests.sort(key=lambda x: x["urs_id"])
        
        # Create traceability table
        trace_data = [["URS ID", "Test Name", "Phase", "Status"]]
        
        for test in all_tests:
            trace_data.append([
                test["urs_id"],
                test["test_name"],
                test["phase"],
                test["status"]
            ])
        
        trace_table = Table(trace_data, colWidths=[1.5 * inch, 2.5 * inch, 0.8 * inch, 0.8 * inch])
        
        # Build table style with conditional coloring
        table_style = [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]
        
        # Add color coding for PASS/FAIL
        for i, test in enumerate(all_tests, start=1):
            if test["status"] == "PASS":
                table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.green))
            else:
                table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.red))
        
        trace_table.setStyle(TableStyle(table_style))
        elements.append(trace_table)
        
        # Summary statistics
        elements.append(Spacer(1, 0.3 * inch))
        unique_urs = len(set(test["urs_id"] for test in all_tests))
        elements.append(Paragraph(
            f"<b>Traceability Summary:</b> {unique_urs} unique URS requirements validated "
            f"by {len(all_tests)} tests",
            self.styles['Normal']
        ))
        
        return elements

    def _calculate_certificate_hash(self, certificate_path: Path) -> str:
        """Calculate SHA-256 hash of certificate PDF.
        
        Args:
            certificate_path: Path to certificate PDF file
        
        Returns:
            Hexadecimal hash string
        
        Validates: Requirements 26.1, 26.2
        """
        sha256_hash = hashlib.sha256()
        
        with open(certificate_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
