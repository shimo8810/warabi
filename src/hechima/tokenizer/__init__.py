from abc import abstractmethod
from collections.abc import Generator
from typing import Protocol


class Tokenizer(Protocol):
    @abstractmethod
    def tokenize(self, text: str) -> Generator[str]:
        """Tokenize a given text into tokens.

        Args:
            text: The text to tokenize.

        Returns:
            A generator of tokens.
        """
        raise NotImplementedError(
            "This method should be overridden by subclasses."
        )
