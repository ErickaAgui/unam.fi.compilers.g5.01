import sys
from pathlib import Path
from lark_pipeline import check_source

def analyze_source(source):
    result = check_source(source)
    print(result.formatted())
    return result.ok

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            code = Path(sys.argv[1]).read_text(encoding='utf-8')
        except OSError as exc:
            print(f'Unable to read input: {exc}', file=sys.stderr)
            sys.exit(2)
    else:
        print('Enter source; finish with Ctrl+D (Unix) / Ctrl+Z then Enter (Windows):')
        code = sys.stdin.read()
    sys.exit(0 if analyze_source(code) else 1)
