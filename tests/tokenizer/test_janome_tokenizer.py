import pytest

from warabi.tokenizer.janome_tokenizer import JanomeTokenizer


@pytest.fixture
def tokenizer() -> JanomeTokenizer:
    """Fixture for the Janome tokenizer."""
    return JanomeTokenizer()


def test_tokenize(tokenizer: JanomeTokenizer):
    """Test the Janome tokenizer with a sample text."""
    # given
    text = "これはテストです。"

    # when
    tokens = list(tokenizer.tokenize(text))

    # then
    assert isinstance(tokens, list)
    assert all(isinstance(token, str) for token in tokens)

    assert tokens == ["これ", "は", "テスト", "です", "。"]


def test_tokenize_empty(tokenizer: JanomeTokenizer):
    """Test the Janome tokenizer with an empty string."""
    # given
    text = ""

    # when
    tokens = list(tokenizer.tokenize(text))

    # then
    assert tokens == []


def test_tokenize_whitespace(tokenizer: JanomeTokenizer):
    """Test the Janome tokenizer with a string containing only whitespace."""
    # given
    text = "   "

    # when
    tokens = list(tokenizer.tokenize(text))

    # then
    assert tokens == []
