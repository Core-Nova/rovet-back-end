#!/usr/bin/env python3
"""Parse and display test coverage information."""

import json
import os

def get_coverage_summary():
    """Read and display coverage information from status.json."""
    status_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "htmlcov", "status.json")
    
    if not os.path.exists(status_file):
        print("Coverage report not found. Run: pytest --cov=app --cov-report=html")
        return
    
    with open(status_file, 'r') as f:
        data = json.load(f)
    
    files = data.get('files', {})
    
    # Calculate totals
    total_statements = 0
    total_missing = 0
    total_excluded = 0
    
    file_coverage = []
    
    for file_key, file_data in files.items():
        index = file_data.get('index', {})
        nums = index.get('nums', {})
        
        statements = nums.get('n_statements', 0)
        missing = nums.get('n_missing', 0)
        excluded = nums.get('n_excluded', 0)
        covered = statements - missing - excluded
        
        if statements > 0:
            coverage_pct = (covered / statements) * 100
        else:
            coverage_pct = 100.0
        
        total_statements += statements
        total_missing += missing
        total_excluded += excluded
        
        file_path = index.get('file', 'unknown')
        file_coverage.append({
            'file': file_path,
            'statements': statements,
            'covered': covered,
            'missing': missing,
            'excluded': excluded,
            'coverage': coverage_pct
        })
    
    # Calculate overall coverage
    total_covered = total_statements - total_missing - total_excluded
    if total_statements > 0:
        overall_coverage = (total_covered / total_statements) * 100
    else:
        overall_coverage = 0.0
    
    # Display summary
    print("=" * 70)
    print("TEST COVERAGE SUMMARY")
    print("=" * 70)
    print(f"\nOverall Coverage: {overall_coverage:.1f}%")
    print(f"Total Statements: {total_statements}")
    print(f"Covered: {total_covered}")
    print(f"Missing: {total_missing}")
    print(f"Excluded: {total_excluded}")
    
    # Sort by coverage percentage
    file_coverage.sort(key=lambda x: x['coverage'])
    
    print("\n" + "=" * 70)
    print("COVERAGE BY FILE (sorted by coverage)")
    print("=" * 70)
    print(f"{'File':<50} {'Coverage':<10} {'Statements':<12} {'Missing':<10}")
    print("-" * 70)
    
    for file_info in file_coverage:
        coverage_bar = "█" * int(file_info['coverage'] / 2)
        print(f"{file_info['file']:<50} {file_info['coverage']:>6.1f}% {file_info['statements']:>6}/{file_info['statements']:<5} {file_info['missing']:>6}")
    
    # Files with low coverage
    low_coverage = [f for f in file_coverage if f['coverage'] < 70 and f['statements'] > 0]
    if low_coverage:
        print("\n" + "=" * 70)
        print("FILES WITH LOW COVERAGE (< 70%)")
        print("=" * 70)
        for file_info in low_coverage:
            print(f"  {file_info['file']}: {file_info['coverage']:.1f}% ({file_info['missing']} missing lines)")
    
    print("\n" + "=" * 70)
    print("To view detailed HTML report: open htmlcov/index.html")
    print("=" * 70)

if __name__ == "__main__":
    get_coverage_summary()

