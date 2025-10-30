#!/usr/bin/env python3
"""
Barcha importlarni tekshirish va tahlil qilish
"""

import os
import sys
import ast
import importlib
from pathlib import Path
from collections import defaultdict
import json

class ImportChecker:
    def __init__(self, base_path='traffic_share'):
        self.base_path = base_path
        self.results = {
            'files_checked': 0,
            'total_imports': 0,
            'missing_imports': [],
            'valid_imports': [],
            'errors': [],
            'import_graph': defaultdict(list)
        }
    
    def check_file(self, file_path):
        """Check imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=file_path)
            
            self.results['files_checked'] += 1
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            'type': 'import',
                            'module': alias.name,
                            'name': None,
                            'line': node.lineno
                        })
                        self.results['total_imports'] += 1
                        
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append({
                            'type': 'from',
                            'module': module,
                            'name': alias.name,
                            'line': node.lineno
                        })
                        self.results['total_imports'] += 1
            
            # Test imports
            for imp in imports:
                self.test_import(imp, file_path)
            
            return imports
            
        except SyntaxError as e:
            self.results['errors'].append({
                'file': file_path,
                'error': f"Syntax error: {e}",
                'line': e.lineno
            })
            return []
        except Exception as e:
            self.results['errors'].append({
                'file': file_path,
                'error': str(e)
            })
            return []
    
    def test_import(self, imp, file_path):
        """Test if import actually works"""
        try:
            if imp['type'] == 'import':
                importlib.import_module(imp['module'])
                self.results['valid_imports'].append({
                    'file': file_path,
                    'import': imp['module'],
                    'line': imp['line']
                })
            else:
                module = importlib.import_module(imp['module'])
                if imp['name'] != '*':
                    if hasattr(module, imp['name']):
                        self.results['valid_imports'].append({
                            'file': file_path,
                            'import': f"{imp['module']}.{imp['name']}",
                            'line': imp['line']
                        })
                    else:
                        self.results['missing_imports'].append({
                            'file': file_path,
                            'import': f"{imp['module']}.{imp['name']}",
                            'line': imp['line'],
                            'reason': 'Attribute not found'
                        })
                        
        except ModuleNotFoundError as e:
            self.results['missing_imports'].append({
                'file': file_path,
                'import': imp['module'],
                'line': imp['line'],
                'reason': str(e)
            })
        except Exception as e:
            self.results['errors'].append({
                'file': file_path,
                'import': f"{imp.get('module', '')}.{imp.get('name', '')}",
                'error': str(e)
            })
    
    def scan_all(self):
        """Scan all Python files"""
        for root, dirs, files in os.walk(self.base_path):
            # Skip __pycache__ and other common directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.check_file(file_path)
    
    def print_report(self):
        """Print detailed report"""
        print("=" * 80)
        print("IMPORT TAHLILI HISOBOTI")
        print("=" * 80)
        print(f"\n📊 Umumiy Statistika:")
        print(f"   Tekshirilgan fayllar: {self.results['files_checked']}")
        print(f"   Jami importlar: {self.results['total_imports']}")
        print(f"   To'g'ri importlar: {len(self.results['valid_imports'])}")
        print(f"   Muammoli importlar: {len(self.results['missing_imports'])}")
        print(f"   Xatoliklar: {len(self.results['errors'])}")
        
        if self.results['missing_imports']:
            print(f"\n❌ MUAMMOLI IMPORTLAR ({len(self.results['missing_imports'])}):")
            for imp in self.results['missing_imports']:
                print(f"   {imp['file']}:{imp['line']} - {imp['import']}")
                print(f"      Sabab: {imp['reason']}")
        
        if self.results['errors']:
            print(f"\n⚠️  XATOLIKLAR ({len(self.results['errors'])}):")
            for err in self.results['errors']:
                print(f"   {err['file']}: {err['error']}")
        
        # Success rate
        if self.results['total_imports'] > 0:
            success_rate = (len(self.results['valid_imports']) / self.results['total_imports']) * 100
            print(f"\n✅ Muvaffaqiyat darajasi: {success_rate:.1f}%")
        
        print("=" * 80)
    
    def save_report(self, filename='import_report.json'):
        """Save report to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Hisobot saqlandi: {filename}")


if __name__ == '__main__':
    print("🔍 Import tekshiruvi boshlanmoqda...\n")
    
    checker = ImportChecker()
    checker.scan_all()
    checker.print_report()
    checker.save_report()
    
    # Exit code
    if checker.results['missing_imports'] or checker.results['errors']:
        sys.exit(1)
    else:
        print("\n🎉 Barcha importlar to'g'ri!")
        sys.exit(0)
