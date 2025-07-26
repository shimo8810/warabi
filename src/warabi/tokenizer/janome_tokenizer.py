from collections.abc import Generator

import janome.tokenizer

from . import Tokenizer


class JanomeTokenizer(Tokenizer):
    def __init__(self):
        """Initialize the Janome tokenizer."""
        self._tokenizer = janome.tokenizer.Tokenizer()

    def tokenize(self, text: str) -> Generator[str]:
        """Tokenize a given text into tokens.

        Args:
            text: The text to tokenize.

        Returns:
            A generator of tokens.
        """
        for t in self._tokenizer.tokenize(
            text,
            wakati=True,
        ):
            if token := str(t).strip():
                yield token
