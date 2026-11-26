"""Jacaranda final CLI: source-file interpretation."""
import argparse
from pathlib import Path
from engine import run,parse,JacarandaError

def main():
    parser=argparse.ArgumentParser(description='Jacaranda: Lark parser, semantic analyzer, and interpreter')
    parser.add_argument('source',help='Path to a UTF-8 C-like source file')
    parser.add_argument('--max-steps',type=int,default=100000,help='Execution safety limit')
    parser.add_argument('--parse-only',action='store_true',help='Show Lark parse tree without running')
    args=parser.parse_args()
    try:source=Path(args.source).read_text(encoding='utf-8')
    except (OSError,UnicodeError) as e:
        parser.error(f'Could not load source file: {e}')
    if args.parse_only:
        try:print(parse(source).pretty());return
        except JacarandaError as e:print(e);raise SystemExit(1)
    result=run(source,max_steps=args.max_steps)
    print(result.formatted())
    if not result.ok:raise SystemExit(1)

if __name__=='__main__':main()
