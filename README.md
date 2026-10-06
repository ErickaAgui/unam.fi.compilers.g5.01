# Jacaranda Lexical Analyzer

Jacaranda is a lexical analyzer developed for the **Compilers** course at the Faculty of Engineering, UNAM.

**Team 01 — Group 5**  
**Semester 2027-1**

This project analyzes source text and separates it into lexical tokens. It can recognize keywords, identifiers, operators, constants, and punctuation symbols, while also reporting the total number of tokens found.

The analyzer is C-oriented and was developed in Python using **RPLY**. It is an educational lexer created for the requirements of this course, so it does not try to implement the complete C lexical specification.

---

## Main Features

Jacaranda can:

- Analyze source code written directly by the user.
- Analyze source code from a file.
- Recognize keywords, identifiers, operators, constants, and punctuation.
- Recognize `print` as a keyword, as required by the activity.
- Handle integer, real, Boolean, and string constants.
- Ignore whitespace and supported single-line comments.
- Detect unsupported symbols and report their line and column.
- Display the complete token sequence.
- Report the total number of recognized tokens.
- Use the same lexical analyzer from both the terminal and graphical interfaces.

The graphical interface supports `.txt`, `.c`, and `.h` files.

---

## Project Structure

```text
unam.fi.compilers.g5.01/
│
├── A. Diagramas léxicos/
│   │
│   ├── Diagram PDF/
│   │   ├── architecture.pdf
│   │   ├── boolean.pdf
│   │   ├── identifier.pdf
│   │   ├── ignored.pdf
│   │   ├── keywords.pdf
│   │   ├── leftfactoring.pdf
│   │   ├── numeric.pdf
│   │   ├── operators.pdf
│   │   ├── punctuation.pdf
│   │   ├── string.pdf
│   │   └── workflow.pdf
│   │
│   └── Text/
│       ├── architecture.tex
│       ├── boolean.tex
│       ├── identifier.tex
│       ├── ignored.tex
│       ├── keywords.tex
│       ├── leftfactoring.tex
│       ├── numeric.tex
│       ├── operators.tex
│       ├── punctuation.tex
│       ├── string.tex
│       └── workflow.tex
│
├── assets/
│   ├── jacaranda.ico
│   └── jacaranda_icon.png
│
├── docs/
│   └── 01-Compilers-Lexer.pdf
│
├── examples/
│   ├── 40_tokens.txt
│   ├── ejemplo_error.txt
│   ├── ejemplo_espacios.txt
│   ├── ejemplo_int.txt
│   ├── ejemplo_print.txt
│   ├── ejemplo_printf.txt
│   └── ejemplo_switch.txt
│
├── project_management/
│   └── kanban_board.png
│
├── src/
│   ├── LexicalAnalyzer.py
│   ├── gui.py
│   └── main.py
│
├── README.md
├── requirements.pdf
└── .gitignore
```