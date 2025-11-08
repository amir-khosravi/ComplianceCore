#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Benchmark and evaluation system for CAELUS compliance checking.
This module provides comprehensive testing and evaluation capabilities.
"""

import os
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CAELUSBenchmark:
    """Comprehensive benchmark and evaluation system for CAELUS."""
    
    def __init__(self, output_dir: str = "output/benchmarks"):
        """
        Initialize the benchmark system.
        
        Args:
            output_dir: Directory to save benchmark results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Benchmark datasets
        self.test_cases = self._load_test_cases()
        
        # Performance metrics
        self.metrics = {
            'accuracy': [],
            'precision': [],
            'recall': [],
            'f1_score': [],
            'processing_time': [],
            'memory_usage': []
        }
        
        logger.info(f"CAELUSBenchmark initialized with output directory: {self.output_dir}")
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load predefined test cases for benchmarking."""
        test_cases = [
            # Test Case 1: Insulation Thickness
            {
                "id": "TC001",
                "name": "Insulation Thickness Compliance",
                "design": "The cooling system connections are insulated with standard thermal insulation with a thickness of 45mm.",
                "regulation": "All cooling system connections must have standard thermal insulation with a minimum thickness of 50 mm.",
                "expected_status": "Non-Compliant",
                "expected_reasoning": "thickness less than required",
                "category": "material_specifications"
            },
            # Test Case 2: Seismic Resistance
            {
                "id": "TC002",
                "name": "Seismic Resistance Compliance",
                "design": "All cooling system components are designed to withstand seismic events up to 0.25g intensity.",
                "regulation": "Seismic resistance with a minimum intensity of 0.35g is mandatory for all cooling system components.",
                "expected_status": "Non-Compliant",
                "expected_reasoning": "seismic resistance below requirement",
                "category": "safety_requirements"
            },
            # Test Case 3: Emergency Power Duration
            {
                "id": "TC003",
                "name": "Emergency Power Duration Compliance",
                "design": "The emergency cooling system can operate without external power for 96 hours.",
                "regulation": "The emergency cooling system must be able to operate for at least 72 hours without an external power source in case of power failure.",
                "expected_status": "Compliant",
                "expected_reasoning": "duration exceeds requirement",
                "category": "emergency_systems"
            },
            # Test Case 4: Pump Count
            {
                "id": "TC004",
                "name": "Containment Pump Count Compliance",
                "design": "Containment spray system consists of two independent pumps with separate power supplies.",
                "regulation": "The containment spray system must consist of at least three independent pumps.",
                "expected_status": "Non-Compliant",
                "expected_reasoning": "insufficient pump count",
                "category": "safety_systems"
            },
            # Test Case 5: Pipe Wall Thickness
            {
                "id": "TC005",
                "name": "Pipe Wall Thickness Compliance",
                "design": "The pipe wall thickness is 38 mm.",
                "regulation": "The wall thickness of the main pipes must be calculated according to pressure and temperature and must not be less than 40 mm.",
                "expected_status": "Non-Compliant",
                "expected_reasoning": "wall thickness below minimum",
                "category": "structural_requirements"
            },
            # Test Case 6: Material Specification
            {
                "id": "TC006",
                "name": "Material Specification Compliance",
                "design": "Primary cooling system pipes are made of 316L stainless steel.",
                "regulation": "Primary cooling system pipes must be made of 300-series stainless steel or equivalent resistant alloys.",
                "expected_status": "Compliant",
                "expected_reasoning": "material meets specification",
                "category": "material_specifications"
            }
        ]
        
        logger.info(f"Loaded {len(test_cases)} test cases for benchmarking")
        return test_cases
    
    def run_compliance_benchmark(self, compliance_checker) -> Dict[str, Any]:
        """
        Run comprehensive compliance checking benchmark.
        
        Args:
            compliance_checker: Instance of ComplianceChecker
            
        Returns:
            Dictionary containing benchmark results
        """
        logger.info("Starting compliance benchmark...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "test_cases": [],
            "summary": {},
            "performance": {}
        }
        
        start_time = time.time()
        
        for test_case in self.test_cases:
            logger.info(f"Running test case: {test_case['id']} - {test_case['name']}")
            
            case_start_time = time.time()
            
            # Run compliance check
            try:
                result = compliance_checker.check_compliance(
                    design_text=test_case["design"],
                    regulation_text=test_case["regulation"]
                )
                
                case_end_time = time.time()
                processing_time = case_end_time - case_start_time
                
                # Evaluate result
                actual_status = result.get("compliance_status", "Unknown")
                actual_reasoning = result.get("reasoning", "")
                
                is_correct = actual_status == test_case["expected_status"]
                
                case_result = {
                    "test_case_id": test_case["id"],
                    "test_case_name": test_case["name"],
                    "category": test_case["category"],
                    "expected_status": test_case["expected_status"],
                    "actual_status": actual_status,
                    "expected_reasoning": test_case["expected_reasoning"],
                    "actual_reasoning": actual_reasoning,
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
        results["summary"] = self._calculate_summary_metrics(results["test_cases"])
        results["performance"] = {
            "total_processing_time": total_time,
            "average_processing_time": total_time / len(self.test_cases),
            "test_cases_per_second": len(self.test_cases) / total_time
        }
        
        logger.info(f"Benchmark completed in {total_time:.2f} seconds")
        return results
    
    def _calculate_summary_metrics(self, test_cases: List[Dict]) -> Dict[str, Any]:
        """Calculate summary metrics from test case results."""
        total_cases = len(test_cases)
        correct_cases = sum(1 for case in test_cases if case.get("is_correct", False))
        
        # Overall accuracy
        accuracy = (correct_cases / total_cases * 100) if total_cases > 0 else 0
        
        # Category-wise performance
        categories = {}
        for case in test_cases:
            category = case.get("category", "unknown")
            if category not in categories:
                categories[category] = {"total": 0, "correct": 0}
            
            categories[category]["total"] += 1
            if case.get("is_correct", False):
                categories[category]["correct"] += 1
        
        # Calculate category accuracy
        for category in categories:
            total = categories[category]["total"]
            correct = categories[category]["correct"]
            categories[category]["accuracy"] = (correct / total * 100) if total > 0 else 0
        
        # Status-wise breakdown
        status_counts = {}
        for case in test_cases:
            status = case.get("actual_status", "Unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_test_cases": total_cases,
            "correct_predictions": correct_cases,
            "overall_accuracy": accuracy,
            "category_performance": categories,
            "status_distribution": status_counts
        }
    
    def run_performance_benchmark(self, compliance_checker, iterations: int = 10) -> Dict[str, Any]:
        """
        Run performance benchmark with multiple iterations.
        
        Args:
            compliance_checker: Instance of ComplianceChecker
            iterations: Number of iterations to run
            
        Returns:
            Performance benchmark results
        """
        logger.info(f"Starting performance benchmark with {iterations} iterations...")
        
        performance_results = {
            "timestamp": datetime.now().isoformat(),
            "iterations": iterations,
            "processing_times": [],
            "memory_usage": [],
            "throughput": []
        }
        
        # Use a representative test case for performance testing
        test_case = self.test_cases[0]  # Use first test case
        
        for i in range(iterations):
            logger.info(f"Performance iteration {i+1}/{iterations}")
            
            start_time = time.time()
            
            # Run compliance check
            result = compliance_checker.check_compliance(
                design_text=test_case["design"],
                regulation_text=test_case["regulation"]
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            performance_results["processing_times"].append(processing_time)
            performance_results["throughput"].append(1 / processing_time)  # checks per second
        
        # Calculate performance statistics
        processing_times = performance_results["processing_times"]
        throughput_rates = performance_results["throughput"]
        
        performance_results["statistics"] = {
            "mean_processing_time": np.mean(processing_times),
            "std_processing_time": np.std(processing_times),
            "min_processing_time": np.min(processing_times),
            "max_processing_time": np.max(processing_times),
            "mean_throughput": np.mean(throughput_rates),
            "std_throughput": np.std(throughput_rates)
        }
        
        logger.info("Performance benchmark completed")
        return performance_results
    
    def generate_benchmark_report(self, compliance_results: Dict, performance_results: Dict = None) -> str:
        """
        Generate comprehensive benchmark report.
        
        Args:
            compliance_results: Results from compliance benchmark
            performance_results: Results from performance benchmark
            
        Returns:
            Path to generated report
        """
        logger.info("Generating benchmark report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"benchmark_report_{timestamp}.html"
        
        # Create HTML report
        html_content = self._generate_html_report(compliance_results, performance_results)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Also save JSON results
        json_path = self.output_dir / f"benchmark_results_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "compliance_results": compliance_results,
                "performance_results": performance_results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Benchmark report saved to: {report_path}")
        return str(report_path)
    
    def _generate_html_report(self, compliance_results: Dict, performance_results: Dict = None) -> str:
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
        """
        
        if performance_results:
            html += f"""
            <div class="section">
                <h2>⚡ Performance Benchmark Results</h2>
                <div class="metric">
                    <strong>Mean Processing Time:</strong> {performance_results['statistics']['mean_processing_time']:.3f}s
                </div>
                <div class="metric">
                    <strong>Mean Throughput:</strong> {performance_results['statistics']['mean_throughput']:.1f} checks/sec
                </div>
                <div class="metric">
                    <strong>Total Iterations:</strong> {performance_results['iterations']}
                </div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def save_benchmark_results(self, results: Dict, filename: str = None) -> str:
        """
        Save benchmark results to file.
        
        Args:
            results: Benchmark results
            filename: Optional filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
        
        file_path = self.output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Benchmark results saved to: {file_path}")
        return str(file_path)


