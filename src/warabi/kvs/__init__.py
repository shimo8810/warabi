from typing import Protocol

from ..common import Document, DocumentId


class KVStore(Protocol):
    """A protocol for key-value store operations."""

    def insert(self, doc: Document, doc_id: DocumentId) -> None:
        """Insert a document into the store

        Args:
            doc: A dictionary representing the document to insert
            doc_id: The ID of the document
        """
        raise NotImplementedError

    def get(self, doc_id: DocumentId) -> Document | None:
        """Get the value associated with the given document ID

        Args:
            doc_id: The ID of the document to retrieve
        Returns:
            A dictionary representing the document, or None if not found
        """
        raise NotImplementedError

    def update(self, doc: Document, doc_id: DocumentId) -> None:
        """Update an existing document in the store

        Args:
            doc: A dictionary representing the updated document
            doc_id: The ID of the document to update
        """
        raise NotImplementedError

    def delete(self, doc_id: DocumentId) -> None:
        """Delete the document with the given ID

        Args:
            doc_id: The ID of the document to delete
        """
        raise NotImplementedError
