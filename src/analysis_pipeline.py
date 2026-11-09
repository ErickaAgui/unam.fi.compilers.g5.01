"""Reusable pipeline for GUI/CLI/tests; parsing and SDT run as separate phases."""
from dataclasses import dataclass
from LexicalAnalyzer import Lexer
from Parser import Parser, ParseError
from SemanticAnalyzer import SemanticAnalyzer, SemanticError

@dataclass
class AnalysisResult:
    phase: str
    message: str
    line: int = 0
    tokens: list = None
    ast: object = None
    parse_tree: object = None
    symbols: dict = None

    @property
    def ok(self): return self.phase == 'success'

    def formatted(self):
        if self.phase == 'lexical':
            return f'Lexical error in line {self.line}: {self.message}'
        if self.phase == 'syntax':
            return f'Parsing error in line {self.line}: {self.message}'
        out = ['Parsing Success!', '', 'Parse tree:', self.parse_tree.pretty(),
               '', 'Abstract syntax tree:', self.ast.pretty()]
        if self.phase == 'semantic':
            out += ['', f'SDT error in line {self.line}: {self.message}']
        else:
            out += ['', 'SDT Verified!', '', f'Symbol table: {self.symbols}']
        return '\n'.join(out)

def analyze(source):
    try:
        tokens = list(Lexer().get_lexer().lex(source))
    except Exception as exc:
        if not hasattr(exc, 'getsourcepos'):
            raise
        index = exc.getsourcepos().idx
        line = source.count('\n', 0, index) + 1
        character = repr(source[index]) if index < len(source) else 'EOF'
        return AnalysisResult('lexical', f'unrecognized character {character}', line)
    parser = Parser(tokens, source)
    try:
        ast = parser.parse()
    except ParseError as exc:
        return AnalysisResult('syntax', str(exc), exc.line, tokens=tokens)
    semantics = SemanticAnalyzer()
    try:
        symbols = semantics.verify(ast)
    except SemanticError as exc:
        return AnalysisResult('semantic', str(exc), exc.line, tokens, ast, parser.parse_tree)
    return AnalysisResult('success', 'OK', tokens=tokens, ast=ast,
                          parse_tree=parser.parse_tree, symbols=symbols)
