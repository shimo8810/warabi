import os
import sqlite3
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Iterator, NoReturn, Protocol, Union

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from .tokenizer.janome_tokenizer import JanomeTokenizer


class WarabiDB:
    """"""

    def __init__(
        self,
        path: str | os.PathLike | None = None,
    ):
        """Initialize WarabiDB.

        Args:
            path: Path to the database file. If None, uses in-memory storage.
        """
        # Initialize TinyDB for document storage
        if path is None:
            self._tinydb = TinyDB(storage=MemoryStorage)
        else:
            self._tinydb = TinyDB(path)

        # Initialize SQLite FTS for search index
        self._fts_conn = sqlite3.connect(":memory:")
        self._fts_cursor = self._fts_conn.cursor()
        self._fts_cursor.execute(
            """
            CREATE VIRTUAL TABLE fts_index USING fts5(
                text_id INTEGER PRIMARY KEY,
                doc_id,
                key,
                text,
                tokenize = "unicode61 remove_diacritics 0"
            );
            """
        )
        self._fts_conn.commit()

        # Initialize tokenizer
        self._tokenizer = JanomeTokenizer()

    def insert(self, document: dict) -> int:
        """Insert a document into the database.

        Args:
            document: Dictionary containing document data.
                     Must contain at least 'content' field for full-text search.

        Returns:
            Document ID assigned by TinyDB.
        """
        # Insert document into TinyDB
        doc_id = self._tinydb.insert(document)

        # Index content for full-text search if available
        if "content" in document:
            self._index_document(doc_id, document["content"])

        return doc_id

    def all(self) -> list[dict]:
        """Get all documents from the database.

        Returns:
            List of all documents in the database.
        """
        return self._tinydb.all()

    def __iter__(self) -> Iterator[dict]:
        """Iterate over all documents in the database."""
        for doc in self._tinydb:
            yield doc

    def search(self, query: str) -> list[dict]:
        """Search for documents matching the query.

        Args:
            query: Search query string in Japanese.

        Returns:
            List of documents matching the search query.
        """
        # Tokenize query for better search results
        tokens = list(self._tokenizer.tokenize(query))
        search_query = " ".join(tokens)

        # Search in FTS index
        self._fts_cursor.execute(
            "SELECT doc_id FROM fts_index WHERE content MATCH ?",
            (search_query,),
        )

        # Get document IDs from search results
        doc_ids = [row[0] for row in self._fts_cursor.fetchall()]

        # Retrieve full documents from TinyDB
        results = []
        for doc_id in doc_ids:
            doc = self._tinydb.get(doc_id=doc_id)
            if doc:
                results.append(doc)

        return results

    def remove(self, doc_id: int) -> bool:
        """Remove a document by its ID.

        Args:
            doc_id: Document ID to remove.

        Returns:
            True if document was removed, False if not found.
        """
        # Remove from TinyDB
        removed_docs = self._tinydb.remove(doc_ids=[doc_id])

        if removed_docs:
            # Remove from FTS index
            self._fts_cursor.execute(
                "DELETE FROM fts_index WHERE doc_id = ?",
                (doc_id,),
            )
            self._fts_conn.commit()
            return True

        return False

    def truncate(self) -> None:
        """Remove all documents from the database."""
        self._tinydb.truncate()
        self._fts_cursor.execute("DELETE FROM fts_index")
        self._fts_conn.commit()

    def update(self, doc_id: int, document: dict) -> bool:
        """Update a document by its ID.

        Args:
            doc_id: Document ID to update.
            document: New document data.

        Returns:
            True if document was updated, False if not found.
        """
        # Update in TinyDB
        updated = self._tinydb.update(document, doc_ids=[doc_id])

        if updated:
            # Update FTS index if content changed
            if "content" in document:
                # Remove old index entry
                self._fts_cursor.execute(
                    "DELETE FROM fts_index WHERE doc_id = ?",
                    (doc_id,),
                )
                # Add new index entry
                self._index_document(doc_id, document["content"])

            return True

        return False
