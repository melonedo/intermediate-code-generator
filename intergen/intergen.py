from lark import Lark, Transformer, v_args


"简化版，只包含生成代码的语法。非常不完全，自行添加需要的语法。"
pl0_grammar3 = """
    start: stmt
    
    ?stmt: s | open_stmt

    s:  "if"i b "then"i m s n "else"i m s   -> s_if_else
        | a                                 -> s_a
        | "{" l "}"

    open_stmt: "if"i b "then"i m stmt               -> s_if
        | "if"i b "then"i m s n "else"i m open_stmt -> s_if_else_open

    a:  id ":=" expression

    expression: [ "+"|"-"] term ( ("+"|"-") term)*

    term: factor (("*"|"/") factor)*

    factor: id                  -> factor1
        | num
        | "(" expression ")"

    m:

    n:

    b:  b "and"i m b
        | expression relop expression
        | "(" b ")"
        | expression            -> bool_expression

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
            # self.symbol_counter += 1
        return self.symbol_table[id]

    def emit(self, code):
        self.next_quad += 1
        self.codes.append(code)

    def makelist(self, *args):
        return [*args]
    
    def merge(self, l1, l2):
        return [*l1, *l2]

    def backpatch(self, truelist, quad):
        for i in truelist:
            old_code = self.codes[i]
            new_code = old_code[:-1] + str(quad)
            self.codes[i] = new_code
    
    def newtemp(self):
        return f"temp{self.symbol_counter}"

    def start(self, s):
        # 由于某些代码还没有nextlist，先不启用
        self.backpatch(s.nextlist, self.next_quad)
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
    def term(self, factors):
        "只处理了含有一个项的情况"
        return factors[0]

    @v_args(inline=False)
    def expression(self, terms):
        "只处理了含有一个项的情况"
        return terms[0]
    
    def bool_expression(self, i):
        b = struct()
        b.truelist = self.makelist(self.next_quad)
        b.falselist = self.makelist(self.next_quad + 1)
        self.emit(f"jnz, {i.place}, -, 0")
        self.emit(f"j, -, -, 0")
        return b

    def s_if(self, b, m, s1):
        s = struct()
        self.backpatch(b.truelist, m.quad)
        s.nextlist = self.merge(b.falselist, s1.nextlist)
        return s
    
    def s_if_else(self, b, m1, s1, n, m2, s2):
        s = struct()
        self.backpatch(b.truelist, m1.quad)
        self.backpatch(b.falselist, m2.quad)
        s.nextlist = self.merge(s1.nextlist, self.merge(s2.nextlist, n.nextlist))
        return s

    def s_a(self, a):
        s = struct()
        s.nextlist = self.makelist()
        return s

    def m(self):
        m = struct()
        m.quad = self.next_quad
        return m
    
    def n(self):
        n = struct()
        n.nextlist = self.makelist(self.next_quad)
        self.emit(f"j, -, -, 0")
        return n


def get_parser(transform=True):
    transformer = Pl0Tree() if transform else None
    pl0_parser = Lark(pl0_grammar3, parser='lalr', transformer=transformer)
    parser = pl0_parser.parse
    return parser


