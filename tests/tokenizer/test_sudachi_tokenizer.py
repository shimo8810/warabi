import pytest

from warabi.tokenizer.sudachi_tokenizer import SudachiTokenizer


@pytest.fixture
def tokenizer() -> SudachiTokenizer:
    """Fixture for the Sudachi tokenizer."""
    return SudachiTokenizer()


def test_tokenize(tokenizer: SudachiTokenizer):
    """Test the Sudachi tokenizer with a sample text."""
    # given
    text = "これはテストです。"

    # when
    tokens = list(tokenizer.tokenize(text))

    # then
    assert isinstance(tokens, list)
    assert all(isinstance(token, str) for token in tokens)

    assert tokens == ["これ", "は", "テスト", "です", "。"]


def test_tokenize_empty(tokenizer: SudachiTokenizer):
    """Test the Sudachi tokenizer with an empty string."""
    # given
    text = ""

    # when
    tokens = list(tokenizer.tokenize(text))

    # then
    assert tokens == []


def test_tokenize_whitespace(tokenizer: SudachiTokenizer):
    """Test the Sudachi tokenizer with a string containing only whitespace."""
    # given
    text = "   "

    # when
    tokens = list(tokenizer.tokenize(text))

    # then
    assert tokens == []
