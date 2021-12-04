from intergen.calculator import calc
from intergen.intergen import get_parser, get_tree_parser

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


def test_pl0_to_tree():
    code = "x := 1"
    tree_parser = get_tree_parser()
    tree = tree_parser(code)
    assert tree == ('S', ('A', ('id', 'x'), ('num', '1')))