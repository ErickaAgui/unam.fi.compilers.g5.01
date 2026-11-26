import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from engine import run,parse
from lark_pipeline import check_source, as_display_tree
from ParseTreeViewer import tree_layout

class JacarandaFinalTests(unittest.TestCase):
    def test_examples(self):
        expectations={
            '01_hello.c':('success','Hello, Jacaranda!\n14'),
            '02_functions.c':('success','Result: 15'),
            '03_loops.c':('success','15\n0\n1\n2'),
            '04_conditionals.c':('success','Greater than five'),
            '05_semantic_error.c':('SDT','Type mismatch'),
            '06_syntax_error.c':('Parsing','Unexpected token'),
            '07_duplicate.c':('SDT','already declared'),
            '08_runtime_error.c':('Runtime','Division by zero'),
            '09_do_while.c':('success','0\n1\n2'),
            '10_forward_function.c':('success','7'),
            '11_missing_function.c':('SDT','not declared'),
            '12_shadowing.c':('success','9'),
            '13_wrong_arguments.c':('SDT','expects 2 arguments'),
            '14_unreachable_error.c':('SDT','not declared'),
            '15_infinite_loop.c':('Runtime','Step limit exceeded'),
        }
        for name,(phase,text) in expectations.items():
            with self.subTest(name=name):
                source=(ROOT/'examples'/'final_project'/name).read_text(encoding='utf-8')
                result=run(source,max_steps=3000)
                self.assertEqual(phase,result.phase)
                self.assertIn(text,result.output if result.ok else result.message)
    def test_precedence(self):
        self.assertEqual(run('int main(){print(2+3*4);return 0;}').output,'14')
    def test_static_checks_in_unreachable_branch(self):
        result=run('int main(){if(false){print(not_found);}return 0;}')
        self.assertEqual(result.phase,'SDT')
    def test_for_scope(self):
        result=run('int main(){for(int i=0;i<1;i++){print(i);} print(i);return 0;}')
        self.assertEqual(result.phase,'SDT')
    def test_short_circuit(self):
        result=run('int main(){ if(true || 1/0 > 0){print(9);} return 0;}')
        self.assertTrue(result.ok,result.message)
        self.assertEqual(result.output,'9')
    def test_original_tree_viewer_accepts_lark(self):
        result = check_source('int main(){return 0;}')
        self.assertTrue(result.ok)
        self.assertGreater(len(tree_layout(result.display_tree)[0]), 3)

    def test_tree_available_even_if_sdt_rejects(self):
        result = check_source('int x = true;')
        self.assertFalse(result.ok)
        self.assertIsNotNone(result.display_tree)
        self.assertIn('Parsing Success!',result.formatted())

    def test_parse_tree_generated_by_library(self):
        self.assertIn('function',parse('int main(){return 0;}').pretty())

if __name__=='__main__':unittest.main()
