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
    parse = get_parser(False)
    parse(code)
    
