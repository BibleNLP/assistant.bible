"""Interface definition and common implemetations for embedding classes"""
import os
from typing import List

import schema

# pylint: disable=too-few-public-methods, unused-argument


class EmbeddingInterface:
    """Interface for embedding technology and its use"""

    api_key: str
    api_object = None

    def __init__(self, key: str, **kwargs) -> None:
        """Sets the API key and initializes library objects if any"""
        self.api_key = key

    def get_embeddings(self, doc_list: List[schema.Document]) -> None:
        """Generate embedding for the .text values and sets them to .embedding field of i/p items"""
        return
