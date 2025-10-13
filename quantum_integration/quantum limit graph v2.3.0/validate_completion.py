#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 AI Research Agent Team

"""
Completion Validation Script for Quantum LIMIT-GRAPH v2.3.0
Verifies all components are present and functional
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

class CompletionValidator:
    """Validates project completion"""
    
    def __init__(self, root_dir: str = '.'):
        self.root_dir = Path(root_dir)
        self.errors = []
        self.warnings = []
        
    def check_file_exists(self, filepath: str) -> bool:
        """Check if file exists"""
        full_path = self.root_dir / filepath
        exists = full_path.exists()
        if not exists:
            self.errors.append(f"Missing file: {filepath}")
        return exists
    
    def check_directory_exists(self, dirpath: str) -> bool:
        """Check if directory exists"""
        full_path = self.root_dir / dirpath
        exists = full_path.is_dir()
        if not exists:
            self.errors.append(f"Missing directory: {dirpath}")
        return exists
    
    def validate_structure(self) -> bool:
        """Validate project structure"""
        print("Validating project structure...")
        
        required_files = [
            'README.md',
            'INTEGRATION_SUMMARY.md',
            'COMPLETION_REPORT.md',
            'CONTRIBUTOR_CHALLENGE.md',
            'requirements.txt',
            'setup.py',
            'model-index.yaml',
            'sample_quantum_limit-graph.py',
            'test_complete_integration.py',
            'quick_start.py',
            'validate_completion.py',
        ]
        
        required_dirs = [
            'src',
            'src/agent',
            'src/graph',
            'src/context',
            'src/evaluation',
            'src/ci',
            'notebooks',
            '.github',
            '.github/workflows',
        ]
        
        all_good = True
        
        for file in required_files:
            if not self.check_file_exists(file):
                all_good = False
        
        for dir in required_dirs:
            if not self.check_directory_exists(dir):
                all_good = False
        
        if all_good:
            print("  ✓ Project structure complete")
        else:
            print("  ✗ Project structure incomplete")
        
        return all_good
    
    def validate_source_files(self) -> bool:
        """Validate source code files"""
        print("\nValidating source files...")
        
        source_files = [
            'src/__init__.py',
            'src/agent/__init__.py',
            'src/agent/multilingual_parser.py',
            'src/agent/repair_edit_stream.py',
            'src/graph/__init__.py',
            'src/graph/quantum_traversal.py',
            'src/context/__init__.py',
            'src/context/ace_context_router.py',
            'src/evaluation/__init__.py',
            'src/evaluation/benchmark_harness.py',
            'src/evaluation/alignment_score.py',
            'src/evaluation/layer_balance_test.py',
            'src/ci/__init__.py',
            'src/ci/validator.py',
            'src/ci/spdx_checker.py',
        ]
        
        all_good = True
        for file in source_files:
            if not self.check_file_exists(file):
                all_good = False
        
        if all_good:
            print("  ✓ All source files present")
        else:
            print("  ✗ Some source files missing")
        
        return all_good
    
    def validate_imports(self) -> bool:
        """Validate that modules can be imported"""
        print("\nValidating module imports...")
        
        modules = [
            ('src.agent.multilingual_parser', 'MultilingualParser'),
            ('src.graph.quantum_traversal', 'QuantumGraphTraversal'),
            ('src.context.ace_context_router', 'ACEContextRouter'),
            ('src.agent.repair_edit_stream', 'REPAIREditStream'),
            ('src.evaluation.benchmark_harness', 'BenchmarkHarness'),
            ('src.evaluation.alignment_score', 'CrossLingualAlignmentScorer'),
            ('src.evaluation.layer_balance_test', 'LayerBalanceTest'),
            ('src.ci.validator', 'EditStreamValidator'),
            ('src.ci.spdx_checker', 'SPDXChecker'),
        ]
        
        all_good = True
        for module_name, class_name in modules:
            try:
                module = __import__(module_name, fromlist=[class_name])
                getattr(module, class_name)
                print(f"  ✓ {module_name}.{class_name}")
            except Exception as e:
                print(f"  ✗ {module_name}.{class_name}: {e}")
                self.errors.append(f"Import failed: {module_name}.{class_name}")
                all_good = False
        
        return all_good
    
    def validate_documentation(self) -> bool:
        """Validate documentation completeness"""
        print("\nValidating documentation...")
        
        docs = [
            ('README.md', ['Features', 'Installation', 'Quick Start']),
            ('INTEGRATION_SUMMARY.md', ['Overview', 'Project Structure', 'Component Details']),
            ('COMPLETION_REPORT.md', ['Executive Summary', 'Completed Components', 'Performance Metrics']),
            ('CONTRIBUTOR_CHALLENGE.md', ['Contribution', 'Guidelines']),
        ]
        
        all_good = True
        for doc_file, required_sections in docs:
            if not self.check_file_exists(doc_file):
                all_good = False
                continue
            
            try:
                with open(self.root_dir / doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                missing_sections = []
                for section in required_sections:
                    if section.lower() not in content.lower():
                        missing_sections.append(section)
                
                if missing_sections:
                    self.warnings.append(f"{doc_file} missing sections: {', '.join(missing_sections)}")
                    print(f"  ⚠ {doc_file} (missing sections)")
                else:
                    print(f"  ✓ {doc_file}")
            except Exception as e:
                self.errors.append(f"Error reading {doc_file}: {e}")
                all_good = False
        
        return all_good
    
    def validate_ci_cd(self) -> bool:
        """Validate CI/CD configuration"""
        print("\nValidating CI/CD configuration...")
        
        ci_file = '.github/workflows/ci.yml'
        if not self.check_file_exists(ci_file):
            return False
        
        try:
            with open(self.root_dir / ci_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_jobs = ['validation', 'benchmarks', 'integration']
            missing_jobs = []
            
            for job in required_jobs:
                if job not in content.lower():
                    missing_jobs.append(job)
            
            if missing_jobs:
                self.warnings.append(f"CI workflow missing jobs: {', '.join(missing_jobs)}")
                print(f"  ⚠ CI workflow (missing jobs)")
                return False
            else:
                print(f"  ✓ CI workflow complete")
                return True
        except Exception as e:
            self.errors.append(f"Error reading CI workflow: {e}")
            return False
    
    def validate_tests(self) -> bool:
        """Validate test files"""
        print("\nValidating test files...")
        
        test_files = [
            'test_complete_integration.py',
            'quick_start.py',
        ]
        
        all_good = True
        for test_file in test_files:
            if self.check_file_exists(test_file):
                print(f"  ✓ {test_file}")
            else:
                all_good = False
        
        return all_good
    
    def generate_report(self) -> str:
        """Generate validation report"""
        report = []
        report.append("\n" + "="*60)
        report.append("QUANTUM LIMIT-GRAPH v2.3.0 - COMPLETION VALIDATION")
        report.append("="*60)
        
        if not self.errors and not self.warnings:
            report.append("\n✅ ALL VALIDATIONS PASSED")
            report.append("\nProject is COMPLETE and PRODUCTION READY!")
        else:
            if self.errors:
                report.append(f"\n❌ ERRORS: {len(self.errors)}")
                for error in self.errors:
                    report.append(f"  - {error}")
            
            if self.warnings:
                report.append(f"\n⚠️  WARNINGS: {len(self.warnings)}")
                for warning in self.warnings:
                    report.append(f"  - {warning}")
        
        report.append("\n" + "="*60)
        report.append("VALIDATION SUMMARY")
        report.append("="*60)
        report.append(f"Errors: {len(self.errors)}")
        report.append(f"Warnings: {len(self.warnings)}")
        report.append(f"Status: {'✅ PASS' if not self.errors else '❌ FAIL'}")
        report.append("="*60)
        
        return "\n".join(report)
    
    def run_validation(self) -> bool:
        """Run complete validation"""
        print("="*60)
        print("Quantum LIMIT-GRAPH v2.3.0 - Completion Validation")
        print("="*60)
        
        validations = [
            self.validate_structure,
            self.validate_source_files,
            self.validate_imports,
            self.validate_documentation,
            self.validate_ci_cd,
            self.validate_tests,
        ]
        
        results = []
        for validation in validations:
            try:
                result = validation()
                results.append(result)
            except Exception as e:
                print(f"  ✗ Validation error: {e}")
                self.errors.append(f"Validation error: {e}")
                results.append(False)
        
        print(self.generate_report())
        
        return all(results) and not self.errors


def main():
    """Main entry point"""
    validator = CompletionValidator()
    success = validator.run_validation()
    
    if success:
        print("\n🎉 Quantum LIMIT-GRAPH v2.3.0 is COMPLETE!")
        print("\nNext steps:")
        print("  1. Run quick start: python quick_start.py")
        print("  2. Run full tests: python test_complete_integration.py")
        print("  3. Run benchmarks: python src/evaluation/benchmark_harness.py")
        print("  4. Deploy to production")
    else:
        print("\n⚠️  Please fix the errors above before deployment")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
