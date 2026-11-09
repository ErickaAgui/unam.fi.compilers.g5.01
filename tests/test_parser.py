"""Run from repository root: python -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from analysis_pipeline import analyze

class ParserTests(unittest.TestCase):
    def test_file_cases(self):
        expectations = {
            '01_correct_basic': 'success', '02_correct_program': 'success',
            '03_correct_parentheses': 'success', '04_syntax_missing_expression': 'syntax',
            '05_syntax_missing_semicolon': 'syntax', '06_semantic_type': 'semantic',
            '07_semantic_undeclared': 'semantic', '08_semantic_duplicate': 'semantic',
            '09_semantic_numeric_operator': 'semantic', '10_lexical_invalid': 'lexical',
            '11_valid_if': 'success', '12_multiline_semantic': 'semantic',
            '13_valid_comment': 'success', '14_invalid_string_assignment': 'semantic',
            '15_invalid_self_reference': 'semantic', '16_syntax_operator': 'syntax',
            '17_valid_empty': 'success', '18_valid_float_widen': 'success',
            '19_invalid_trailing': 'syntax', '20_valid_precedence': 'success'
        }
        for name, expected in expectations.items():
            with self.subTest(name=name):
                code = (ROOT / 'examples' / 'parser' / (name+'.c')).read_text(encoding='utf-8')
                self.assertEqual(analyze(code).phase, expected)

    def test_parse_tree_contains_terminals(self):
        result = analyze('int x = 10;')
        self.assertTrue(result.ok)
        self.assertIn("PUNCTUATION -> ';'", result.parse_tree.pretty())
        self.assertIn('EOF', result.parse_tree.pretty())

    def test_operator_precedence(self):
        ast = analyze('int a = 1 + 2 * 3;').ast
        expr = ast.children[0].children[0]
        self.assertEqual(expr.value, '+')
        self.assertEqual(expr.children[1].value, '*')

    def test_multiline_error(self):
        result = analyze('int x = 1;\nfloat y = 3.0;\nint z = false;')
        self.assertEqual(result.phase, 'semantic')
        self.assertEqual(result.line, 3)

    def test_bool_identifier_boundary(self):
        result = analyze('int trueValue = 5;')
        self.assertTrue(result.ok)

if __name__ == '__main__': unittest.main()
