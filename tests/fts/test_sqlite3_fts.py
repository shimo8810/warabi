from pathlib import Path

import pytest

from warabi.common import Document, DocumentId
from warabi.fts.sqlite3_fts import (
    SqlLite3FullTextSearchEngine,
    _flatten_document,
)
from warabi.tokenizer import Tokenizer


class MockTokenizer(Tokenizer):
    def tokenize(self, text: str) -> list[str]:
        return text.split()


@pytest.fixture
def tokenizer() -> MockTokenizer:
    return MockTokenizer()


@pytest.fixture
def in_memory_fts_engine(tokenizer: Tokenizer) -> SqlLite3FullTextSearchEngine:
    """Provides an in-memory FTS engine for testing."""
    return SqlLite3FullTextSearchEngine(tokenizer)


@pytest.fixture
def file_fts_engine(
    tokenizer: Tokenizer,
    tmp_path: Path,
) -> SqlLite3FullTextSearchEngine:
    """Provides a file-based FTS engine for testing."""
    return SqlLite3FullTextSearchEngine(tokenizer, tmp_path / "test.db")


@pytest.fixture(params=["in_memory", "file"])
def fts_engine(
    request,
    in_memory_fts_engine,
    file_fts_engine,
) -> SqlLite3FullTextSearchEngine:
    """Parametrized fixture to test both in-memory and file-based engines."""
    if request.param == "in_memory":
        return in_memory_fts_engine
    return file_fts_engine


def test_flatten_simple_dict():
    """Test flattening a simple dictionary."""
    # given
    doc = Document(
        {"title": "hello world", "body": "this is a test"},
    )
    expected = Document(
        {
            "@root.title": "hello world",
            "@root.body": "this is a test",
        }
    )

    # when
    flattened_doc = _flatten_document(doc)

    # then
    assert flattened_doc == expected


def test_flatten_nested_dict():
    """Test flattening a nested dictionary."""
    # given
    doc = Document(
        {"a": {"b": {"c": "value"}}},
    )
    expected = Document(
        {"@root.a.b.c": "value"},
    )

    # when
    flattened_doc = _flatten_document(doc)

    # then
    assert flattened_doc == expected


def test_flatten_with_list():
    """Test flattening a dictionary with a list of simple values."""
    # given
    doc = Document({"tags": ["python", "search"]})
    expected = Document(
        {"@root.tags[0]": "python", "@root.tags[1]": "search"},
    )

    # when
    flattened_doc = _flatten_document(doc)

    # then
    assert flattened_doc == expected


def test_flatten_with_list_of_dicts():
    """Test flattening a dictionary with a list of dictionaries."""
    # given
    doc = Document({"items": [{"name": "item1"}, {"name": "item2"}]})
    expected = Document(
        {
            "@root.items[0].name": "item1",
            "@root.items[1].name": "item2",
        }
    )

    # when
    flattened_doc = _flatten_document(doc)

    # then
    assert flattened_doc == expected


def test_flatten_mixed_types():
    """Test flattening a dictionary with mixed data types."""
    # given
    doc = Document(
        {
            "title": "My Document",
            "author": {"name": "John Doe"},
            "tags": ["tech", 123, True],
        }
    )
    expected = Document(
        {
            "@root.title": "My Document",
            "@root.author.name": "John Doe",
            "@root.tags[0]": "tech",
            "@root.tags[1]": "123",
            "@root.tags[2]": "True",
        }
    )

    # when
    flattened_doc = _flatten_document(doc)

    # then
    assert flattened_doc == expected


def test_flatten_empty_dict():
    """Test flattening an empty dictionary results in an empty one."""
    # given
    doc = Document({})

    # when
    flattened_doc = _flatten_document(doc)

    # then
    assert flattened_doc == Document({})