def main():
    """Main function to run benchmarks."""
    from compliance_checker import ComplianceChecker
    
    # Initialize benchmark system
    benchmark = CAELUSBenchmark()
    
    # Initialize compliance checker
    checker = ComplianceChecker(use_llm=False)  # Use rule-based for consistent benchmarking
    
    # Run compliance benchmark
    logger.info("Running compliance benchmark...")
    compliance_results = benchmark.run_compliance_benchmark(checker)
    
    # Run performance benchmark
    logger.info("Running performance benchmark...")
    performance_results = benchmark.run_performance_benchmark(checker, iterations=5)
    
    # Generate report
    report_path = benchmark.generate_benchmark_report(compliance_results, performance_results)
    
    # Print summary
    print("\n" + "="*50)
    print("BENCHMARK SUMMARY")
    print("="*50)
    print(f"Overall Accuracy: {compliance_results['summary']['overall_accuracy']:.1f}%")
    print(f"Total Test Cases: {compliance_results['summary']['total_test_cases']}")
    print(f"Correct Predictions: {compliance_results['summary']['correct_predictions']}")
    print(f"Mean Processing Time: {performance_results['statistics']['mean_processing_time']:.3f}s")
    print(f"Mean Throughput: {performance_results['statistics']['mean_throughput']:.1f} checks/sec")
    print(f"Report saved to: {report_path}")
    print("="*50)


if __name__ == "__main__":
    main() 