from rply import LexerGenerator


class Lexer:
    """Builds the lexical analyzer used by the Jacaranda project.

    The language recognized by this project is a small C-oriented subset.  It
    also keeps ``print`` and ``printf`` as project keywords because those words
    appear in the assignment examples.
    """

    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        # 1. KEYWORDS
        # They are registered before IDENTIFIER so reserved words are not
        # classified as ordinary identifiers. C is case-sensitive, therefore
        # INT and int are intentionally different lexemes.
        self.lexer.add(
            'KEYWORD',
            r'(auto|break|case|char|const|continue|default|do|double|else|enum|'
            r'extern|float|for|goto|if|int|long|register|return|short|signed|'
            r'sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|'
            r'while|_Packed|print|printf|bool)'
            r'(?![a-zA-Z0-9_])'
        )

        # 2. CONSTANTS
        # A complete string is kept as a single token, including spaces inside
        # quotation marks.
        self.lexer.add('STRING', r'"([^"\\]|\\.)*"')
        self.lexer.add('REAL', r'[0-9]+\.[0-9]+')
        self.lexer.add('INTEGER', r'[0-9]+')

        # true and false are represented as Boolean constants in this project.
        self.lexer.add('BOOLEAN', r'(true|false)(?![a-zA-Z0-9_])')

        # 3. OPERATORS
        # Multi-character operators are placed before their shorter forms.
        self.lexer.add(
            'OPERATOR',
            r'==|!=|<=|>=|\+\+|--|&&|\|\||\+|-|\*|/|%|=|<|>|!'
        )

        # 4. PUNCTUATION
        # ':' is included for labels such as case 1: and default:.
        self.lexer.add('PUNCTUATION', r'[;,:(){}\[\]]')

        # 5. IDENTIFIERS
        # Uppercase letters are valid in identifiers; only keywords are
        # intentionally case-sensitive.
        self.lexer.add('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*')

        # 6. IGNORED INPUT
        # \s+ covers spaces, tabs, carriage returns and new lines. Spaces
        # inside strings are not affected because STRING is matched as a token.
        self.lexer.ignore(r'\s+')
        self.lexer.ignore(r'//[^\n]*')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
