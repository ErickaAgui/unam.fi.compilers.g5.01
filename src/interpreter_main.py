"""Run the final Lark interpreter from the terminal.
Usage: python src/interpreter_main.py examples/final_project/03_loops.c
"""
import sys
from pathlib import Path
from lark_pipeline import execute_source

def main():
    if len(sys.argv) != 2:
        print('Usage: python src/interpreter_main.py <source.c>')
        return 2
    try:
        source = Path(sys.argv[1]).read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        print(f'Input file error: {exc}', file=sys.stderr)
        return 2
    result = execute_source(source)
    print(result.formatted())
    return 0 if result.ok else 1

if __name__ == '__main__':
    sys.exit(main())
