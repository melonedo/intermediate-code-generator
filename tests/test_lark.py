import sys
sys.path.append('.')
from intergen.calculator import calc
from intergen.intergen import get_parser

def test_calc():
    assert calc("a = 1+2") == 3
    assert calc("1+a*-3") == -8

def test_pl0():
    code = """
        if x > e then { A := x + d ; C := x }
        else B := c
    """
    parse = get_parser(False)
    result = parse(code)
    print(result.pretty())
