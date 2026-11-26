"""Lark-powered syntax analysis, SDT validation and bounded AST interpreter.
The separate historic RPLY lexer remains in LexicalAnalyzer.py for comparison.
This final pipeline uses Lark's LALR lexer+parser (one grammar source).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import ast as pyast
import operator
import re
from lark import Lark, Tree, Token, UnexpectedInput

GRAMMAR = Path(__file__).with_name('jacaranda.lark')
PARSER = Lark.open(str(GRAMMAR), parser='lalr', propagate_positions=True, maybe_placeholders=False)
NUMERIC = ('int','float','double')
TYPE_DEFAULT = {'int':0,'float':0.0,'double':0.0,'bool':False,'char':''}

class JacarandaError(Exception):
    def __init__(self, phase, message, line=1):
        self.phase, self.message, self.line = phase,message,line
        super().__init__(f'{phase} error in line {line}: {message}')

@dataclass
class Value:
    type: str
    value: object

@dataclass
class Frame:
    parent: 'Frame | None' = None
    vars: dict = field(default_factory=dict)
    def declare(self,name,value,line):
        if name in self.vars:
            raise JacarandaError('SDT',f"Variable '{name}' is already declared in this scope",line)
        self.vars[name] = value
    def lookup(self,name,line):
        frame=self
        while frame:
            if name in frame.vars:return frame.vars[name]
            frame=frame.parent
        raise JacarandaError('SDT',f"Variable '{name}' is not declared",line)
    def assign(self,name,value,line):
        frame=self
        while frame:
            if name in frame.vars:
                frame.vars[name]=coerce(frame.vars[name].type,value,line)
                return
            frame=frame.parent
        raise JacarandaError('SDT',f"Variable '{name}' is not declared",line)

def coerce(dest, v, line):
    if dest=='void':raise JacarandaError('SDT','void cannot be a variable type',line)
    if dest==v.type:return Value(dest,v.value)
    if dest in ('float','double') and v.type=='int':return Value(dest,float(v.value))
    if dest=='double' and v.type=='float':return Value(dest,float(v.value))
    raise JacarandaError('SDT',f'Type mismatch: cannot assign {v.type} to {dest}',line)

def tname(node):return str(node.data) if isinstance(node,Tree) else str(node)
def line(node):return getattr(getattr(node,'meta',None),'line',getattr(node,'line',1))
def eval_type(val):
    if isinstance(val,bool):return 'bool'
    if isinstance(val,int):return 'int'
    if isinstance(val,float):return 'float'
    return 'string'

class Interpreter:
    def __init__(self, tree, max_steps=100000, max_depth=64):
        self.tree=tree
        self.max_steps=max_steps
        self.max_depth=max_depth
        self.steps=0
        self.depth=0
        self.output=[]
        self.global_scope=Frame()
        self.functions={}
        for node in tree.children:
            if tname(node)=='function':
                name=str(node.children[1])
                if name in self.functions:raise JacarandaError('SDT',f"Function '{name}' is already defined",line(node))
                self.functions[name]=node

    def tick(self,node):
        self.steps+=1
        if self.steps>self.max_steps:
            raise JacarandaError('Runtime','Step limit exceeded (possible infinite loop)',line(node))

    def execute(self):
        for node in self.tree.children:
            if tname(node)!='function':self.exec_stmt(node,self.global_scope)
        if 'main' in self.functions:self.call_function('main',[],self.functions['main'])
        return '\n'.join(self.output)

    def call_function(self,name,values,origin):
        if name not in self.functions:raise JacarandaError('SDT',f"Function '{name}' is not declared",line(origin))
        if self.depth>=self.max_depth:raise JacarandaError('Runtime','Maximum call depth exceeded',line(origin))
        node=self.functions[name]
        typ=str(node.children[0]); i=2
        params=[]
        if tname(node.children[i])=='parameters':
            params=node.children[i].children;i+=1
        if len(params)!=len(values):raise JacarandaError('SDT',f"Function '{name}' expects {len(params)} arguments but got {len(values)}",line(origin))
        local=Frame(self.global_scope)
        for param,value in zip(params,values):
            ptype,pname=map(str,param.children)
            local.declare(pname,coerce(ptype,value,line(origin)),line(origin))
        self.depth+=1
        try:
            try:self.exec_block(node.children[i],local,new_frame=False)
            except ReturnSignal as ret:
                if typ=='void':
                    if ret.value is not None:raise JacarandaError('SDT','void function cannot return a value',line(origin))
                    return Value('void',None)
                if ret.value is None:raise JacarandaError('SDT',f'Function {name} must return {typ}',line(origin))
                return coerce(typ,ret.value,line(origin))
            if typ!='void':raise JacarandaError('SDT',f"Function '{name}' must return {typ}",line(origin))
            return Value('void',None)
        finally:self.depth-=1

    def exec_block(self,node,frame,new_frame=True):
        child_frame=Frame(frame) if new_frame else frame
        for stmt in node.children:self.exec_stmt(stmt,child_frame)

    def exec_stmt(self,node,frame):
        self.tick(node)
        kind=tname(node)
        if kind in ('statement_decl','statement_assign','statement_print','statement_postfix','statement_call'):
            return self.exec_stmt(node.children[0],frame)
        if kind=='declaration':
            typ,name=map(str,node.children[:2])
            if typ=='void':raise JacarandaError('SDT','Variable cannot be void',line(node))
            val=self.eval(node.children[2],frame) if len(node.children)>2 else Value(typ,TYPE_DEFAULT[typ])
            frame.declare(name,coerce(typ,val,line(node)),line(node));return
        if kind=='assignment':
            frame.assign(str(node.children[0]),self.eval(node.children[1],frame),line(node));return
        if kind=='postfix':
            name,op=map(str,node.children)
            previous=frame.lookup(name,line(node))
            if previous.type not in NUMERIC:raise JacarandaError('SDT','Increment/decrement requires numeric variable',line(node))
            frame.assign(name,Value(previous.type,previous.value+(1 if op=='++' else -1)),line(node));return
        if kind=='print_stmt':
            vals=self.args_from(node.children,frame)
            if vals and vals[0].type=='string' and len(vals)>1:
                fmt=vals[0].value
                if '%' in fmt:
                    try:output=fmt%tuple(v.value for v in vals[1:])
                    except (TypeError,ValueError) as e:raise JacarandaError('Runtime',f'Invalid format string: {e}',line(node))
                else: output=' '.join(str(v.value) for v in vals)
            else: output=' '.join(self.to_text(v) for v in vals)
            self.output.append(output);return
        if kind=='statement_call':return self.eval(node.children[0],frame)
        if kind=='call':return self.eval(node,frame)
        if kind=='nested_block':return self.exec_block(node.children[0],frame)
        if kind=='block':return self.exec_block(node,frame)
        if kind=='return_stmt':
            value=self.eval(node.children[0],frame) if node.children else None
            raise ReturnSignal(value)
        if kind=='if_stmt':
            condition=self.eval(node.children[0],frame)
            if self.is_true(condition,node):self.exec_stmt(node.children[1],Frame(frame))
            elif len(node.children)>2:self.exec_stmt(node.children[2],Frame(frame))
            return
        if kind=='while_stmt':
            while self.is_true(self.eval(node.children[0],frame),node):self.exec_stmt(node.children[1],Frame(frame))
            return
        if kind=='do_stmt':
            while True:
                self.exec_stmt(node.children[0],Frame(frame))
                if not self.is_true(self.eval(node.children[1],frame),node):break
            return
        if kind=='for_stmt':
            # grammar emits only nonempty optional fields; use explicit wrappers
            parts=list(node.children)
            local=Frame(frame)
            init=next((c for c in parts if tname(c)=='for_init'),None)
            cond=next((c for c in parts if tname(c)=='for_condition'),None)
            update=next((c for c in parts if tname(c)=='for_update'),None)
            body=parts[-1]
            if init:self.exec_stmt(init.children[0],local)
            while cond is None or self.is_true(self.eval(cond.children[0],local),node):
                self.exec_stmt(body,Frame(local))
                if update:self.exec_stmt(update.children[0],local)
            return
        if kind in ('for_init','for_update'):return self.exec_stmt(node.children[0],frame)
        raise JacarandaError('Runtime',f'Unsupported statement {kind}',line(node))

    def to_text(self,v):
        if v.type=='bool':return 'true' if v.value else 'false'
        return str(v.value)
    def is_true(self,v,node):
        if v.type not in NUMERIC+('bool',):raise JacarandaError('SDT','Condition must be numeric or bool',line(node))
        return bool(v.value)
    def args_from(self,children,frame):
        if not children:return []
        if tname(children[0])=='args':return [self.eval(c,frame) for c in children[0].children]
        return [self.eval(c,frame) for c in children]
    def eval(self,node,frame):
        self.tick(node)
        kind=tname(node)
        if kind=='grouped':return self.eval(node.children[0],frame)
        if kind=='number':
            s=str(node.children[0]);value=float(s) if any(c in s.lower() for c in '.e') else int(s)
            return Value(eval_type(value),value)
        if kind=='string':return Value('string',pyast.literal_eval(str(node.children[0])))
        if kind=='char_literal':return Value('char',pyast.literal_eval(str(node.children[0])))
        if kind in ('true','false'):return Value('bool',kind=='true')
        if kind=='variable':return frame.lookup(str(node.children[0]),line(node))
        if kind=='call':return self.call_function(str(node.children[0]),self.args_from(node.children[1:],frame),node)
        if kind=='unary':
            op=str(node.children[0]);a=self.eval(node.children[1],frame)
            if op=='!':return Value('bool',not self.is_true(a,node))
            if a.type not in NUMERIC:raise JacarandaError('SDT','Unary +/- requires numeric value',line(node))
            return Value(a.type,-a.value if op=='-' else +a.value)
        if kind in ('or_expr','and_expr','equality','comparison','additive','multiplicative'):
            parts=node.children
            value=self.eval(parts[0],frame)
            if len(parts)==1:return value
            idx=1
            while idx<len(parts):
                op='||' if kind=='or_expr' else ('&&' if kind=='and_expr' else str(parts[idx]))
                right_index=idx if kind in ('or_expr','and_expr') else idx+1
                if op=='||' and self.is_true(value,node):value=Value('bool',True)
                elif op=='&&' and not self.is_true(value,node):value=Value('bool',False)
                else:
                    right=self.eval(parts[right_index],frame)
                    value=self.binary(op,value,right,node)
                idx+=1 if kind in ('or_expr','and_expr') else 2
            return value
        raise JacarandaError('Runtime',f'Unsupported expression {kind}',line(node))

    def binary(self,op,a,b,node):
        if op in ('||','&&'):
            return Value('bool',(self.is_true(a,node) or self.is_true(b,node)) if op=='||' else (self.is_true(a,node) and self.is_true(b,node)))
        if op in ('==','!='):
            if a.type!=b.type and not (a.type in NUMERIC and b.type in NUMERIC):raise JacarandaError('SDT','Cannot compare incompatible types',line(node))
            return Value('bool',(a.value==b.value) if op=='==' else (a.value!=b.value))
        if a.type not in NUMERIC or b.type not in NUMERIC:
            raise JacarandaError('SDT',f'Operator {op} requires numeric operands',line(node))
        if op in ('<','>','<=','>='):
            return Value('bool',{'<':operator.lt,'>':operator.gt,'<=':operator.le,'>=':operator.ge}[op](a.value,b.value))
        if op in ('/','%') and b.value==0:raise JacarandaError('Runtime','Division by zero',line(node))
        op_map={'+':operator.add,'-':operator.sub,'*':operator.mul,'/':operator.truediv,'%':operator.mod}
        val=op_map[op](a.value,b.value)
        typ='float' if op=='/' else ('double' if 'double' in (a.type,b.type) else ('float' if 'float' in (a.type,b.type) else 'int'))
        return Value(typ,val)

class ReturnSignal(BaseException):
    def __init__(self,value):self.value=value

@dataclass
class Result:
    ok:bool
    phase:str
    message:str
    output:str=''
    tree:object=None
    variables:dict=field(default_factory=dict)
    def formatted(self):
        prefix='Parsing Success!\nSDT Verified!' if self.ok else self.message
        if self.ok:return prefix+'\n\nExecution output:\n'+(self.output or '(no output)')
        return prefix

def parse(source):
    try:return PARSER.parse(source)
    except UnexpectedInput as exc:
        raise JacarandaError('Parsing',str(exc).split('\n')[0],getattr(exc,'line',1)) from exc

def run(source,max_steps=100000):
    try:
        tree=parse(source)
        engine=Interpreter(tree,max_steps=max_steps)
        output=engine.execute()
        return Result(True,'success','OK',output,tree,engine.global_scope.vars)
    except JacarandaError as exc:
        return Result(False,exc.phase,str(exc))

# Final public pipeline: parse -> static SDT -> interpret.
def run(source,max_steps=100000):
    try:
        tree=parse(source)
        from semantics import SemanticChecker
        SemanticChecker(tree).check()
        engine=Interpreter(tree,max_steps=max_steps)
        output=engine.execute()
        return Result(True,'success','OK',output,tree,engine.global_scope.vars)
    except JacarandaError as exc:
        return Result(False,exc.phase,str(exc))