def test_insert_and_search(fts_engine: SqlLite3FullTextSearchEngine):
    """Test inserting documents and searching for them."""
    # given
    doc1 = Document({"content": "this is a test document"})
    doc2 = Document({"content": "another document for testing"})
    doc3 = Document({"title": "complex", "body": "this is a complex test"})

    # when
    fts_engine.insert(doc1, DocumentId("doc1"))
    fts_engine.insert(doc2, DocumentId("doc2"))
    fts_engine.insert(doc3, DocumentId("doc3"))

    # then
    # Search for a word in multiple documents
    results_doc = fts_engine.search("document")
    assert set(results_doc) == {"doc1", "doc2"}

    # Search for a word in a specific field (implicitly)
    results_complex = fts_engine.search("complex")
    assert set(results_complex) == {"doc3"}

    # Search for a word that doesn't exist
    results_none = fts_engine.search("nonexistent")
    assert results_none == []


def test_search_returns_doc_id_per_match(
    fts_engine: SqlLite3FullTextSearchEngine,
):
    """Test that search returns a document ID for each field match."""
    # given
    doc = Document({"title": "test", "body": "another test"})
    fts_engine.insert(doc, DocumentId("doc1"))

    # when
    # "test" appears in two fields, so the doc_id should be returned twice
    results = fts_engine.search("test")

    # then
    assert sorted(results) == ["doc1", "doc1"]


def test_delete(fts_engine: SqlLite3FullTextSearchEngine):
    """Test deleting a document from the index."""
    # given
    doc1 = Document({"content": "document to be deleted"})
    doc2 = Document({"content": "document to be kept"})
    fts_engine.insert(doc1, DocumentId("doc1_del"))
    fts_engine.insert(doc2, DocumentId("doc2_keep"))
    assert set(fts_engine.search("document")) == {"doc1_del", "doc2_keep"}

    # when
    fts_engine.delete(DocumentId("doc1_del"))

    # then
    assert set(fts_engine.search("document")) == {"doc2_keep"}
    assert fts_engine.search("deleted") == []


def test_delete_nonexistent_doc(
    fts_engine: SqlLite3FullTextSearchEngine,
):
    """Test that deleting a non-existent document does not raise an error."""
    # given
    doc1 = Document({"content": "a document"})
    fts_engine.insert(doc1, DocumentId("doc1"))

    # when
    # Deleting a non-existent doc_id should not raise an error
    fts_engine.delete(DocumentId("nonexistent_id"))

    # then
    assert set(fts_engine.search("document")) == {"doc1"}


def test_update_by_delete_and_insert(
    fts_engine: SqlLite3FullTextSearchEngine,
):
    """Test updating a document by deleting and re-inserting."""
    # given
    doc_v1 = Document({"content": "original content"})
    fts_engine.insert(doc_v1, DocumentId("doc1"))
    assert set(fts_engine.search("original")) == {"doc1"}
    assert fts_engine.search("updated") == []

    # when
    # To update, first delete the old document
    fts_engine.delete(DocumentId("doc1"))
    # Then insert the new version with the same doc_id
    doc_v2 = Document({"content": "updated content"})
    fts_engine.insert(doc_v2, DocumentId("doc1"))

    # then
    assert fts_engine.search("original") == []
    assert set(fts_engine.search("updated")) == {"doc1"}


def test_persistence(tokenizer: Tokenizer, tmp_path: Path):
    """Test that the index is persisted to a file."""
    # given
    db_path = tmp_path / "test.db"
    doc1 = Document({"content": "persistent data"})

    # when
    # First session: create db and insert data
    engine1 = SqlLite3FullTextSearchEngine(tokenizer=tokenizer, path=db_path)
    engine1.insert(doc1, DocumentId("doc1"))
    # Close connection by letting the object go out of scope (or explicitly)
    del engine1

    # then
    # Second session: connect to existing db and search
    engine2 = SqlLite3FullTextSearchEngine(tokenizer=tokenizer, path=db_path)
    results = engine2.search("persistent")
    assert set(results) == {"doc1"}
