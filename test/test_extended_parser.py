"""Additional regression tests for full RPLY -> parser -> SDT pipeline."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from analysis_pipeline import analyze

class ExtendedParserTests(unittest.TestCase):
    def test_valid_programs(self):
        cases=[
            'int main(){printf("Hola mundo\\n");return 0;}',
            'int suma(int a,int b){return a+b;} int main(){int z=suma(3,4);return z;}',
            'int main(){int a=2; if(a>1){a=a+1;}else{a=0;}return a;}',
            'int main(){int x=3;while(x>0){x=x-1;}return 0;}',
            'int main(){int i=0;for(i=0;i<5;i++){print(i);}return 0;}',
            'int main(){for(int i=0;i<3;i++){print(i);}return 0;}',
            'int main(){int x=0;do{x=x+1;}while(x<3);return x;}',
            'bool check(int a){return a>0 && a<10;} int main(){bool b=check(4);return 0;}',
            'int main(){int x=2; {int x=3;print(x);} return x;}',
            'void hello(){print("hola");return;} int main(){hello();return 0;}',
            'int plus(int a); int main(){return plus(2);} int plus(int a){return a+1;}',
            'int main(){printf("valor: %d",4);return 0;}',
            'int f(int x){return x;} int main(){return f(true);}',
            'int f(int x){return x;} int main(){return f();}',
        ]
        for code in cases:
            with self.subTest(code=code):self.assertEqual(analyze(code).phase,'success',analyze(code).formatted()[:200])
    def test_semantic_errors(self):
        cases=[
            'int f(){return true;}',
            'int main(){int x=1;int x=2;return 0;}',
            'int f(){return z;}',
            'int f(){return 1;} int f(){return 2;}',
            'void f(){return 3;}',
            'int main(){if("hello")return 1;return 0;}',
            'int main(){for(int i=0;i<3;i++){}return i;}',
            'int main(){printf(42);return 0;}',
        ]
        for code in cases:
            with self.subTest(code=code):self.assertEqual(analyze(code).phase,'semantic',analyze(code).formatted()[:200])
    def test_syntax_errors(self):
        for code in ['int main( {return 0;}','int main(){return 0;','int main(){if(1) return 0}',
                     'int main(){while(1) { x=1; }','int main(){for(int i=0 i<3;i++){}}']:
            with self.subTest(code=code):self.assertEqual(analyze(code).phase,'syntax')
    def test_extended_example_files(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1] / 'examples' / 'parser'
        expectations = {
            '21_function_main': 'success',
            '22_functions_parameters': 'success',
            '23_if_else': 'success',
            '24_while': 'success',
            '25_for': 'success',
            '26_do_while': 'success',
            '27_nested_scope': 'success',
            '28_semantic_return_type': 'semantic',
            '29_valid_function_call': 'success',
            '30_semantic_scope': 'semantic',
            '31_semantic_duplicate_function': 'semantic',
            '32_syntax_missing_brace': 'syntax',
            '33_logic_comparison': 'success',
            '34_semantic_undeclared_function': 'semantic',
        }
        for name, expected in expectations.items():
            with self.subTest(name=name):
                source = (root / f'{name}.c').read_text(encoding='utf-8')
                self.assertEqual(analyze(source).phase, expected)

    def test_tree_and_old_cases(self):
        out=analyze('int main(){int x=10;return x;}')
        self.assertTrue(out.ok)
        self.assertIn('function',out.parse_tree.pretty())
        self.assertIn('return_stmt',out.parse_tree.pretty())
        self.assertIn('EOF',out.parse_tree.pretty())
