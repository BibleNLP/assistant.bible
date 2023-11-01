"""Implemetations for embedding interface"""
from typing import List
from log_configs import log

import schema
from core.embedding import EmbeddingInterface


# pylint: disable=super-init-not-called,too-few-public-methods,,import-outside-toplevel
class SentenceTransformerEmbedding(EmbeddingInterface):
    """Uses sentence_transformers to generate embeddings."""

    default_model: str = "thenlper/gte-small"

    def __init__(self, model: str = default_model) -> None:
        """Initializes the model"""

        # If SentenceTransformerEmbedding is being instantiated for the first
        # time, it will download the model from the internet. Delay will depend
        # on model size. Downloaded model will be stored in root/.cache by default
        log.info(
            f"Initializing SentenceTransformerEmbedding with model: {model}.")

        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model)

    def get_embeddings(self, doc_list: List[schema.Document]) -> None:
        """
        Generates embeddings for the .text values and sets them to .embedding field of i/p items
        """
        for doc in doc_list:
            doc_text_stripped = doc.text.strip()
            encoded_doc_text = self.model.encode([doc_text_stripped])
            doc.embedding = encoded_doc_text[0]
