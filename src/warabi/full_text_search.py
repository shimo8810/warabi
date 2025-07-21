from abc import abstractmethod
from typing import Protocol


class FullTextSearcher(Protocol):
    @abstractmethod
    def search(self, query: str) -> list[str]:
        """Search for documents matching the query."""
        pass

    @abstractmethod
    def index_document(self, document: str) -> None:
        """Index a new document."""
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        """Delete a document from the index."""
        pass
