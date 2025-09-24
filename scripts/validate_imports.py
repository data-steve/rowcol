#!/usr/bin/env python3
"""
Import Validation Script - Enforce Architectural Import Rules

This script validates that the codebase adheres to the architectural import rules
defined in ADR-001: Domains vs Runway Separation.

Usage:
    poetry run python scripts/validate_imports.py
    poetry run python scripts/validate_imports.py --fix-violations
    poetry run python scripts/validate_imports.py --verbose
    poetry run python scripts/validate_imports.py --verify-imports
    poetry run python scripts/validate_imports.py --verify-all

Import Rules:
    ✅ runway/ can import from domains/
    ✅ domains/ can import from other domains/
    ✅ Both can import from common/, config/, db/
    ❌ domains/ cannot import from runway/
    ❌ No circular dependencies allowed

Exit Codes:
    0: No violations found
    1: Import violations detected
    2: Circular dependencies detected
    3: Script error
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import argparse

class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to extract import statements from Python files."""
    
    def __init__(self):
        self.imports = []
        self.from_imports = []
    
    def visit_Import(self, node):
        """Handle 'import module' statements."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Handle 'from module import ...' statements."""
        if node.module:
            self.from_imports.append(node.module)
        self.generic_visit(node)

class ImportValidator:
    """Validates import rules across the Oodaloo codebase."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.violations = []
        self.circular_deps = []
        self.import_graph = defaultdict(set)
        
        # Define allowed import patterns
        self.allowed_patterns = {
            'runway_to_domains': True,      # runway/ can import domains/
            'domains_to_domains': True,     # domains/ can import other domains/
            'both_to_common': True,         # Both can import common/, config/, db/
            'domains_to_runway': False,     # domains/ CANNOT import runway/
        }
    
    def validate_all(self) -> Dict[str, any]:
        """Run all validation checks."""
        print("🔍 Validating import rules across Oodaloo codebase...")
        
        # Find all Python files
        python_files = self._find_python_files()
        print(f"📁 Found {len(python_files)} Python files to analyze")
        
        # Analyze imports in each file
        file_imports = {}
        for file_path in python_files:
            imports = self._analyze_file_imports(file_path)
            file_imports[file_path] = imports
            self._build_import_graph(file_path, imports)
        
        # Check import rules
        self._check_import_violations(file_imports)
        
        # Check for circular dependencies
        self._check_circular_dependencies()
        
        # Generate report
        return self._generate_report()
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project (excluding tests and scripts)."""
        python_files = []
        
        # Include main application directories
        include_dirs = ['domains', 'runway', 'common', 'config', 'db']
        
        for directory in include_dirs:
            dir_path = self.project_root / directory
            if dir_path.exists():
                for py_file in dir_path.rglob('*.py'):
                    if not py_file.name.startswith('__pycache__'):
                        python_files.append(py_file)
        
        # Also include main.py
        main_py = self.project_root / 'main.py'
        if main_py.exists():
            python_files.append(main_py)
        
        return python_files
    
    def _analyze_file_imports(self, file_path: Path) -> Dict[str, List[str]]:
        """Analyze imports in a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            analyzer = ImportAnalyzer()
            analyzer.visit(tree)
            
            return {
                'direct_imports': analyzer.imports,
                'from_imports': analyzer.from_imports,
                'all_imports': analyzer.imports + analyzer.from_imports
            }
            
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
            return {'direct_imports': [], 'from_imports': [], 'all_imports': []}
    
    def _build_import_graph(self, file_path: Path, imports: Dict[str, List[str]]):
        """Build import dependency graph for circular dependency detection."""
        file_module = self._path_to_module(file_path)
        
        for import_name in imports['all_imports']:
            # Only track internal imports (not external packages)
            if self._is_internal_import(import_name):
                self.import_graph[file_module].add(import_name)
    
    def _check_import_violations(self, file_imports: Dict[Path, Dict[str, List[str]]]):
        """Check for import rule violations."""
        for file_path, imports in file_imports.items():
            file_module = self._path_to_module(file_path)
            
            for import_name in imports['all_imports']:
                violation = self._check_single_import(file_module, import_name)
                if violation:
                    self.violations.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'import': import_name,
                        'rule': violation['rule'],
                        'reason': violation['reason']
                    })
    
    def _check_single_import(self, source_module: str, import_name: str) -> Optional[Dict[str, str]]:
        """Check if a single import violates architectural rules."""
        # Skip external imports
        if not self._is_internal_import(import_name):
            return None
        
        # Check domains/ → runway/ violation
        if source_module.startswith('domains.') and import_name.startswith('runway.'):
            return {
                'rule': 'domains_to_runway_forbidden',
                'reason': 'Domain services cannot import runway-specific code'
            }
        
        # Check for relative imports that might bypass rules
        if import_name.startswith('..runway') and source_module.startswith('domains.'):
            return {
                'rule': 'relative_import_bypass',
                'reason': 'Relative imports cannot bypass architectural boundaries'
            }
        
        return None
    
    def _check_circular_dependencies(self):
        """Detect circular dependencies using topological sort."""
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                self.circular_deps.append(cycle)
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.import_graph.get(node, []):
                if has_cycle(neighbor, path.copy()):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.import_graph:
            if node not in visited:
                has_cycle(node, [])
    
    def _path_to_module(self, file_path: Path) -> str:
        """Convert file path to Python module name."""
        relative_path = file_path.relative_to(self.project_root)
        module_parts = list(relative_path.parts)[:-1]  # Remove .py extension
        
        if relative_path.name != '__init__.py':
            module_parts.append(relative_path.stem)
        
        return '.'.join(module_parts)
    
    def _is_internal_import(self, import_name: str) -> bool:
        """Check if import is internal to our project."""
        internal_prefixes = ['domains', 'runway', 'common', 'config', 'db']
        return any(import_name.startswith(prefix) for prefix in internal_prefixes)
    
    def _generate_report(self) -> Dict[str, any]:
        """Generate validation report."""
        total_violations = len(self.violations)
        total_circular_deps = len(self.circular_deps)
        
        status = "PASS"
        if total_violations > 0:
            status = "FAIL - Import Violations"
        elif total_circular_deps > 0:
            status = "FAIL - Circular Dependencies"
        
        return {
            'status': status,
            'violations': self.violations,
            'circular_dependencies': self.circular_deps,
            'summary': {
                'total_violations': total_violations,
                'total_circular_deps': total_circular_deps,
                'architecture_compliant': total_violations == 0 and total_circular_deps == 0
            }
        }
    
    def print_report(self, report: Dict[str, any], verbose: bool = False):
        """Print validation report to console."""
        summary = report['summary']
        
        print("\n🎯 Import Validation Results")
        print(f"{'='*50}")
        print(f"Status: {report['status']}")
        print(f"Import Violations: {summary['total_violations']}")
        print(f"Circular Dependencies: {summary['total_circular_deps']}")
        print(f"Architecture Compliant: {'✅ Yes' if summary['architecture_compliant'] else '❌ No'}")
        
        # Print violations
        if report['violations']:
            print("\n❌ Import Rule Violations:")
            for violation in report['violations']:
                print(f"  📄 {violation['file']}")
                print(f"     Import: {violation['import']}")
                print(f"     Rule: {violation['rule']}")
                print(f"     Reason: {violation['reason']}")
                print()
        
        # Print circular dependencies
        if report['circular_dependencies']:
            print("\n🔄 Circular Dependencies:")
            for i, cycle in enumerate(report['circular_dependencies'], 1):
                print(f"  {i}. {' → '.join(cycle)}")
        
        # Success message
        if summary['architecture_compliant']:
            print("\n🎉 All import rules validated successfully!")
            print("✅ Domains vs Runway separation maintained")
            print("✅ No circular dependencies detected")
            print("✅ Architecture ready for production")

def verify_critical_imports():
    """Verify that all critical imports are working correctly after refactoring."""
    critical_imports = [
        ("domains.integrations.qbo", ["QBOAPIClient", "get_qbo_client"], "QBO Integration"),
        ("runway.experiences.tray", ["TrayService"], "Tray Service"),
        ("runway.experiences.test_drive", ["DemoTestDriveService"], "Test Drive Service"),
        ("domains.ap.services.payment", ["PaymentService"], "Payment Service"),
        ("domains.ap.services.bill_ingestion", ["BillService"], "Bill Service"),
        ("runway.core.runway_calculator", ["RunwayCalculator"], "Runway Calculator"),
        ("runway.core.data_quality_analyzer", ["DataQualityAnalyzer"], "Data Quality Analyzer"),
        ("domains.integrations", ["SmartSyncService"], "Smart Sync Service"),
    ]
    
    return _run_import_tests(critical_imports, "Critical Imports")

def verify_comprehensive_imports():
    """Verify comprehensive imports across all domains and runway modules."""
    comprehensive_imports = [
        # Domains - Core
        ("domains.core.services", ["KPIService", "UserService"], "Core Services"),
        ("domains.core.models", ["Business", "User"], "Core Models"),
        
        # Domains - AP (Accounts Payable)
        ("domains.ap.services.bill_ingestion", ["BillService"], "Bill Service"),
        ("domains.ap.services.payment", ["PaymentService"], "Payment Service"),
        ("domains.ap.services.vendor", ["VendorService"], "Vendor Service"),
        ("domains.ap.models", ["Bill", "Payment", "Vendor"], "AP Models"),
        
        # Domains - AR (Accounts Receivable)
        ("domains.ar.services", ["CollectionsService", "CustomerService", "InvoiceService"], "AR Services"),
        ("domains.ar.models", ["Invoice", "Customer"], "AR Models"),
        
        # Domains - Integrations
        ("domains.integrations.qbo", ["QBOAPIClient", "QBOAuthService"], "QBO Integration"),
        ("domains.integrations", ["SmartSyncService"], "Smart Sync"),
        
        # Domains - Policy
        ("domains.policy.services", ["PolicyEngineService"], "Policy Services"),
        
        # Runway - Core
        ("runway.core.runway_calculator", ["RunwayCalculator"], "Runway Calculator"),
        ("runway.core.data_quality_analyzer", ["DataQualityAnalyzer"], "Data Quality Analyzer"),
        ("runway.core.reserve_runway", ["RunwayReserveService"], "Reserve Runway"),
        
        # Runway - Experiences
        ("runway.experiences.onboarding", ["OnboardingService"], "Onboarding Service"),
        ("runway.experiences.tray", ["TrayService", "QBOTrayDataProvider"], "Tray Service"),
        ("runway.experiences.test_drive", ["DemoTestDriveService"], "Test Drive Service"),
        
        # Runway - Routes
        ("runway.routes.bills", ["router"], "Bills Routes"),
        ("runway.routes.payments", ["router"], "Payments Routes"),
        ("runway.routes.vendors", ["router"], "Vendors Routes"),
        ("runway.routes.invoices", ["router"], "Invoices Routes"),
        
        # Runway - Infrastructure
        ("runway.infrastructure.qbo_setup.qbo_setup_service", ["QBOSetupService"], "QBO Setup Service"),
        
        # Config
        ("config.business_rules", ["RunwayAnalysisSettings"], "Business Rules"),
    ]
    
    return _run_import_tests(comprehensive_imports, "Comprehensive Imports")

def _run_import_tests(imports_list, test_name):
    """Run import tests for a given list of imports."""
    passed = 0
    total = len(imports_list)
    
    print(f"🔍 Running {test_name}...\n")
    
    for module_path, items, test_name in imports_list:
        try:
            # Add current directory to path
            import sys
            import os
            sys.path.insert(0, os.getcwd())
            
            module = __import__(module_path, fromlist=items)
            for item in items:
                if not hasattr(module, item):
                    print(f"❌ {test_name}: Missing {item}")
                    break
            else:
                print(f"✅ {test_name}: All imports working")
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
    
    print(f"\n📊 {test_name} Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"🎉 All {test_name.lower()} working correctly!")
        return True
    else:
        print(f"⚠️  Some {test_name.lower()} failed - check errors above")
        return False

def main():
    """Main validation script entry point."""
    parser = argparse.ArgumentParser(description="Validate Oodaloo import rules")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--fix-violations", action="store_true", help="Attempt to fix violations automatically")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--verify-imports", action="store_true", help="Verify critical imports are working")
    parser.add_argument("--verify-all", action="store_true", help="Verify comprehensive imports across all domains and runway modules")
    
    args = parser.parse_args()
    
    # Get project root
    project_root = os.path.abspath(args.project_root)
    if not os.path.exists(os.path.join(project_root, "main.py")):
        print(f"❌ Invalid project root: {project_root}")
        print("   Expected to find main.py in project root")
        sys.exit(3)
    
    print("🚀 Starting Import Validation")
    print(f"Project Root: {project_root}")
    print(f"Timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Handle verify-imports options
        if args.verify_imports:
            success = verify_critical_imports()
            sys.exit(0 if success else 1)
        elif args.verify_all:
            success = verify_comprehensive_imports()
            sys.exit(0 if success else 1)
        
        # Run normal import validation
        validator = ImportValidator(project_root)
        report = validator.validate_all()
        validator.print_report(report, verbose=args.verbose)
        
        # Fix violations if requested
        if args.fix_violations and report['violations']:
            print("\n🔧 Attempting to fix violations...")
            # TODO: Implement automatic fixing
            print("⚠️  Automatic fixing not yet implemented")
        
        # Exit with appropriate code
        if not report['summary']['architecture_compliant']:
            if report['violations']:
                sys.exit(1)  # Import violations
            elif report['circular_dependencies']:
                sys.exit(2)  # Circular dependencies
        
        sys.exit(0)  # Success
        
    except KeyboardInterrupt:
        print("\n⏹️  Validation interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()
