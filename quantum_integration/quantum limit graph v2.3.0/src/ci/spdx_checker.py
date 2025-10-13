# -*- coding: utf-8 -*-
"""
SPDX Compliance Checker for Quantum LIMIT-GRAPH v2.3.0
Validates SPDX license headers and metadata
"""

import os
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class SPDXCheckResult:
    """SPDX check result for a file"""
    filepath: str
    has_header: bool
    license_id: str
    copyright_present: bool
    compliant: bool
    issues: List[str]

class SPDXChecker:
    """
    Checks SPDX compliance in source files
    """
    
    VALID_LICENSES = [
        'Apache-2.0', 'MIT', 'BSD-3-Clause', 'GPL-3.0',
        'LGPL-3.0', 'MPL-2.0', 'CC-BY-4.0'
    ]
    
    SPDX_PATTERN = re.compile(
        r'SPDX-License-Identifier:\s*([A-Za-z0-9\-\.]+)',
        re.IGNORECASE
    )
    
    COPYRIGHT_PATTERN = re.compile(
        r'Copyright\s+(?:\(c\)\s*)?(\d{4}(?:-\d{4})?)',
        re.IGNORECASE
    )
    
    def __init__(self, root_dir: str = '.'):
        """
        Initialize SPDX checker
        
        Args:
            root_dir: Root directory to check
        """
        self.root_dir = root_dir
        self.results: List[SPDXCheckResult] = []
        
    def check_file(self, filepath: str) -> SPDXCheckResult:
        """
        Check SPDX compliance for a single file
        
        Args:
            filepath: Path to file
            
        Returns:
            Check result
        """
        issues = []
        has_header = False
        license_id = None
        copyright_present = False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Read first 20 lines (header area)
                header_lines = [f.readline() for _ in range(20)]
                header_text = ''.join(header_lines)
            
            # Check for SPDX identifier
            spdx_match = self.SPDX_PATTERN.search(header_text)
            if spdx_match:
                has_header = True
                license_id = spdx_match.group(1)
                
                # Validate license
                if license_id not in self.VALID_LICENSES:
                    issues.append(f"Invalid license identifier: {license_id}")
            else:
                issues.append("Missing SPDX-License-Identifier header")
            
            # Check for copyright notice
            copyright_match = self.COPYRIGHT_PATTERN.search(header_text)
            if copyright_match:
                copyright_present = True
            else:
                issues.append("Missing copyright notice")
            
            compliant = has_header and copyright_present and not issues
            
        except Exception as e:
            issues.append(f"Error reading file: {str(e)}")
            compliant = False
        
        return SPDXCheckResult(
            filepath=filepath,
            has_header=has_header,
            license_id=license_id or 'NONE',
            copyright_present=copyright_present,
            compliant=compliant,
            issues=issues
        )
    
    def check_directory(self, extensions: List[str] = ['.py', '.js', '.ts']) -> List[SPDXCheckResult]:
        """
        Check all files in directory
        
        Args:
            extensions: File extensions to check
            
        Returns:
            List of check results
        """
        results = []
        
        for root, dirs, files in os.walk(self.root_dir):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, file)
                    result = self.check_file(filepath)
                    results.append(result)
        
        self.results = results
        return results
    
    def generate_report(self) -> str:
        """
        Generate compliance report
        
        Returns:
            Report string
        """
        if not self.results:
            return "No files checked"
        
        total = len(self.results)
        compliant = sum(1 for r in self.results if r.compliant)
        compliance_rate = compliant / total if total > 0 else 0.0
        
        report = []
        report.append("="*60)
        report.append("SPDX COMPLIANCE REPORT")
        report.append("="*60)
        report.append(f"Total Files: {total}")
        report.append(f"Compliant: {compliant}")
        report.append(f"Non-Compliant: {total - compliant}")
        report.append(f"Compliance Rate: {compliance_rate:.1%}")
        report.append("")
        
        # List non-compliant files
        non_compliant = [r for r in self.results if not r.compliant]
        if non_compliant:
            report.append("Non-Compliant Files:")
            for result in non_compliant:
                report.append(f"\n  {result.filepath}")
                for issue in result.issues:
                    report.append(f"    - {issue}")
        
        report.append("\n" + "="*60)
        report.append(f"Status: {'✓ PASS' if compliance_rate >= 0.95 else '✗ FAIL'}")
        report.append("="*60)
        
        return "\n".join(report)
    
    def is_compliant(self, threshold: float = 0.95) -> bool:
        """
        Check if project meets compliance threshold
        
        Args:
            threshold: Minimum compliance rate required
            
        Returns:
            True if compliant
        """
        if not self.results:
            return False
        
        compliant = sum(1 for r in self.results if r.compliant)
        rate = compliant / len(self.results)
        
        return rate >= threshold


def check_spdx_compliance(root_dir: str = '.') -> bool:
    """
    Convenience function to check SPDX compliance
    
    Args:
        root_dir: Root directory to check
        
    Returns:
        True if compliant
    """
    checker = SPDXChecker(root_dir)
    checker.check_directory()
    
    print(checker.generate_report())
    
    return checker.is_compliant()


if __name__ == '__main__':
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    compliant = check_spdx_compliance(root)
    exit(0 if compliant else 1)
