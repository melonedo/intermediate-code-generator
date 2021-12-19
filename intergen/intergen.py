from typing import ValuesView
from lark import Lark, Transformer, v_args
import csv
import json
from lark.exceptions import ParseError

from lark.load_grammar import Grammar

"简化版，只包含生成代码的语法。非常不完全，自行添加需要的语法。"
pl0_grammar3 = """
    start: stmt
    
    ?stmt: s | open_stmt

    s:  "if"i b_expr "then"i m s n "else"i m s   -> s_if_else
        | a                                      -> s_a
        | "{" l "}"                              -> s_brackets
        | "while"i m b_expr "do"i m s            -> s_while
        | "call"i id "(" e_list ")"              -> s_call
        | label s                                -> s_label_s
        | "goto"i id                             -> s_goto

    open_stmt: "if"i b_expr "then"i m stmt               -> s_if
        | "if"i b_expr "then"i m s n "else"i m open_stmt -> s_if_else_open

    a:  id ":=" expression
    
    expression: negative                    -> expression_num
        | expression "+" term               -> expression_add

    negative: term                          -> expression_num 
        | "-" term                          -> expression_negative     

    term: factor                            -> expression_num
        | term "*" factor                   -> expression_mutiply

    factor: id                              -> expression_id
        | "(" expression ")"                -> expression_brackets

    label: id ":"                           -> s_label

    m:

    n:

    b_expr: b_and                    -> bool_trans
        | b_expr "or"i m b_and       -> bool_or

    b_and: b_not                     -> bool_trans
        | b_and "and"i m b_not       -> bool_and

    b_not: b_comparison              -> bool_trans
        | "not"i b_not               -> bool_not

    b_comparison: expression relop expression  -> bool_expression_relop_expression
        | expression                           -> bool_expression
        | "(" b_expr ")"                       -> bool_trans

    l:  l ";" m s                              -> s_semicolon
        | s                                    -> s_semicolon_s
        
    e_list: expression                   -> call_init     
        | e_list "," expression          -> call_add

    id: CNAME
    !relop: "="|"<>"|"<"|"<="|">"|">="

    %import common.CNAME
    %import common.WS
    %ignore WS
"""

class struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class GrammarError(Exception):
    pass

class ParsingError(Exception):
    pass

@v_args(inline=True)
class Pl0Tree(Transformer):
    symbol_table: dict
    symbol_counter: int
    next_quad: int
    codes: list

    def __init__(self):
        self.symbol_table = {}
        self.symbol_counter = -1
        self.next_quad = 0
        self.codes = []

    def lookup(self, id, **kwargs):
        if id not in self.symbol_table:
            s = struct(**kwargs)
            self.symbol_table[id] = s
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
        self.symbol_counter += 1
        return f"temp{self.symbol_counter}"

    def start(self, s):
        self.backpatch(s.nextlist, self.next_quad)
        return self.codes

    def id(self, s):
        i = struct()
        i.name = s
        return i

    def a(self, id, E):
        p = self.lookup(id.name, type="variable", place=id.name)
        if p is not None:
            self.emit(f"{p.place} := {E.place}")
        else:
            raise GrammarError()

    def expression_id(self, id):
        e = struct()
        p = self.lookup(id.name, type="variable", place=id.name)
        if p is not None:
            e.place = p.place
            return e
        else:
            raise GrammarError()
    
    def relop(self, r):
        e = struct()
        e.op = r
        return e

    def bool_or(self, b1, m, b2):
        b = struct()
        self.backpatch(b1.falselist, m.quad)
        b.truelist = self.merge(b1.truelist, b2.truelist)
        b.falselist = b2.falselist
        return b
    
    def bool_and(self, b1, m, b2):
        b = struct()
        self.backpatch(b1.truelist, m.quad)
        b.truelist = b2.truelist
        b.falselist = self.merge(b1.falselist, b2.falselist)    
        return b
    
    def bool_not(self, b1):
        b = struct()
        b.truelist = b1.falselist
        b.falselist = b1.truelist
        return b
    
    def bool_trans(self, b1):
        b = struct()
        b.truelist = b1.truelist
        b.falselist = b1.falselist
        return b

    def bool_expression_relop_expression(self, e1, r, e2):
        b = struct()
        b.truelist = self.makelist(self.next_quad)
        b.falselist = self.makelist(self.next_quad + 1)
        self.emit(f"j{r.op}, {e1.place}, {e2.place}, 0")
        self.emit(f"j, -, -, 0")
        return b
    
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

    def s_label(self, id):
        if id.name in self.symbol_table:
            entry = self.symbol_table[id.name]
            if entry.type != "label" or entry.defined:
                raise GrammarError()
            else:
                entry.defined = True
                self.backpatch(entry.quad_list, self.next_quad)
        else:
            entry = struct(type="label", defined=True, place=self.next_quad)
            self.symbol_table[id.name] = entry
    
    def s_goto(self, id):
        if id.name in self.symbol_table:
            entry = self.symbol_table[id.name]
            if entry.type == "label":
                if entry.defined:
                    self.emit(f"j, -, -, {entry.place}")
                else:
                    entry.quad_list.append(self.next_quad)
                    self.emit("j, -, -, 0")
            else:
                raise GrammarError()
        else:
            quad_list = self.makelist(self.next_quad)
            entry = struct(type="label", defined=False, quad_list=quad_list)
            self.symbol_table[id.name] = entry
            self.emit("j, -, -, 0")

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
    
    def expression_add(self,e1,e2):
        e = struct()
        e.place = self.newtemp()
        self.emit(f"{e.place} := {e1.place} + {e2.place}")
        return e
    
    def expression_negative(self,e1):
        e = struct()
        e.place = self.newtemp()
        self.emit(f"{e.place} := uminus {e1.place}")
        return e

    def expression_brackets(self,e1):
        e = struct()
        e.place = e1.place
        return e

    def expression_num(self,num):
        e = struct()
        e.place = num.place
        return e

    def expression_mutiply(self,e1,factor):
        e = struct()
        e.place = self.newtemp()
        self.emit(f"{e.place} := {e1.place} * {factor.place}")
        return e

    def s_label_s(self,id,s):
        return s

    def s_brackets(self, s):
        return s

    def s_semicolon(self,l,m,s):
        self.backpatch(l.nextlist,m.quad)
        l.nextlist = s.nextlist
        return l

    def s_semicolon_s(self,s):
        l = struct()
        l.nextlist = s.nextlist
        return l

    def s_while(self, m1, b, m2, s1):
        s = struct()
        self.backpatch(s1.nextlist, m1.quad)
        self.backpatch(b.truelist, m2.quad)
        s.nextlist = b.falselist
        self.emit(f"j, -, -, {m1.quad}")
        return s

    def s_call(self, id, e_list):
        s = struct()
        for p in e_list:
            self.emit(f"param {p}")
        self.emit(f"call {id.name}")
        s.nextlist = []
        return s

    def call_add(self, e_list, e):
        e_list.append(e.place)
        return e_list

    def call_init(self, e):
        e_list = [e.place]
        return e_list

