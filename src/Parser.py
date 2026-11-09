from dataclasses import dataclass, field
from functools import wraps

class ParseError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line

@dataclass
class Node:
    kind: str
    value: str = ''
    children: list = field(default_factory=list)
    line: int = 1
    def pretty(self, level=0):
        return '\n'.join(['  '*level+self.kind+(f' ({self.value})' if self.value else '')] +
                         [c.pretty(level+1) for c in self.children])

@dataclass
class ParseTreeNode:
    symbol: str
    children: list = field(default_factory=list)
    def pretty(self, level=0):
        return '\n'.join(['  '*level+self.symbol]+[c.pretty(level+1) for c in self.children])

def production(name):
    def wrap(method):
        @wraps(method)
        def inner(self,*args,**kwargs):
            branch=ParseTreeNode(name)
            if self._parse_stack:
                self._parse_stack[-1].children.append(branch)
            self._parse_stack.append(branch)
            try:
                out=method(self,*args,**kwargs)
                if name=='program': self.parse_tree=branch
                return out
            finally:
                self._parse_stack.pop()
        return inner
    return wrap

class Parser:
    TYPES={'int','float','double','bool','void'}
    def __init__(self,tokens,source):
        self.tokens=list(tokens); self.source=source; self.index=0
        self._parse_stack=[]; self.parse_tree=None
    def peek(self,offset=0):
        i=self.index+offset
        return self.tokens[i] if i<len(self.tokens) else None
    def line(self,token=None):
        token=token or self.peek()
        return self.source.count('\n',0,token.getsourcepos().idx)+1 if token is not None else self.source.count('\n')+1
    def is_token(self,kind=None,text=None,offset=0):
        tok=self.peek(offset)
        return tok is not None and (kind is None or tok.gettokentype()==kind) and (text is None or tok.getstr()==text)
    def is_type(self): return self.is_token('KEYWORD') and self.peek().getstr() in self.TYPES
    def take(self,kind=None,text=None):
        if not self.is_token(kind,text):
            expected=text if text is not None else (kind or 'token')
            actual=repr(self.peek().getstr()) if self.peek() else 'end of input'
            raise ParseError(f'Expected {expected}, found {actual}',self.line())
        tok=self.peek(); self.index+=1
        if self._parse_stack:
            self._parse_stack[-1].children.append(ParseTreeNode(f'{tok.gettokentype()} -> {tok.getstr()!r}'))
        return tok
    def match(self,kind,text):
        if self.is_token(kind,text): self.take(kind,text); return True
        return False
    def _identifier(self): return self.take('IDENTIFIER')

    @production('program')
    def parse(self):
        children=[]
        while self.peek() is not None:
            if self.is_type(): children.append(self.global_declaration())
            else: children.append(self.statement()) # backwards compatibility for original examples
        self._parse_stack[-1].children.append(ParseTreeNode('EOF'))
        return Node('Program',children=children)

    @production('global')
    def global_declaration(self):
        typ=self.take('KEYWORD'); name=self._identifier()
        if self.is_token('PUNCTUATION','('):
            return self.function_tail(typ,name)
        return self.declaration_tail(typ,name)

    @production('function')
    def function_tail(self,typ,name):
        self.take('PUNCTUATION','(')
        params=[]
        if not self.is_token('PUNCTUATION',')'):
            if self.is_token('KEYWORD','void') and self.is_token('PUNCTUATION',')',1):
                self.take('KEYWORD','void')
            else:
                while True:
                    if not self.is_type(): raise ParseError('Expected parameter type',self.line())
                    t=self.take('KEYWORD'); n=self._identifier()
                    if t.getstr()=='void': raise ParseError('Parameter cannot have type void',self.line(t))
                    params.append(Node('Parameter',f'{t.getstr()} {n.getstr()}',line=self.line(t)))
                    if not self.match('PUNCTUATION',','): break
        self.take('PUNCTUATION',')')
        if self.match('PUNCTUATION',';'):
            return Node('Prototype',f'{typ.getstr()} {name.getstr()}',params,self.line(typ))
        body=self.block()
        return Node('Function',f'{typ.getstr()} {name.getstr()}',params+[body],self.line(typ))

    @production('statement')
    def statement(self):
        if self.is_type(): return self.declaration()
        if self.is_token('PUNCTUATION','{'): return self.block()
        if self.is_token('KEYWORD','if'): return self.if_statement()
        if self.is_token('KEYWORD','while'): return self.while_statement()
        if self.is_token('KEYWORD','for'): return self.for_statement()
        if self.is_token('KEYWORD','do'): return self.do_statement()
        if self.is_token('KEYWORD','return'): return self.return_statement()
        if self.is_token('KEYWORD','print') or self.is_token('KEYWORD','printf'):
            return self.print_statement()
        if self.is_token('IDENTIFIER'):
            if self.is_token('PUNCTUATION','(',1):
                call=self.call(); self.take('PUNCTUATION',';'); return Node('ExpressionStatement',children=[call],line=call.line)
            return self.assignment()
        if self.match('PUNCTUATION',';'): return Node('Empty',line=self.line())
        raise ParseError('Expected a supported statement',self.line())

    @production('block')
    def block(self):
        start=self.take('PUNCTUATION','{'); body=[]
        while not self.is_token('PUNCTUATION','}'):
            if self.peek() is None: raise ParseError('Expected } before end of input',self.line())
            body.append(self.statement())
        self.take('PUNCTUATION','}')
        return Node('Block',children=body,line=self.line(start))

    @production('declaration')
    def declaration(self):
        typ=self.take('KEYWORD'); name=self._identifier()
        return self.declaration_tail(typ,name)

    @production('declaration_tail')
    def declaration_tail(self,typ,name,semicolon=True):
        if typ.getstr()=='void': raise ParseError('Variable cannot have type void',self.line(typ))
        children=[]
        if self.match('OPERATOR','='): children.append(self.expression())
        if semicolon: self.take('PUNCTUATION',';')
        return Node('Declaration',f'{typ.getstr()} {name.getstr()}',children,self.line(typ))

    @production('assignment')
    def assignment(self,semicolon=True):
        name=self._identifier(); op=self.take('OPERATOR')
        if op.getstr() not in ('=','++','--'):
            raise ParseError('Expected assignment or ++/-- operator',self.line(op))
        if op.getstr() in ('++','--'):
            node=Node('IncDec',f'{name.getstr()} {op.getstr()}',line=self.line(name))
        else:
            node=Node('Assignment',name.getstr(),[self.expression()],self.line(name))
        if semicolon:self.take('PUNCTUATION',';')
        return node

    @production('print_stmt')
    def print_statement(self):
        name=self.take('KEYWORD'); self.take('PUNCTUATION','(')
        args=self.arguments()
        self.take('PUNCTUATION',')'); self.take('PUNCTUATION',';')
        return Node('Print' if name.getstr()=='print' else 'Printf',children=args,line=self.line(name))

    @production('return_stmt')
    def return_statement(self):
        start=self.take('KEYWORD','return'); expr=[]
        if not self.is_token('PUNCTUATION',';'):expr=[self.expression()]
        self.take('PUNCTUATION',';')
        return Node('Return',children=expr,line=self.line(start))

    @production('if_stmt')
    def if_statement(self):
        start=self.take('KEYWORD','if'); self.take('PUNCTUATION','(')
        condition=self.expression(); self.take('PUNCTUATION',')'); then=self.statement()
        children=[condition,then]
        if self.match('KEYWORD','else'):children.append(self.statement())
        return Node('If',children=children,line=self.line(start))

    @production('while_stmt')
    def while_statement(self):
        start=self.take('KEYWORD','while'); self.take('PUNCTUATION','(')
        condition=self.expression(); self.take('PUNCTUATION',')'); body=self.statement()
        return Node('While',children=[condition,body],line=self.line(start))

    @production('do_while_stmt')
    def do_statement(self):
        start=self.take('KEYWORD','do'); body=self.statement()
        self.take('KEYWORD','while'); self.take('PUNCTUATION','(')
        cond=self.expression(); self.take('PUNCTUATION',')'); self.take('PUNCTUATION',';')
        return Node('DoWhile',children=[body,cond],line=self.line(start))

    @production('for_stmt')
    def for_statement(self):
        start=self.take('KEYWORD','for'); self.take('PUNCTUATION','(')
        if self.is_token('PUNCTUATION',';'): init=Node('Empty',line=self.line())
        elif self.is_type():
            t=self.take('KEYWORD');n=self._identifier();init=self.declaration_tail(t,n,semicolon=False)
        else:init=self.assignment(semicolon=False)
        self.take('PUNCTUATION',';')
        cond=Node('Empty',line=self.line()) if self.is_token('PUNCTUATION',';') else self.expression()
        self.take('PUNCTUATION',';')
        update=Node('Empty',line=self.line()) if self.is_token('PUNCTUATION',')') else self.assignment(semicolon=False)
        self.take('PUNCTUATION',')'); body=self.statement()
        return Node('For',children=[init,cond,update,body],line=self.line(start))

    @production('expression')
    def expression(self):return self.logic_or()
    @production('logic_or')
    def logic_or(self):return self._binary_chain(self.logic_and,('||',))
    @production('logic_and')
    def logic_and(self):return self._binary_chain(self.equality,('&&',))
    @production('equality')
    def equality(self):return self._binary_chain(self.comparison,('==','!='))
    @production('comparison')
    def comparison(self):return self._binary_chain(self.additive,('<','>','<=','>='))
    @production('additive')
    def additive(self):return self._binary_chain(self.term,('+','-'))
    @production('term')
    def term(self):return self._binary_chain(self.unary,('*','/','%'))
    def _binary_chain(self,next_rule,operators):
        left=next_rule()
        while self.is_token('OPERATOR') and self.peek().getstr() in operators:
            op=self.take('OPERATOR');right=next_rule()
            left=Node('Binary',op.getstr(),[left,right],self.line(op))
        return left
    @production('unary')
    def unary(self):
        if self.is_token('OPERATOR') and self.peek().getstr() in ('+','-','!'):
            op=self.take('OPERATOR');return Node('Unary',op.getstr(),[self.unary()],self.line(op))
        return self.primary()
    @production('primary')
    def primary(self):
        tok=self.peek()
        if tok and tok.gettokentype() in ('INTEGER','REAL','BOOLEAN','STRING'):
            self.take();return Node('Literal',f'{tok.gettokentype()}:{tok.getstr()}',line=self.line(tok))
        if self.is_token('IDENTIFIER'):
            if self.is_token('PUNCTUATION','(',1):return self.call()
            tok=self.take('IDENTIFIER');return Node('Identifier',tok.getstr(),line=self.line(tok))
        if self.match('PUNCTUATION','('):
            node=self.expression();self.take('PUNCTUATION',')');return node
        raise ParseError('Expected an expression',self.line())
    @production('call')
    def call(self):
        name=self._identifier();self.take('PUNCTUATION','(')
        args=self.arguments();self.take('PUNCTUATION',')')
        return Node('Call',name.getstr(),args,self.line(name))
    @production('arguments')
    def arguments(self):
        args=[]
        if not self.is_token('PUNCTUATION',')'):
            args.append(self.expression())
            while self.match('PUNCTUATION',','):args.append(self.expression())
        return args
