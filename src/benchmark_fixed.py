 #!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Benchmark and evaluation system for CAELUS compliance checking.
"""

import os
import json
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CAELUSBenchmark:
    """Comprehensive benchmark and evaluation system for CAELUS."""
    
    def __init__(self, output_dir: str = "output/benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.test_cases = self._load_test_cases()
        logger.info(f"CAELUSBenchmark initialized with output directory: {self.output_dir}")
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load predefined test cases for benchmarking."""
        test_cases = [
            {
                "id": "TC001",
                "name": "Insulation Thickness Compliance",
                "design": "The cooling system connections are insulated with standard thermal insulation with a thickness of 45mm.",
                "regulation": "All cooling system connections must have standard thermal insulation with a minimum thickness of 50 mm.",
                "expected_status": "Non-Compliant",
                "category": "material_specifications"
            },
            {
                "id": "TC002",
                "name": "Seismic Resistance Compliance",
                "design": "All cooling system components are designed to withstand seismic events up to 0.25g intensity.",
                "regulation": "Seismic resistance with a minimum intensity of 0.35g is mandatory for all cooling system components.",
                "expected_status": "Non-Compliant",
                "category": "safety_requirements"
            },
            {
                "id": "TC003",
                "name": "Emergency Power Duration Compliance",
                "design": "The emergency cooling system can operate without external power for 96 hours.",
                "regulation": "The emergency cooling system must be able to operate for at least 72 hours without an external power source in case of power failure.",
                "expected_status": "Compliant",
                "category": "emergency_systems"
            }
        ]
        logger.info(f"Loaded {len(test_cases)} test cases for benchmarking")
        return test_cases
    
    def run_compliance_benchmark(self, compliance_checker) -> Dict[str, Any]:
        """Run comprehensive compliance checking benchmark."""
        logger.info("Starting compliance benchmark...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "test_cases": [],
            "summary": {}
        }
        
        start_time = time.time()
        
        for test_case in self.test_cases:
            logger.info(f"Running test case: {test_case['id']} - {test_case['name']}")
            
            case_start_time = time.time()
            
            try:
                result = compliance_checker.check_compliance(
                    design_text=test_case["design"],
                    regulation_text=test_case["regulation"]
                )
                
                case_end_time = time.time()
                processing_time = case_end_time - case_start_time
                
                actual_status = result.get("compliance_status", "Unknown")
                is_correct = actual_status == test_case["expected_status"]
                
                case_result = {
                    "test_case_id": test_case["id"],
                    "test_case_name": test_case["name"],
                    "category": test_case["category"],
                    "expected_status": test_case["expected_status"],
                    "actual_status": actual_status,
                    "is_correct": is_correct,
                    "processing_time": processing_time,
                    "raw_result": result
                }
                
                results["test_cases"].append(case_result)
                logger.info(f"Test case {test_case['id']}: {'PASS' if is_correct else 'FAIL'}")
                
            except Exception as e:
                logger.error(f"Error in test case {test_case['id']}: {e}")
                case_result = {
                    "test_case_id": test_case["id"],
                    "test_case_name": test_case["name"],
                    "category": test_case["category"],
                    "error": str(e),
                    "is_correct": False,
                    "processing_time": 0
                }
                results["test_cases"].append(case_result)
        
        total_time = time.time() - start_time
        
        # Calculate summary metrics
        total_cases = len(results["test_cases"])
        correct_predictions = sum(1 for case in results["test_cases"] if case.get('is_correct', False))
        
        results["summary"] = {
            "total_test_cases": total_cases,
            "correct_predictions": correct_predictions,
            "overall_accuracy": (correct_predictions / total_cases * 100) if total_cases > 0 else 0,
            "total_processing_time": total_time,
            "average_processing_time": total_time / total_cases if total_cases > 0 else 0
        }
        
        logger.info("Compliance benchmark completed")
        return results
    
    def generate_benchmark_report(self, compliance_results: Dict) -> str:
        """Generate comprehensive benchmark report."""
        logger.info("Generating benchmark report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"benchmark_report_{timestamp}.html"
        
        # Create HTML report
        html_content = self._generate_html_report(compliance_results)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Also save JSON results
        json_path = self.output_dir / f"benchmark_results_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(compliance_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Benchmark report saved to: {report_path}")
        return str(report_path)
    
    def _generate_html_report(self, compliance_results: Dict) -> str:
        """Generate HTML report content."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CAELUS Benchmark Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 3px; }}
                .pass {{ color: green; }}
                .fail {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 CAELUS Benchmark Report</h1>
                <p><strong>Generated:</strong> {compliance_results.get('timestamp', 'Unknown')}</p>
            </div>
            
            <div class="section">
                <h2>📊 Compliance Benchmark Summary</h2>
                <div class="metric">
                    <strong>Overall Accuracy:</strong> {compliance_results['summary']['overall_accuracy']:.1f}%
                </div>
                <div class="metric">
                    <strong>Total Test Cases:</strong> {compliance_results['summary']['total_test_cases']}
                </div>
                <div class="metric">
                    <strong>Correct Predictions:</strong> {compliance_results['summary']['correct_predictions']}
                </div>
                <div class="metric">
                    <strong>Average Processing Time:</strong> {compliance_results['summary']['average_processing_time']:.3f}s
                </div>
            </div>
            
            <div class="section">
                <h2>📋 Detailed Test Results</h2>
                <table>
                    <tr>
                        <th>Test Case</th>
                        <th>Category</th>
                        <th>Expected</th>
                        <th>Actual</th>
                        <th>Status</th>
                        <th>Processing Time (s)</th>
                    </tr>
        """
        
        for case in compliance_results['test_cases']:
            status_class = "pass" if case.get('is_correct', False) else "fail"
            status_text = "PASS" if case.get('is_correct', False) else "FAIL"
            
            html += f"""
                    <tr>
                        <td>{case['test_case_name']}</td>
                        <td>{case['category']}</td>
                        <td>{case['expected_status']}</td>
                        <td>{case['actual_status']}</td>
                        <td class="{status_class}">{status_text}</td>
                        <td>{case.get('processing_time', 0):.3f}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
        </body>
        </html>
        """
        
        return html


def main():
    """Main function to run benchmarks."""
    from compliance_checker import ComplianceChecker
    
    # Initialize benchmark system
    benchmark = CAELUSBenchmark()
    
    # Initialize compliance checker
    checker = ComplianceChecker()  # Use default settings for consistent benchmarking
    
    # Run compliance benchmark
    logger.info("Running compliance benchmark...")
    compliance_results = benchmark.run_compliance_benchmark(checker)
    
    # Generate report
    report_path = benchmark.generate_benchmark_report(compliance_results)
    
    # Print summary
    print("\n" + "="*50)
    print("BENCHMARK SUMMARY")
    print("="*50)
    print(f"Overall Accuracy: {compliance_results['summary']['overall_accuracy']:.1f}%")
    print(f"Total Test Cases: {compliance_results['summary']['total_test_cases']}")
    print(f"Correct Predictions: {compliance_results['summary']['correct_predictions']}")
    print(f"Average Processing Time: {compliance_results['summary']['average_processing_time']:.3f}s")
    print(f"Report saved to: {report_path}")
    print("="*50)


if __name__ == "__main__":
    main()