def get_parser(transform=True):
    transformer = Pl0Tree() if transform else None
    # pl0_parser = Lark(pl0_grammar3, parser='lalr', transformer=transformer)
    pl0_parser = PL0Parser()
    parser = pl0_parser.parse
    return parser


parsing_table = []
with open('parsing-table.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        parsing_table.append(row)

with open('productions.json') as f:
    productions = json.load(f)

terminals = frozenset(["'('", "')'", "'*'", "'+'", "','", "'-'", "':'", "':='", "';'", "'<'", "'<='", "'<>'", "'='", "'>'", "'>='", "'and'", "'call'", "'do'", "'else'", "'goto'", "'if'", "'not'", "'or'", "'then'", "'while'", "'{'", "'}'"])

terminals_to_keep = frozenset(["'<'", "'<='", "'<>'", "'='", "'>'", "'>='"])

terminals_to_drop = terminals - terminals_to_keep

def keep_terminal(t):
    return not (isinstance(t, str) and f"'{t}'" in terminals_to_drop)

def classify(tok):
    quoted = f"'{tok}'"
    if quoted in terminals:
        return quoted, tok
    else:
        return "CNAME", tok

def lex(code):
    lexemes = code.split()
    tokens = list(map(classify, lexemes))
    tokens.append(("$end", ""))
    return tokens

class PL0Parser(Pl0Tree):
    def parse(self, code):
        tokens = lex(code)
        ind = 0
        stack = [0]
        value_stack = []
        while True:
            a = tokens[ind]
            ttype, tvalue = a
            s = stack[-1]
            action = parsing_table[s].get(ttype, "")
            if action.startswith('s'):
                t = int(action[1:])
                stack.append(t)
                value_stack.append(tvalue)
                ind += 1
            elif action.startswith('r'):
                i = int(action[1:])
                rule_name, rule_len, action_name = productions[i]
                del stack[len(stack)-rule_len:]
                t = stack[-1]
                goto = int(parsing_table[t][rule_name])
                stack.append(goto)
                action = getattr(self, action_name, None)
                if action is None:
                    assert rule_len == 1
                    svalue = value_stack[-1]
                else:
                    args = [v for v in value_stack[len(value_stack)-rule_len:] if keep_terminal(v)]
                    svalue = action(*args)
                del value_stack[len(value_stack)-rule_len:]
                value_stack.append(svalue)
            elif action == "a":
                assert len(value_stack) == 1
                return value_stack[0]
            else:
                raise ParseError()
