import os

from tinydb import Query, TinyDB
from tinydb.storages import MemoryStorage

from ..common import Document, DocumentId
from . import KVStore


class TinyDbKVStore(KVStore):
    def __init__(
        self,
        path: str | os.PathLike | None = None,
    ):
        """Initialize TinyDbKVStore.

        Args:
            path: The file path to the TinyDB database.
                   If None, uses in-memory storage.
        """
        if path is None:
            self._db = TinyDB(storage=MemoryStorage)
        else:
            self._db = TinyDB(path)

    def insert(self, doc: Document, doc_id: DocumentId) -> None:
        """Insert a document into the store.

        Args:
            doc: A dictionary representing the document to insert.
            doc_id: The ID of the document.
        """
        self._db.insert({"doc_id": str(doc_id), "document": doc})

    def get(self, doc_id: DocumentId) -> Document | None:
        """Get the value associated with the given document ID.

        Args:
            doc_id: The ID of the document to retrieve.
        Returns:
            A dictionary representing the document, or None if not found.
        """
        result = self._db.search(Query().doc_id == str(doc_id))
        return result[0]["document"] if result else None

    def update(self, doc: Document, doc_id: DocumentId) -> None:
        """Update an existing document in the store.

        Args:
            doc: A dictionary representing the updated document.
            doc_id: The ID of the document to update.
        """
        self._db.update({"document": doc}, Query().doc_id == str(doc_id))

    def delete(self, doc_id: DocumentId) -> None:
        """Delete the document with the given ID.

        Args:
            doc_id: The ID of the document to delete.
        """
        self._db.remove(Query().doc_id == str(doc_id))
