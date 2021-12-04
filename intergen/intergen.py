from lark import Lark, Transformer, v_args


"简化版，只包含生成代码的语法。非常不完全，自行添加需要的语法。"
pl0_grammar3 = """
    start: s

    s:  "if"i b "then"i m s n "else"i m s
        | a                                 -> s1
        | "{" l "}"

    a:  id ":=" expression

    expression: term            -> expression1
        | expression "+" term   -> expression2

    term: factor                -> term1
        | term "*" factor       -> term2

    factor: id                  -> factor1
        | num                   -> factor2
        | "(" expression ")"    -> factor3

    m:

    n:

    b:  b "and"i m b
        | expression relop expression
        | "(" b ")"

    l:  l ";" m s
        | s

    id: CNAME
    num: INT
    relop: "="|"#"|"<"|"<="|">"|">="

    %import common.CNAME
    %import common.INT
    %import common.WS
    %ignore WS
"""

class struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class GrammarError(Exception):
    pass


@v_args(inline=True)
class Pl0Tree(Transformer):
    symbol_table: dict
    symbol_counter: int
    next_quad: int
    codes: list

    def __init__(self):
        self.symbol_table = {}
        self.symbol_counter = 0
        self.next_quad = 0
        self.codes = []

    def lookup(self, id):
        if id not in self.symbol_table:
            self.symbol_table[id] = id
            self.symbol_counter += 1
        return self.symbol_table[id]

    def emit(self, code):
        self.next_quad += 1
        self.codes.append(code)

    def start(self, _):
        return self.codes

    def id(self, s):
        i = struct()
        i.name = s
        return i

    def a(self, id, E):
        p = self.lookup(id.name)
        if p is not None:
            self.emit(f"{p} := {E.place}")
        else:
            raise GrammarError()

    def factor1(self, id):
        e = struct()
        p = self.lookup(id.name)
        if p is not None:
            e.place = p
            return e
        else:
            raise GrammarError()

    @v_args(inline=False)
    def term1(self, factors):
        "只处理了含有一个项的情况"
        return factors[0]

    @v_args(inline=False)
    def expression1(self, terms):
        "只处理了含有一个项的情况"
        return terms[0]

@v_args(inline=True)
class Pl0ToTree(Transformer):
    "把pl/0LR解析出的语法转换为语法树"

    def start(self, s):
        return s

    def id(self, i):
        return "id", str(i)
    
    def num(self, i):
        return "num", str(i)

    def s1(self, a):
        return "S", a

    def a(self, l, r):
        return "A", l, r

    def expression1(self, t):
        return t

    def term1(self, f):
        return f

    def factor(self, i):
        return "E", i

    def expression2(self, t1, t2):
        return "E", t1, "+", t2

class InterGen(object):
    def __init__(self):
        self.cache = {}

        self.symbol_table = {}
        self.symbol_counter = 0
        self.next_quad = 0
        self.codes = []
    
    def traverse(self, node):
        if not isinstance(node, tuple):
            return node
        head = node[0]
        meth = self.cache.get(head, None)

        # 尽早报错
        if meth == None:
            meth = getattr(self, head, None)
            if meth == None:
                raise GrammarError()
            self.cache[head] = meth
        
        body = [self.traverse(n) for n in node[1:]]
        return meth(*body)
    
    def lookup(self, id):
        if id not in self.symbol_table:
            self.symbol_table[id] = id
            self.symbol_counter += 1
        return self.symbol_table[id]

    def emit(self, code):
        self.next_quad += 1
        self.codes.append(code)

    def S(self, s):
        return s
    
    def A(self, id, E):
        p = self.lookup(id.name)
        if p is not None:
            self.emit(f"{p} := {E.place}")
        else:
            raise GrammarError()
    
    def E(self, *args):
        if len(args) == 1:
            arg = args[0]
            if arg[0] == "id":
                e = struct()
                p = self.lookup(id.name)
                if p is not None:
                    e.place = p
                    return e
                else:
                    raise GrammarError()

    def id(self, s):
        i = struct()
        i.name = s
        return i
    
    def num(self, n):
        return n

def get_parser(transform=True):
    transformer = Pl0Tree() if transform else None
    pl0_parser = Lark(pl0_grammar3, parser='lalr', transformer=transformer)
    parser = pl0_parser.parse
    return parser

def get_tree_parser():
    return Lark(pl0_grammar3, parser='lalr', transformer=Pl0ToTree()).parse

def reduce(code):
    gen = InterGen()
    gen.traverse(code)
    return gen.codes