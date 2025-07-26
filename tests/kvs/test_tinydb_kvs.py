import tempfile
from pathlib import Path

import pytest
from tinydb.storages import JSONStorage, MemoryStorage

from warabi.common import Document, DocumentId
from warabi.kvs.tinydb_kvs import TinyDbKVStore


@pytest.fixture
def in_memory_kvs() -> TinyDbKVStore:
    """Fixture for an in-memory TinyDbKVStore."""
    return TinyDbKVStore()


@pytest.fixture
def file_kvs():
    """Fixture for a file-based TinyDbKVStore that is cleaned up."""

    with tempfile.NamedTemporaryFile(suffix=".json") as file:
        kv = TinyDbKVStore(path=file.name)
        yield kv


@pytest.fixture(params=["in_memory", "file"])
def kvs(
    request,
    in_memory_kvs,
    file_kvs,
) -> TinyDbKVStore:
    """Parametrized fixture to test both in-memory and file-based stores."""
    if request.param == "in_memory":
        return in_memory_kvs
    return file_kvs


def test_init_in_memory():
    """Test that the store uses in-memory storage when no path is provided."""
    kvs = TinyDbKVStore()
    assert isinstance(kvs._db.storage, MemoryStorage)


def test_init_with_path(tmp_path: Path):
    """Test that the store uses file-based storage when a path is provided."""
    with tempfile.NamedTemporaryFile(suffix=".json") as file:
        kvs = TinyDbKVStore(path=file.name)
        assert isinstance(kvs._db.storage, JSONStorage)


def test_insert_and_get(kvs: TinyDbKVStore):
    """Test inserting a document and retrieving it."""
    # given
    doc_id = DocumentId("1")
    doc = Document({"text": "This is a test document."})

    # when
    kvs.insert(doc, doc_id)
    retrieved_doc = kvs.get(doc_id)

    # then
    assert retrieved_doc == doc


def test_get_nonexistent(kvs: TinyDbKVStore):
    """Test that getting a non-existent document returns None."""
    # when
    doc_id = DocumentId("999")

    # given
    doc = kvs.get(doc_id)

    # then
    assert doc is None


def test_update(kvs: TinyDbKVStore):
    """Test updating an existing document."""
    # given
    doc_id = DocumentId("1")
    initial_doc = Document({"text": "Initial version."})
    updated_doc = Document({"text": "Updated version."})

    # when
    kvs.insert(initial_doc, doc_id)
    kvs.update(updated_doc, doc_id)

    # then
    retrieved_doc = kvs.get(doc_id)
    assert retrieved_doc == updated_doc


def test_update_nonexistent(kvs: TinyDbKVStore):
    """Test that updating a non-existent document does nothing."""
    # given
    doc = Document({"text": "some text"})
    doc_id = DocumentId("999")

    # when
    kvs.update(doc, doc_id)

    # then
    assert kvs.get(doc_id) is None


def test_delete(kvs: TinyDbKVStore):
    """Test deleting an existing document."""
    # given
    doc_id = DocumentId("1")
    doc = Document({"text": "This document will be deleted."})
    kvs.insert(doc, doc_id)

    # when
    kvs.delete(doc_id)

    # then
    assert kvs.get(doc_id) is None
