from abc import abstractmethod
from typing import Protocol

from ..common import Document, DocumentId


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
    def insert(self, doc: Document, doc_id: DocumentId) -> None:
        """Insert a document into the full-text search index.

        Args:
            doc: A dictionary representing the document to insert.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, doc_id: DocumentId) -> None:
        """Delete a document from the full-text search index.

        Args:
            doc_id: The ID of the document to delete.
        """
        raise NotImplementedError
