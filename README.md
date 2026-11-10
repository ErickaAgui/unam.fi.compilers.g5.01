# Jacaranda | Lexical, Syntax and Semantic Analyzer

Jacaranda is a Python project developed for the **Compilers** course at the Faculty of Engineering, National Autonomous University of Mexico (UNAM).

**Team 01 — Group 5**  
**Semester 2027-1**

The first part of the project was a lexical analyzer. The second part adds a **syntax analyzer (Parser)** and **semantic checks (SDT)**. Jacaranda recognizes a selected set of C-like instructions, checks how tokens are organized, and reports errors found during the analysis.

This is an educational project. It **does not execute the entered code** or implement the complete C language.

## Main Features

### Lexical Analysis

- Analyze source code typed by the user or loaded from a `.txt`, `.c`, or `.h` file.
- Recognize keywords, identifiers, operators, constants, and punctuation.
- Recognize the course-specific `print` keyword.
- Handle integer, real, Boolean, and string constants.
- Ignore whitespace and supported comments.
- Display the token sequence and the total number of tokens.
- Report unrecognized symbols and their location.
- Use the original lexer developed with **RPLY**.

### Syntax Analysis (Parser)

- Check declarations, assignments, expressions, and blocks of statements.
- Recognize functions, parameters, function calls, and return statements.
- Recognize basic conditional and repetition statements: `if`, `else`, `while`, `for`, and `do-while`.
- Apply operator precedence when processing expressions.
- Build a parse tree to show the recognized grammatical structure.
- Report syntax errors when the tokens do not follow the supported grammar.

The parser follows a **top-down recursive-descent approach**: Python functions recognize the supported instructions without using an external parser generator.

### Semantic Analysis (SDT)

- Use a **symbol table** to keep track of declared variables and their types.
- Check whether variables have been declared and avoid repeated declarations in the same block.
- Check types used in declarations, assignments, and expressions.
- Recognize functions and parameters; check that called functions exist and that return values have compatible types.
- Report semantic errors separately from syntax errors.

### User Interface

- Analyze input using the lexer.
- Run the Parser & SDT analysis from the graphical interface.
- Open the **Parse Tree** viewer, zoom, and navigate through the tree.
- Save the tree as SVG, PNG, or JPG.

## Requirements

- Python 3.10 or newer
- RPLY 0.7.8
- Pillow (for PNG/JPG export)
- Tkinter (included with many Python installations)

Install the Python dependencies from the project folder:

```bash
python -m pip install -r requirements.txt
```

On Windows, `py` can be used instead of `python`.

## How to Run

Graphical interface:

```bash
python src/gui.py
```

Lexical analyzer in the terminal:

```bash
python src/main.py
```

Parser & SDT with a sample file:

```bash
python src/parser_main.py examples/parser_sdt/21_function_main.c
```

## Examples and Tests

- `examples/lexer/` contains the examples from the first delivery.
- `examples/parser_sdt/` contains **34 numbered input examples**, including valid cases and cases with expected errors.
- `tests/` contains automated checks for the parser, semantic analysis, and tree visualization.

Run the tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

## Project Structure

```text
unam.fi.compilers.g5.01/
├── assets/                  # Application icons
├── docs/
│   ├── lexer/               # Lexical analyzer report and presentation
│   └── parser_sdt/          # Parser & SDT report and presentation
├── examples/
│   ├── lexer/               # Lexer examples
│   └── parser_sdt/          # Parser & SDT examples
├── lexical_diagrams/
│   ├── diagrams_pdf/
│   └── tex/
├── parser_diagrams/         # Parser and semantic-analysis diagrams
│   ├── diagrams_pdf/
│   └── tex/
├── project_management/
├── src/
│   ├── LexicalAnalyzer.py
│   ├── Parser.py
│   ├── SemanticAnalyzer.py
│   ├── analysis_pipeline.py
│   ├── parser_main.py
│   ├── ParseTreeViewer.py
│   ├── gui.py
│   └── main.py
├── tests/
├── .gitignore
├── README.md
├── PARSER_README.md
└── requirements.txt
```

## Documentation

- [Parser & SDT documentation](PARSER_README.md)
- [Lexical diagrams](lexical_diagrams/)
- [Parser diagrams](parser_diagrams/)
- [Course reports](docs/)

## Repository

https://github.com/ErickaAgui/unam.fi.compilers.g5.01
