from collections.abc import Generator

import sudachipy.dictionary
import sudachipy.tokenizer

from ..tokenizer import Tokenizer


class SudachiTokenizer(Tokenizer):
    def __init__(self):
        """Initialize the Sudachi tokenizer."""
        self._tokenizer = sudachipy.dictionary.Dictionary().create()
        self._mode = sudachipy.tokenizer.Tokenizer.SplitMode.C

    def tokenize(self, text: str) -> Generator[str]:
        """Tokenize a given text into tokens.

        Args:
            text: The text to tokenize.

        Returns:
            A generator of tokens.
        """
        for t in self._tokenizer.tokenize(text, self._mode):
            yield t.surface()
