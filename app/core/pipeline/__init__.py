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
    file_processing_tech: FileProcessingInterface = None
    embedding_tech: EmbeddingInterface = None
    vectordb_tech: VectordbInterface = None

    def __init__(self,
        file_processing_tech: FileProcessingInterface=LangchainLoader,
        embedding_tech: EmbeddingInterface=OpenAIEmbedding,
        vectordb_tech: VectordbInterface=Chroma) -> None:
        '''Define the stack with defaults, in the constructor'''
        self.file_processing_tech = file_processing_tech()
        self.embedding_tech = embedding_tech()
        self.vectordb_tech = vectordb_tech()

    def set_file_processing_tech(self,
        choice: schema.FileProcessingTech,
        **kwargs) -> None:
        '''Change the default tech with one of our choice'''
        if choice == schema.FileProcessingTech.LANGCHAIN:
            self.file_processing_tech = LangchainLoader()
        else:
            raise GenericException("This technology type is not supported (yet)!")

    def set_embedding_tech(self,
        choice:schema.EmbeddingTech,
        api_key:str=None,
        model:str=None,
        **kwargs) -> None:
        '''Change the default tech with one of our choice'''
        if choice == schema.EmbeddingTech.OPENAI:
            args = {}
            if not api_key is None:
                args['key'] = api_key
            if not model is None:
                args['model'] = model
            self.embedding_tech = OpenAIEmbedding(**args)
        else:
            raise GenericException("This technology type is not supported (yet)!")

    def set_vectordb_tech(self,
        choice:schema.DatabaseTech,
        host_n_port:schema.HostnPortPattern=None,
        path:str=None,
        collection_name:str=None,
        **kwargs) -> None:
        '''Change the default tech with one of our choice'''
        if choice == schema.DatabaseTech.CHROMA:
            args = {}
            if not host_n_port is None:
                parts = host_n_port.split(":")
                args['host'] = "".join(parts[:-1])
                args['port'] = parts[-1]
            if not path is None:
                args['path'] = path
            if not collection_name is None:
                args['collection_name'] = collection_name
            self.vectordb_tech = Chroma(**args)
        else:
            raise GenericException("This technology type is not supported (yet)!")

