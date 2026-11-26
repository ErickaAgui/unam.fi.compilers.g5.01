"""Static semantic pass over Lark trees: type synthesis and nested scopes."""
from engine import Frame,Value,JacarandaError,coerce,tname,line,NUMERIC

class SemanticChecker:
    def __init__(self,tree):
        self.tree=tree; self.scope=Frame();self.functions={}
        for n in tree.children:
            if tname(n)=='function':
                name=str(n.children[1]);rt=str(n.children[0]);params=n.children[2].children if len(n.children)>3 else []
                if name in self.functions:raise JacarandaError('SDT',f"Duplicate function '{name}'",line(n))
                self.functions[name]=(rt,[(str(p.children[0]),str(p.children[1])) for p in params],n)

    def infer(self,node,frame):
        k=tname(node)
        if k=='grouped':return self.infer(node.children[0],frame)
        if k=='number':return 'float' if any(ch in str(node.children[0]).lower() for ch in '.e') else 'int'
        if k=='string':return 'string'
        if k=='char_literal':return 'char'
        if k in ('true','false'):return 'bool'
        if k=='variable':return frame.lookup(str(node.children[0]),line(node)).type
        if k=='call':
            name=str(node.children[0]);fn=self.functions.get(name)
            if not fn:raise JacarandaError('SDT',f"Function '{name}' is not declared",line(node))
            rt,params,_=fn; args=node.children[1].children if len(node.children)>1 else []
            if len(args)!=len(params):raise JacarandaError('SDT',f"Function '{name}' expects {len(params)} arguments, got {len(args)}",line(node))
            for arg,(pt,_) in zip(args,params):coerce(pt,Value(self.infer(arg,frame),None),line(arg))
            return rt
        if k=='unary':
            op=str(node.children[0]);typ=self.infer(node.children[1],frame)
            if op=='!':
                if typ not in NUMERIC+('bool',):raise JacarandaError('SDT','Logical negation requires numeric or bool',line(node))
                return 'bool'
            if typ not in NUMERIC:raise JacarandaError('SDT','Unary +/- requires numeric type',line(node))
            return typ
        if k in ('or_expr','and_expr','equality','comparison','additive','multiplicative'):
            c=node.children; typ=self.infer(c[0],frame);i=1
            while i<len(c):
                op=('||' if k=='or_expr' else '&&') if k in ('or_expr','and_expr') else str(c[i]);j=i if k in ('or_expr','and_expr') else i+1
                other=self.infer(c[j],frame)
                if op in ('&&','||'):
                    if typ not in NUMERIC+('bool',) or other not in NUMERIC+('bool',):raise JacarandaError('SDT','Logical operands must be numeric or bool',line(node))
                    typ='bool'
                elif op in ('==','!='):
                    if typ!=other and not (typ in NUMERIC and other in NUMERIC):raise JacarandaError('SDT','Incompatible equality operands',line(node))
                    typ='bool'
                else:
                    if typ not in NUMERIC or other not in NUMERIC:raise JacarandaError('SDT',f'{op} requires numeric operands',line(node))
                    typ='bool' if op in ('<','>','<=','>=') else ('float' if op=='/' else ('double' if 'double' in (typ,other) else ('float' if 'float' in (typ,other) else 'int')))
                i+=1 if k in ('or_expr','and_expr') else 2
            return typ
        raise JacarandaError('SDT',f'Unsupported expression: {k}',line(node))

    def stmt(self,node,frame,rt=None,new_scope=True):
        k=tname(node)
        if k.startswith('statement_') or k in ('for_init','for_update','nested_block'):
            return self.stmt(node.children[0],frame,rt)
        if k=='block':
            inner=Frame(frame) if new_scope else frame
            for child in node.children:self.stmt(child,inner,rt)
            return
        if k=='declaration':
            typ,name=map(str,node.children[:2])
            if typ=='void':raise JacarandaError('SDT','Variable cannot have type void',line(node))
            if len(node.children)>2:coerce(typ,Value(self.infer(node.children[2],frame),None),line(node))
            frame.declare(name,Value(typ,None),line(node));return
        if k=='assignment':
            name=str(node.children[0]);old=frame.lookup(name,line(node));coerce(old.type,Value(self.infer(node.children[1],frame),None),line(node));return
        if k=='postfix':
            v=frame.lookup(str(node.children[0]),line(node))
            if v.type not in NUMERIC:raise JacarandaError('SDT','Increment requires numeric variable',line(node))
            return
        if k=='print_stmt':
            if node.children:
                for a in node.children[0].children:self.infer(a,frame)
            return
        if k=='call':self.infer(node,frame);return
        if k=='return_stmt':
            if rt is None:raise JacarandaError('SDT','return outside function',line(node))
            actual=self.infer(node.children[0],frame) if node.children else 'void'
            coerce(rt,Value(actual,None),line(node)) if rt!='void' else (None if actual=='void' else (_ for _ in ()).throw(JacarandaError('SDT','void function cannot return value',line(node))))
            return
        if k=='if_stmt':
            typ=self.infer(node.children[0],frame)
            if typ not in NUMERIC+('bool',):raise JacarandaError('SDT','Condition must be numeric or bool',line(node))
            self.stmt(node.children[1],Frame(frame),rt)
            if len(node.children)>2:self.stmt(node.children[2],Frame(frame),rt)
            return
        if k=='while_stmt':
            typ=self.infer(node.children[0],frame)
            if typ not in NUMERIC+('bool',):raise JacarandaError('SDT','Condition must be numeric or bool',line(node))
            self.stmt(node.children[1],Frame(frame),rt);return
        if k=='do_stmt':
            self.stmt(node.children[0],Frame(frame),rt)
            if self.infer(node.children[1],frame) not in NUMERIC+('bool',):raise JacarandaError('SDT','Condition must be numeric or bool',line(node))
            return
        if k=='for_stmt':
            local=Frame(frame)
            for c in node.children:
                if tname(c)=='for_condition':
                    if self.infer(c.children[0],local) not in NUMERIC+('bool',):raise JacarandaError('SDT','Condition must be numeric or bool',line(c))
                else:self.stmt(c,local,rt)
            return
        raise JacarandaError('SDT',f'Unsupported statement: {k}',line(node))

    def check(self):
        for n in self.tree.children:
            if tname(n)!='function':self.stmt(n,self.scope)
        for name,(rt,params,n) in self.functions.items():
            local=Frame(self.scope)
            for typ,pname in params:local.declare(pname,Value(typ,None),line(n))
            self.stmt(n.children[-1],local,rt,new_scope=False)
        return self.scope.vars
