from intergen.intergen import get_parser
import pytest

@pytest.fixture
def parser():
    return get_parser()

def test_assign(parser):
    "最简单的assign"
    code = "a := b"
    result = parser(code)
    assert len(result) == 1
    assert result[0] == 'a := b'

def test_expression(parser):
    "来自讲义随堂练习"
    code = "a := b * (-c+d)"
    result = parser(code)
    assert result == ['temp0 := uminus c', 'temp1 := temp0 + d', 'temp2 := b * temp1', 'a := temp2']

def test_expression2(parser):
    code = "e := - ( a + b ) * ( c + d ) + ( a + b + c )"
    result = parser(code)
    assert result == ['temp0 := a + b', 'temp1 := c + d', 'temp2 := temp0 * temp1', 'temp3 := uminus temp2', 'temp4 := a + b', 'temp5 := temp4 + c', 'temp6 := temp3 + temp5', 'e := temp6']

def test_expression3(parser):
    "测试优先级"
    code = "e := - a + b * c + d"
    result = parser(code)
    assert result == ['temp0 := uminus a', 'temp1 := b * c', 'temp2 := temp0 + temp1', 'temp3 := temp2 + d', 'e := temp3']

def test_if_then(parser):
    code = "if a then b := c"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 3', 'b := c']

def test_if_else(parser):
    code = "if a then b := c else b := d"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 4', 'b := c', 'j, -, -, 5', 'b := d']

def test_nested_if(parser):
    code = "if a then if b then c := d"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 5', 'jnz, b, -, 4', 'j, -, -, 5', 'c := d']

def test_nested_if_else(parser):
    code = "if a then if b then c := d else e := f"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 7', 'jnz, b, -, 4', 'j, -, -, 6', 'c := d', 'j, -, -, 7', 'e := f']

def test_nested_if_else2(parser):
    code = "if a then if b then c := d else e := f else g := h"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 8', 'jnz, b, -, 4', 'j, -, -, 6', 'c := d', 'j, -, -, 9', 'e := f', 'j, -, -, 9', 'g := h']

def test_expression1(parser):
    code = "a := i + j"
    result = parser(code)
    assert result == ['temp0 := i + j', 'a := temp0']
