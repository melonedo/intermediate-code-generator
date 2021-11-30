from intergen.intergen import get_parser
import pytest

@pytest.fixture
def parser():
    return get_parser()

def test_assign(parser):
    code = "a := b"
    result = parser(code)
    assert len(result) == 1
    assert result[0] == 'a := b'

def test_expression(parser):
    "来自讲义随堂练习"
    code = "a := b * (-c+d)"
    result = parser(code)
    assert result == ['temp_1 := -c', 'temp2 := temp_1 + d', 'temp_3 := b * temp_2', 'a := temp3']
