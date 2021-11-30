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
