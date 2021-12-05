import sys
sys.path.append('.')
from intergen.calculator import calc
from intergen.intergen import get_parser

def test_calc():
    assert calc("a = 1+2") == 3
    assert calc("1+a*-3") == -8

def test_pl0():
    code = """
    {
        x := x + 1;
        if x > 0 then A := x + 1
        else B := 2
    }
    """
    parse = get_parser()
    parse(code)

from intergen.intergen import Pl0Tree, Lark, pl0_grammar3
transformer = Pl0Tree()
pl0_parser = Lark(pl0_grammar3, parser='lalr', transformer=transformer)
def get_name(c):
    try:
        if hasattr(c, '__name__'):
            return c.__name__
        else:
            return c.node_builder.__name__
    except Exception:
        # return str(c)
        return None
cs = [get_name(c) for c in pl0_parser._callbacks.values()]
c = cs[0]
print(cs)
test_pl0()