"""Interface definition and common implemetations for vectordb classes"""
import os
from typing import List
from abc import abstractmethod, ABC

import schema

# pylint: disable=too-few-public-methods, unused-argument


class VectordbInterface(ABC):
    """Interface for vector database technology, its connection, configs and operations"""

    db_host: str = None  # Host name to connect to a remote DB deployment
    db_port: str = None  # Port to connect to a remote DB deployment
    db_path: str = None  # Path for a local DB, if that is being used(in chroma)
    collection_name: str = None  # Collection to connect to a remote/local DB
    db_conn = None

    def __init__(self, host, port, path, collection_name) -> None:
        """Get a connection ready"""
        return

    @abstractmethod
    def add_to_collection(self, docs: List[schema.Document], **kwargs) -> None:
        """Add objects in document format to DB"""
        return

    @abstractmethod
    def get_relevant_documents(self, query: str, **kwargs) -> List:
        """Similarity search on the vector store"""

    @abstractmethod
    def get_available_labels(self) -> List[str]:
        """Query DB and find out the list of labels available in metadata,
        to be used for later filtering"""

    def get(self, **kwargs) -> List:
        """Return properties of the DB"""
        return self.db_conn.get(**kwargs)
