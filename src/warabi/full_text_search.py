import sqlite3
from abc import abstractmethod
from typing import Protocol


class FullTextSearcher(Protocol):
    @abstractmethod
    def search(self, query: str) -> list[str]:
        """Search for documents matching the query

        Args:
            query: The search query string
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def index_document(self, document: str) -> None:
        """Index a new document."""
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        """Delete a document from the index."""
        raise NotImplementedError("Subclasses must implement this method")


class FullTextSearchSqlLit3(FullTextSearcher):
    def __init__(self, db_path: str = ":memory:"):
        self._path = db_path

        self._conn = sqlite3.connect(self._path)
        self._cursor = self._conn.cursor()
        self._cursor.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS articles USING fts5(
                title,
                body,
                content_wakati,
                tokenize = "unicode61 remove_diacritics 0"
            );
            """
        )
        self._conn.commit()

    def search(self, query: str) -> list[str]:
        self._cursor.execute(
            "SELECT title, body FROM articles WHERE content_wakati MATCH ?",
            (query,),
        )
        return [f"{row[0]}: {row[1]}" for row in self._cursor.fetchall()]

    def index_document(self, document: dict) -> None:
        from janome.tokenizer import Tokenizer

        tokenizer = Tokenizer()
        wakati_text = " ".join(
            token.surface for token in tokenizer.tokenize(document["body"])
        )
        self.c.execute(
            "INSERT INTO articles (title, body, content_wakati) VALUES (?, ?, ?)",
            (document["title"], document["body"], wakati_text),
        )
        self.conn.commit()

    def delete_document(self, document_id: str) -> None:
        self.c.execute("DELETE FROM articles WHERE rowid = ?", (document_id,))
        self.conn.commit()
