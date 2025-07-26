import os
import sqlite3
import unicodedata
import uuid
from abc import abstractmethod
from typing import Protocol

from .tokenizer import Tokenizer


class FullTextSearchEngine(Protocol):
    @abstractmethod
    def search(self, query: str) -> list[str]:
        """Search for documents matching the query.
        Args:
            query: The search query string.
        Returns:
            A list of tuples containing doc_id for each matching document.
        """
        raise NotImplementedError

    @abstractmethod
    def insert(self, doc: dict, doc_id: str) -> None:
        """Insert a document into the full-text search index.

        Args:
            doc: A dictionary representing the document to insert.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, doc_id: str) -> None:
        """Delete a document from the full-text search index.

        Args:
            doc_id: The ID of the document to delete.
        """
        raise NotImplementedError


class SqlLite3FullTextSearchEngine(FullTextSearchEngine):
    def __init__(
        self,
        tokenizer: Tokenizer,
        path: str | os.PathLike | None = None,
    ) -> None:
        self._tokenizer = tokenizer
        self._path = str(path) if path is not None else ":memory:"
        self._conn = sqlite3.connect(self._path)
        self._cursor = self._conn.cursor()

        self._cursor.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS texts USING fts5(
                text_id,
                doc_id,
                key,
                text,
                tokenize = "unicode61 remove_diacritics 0"
            );
            """
        )
        self._conn.commit()

    def search(self, query: str) -> list[str]:
        """Search for documents matching the query.
        Args:
            query: The search query string.
        Returns:
            A list of tuples containing text_id, doc_id, key,
            and text for each matching document.
        """
        self._cursor.execute(
            "SELECT text_id, doc_id, key, text FROM texts WHERE text MATCH ?",
            (self._tokenize(query),),
        )
        return [r[1] for r in self._cursor.fetchall()]

    def insert(self, doc: dict, doc_id: str) -> None:
        """Insert a document into the full-text search index.

        Args:
            doc: A dictionary representing the document to insert.
        """

        self._cursor.executemany(
            "INSERT INTO texts (text_id, doc_id, key, text)"
            "VALUES (:text_id, :doc_id, :key, :text)",
            tuple(
                {
                    "text_id": str(uuid.uuid4()),
                    "doc_id": doc_id,
                    "key": k,
                    "text": self._tokenize(v),
                }
                for k, v in _flatten_document(doc).items()
            ),
        )
        self._conn.commit()

    def delete(self, doc_id: str) -> None:
        """Delete a document from the full-text search index.
        Args:
            doc_id: The ID of the document to delete.
        """
        self._cursor.execute(
            "DELETE FROM texts WHERE doc_id = ?",
            (doc_id,),
        )
        self._conn.commit()

    def _tokenize(self, text: str) -> str:
        """Tokenize a given text using the configured tokenizer.

        This method normalizes the text to NFKC form and tokenizes it,
        returning a string of tokens joined by spaces.

        Args:
            text: The text to tokenize.
        Returns:
            A string of tokens joined by spaces.
        """
        return " ".join(
            [
                t
                for t in self._tokenizer.tokenize(
                    unicodedata.normalize("NFKC", text)
                )
            ]
        )


def _flatten_document(doc: dict) -> dict[str, str]:
    """Flatten a nested document dictionary

    This function flattens a nested dictionary into a single-level dictionary
    with keys in dot notation for nested structures.

    Args:
        doc: The dictionary to flatten.
    Returns:
        A flattened dictionary with keys in dot notation.
    """

    def _dfs(d, p):
        if isinstance(d, dict):
            for k, v in d.items():
                yield from _dfs(v, f"{p}.{k}")
        elif isinstance(d, list):
            for i, v in enumerate(d):
                yield from _dfs(v, f"{p}[{i}]")
        else:
            yield str(p), str(d)

    return dict(_dfs(doc, "@root"))
