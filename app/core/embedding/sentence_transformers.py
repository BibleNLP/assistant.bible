"""Implemetations for embedding interface"""
from typing import List
from log_configs import log

import schema
from core.embedding import EmbeddingInterface

"""Implementation for generating sentence_transformers embeddings using Huggingface sentence_transformers"""


class SentenceTransformerEmbedding(EmbeddingInterface):
    """Uses sentence_transformers to generate embeddings."""

    default_model: str = "thenlper/gte-small"

    def __init__(self, model: str = default_model) -> None:
        """Initializes the model"""

        # If SentenceTransformerEmbedding is being instantiated for the first
        # time, it will download the model from the internet. Delay will depend
        # on model size. Downloaded model will be stored in root/.cache by default
        log.info(f"Initializing SentenceTransformerEmbedding with model: {model}.")

        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model)

    def get_embeddings(self, doc_list: List[schema.Document]) -> None:
        """Generates embeddings for the .text values and sets them to .embedding field of i/p items"""
        for doc in doc_list:
            doc.embedding = self.model.encode([doc.text.strip()])[0]
