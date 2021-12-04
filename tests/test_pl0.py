from intergen.intergen import reduce, get_parser, get_tree_parser
import pytest

@pytest.fixture
def parser():
    return get_parser()

@pytest.fixture
def to_tree():
    return get_tree_parser()


def test_assign(to_tree):
    code = "a := b"
    tree = to_tree(code)
    result = reduce(tree)
    assert result == ['a := b']

@pytest.mark.xfail
def test_expression(to_tree):
    "来自讲义随堂练习"
    code = "a := b * (-c+d)"
    result = reduce(to_tree(code))
    assert result == ['temp_1 := -c', 'temp2 := temp_1 + d', 'temp_3 := b * temp_2', 'a := temp3']
