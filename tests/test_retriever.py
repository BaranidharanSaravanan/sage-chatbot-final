# tests/test_retriever.py

from unittest.mock import MagicMock, patch
from src.retrieval.retriever import Retriever


@patch("src.retrieval.retriever.chromadb.PersistentClient")
def test_retriever_initialization(mock_client):
    mock_collection = MagicMock()
    mock_client.return_value.get_collection.return_value = mock_collection

    r = Retriever(top_k=3)
    assert r.top_k == 3
    assert r.collection is mock_collection


@patch("src.retrieval.retriever.chromadb.PersistentClient")
def test_retriever_returns_list(mock_client):
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["doc1", "doc2"]]
    }
    mock_client.return_value.get_collection.return_value = mock_collection

    r = Retriever(top_k=2)
    results = r.retrieve("library hours")

    assert results == ["doc1", "doc2"]


@patch("src.retrieval.retriever.chromadb.PersistentClient")
def test_retriever_empty_result(mock_client):
    mock_collection = MagicMock()
    mock_collection.query.return_value = {"documents": []}
    mock_client.return_value.get_collection.return_value = mock_collection

    r = Retriever()
    assert r.retrieve("unknown query") == []


@patch("src.retrieval.retriever.chromadb.PersistentClient")
def test_retriever_no_crash_on_random_query(mock_client):
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["random doc"]]
    }
    mock_client.return_value.get_collection.return_value = mock_collection

    r = Retriever()
    assert isinstance(r.retrieve("asdkjhaskjdhkajshdk"), list)
