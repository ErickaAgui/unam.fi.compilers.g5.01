"""Lark Parser + SDT adapter for the original Jacaranda GUI.

The first delivery's RPLY lexer is still used by the Analyze button.
This final interpreter uses the Lark lexer/parser generated from jacaranda.lark.
"""
from dataclasses import dataclass, field
from lark import Tree, Token
from engine import parse, run, JacarandaError
from semantics import SemanticChecker

@dataclass
class DisplayNode:
    symbol: str
    children: list = field(default_factory=list)

def as_display_tree(value):
    """Adapt a Lark syntax tree to the unchanged ParseTreeViewer API."""
    if isinstance(value, Tree):
        return DisplayNode(str(value.data), [as_display_tree(c) for c in value.children])
    if isinstance(value, Token):
        return DisplayNode(f"{value.type} -> {value.value!r}")
    return DisplayNode(str(value))

@dataclass
class CheckResult:
    ok: bool
    message: str
    tree: object = None
    display_tree: object = None
    symbols: dict = field(default_factory=dict)

    def formatted(self):
        return self.message

def check_source(source):
    try:
        tree = parse(source)
    except JacarandaError as error:
        return CheckResult(False, str(error))
    display = as_display_tree(tree)
    try:
        symbols = SemanticChecker(tree).check()
    except JacarandaError as error:
        return CheckResult(False,
            'Parsing Success!\n\nLark syntax tree:\n' + tree.pretty()
            + '\n' + str(error), tree, display)
    return CheckResult(True,
        'Parsing Success!\nSDT Verified!\n\nLark syntax tree:\n'
        + tree.pretty() + '\nSymbol table: ' + str(symbols),
        tree, display, symbols)

def execute_source(source, max_steps=100000):
    return run(source, max_steps=max_steps)
