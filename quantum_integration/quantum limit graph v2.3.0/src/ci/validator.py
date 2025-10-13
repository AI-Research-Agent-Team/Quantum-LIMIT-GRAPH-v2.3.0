# -*- coding: utf-8 -*-
"""
Edit Stream Validator for Quantum LIMIT-GRAPH v2.3.0
Validates edit stream integrity and correctness
"""

from typing import Dict, List, Tuple
import json
from dataclasses import dataclass
import sys
sys.path.append('..')

from src.agent.repair_edit_stream import REPAIREditStream, EditType, HallucinationType

@dataclass
class ValidationResult:
    """Validation result"""
    test_name: str
    passed: bool
    message: str
    details: Dict

class EditStreamValidator:
    """
    Validates edit stream operations and integrity
    """
    
    def __init__(self):
        """Initialize validator"""
        self.edit_stream = REPAIREditStream()
        self.results: List[ValidationResult] = []
        
    def validate_edit_application(self) -> ValidationResult:
        """
        Validate that edits are applied correctly
        
        Returns:
            Validation result
        """
        test_cases = [
            {
                'text': 'The quantum computer is fast.',
                'edit_type': EditType.SUBSTITUTION,
                'original': 'fast',
                'corrected': 'powerful',
                'expected': 'The quantum computer is powerful.'
            },
            {
                'text': 'Machine learning algorithms.',
                'edit_type': EditType.INSERTION,
                'position': 8,
                'corrected': 'quantum ',
                'expected': 'Machine quantum learning algorithms.'
            }
        ]
        
        passed = True
        details = []
        
        for i, test in enumerate(test_cases):
            if test['edit_type'] == EditType.SUBSTITUTION:
                edit = self.edit_stream.create_edit(
                    edit_type=test['edit_type'],
                    position=0,
                    original=test['original'],
                    corrected=test['corrected'],
                    confidence=1.0
                )
                result = self.edit_stream.apply_edit(test['text'], edit)
            elif test['edit_type'] == EditType.INSERTION:
                edit = self.edit_stream.create_edit(
                    edit_type=test['edit_type'],
                    position=test['position'],
                    original='',
                    corrected=test['corrected'],
                    confidence=1.0
                )
                result = self.edit_stream.apply_edit(test['text'], edit)
            
            test_passed = result == test['expected']
            passed = passed and test_passed
            
            details.append({
                'test_case': i + 1,
                'passed': test_passed,
                'expected': test['expected'],
                'actual': result
            })
        
        return ValidationResult(
            test_name='edit_application',
            passed=passed,
            message='Edit application validation',
            details={'test_cases': details}
        )
    
    def validate_hallucination_detection(self) -> ValidationResult:
        """
        Validate hallucination detection
        
        Returns:
            Validation result
        """
        test_cases = [
            {
                'text': 'Research shows quantum computers are faster.',
                'context': {'entities': []},
                'should_detect': True
            },
            {
                'text': 'According to Smith et al., quantum computers show promise.',
                'context': {'entities': ['quantum', 'computers']},
                'should_detect': False
            }
        ]
        
        passed = True
        details = []
        
        for i, test in enumerate(test_cases):
            hallucination = self.edit_stream.detect_hallucination(
                test['text'],
                test['context']
            )
            
            detected = hallucination is not None
            test_passed = detected == test['should_detect']
            passed = passed and test_passed
            
            details.append({
                'test_case': i + 1,
                'passed': test_passed,
                'should_detect': test['should_detect'],
                'detected': detected,
                'type': hallucination.value if hallucination else None
            })
        
        return ValidationResult(
            test_name='hallucination_detection',
            passed=passed,
            message='Hallucination detection validation',
            details={'test_cases': details}
        )
    
    def validate_memory_management(self) -> ValidationResult:
        """
        Validate dual-memory architecture
        
        Returns:
            Validation result
        """
        # Add entries to test memory management
        for i in range(150):
            result = self.edit_stream.apply_edits(
                f'Test text {i}',
                {'entities': ['test'], 'source': 'validation'}
            )
        
        stats = self.edit_stream.get_statistics()
        
        # Check capacity constraints
        short_term_ok = stats['short_term_entries'] <= self.edit_stream.short_term_capacity
        long_term_ok = stats['long_term_entries'] <= self.edit_stream.long_term_capacity
        
        passed = short_term_ok and long_term_ok
        
        return ValidationResult(
            test_name='memory_management',
            passed=passed,
            message='Memory management validation',
            details={
                'short_term_entries': stats['short_term_entries'],
                'short_term_capacity': self.edit_stream.short_term_capacity,
                'long_term_entries': stats['long_term_entries'],
                'long_term_capacity': self.edit_stream.long_term_capacity,
                'short_term_ok': short_term_ok,
                'long_term_ok': long_term_ok
            }
        )
    
    def validate_edit_provenance(self) -> ValidationResult:
        """
        Validate edit provenance tracking
        
        Returns:
            Validation result
        """
        # Create test edit
        text = 'Test text for provenance'
        context = {'entities': [], 'source': 'test_source'}
        
        result = self.edit_stream.apply_edits(text, context)
        
        # Check if edits have provenance
        passed = True
        details = []
        
        for edit_info in result['edits_applied']:
            edit_id = edit_info['edit_id']
            provenance = self.edit_stream.get_edit_provenance(edit_id)
            
            has_provenance = provenance is not None
            passed = passed and has_provenance
            
            details.append({
                'edit_id': edit_id,
                'has_provenance': has_provenance,
                'provenance': provenance
            })
        
        return ValidationResult(
            test_name='edit_provenance',
            passed=passed,
            message='Edit provenance tracking validation',
            details={'edits': details}
        )
    
    def run_all_validations(self) -> List[ValidationResult]:
        """
        Run all validation tests
        
        Returns:
            List of validation results
        """
        print("Running Edit Stream Validation Suite...\n")
        
        validations = [
            self.validate_edit_application,
            self.validate_hallucination_detection,
            self.validate_memory_management,
            self.validate_edit_provenance
        ]
        
        for validation_func in validations:
            result = validation_func()
            self.results.append(result)
            
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"{result.test_name}: {status}")
        
        return self.results
    
    def generate_report(self) -> str:
        """
        Generate validation report
        
        Returns:
            Report string
        """
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        
        report = []
        report.append("\n" + "="*60)
        report.append("EDIT STREAM VALIDATION REPORT")
        report.append("="*60)
        report.append(f"Total Tests: {total}")
        report.append(f"Passed: {passed}")
        report.append(f"Failed: {total - passed}")
        report.append("")
        
        for result in self.results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            report.append(f"{result.test_name}: {status}")
            report.append(f"  {result.message}")
        
        report.append("\n" + "="*60)
        report.append(f"Overall: {'✓ ALL TESTS PASSED' if passed == total else '✗ SOME TESTS FAILED'}")
        report.append("="*60)
        
        return "\n".join(report)
    
    def save_results(self, filepath: str = 'validation_results.json'):
        """Save validation results to file"""
        results_dict = {
            'total_tests': len(self.results),
            'passed': sum(1 for r in self.results if r.passed),
            'results': [
                {
                    'test_name': r.test_name,
                    'passed': r.passed,
                    'message': r.message,
                    'details': r.details
                }
                for r in self.results
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"\nResults saved to {filepath}")


def run_validation():
    """Run validation suite"""
    validator = EditStreamValidator()
    validator.run_all_validations()
    
    print(validator.generate_report())
    validator.save_results()
    
    return all(r.passed for r in validator.results)


if __name__ == '__main__':
    success = run_validation()
    exit(0 if success else 1)
