"""Implemetations for embedding interface"""
import os
from typing import List, Optional
import openai

import schema
from core.embedding import EmbeddingInterface
from custom_exceptions import AccessException, OpenAIException


# pylint: disable=too-few-public-methods,super-init-not-called


class OpenAIEmbedding(EmbeddingInterface):
    """Uses OpenAI APIs to create vectors for text"""

    api_key: str = None
    model: str = None
    api_object = None

    def __init__(
        self,  # pylint: disable=super-init-not-called
        key: str = os.getenv("OPENAI_API_KEY"),
        api_key: Optional[str] = os.getenv(
            "OPENAI_API_KEY"
        ),  # the set_embedding method uses api_key, so it's accepted here for cross-compatibility
        model: str = "text-embedding-ada-002",
    ) -> None:
        """Sets the API key and initializes library objects if any"""
        self.api_key = key if key is not None else api_key
        if self.api_key is None:
            raise AccessException(
                "OPENAI_API_KEY needs to be provided."
                + "Visit https://platform.openai.com/account/api-keys"
            )
        self.api_object = openai
        self.api_object.api_key = key
        self.model = model

    def get_embeddings(self, doc_list: List[schema.Document]) -> None:
        """Generate embedding for the .text values and sets them to .embedding field of i/p items"""
        for doc in doc_list:
            input_text = doc.text.replace("\n", " ")
            response = openai.Embedding.create(input=input_text, model=self.model)
            if "data" not in response:
                raise OpenAIException(str(response))
            doc.embedding = response["data"][0]["embedding"]
