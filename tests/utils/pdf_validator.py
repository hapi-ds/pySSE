"""PDF validation utilities for extracting and parsing PDF report content.

This module provides functions to extract text from PDF reports and parse
calculation results for validation testing.
"""

import re
from pathlib import Path
from typing import Any

import pdfplumber


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text content from PDF file.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Extracted text content from all pages
    
    Raises:
        FileNotFoundError: If PDF file does not exist
        Exception: If PDF extraction fails
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    return text


def parse_attribute_results(pdf_text: str) -> dict[str, Any]:
    """Parse attribute analysis results from PDF text.
    
    Args:
        pdf_text: Extracted PDF text content
    
    Returns:
        Dictionary containing parsed results:
        - sample_size: Required sample size (int)
        - confidence: Confidence level (float)
        - reliability: Reliability level (float)
        - failures: Number of allowable failures (int)
        - method: Calculation method (str)
    """
    results = {}
    
    # Extract sample size
    sample_size_match = re.search(r"Required Sample Size[:\s]+(\d+)", pdf_text, re.IGNORECASE)
    if sample_size_match:
        results["sample_size"] = int(sample_size_match.group(1))
    
    # Extract confidence level
    confidence_match = re.search(r"Confidence Level[:\s]+([\d.]+)\s*%", pdf_text, re.IGNORECASE)
    if confidence_match:
        results["confidence"] = float(confidence_match.group(1))
    
    # Extract reliability level
    reliability_match = re.search(r"Reliability[:\s]+([\d.]+)\s*%", pdf_text, re.IGNORECASE)
    if reliability_match:
        results["reliability"] = float(reliability_match.group(1))
    
    # Extract allowable failures
    failures_match = re.search(r"Allowable Failures[:\s]+(\d+)", pdf_text, re.IGNORECASE)
    if failures_match:
        results["failures"] = int(failures_match.group(1))
    
    # Extract method
    if "Success Run" in pdf_text:
        results["method"] = "Success Run"
    elif "Binomial" in pdf_text:
        results["method"] = "Binomial"
    
    return results


def parse_variables_results(pdf_text: str) -> dict[str, Any]:
    """Parse variables analysis results from PDF text.
    
    Args:
        pdf_text: Extracted PDF text content
    
    Returns:
        Dictionary containing parsed results:
        - sample_size: Sample size (int)
        - tolerance_factor: Tolerance factor k (float)
        - lower_tolerance_limit: Lower tolerance limit (float)
        - upper_tolerance_limit: Upper tolerance limit (float)
        - ppk: Process performance index (float, optional)
    """
    results = {}
    
    # Extract sample size
    sample_size_match = re.search(r"Sample Size[:\s]+(\d+)", pdf_text, re.IGNORECASE)
    if sample_size_match:
        results["sample_size"] = int(sample_size_match.group(1))
    
    # Extract tolerance factor
    tolerance_factor_match = re.search(r"Tolerance Factor[:\s\(k\)]+[:\s]+([\d.]+)", pdf_text, re.IGNORECASE)
    if tolerance_factor_match:
        results["tolerance_factor"] = float(tolerance_factor_match.group(1))
    
    # Extract lower tolerance limit
    ltl_match = re.search(r"Lower Tolerance Limit[:\s]+([\d.-]+)", pdf_text, re.IGNORECASE)
    if ltl_match:
        results["lower_tolerance_limit"] = float(ltl_match.group(1))
    
    # Extract upper tolerance limit
    utl_match = re.search(r"Upper Tolerance Limit[:\s]+([\d.-]+)", pdf_text, re.IGNORECASE)
    if utl_match:
        results["upper_tolerance_limit"] = float(utl_match.group(1))
    
    # Extract Ppk (optional)
    ppk_match = re.search(r"Ppk[:\s]+([\d.]+)", pdf_text, re.IGNORECASE)
    if ppk_match:
        results["ppk"] = float(ppk_match.group(1))
    
    return results


def parse_non_normal_results(pdf_text: str) -> dict[str, Any]:
    """Parse non-normal analysis results from PDF text.
    
    Args:
        pdf_text: Extracted PDF text content
    
    Returns:
        Dictionary containing parsed results:
        - transformation: Transformation method used (str)
        - shapiro_wilk_p: Shapiro-Wilk p-value (float)
        - anderson_darling_stat: Anderson-Darling statistic (float)
        - sample_size: Transformed sample size (int, optional)
    """
    results = {}
    
    # Extract transformation method
    if "Log" in pdf_text or "Logarithmic" in pdf_text:
        results["transformation"] = "Log"
    elif "Square Root" in pdf_text:
        results["transformation"] = "Square Root"
    elif "Box-Cox" in pdf_text:
        results["transformation"] = "Box-Cox"
    
    # Extract Shapiro-Wilk p-value
    shapiro_match = re.search(r"Shapiro-Wilk.*?p-value[:\s]+([\d.]+)", pdf_text, re.IGNORECASE | re.DOTALL)
    if shapiro_match:
        results["shapiro_wilk_p"] = float(shapiro_match.group(1))
    
    # Extract Anderson-Darling statistic
    anderson_match = re.search(r"Anderson-Darling.*?statistic[:\s]+([\d.]+)", pdf_text, re.IGNORECASE | re.DOTALL)
    if anderson_match:
        results["anderson_darling_stat"] = float(anderson_match.group(1))
    
    # Extract sample size if present
    sample_size_match = re.search(r"Sample Size[:\s]+(\d+)", pdf_text, re.IGNORECASE)
    if sample_size_match:
        results["sample_size"] = int(sample_size_match.group(1))
    
    return results


def parse_reliability_results(pdf_text: str) -> dict[str, Any]:
    """Parse reliability analysis results from PDF text.
    
    Args:
        pdf_text: Extracted PDF text content
    
    Returns:
        Dictionary containing parsed results:
        - test_duration: Test duration in hours (float)
        - acceleration_factor: Acceleration factor (float)
        - confidence: Confidence level (float)
        - failures: Number of failures (int)
    """
    results = {}
    
    # Extract test duration
    duration_match = re.search(r"Test Duration[:\s]+([\d.]+)\s*(?:hours?|hrs?)", pdf_text, re.IGNORECASE)
    if duration_match:
        results["test_duration"] = float(duration_match.group(1))
    
    # Extract acceleration factor
    af_match = re.search(r"Acceleration Factor[:\s]+([\d.]+)", pdf_text, re.IGNORECASE)
    if af_match:
        results["acceleration_factor"] = float(af_match.group(1))
    
    # Extract confidence level
    confidence_match = re.search(r"Confidence Level[:\s]+([\d.]+)\s*%", pdf_text, re.IGNORECASE)
    if confidence_match:
        results["confidence"] = float(confidence_match.group(1))
    
    # Extract number of failures
    failures_match = re.search(r"Number of Failures[:\s]+(\d+)", pdf_text, re.IGNORECASE)
    if failures_match:
        results["failures"] = int(failures_match.group(1))
    
    return results
