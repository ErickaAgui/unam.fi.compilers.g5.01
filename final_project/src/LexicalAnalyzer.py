from rply import LexerGenerator


class Lexer:

    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        self.lexer.add(
            'KEYWORD',
            r'(auto|break|case|char|const|continue|default|do|double|else|enum|'
            r'extern|float|for|goto|if|int|long|register|return|short|signed|'
            r'sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|'
            r'while|_Packed|print|printf|bool)'
            r'(?![a-zA-Z0-9_])'
        )

        self.lexer.add('STRING', r'"([^"\\]|\\.)*"')
        self.lexer.add('REAL', r'[0-9]+\.[0-9]+')
        self.lexer.add('INTEGER', r'[0-9]+')

        self.lexer.add('BOOLEAN', r'(true|false)(?![a-zA-Z0-9_])')

        self.lexer.add(
            'OPERATOR',
            r'==|!=|<=|>=|\+\+|--|&&|\|\||\+|-|\*|/|%|=|<|>|!'
        )

        self.lexer.add('PUNCTUATION', r'[;,:(){}\[\]]')

        self.lexer.add('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*')

        self.lexer.ignore(r'\s+')
        self.lexer.ignore(r'//[^\n]*')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
