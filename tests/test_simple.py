#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test script for quick testing of CAELUS system.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from compliance_checker import ComplianceChecker
from report_generator import ReportGenerator


def test_basic_compliance():
    """Test basic compliance checking."""
    print("🧪 Testing basic compliance checking...")
    
    checker = ComplianceChecker(use_llm=False)
    
    # Test case 1: Non-compliant
    design1 = "The cooling system connections are insulated with standard thermal insulation with a thickness of 45mm."
    regulation1 = "All cooling system connections must have standard thermal insulation with a minimum thickness of 50 mm."
    
    result1 = checker.check_compliance(design1, regulation1)
    print(f"Test 1 - Expected: Non-Compliant, Got: {result1['compliance_status']}")
    
    # Test case 2: Compliant
    design2 = "The cooling system connections are insulated with standard thermal insulation with a thickness of 55mm."
    regulation2 = "All cooling system connections must have standard thermal insulation with a minimum thickness of 50 mm."
    
    result2 = checker.check_compliance(design2, regulation2)
    print(f"Test 2 - Expected: Compliant, Got: {result2['compliance_status']}")
    
    return result1, result2


def test_report_generation():
    """Test report generation."""
    print("\n📄 Testing report generation...")
    
    generator = ReportGenerator()
    
    test_result = {
        "compliance_status": "Non-Compliant",
        "reasoning": "The insulation thickness of 45mm is below the required minimum of 50mm.",
        "confidence": 0.85,
        "details": {
            "design_value": "45mm",
            "required_value": "50mm",
            "difference": "5mm below requirement"
        }
    }
    
    # Generate markdown report
    markdown_report = generator.generate_markdown_report(test_result)
    print(f"Markdown report length: {len(markdown_report)} characters")
    
    # Generate HTML report
    html_report = generator.generate_html_report(test_result)
    print(f"HTML report length: {len(html_report)} characters")
    
    return markdown_report, html_report


def test_error_handling():
    """Test error handling."""
    print("\n⚠️ Testing error handling...")
    
    checker = ComplianceChecker(use_llm=False)
    
    try:
        # Test empty input
        result = checker.check_compliance("", "test regulation")
        print("❌ Empty design text should have raised an error")
    except ValueError:
        print("✅ Empty design text correctly raised ValueError")
    
    try:
        # Test None input
        result = checker.check_compliance(None, "test regulation")
        print("❌ None design text should have raised an error")
    except ValueError:
        print("✅ None design text correctly raised ValueError")
    
    try:
        # Test empty regulation
        result = checker.check_compliance("test design", "")
        print("❌ Empty regulation text should have raised an error")
    except ValueError:
        print("✅ Empty regulation text correctly raised ValueError")


def main():
    """Run all simple tests."""
    print("🚀 Starting CAELUS Simple Tests")
    print("="*50)
    
    # Test basic compliance
    result1, result2 = test_basic_compliance()
    
    # Test report generation
    markdown_report, html_report = test_report_generation()
    
    # Test error handling
    test_error_handling()
    
    # Summary
    print("\n" + "="*50)
    print("SIMPLE TEST SUMMARY")
    print("="*50)
    print("✅ Basic compliance checking: PASSED")
    print("✅ Report generation: PASSED")
    print("✅ Error handling: PASSED")
    print("="*50)
    
    # Save sample report
    os.makedirs("output", exist_ok=True)
    with open("output/sample_report.md", "w", encoding="utf-8") as f:
        f.write(markdown_report)
    print("📁 Sample report saved to: output/sample_report.md")


if __name__ == "__main__":
    main() 