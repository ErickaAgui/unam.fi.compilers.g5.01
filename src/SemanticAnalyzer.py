class SemanticError(Exception):
    def __init__(self,message,line):super().__init__(message);self.line=line

class SemanticAnalyzer:
    numeric={'int','float','double'}
    def __init__(self):
        self.scopes=[{}];self.functions={};self.current_return=None
        self.symbols=self.scopes[0]
    def fail(self,message,node):raise SemanticError(message,node.line)
    def lookup(self,name,node):
        for scope in reversed(self.scopes):
            if name in scope:return scope[name]
        self.fail(f'Variable {name!r} is not declared',node)
    def declare(self,name,typ,node):
        if name in self.scopes[-1]:self.fail(f'Variable {name!r} is already declared',node)
        self.scopes[-1][name]=typ
    def push(self):self.scopes.append({})
    def pop(self):self.scopes.pop()
    def compatible(self,expected,actual):
        return expected==actual or (expected=='float' and actual=='int') or (expected=='double' and actual in ('int','float'))
    def require_assignment(self,expected,actual,line):
        if not self.compatible(expected,actual):
            raise SemanticError(f'Type mismatch: cannot assign {actual} to {expected}',line)
    def verify(self,tree):
        # Primero registramos los nombres y tipos de retorno de las funciones.
        for node in tree.children:
            if node.kind not in ('Function', 'Prototype'):
                continue
            return_type, name = node.value.split(' ', 1)
            previous = self.functions.get(name)
            if node.kind == 'Function':
                if previous is not None and previous[1]:
                    self.fail(f'Function {name!r} is already defined', node)
                self.functions[name] = (return_type, True)
            elif previous is None:
                self.functions[name] = (return_type, False)

        for node in tree.children:
            if node.kind == 'Function':
                self.function(node)
            elif node.kind != 'Prototype':
                self.statement(node)
        return dict(self.symbols)
    def function(self,node):
        typ,name=node.value.split(' ',1)
        params=node.children[:-1];body=node.children[-1]
        old=self.current_return;self.current_return=typ
        self.push()
        try:
            for param in params:
                t,n=param.value.split(' ',1);self.declare(n,t,param)
            self.statement(body,new_scope=False)
            if typ!='void' and not self.has_return(body):
                self.fail(f'Non-void function {name!r} requires a return statement',node)
        finally:self.pop();self.current_return=old
    def has_return(self,node):
        if node.kind=='Return':return True
        if node.kind=='If' and len(node.children)==3:
            return self.has_return(node.children[1]) and self.has_return(node.children[2])
        if node.kind=='Block':
            return any(self.has_return(c) for c in node.children)
        return False
    def statement(self,n,new_scope=True):
        k=n.kind
        if k=='Block':
            if new_scope:self.push()
            try:
                for child in n.children:self.statement(child)
            finally:
                if new_scope:self.pop()
        elif k=='Declaration':
            typ,name=n.value.split(' ',1)
            if name in self.scopes[-1]:self.fail(f'Variable {name!r} is already declared',n)
            if n.children:self.require_assignment(typ,self.expression_type(n.children[0]),n.line)
            self.declare(name,typ,n)
        elif k=='Assignment':
            typ=self.lookup(n.value,n)
            self.require_assignment(typ,self.expression_type(n.children[0]),n.line)
        elif k=='IncDec':
            name=n.value.split()[0];t=self.lookup(name,n)
            if t not in self.numeric:self.fail('Increment/decrement requires a numeric variable',n)
        elif k in ('Print','Printf'):
            for arg in n.children:self.expression_type(arg)
            if k=='Print' and len(n.children)!=1:self.fail('print requires one argument',n)
            if k=='Printf' and (not n.children or self.expression_type(n.children[0])!='string'):
                self.fail('printf requires a format string as first argument',n)
        elif k=='ExpressionStatement':self.expression_type(n.children[0])
        elif k=='Return':
            if self.current_return is None:self.fail('return outside a function',n)
            if self.current_return=='void':
                if n.children:self.fail('Void function cannot return a value',n)
            else:
                if not n.children:self.fail('Non-void function must return a value',n)
                self.require_assignment(self.current_return,self.expression_type(n.children[0]),n.line)
        elif k=='If':
            self.condition(n.children[0]);self.statement(n.children[1])
            if len(n.children)>2:self.statement(n.children[2])
        elif k=='While':self.condition(n.children[0]);self.statement(n.children[1])
        elif k=='DoWhile':self.statement(n.children[0]);self.condition(n.children[1])
        elif k=='For':
            self.push()
            try:
                for i in (0,):self.statement(n.children[i])
                if n.children[1].kind!='Empty':self.condition(n.children[1])
                self.statement(n.children[2]);self.statement(n.children[3])
            finally:self.pop()
        elif k=='Empty':pass
        else:self.fail('Unsupported statement: '+k,n)
    def condition(self,n):
        typ=self.expression_type(n)
        if typ not in self.numeric|{'bool'}:self.fail('Condition requires numeric or boolean expression',n)
    def expression_type(self,n):
        if n.kind=='Literal':
            return {'INTEGER':'int','REAL':'float','BOOLEAN':'bool','STRING':'string'}[n.value.split(':',1)[0]]
        if n.kind=='Identifier':return self.lookup(n.value,n)
        if n.kind == 'Call':
            if n.value not in self.functions:
                self.fail(f'Function {n.value!r} is not declared', n)
            # Cada argumento debe ser una expresion valida, pero no se compara
            # su cantidad ni su tipo con los parametros de la funcion.
            for argument in n.children:
                self.expression_type(argument)
            return self.functions[n.value][0]
        if n.kind=='Unary':
            typ=self.expression_type(n.children[0])
            if n.value=='!':
                if typ not in self.numeric|{'bool'}:self.fail('! requires a numeric or boolean operand',n)
                return 'bool'
            if typ not in self.numeric:self.fail('Unary +/- requires numeric operand',n)
            return typ
        if n.kind=='Binary':
            left=self.expression_type(n.children[0]);right=self.expression_type(n.children[1]);op=n.value
            if op in ('&&','||'):
                if left not in self.numeric|{'bool'} or right not in self.numeric|{'bool'}:self.fail(f'{op} requires boolean or numeric operands',n)
                return 'bool'
            if op in ('==','!='):
                if left==right or (left in self.numeric and right in self.numeric):return 'bool'
                self.fail(f'Cannot compare {left} and {right}',n)
            if op in ('<','>','<=','>='):
                if left not in self.numeric or right not in self.numeric:self.fail(f'{op} requires numeric operands',n)
                return 'bool'
            if left not in self.numeric or right not in self.numeric:self.fail(f'Operator {op} requires numeric operands, found {left} and {right}',n)
            if op=='%':
                if left!='int' or right!='int':self.fail('% requires integer operands',n)
                return 'int'
            if op=='/':return 'float' # retained teaching rule, not full C semantics
            return 'double' if 'double' in (left,right) else ('float' if 'float' in (left,right) else 'int')
        self.fail('Unsupported expression: '+n.kind,n)
