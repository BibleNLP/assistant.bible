'''Pipeline classes'''
from io import TextIOWrapper
from typing import List

import schema
from custom_exceptions import GenericException
from core.file_processing import FileProcessingInterface
from core.embedding import EmbeddingInterface
from core.vectordb import VectordbInterface

from core.file_processing.langchain_loader import LangchainLoader
from core.embedding.openai import OpenAIEmbedding
from core.vectordb.chroma import Chroma

#pylint: disable=unused-argument

class DataUploadPipeline:
    '''Interface for implementing dataupload tech stack'''
    file_processing: FileProcessingInterface = None
    embedding: EmbeddingInterface = None
    vectordb: VectordbInterface = None

    def __init__(self,
        file_processing_tech: FileProcessingInterface=LangchainLoader,
        embedding_tech: EmbeddingInterface=OpenAIEmbedding,
        vectordb_tech: VectordbInterface=Chroma) -> None:
        '''Define the stack with defaults, in the constructor'''
        self.file_processing = file_processing_tech()
        self.embedding = embedding_tech()
        self.vectordb = vectordb_tech()

    def set_file_processing(self,
        choice: schema.FileProcessingType,
        **kwargs) -> None:
        '''Change the default tech with one of our choice'''
        if choice == schema.FileProcessingType.LANGCHAIN:
            self.file_processing = LangchainLoader()
        else:
            raise GenericException("This technology type is not supported (yet)!")

    def set_embedding(self,
        choice:schema.EmbeddingType,
        api_key:str=None,
        model:str=None,
        **kwargs) -> None:
        '''Change the default tech with one of our choice'''
        if choice == schema.EmbeddingType.OPENAI:
            args = {}
            if not api_key is None:
                args['key'] = api_key
            if not model is None:
                args['model'] = model
            self.embedding = OpenAIEmbedding(**args)
        else:
            raise GenericException("This technology type is not supported (yet)!")

    def set_vectordb(self,
        choice:schema.DatabaseType,
        host_n_port:schema.HostnPortPattern=None,
        path:str=None,
        collection_name:str=None,
        **kwargs) -> None:
        '''Change the default tech with one of our choice'''
        if choice == schema.DatabaseType.CHROMA:
            args = {}
            if not host_n_port is None:
                parts = host_n_port.split(":")
                args['host'] = "".join(parts[:-1])
                args['port'] = parts[-1]
            if not path is None:
                args['path'] = path
            if not collection_name is None:
                args['collection_name'] = collection_name
            self.vectordb = Chroma(**args)
        else:
            raise GenericException("This technology type is not supported (yet)!")
