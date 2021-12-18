import sys
sys.path.append('.')
from intergen.calculator import calc
from intergen.intergen import get_parser

def test_calc():
    assert calc("a = 1+2") == 3
    assert calc("1+a*-3") == -8

def test_pl0():
    code = """
        if x > 0 then A := x + d
        else B := c
    """
    parse = get_parser()
    parse(code)