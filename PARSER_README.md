# Jacaranda | Parser & SDT

This document explains the second part of Jacaranda: **syntax analysis** and **semantic verification** for a limited set of C-like instructions.

The parser works with the tokens produced by the original RPLY lexical analyzer. It checks whether the instructions have a valid structure and then passes the recognized program information to the semantic analyzer.

Jacaranda checks source code; it does **not execute it**.

For installation and general usage, see the [main README](README.md).

## How the Analyzer Works

```text
Source code
    |
    v
Lexical analyzer (LexicalAnalyzer.py)
    |  Tokens
    v
Syntax analyzer (Parser.py)
    |  Recognized structure / parse tree
    v
Semantic analyzer (SemanticAnalyzer.py)
    |
    v
Analysis result or error message
```

The `analysis_pipeline.py` module connects the analysis stages. The graphical interface is implemented in `gui.py`, and the tree viewer in `ParseTreeViewer.py`.

## Syntax Analysis: Top-Down Parser

Jacaranda uses a **recursive-descent parser written in Python**. Instead of using a parsing library, it has functions that recognize different types of instructions. The parser reads the next token and decides which instruction to process.

For example:

```c
int total = 5;
```

The parser recognizes a variable declaration with an initial value.

```c
int main() {
    print("Hello");
    return 0;
}
```

In this example, the parser recognizes a function, its body, a print instruction, and a return statement. Recognizing these instructions does not mean that Jacaranda executes them.

### Supported Instructions

- Variable declarations and assignments.
- Arithmetic and logical expressions, with operator precedence.
- Functions, parameters, function calls, and `return`.
- Blocks delimited by braces.
- `if`/`else`, `while`, `for`, and `do-while` statements.
- `print` and a simplified version of `printf`.

These are only the structures supported by this educational version; not every valid C program can be analyzed.

## Parse Tree

The parser builds a **parse tree** that shows how the input is organized according to the grammar. Jacaranda also keeps a simpler internal tree (AST) to make the semantic checks easier.

The **View Parse Tree** option opens a window where the tree can be inspected. The viewer allows zooming, moving around the tree, and saving it as SVG, PNG, or JPG.

## Semantic Analysis (SDT)

After a successful syntax analysis, Jacaranda checks whether the recognized instructions follow some basic semantic rules.

| Check | Example |
|---|---|
| Declared variables | Using a variable that has not been declared produces an error. |
| Repeated declarations | Declaring the same variable twice in the same block produces an error. |
| Type compatibility | Assigning a Boolean value to an integer variable produces an error. |
| Functions | A call must refer to a declared function. Argument counts and types are not compared with the parameters. |
| Return values | A returned value must be compatible with the function's declared type. |

The **symbol table** is used to store information about declared variables. When a program includes functions or blocks, the analyzer also considers where each variable was declared.

This stage does not calculate program output or execute loops.

## Errors

Jacaranda distinguishes three cases:

1. **Lexical error:** a character or symbol is not recognized by the lexer.
2. **Syntax error:** the sequence of tokens does not follow the supported grammar.
3. **Semantic error:** the instruction has a valid structure but violates one of the implemented semantic rules.

For example:

```c
int total = ;    // Syntax error: missing expression
```

```c
int total = true;    // Semantic error: incompatible type
```

## Examples and Tests

The directory `examples/parser_sdt/` includes **34 numbered examples** covering valid instructions, incorrect syntax, undeclared variables, type errors, functions, and control structures.

Some examples:

| File | Expected result |
|---|---|
| `01_correct_basic.c` | Valid declaration |
| `21_function_main.c` | Valid function and return |
| `22_functions_parameters.c` | Valid functions with parameters |
| `23_if_else.c` | Valid conditional statement |
| `25_for.c` | Valid `for` statement |
| `04_syntax_missing_expression.c` | Syntax error |
| `06_semantic_type.c` | Type error |
| `08_semantic_duplicate.c` | Repeated declaration error |
| `29_valid_function_call.c` | Valid function call |

The project also includes automated tests in `tests/`. Run them from the repository folder:

```bash
python -m unittest discover -s tests -v
```

To analyze one example from the terminal:

```bash
python src/parser_main.py examples/parser_sdt/21_function_main.c
```

## Limitations

Jacaranda is not a complete C compiler. It does not execute instructions, produce an executable, or support every C statement or data type. Calls are not checked against parameter types or counts. Its semantic rules are simplified for this course project; for example, `printf` formatting is not fully checked.

## Diagrams and Report

- [Parser diagrams](parser_diagrams/)
- [Parser & SDT report](docs/parser_sdt/)
- [Main project README](README.md)
