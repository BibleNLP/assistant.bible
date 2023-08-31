'''Pipeline classes'''
from io import TextIOWrapper
from typing import List, Tuple, Optional

import schema
from custom_exceptions import GenericException
from core.file_processor import FileProcessorInterface
from core.embedding import EmbeddingInterface
from core.vectordb import VectordbInterface
from core.llm_framework import LLMFrameworkInterface
from core.audio import AudioTranscriptionInterface

from core.file_processor.langchain_loader import LangchainLoader
from core.file_processor.vanilla_loader import VanillaLoader
from core.embedding.openai import OpenAIEmbedding
from core.embedding.sentence_transformers import SentenceTransformerEmbedding
from core.vectordb.chroma import Chroma
from core.vectordb.chroma4langchain import Chroma as ChromaLC
from core.vectordb.postgres4langchain import Postgres
from core.llm_framework.openai_langchain import LangchainOpenAI
from core.audio.whisper import WhisperAudioTranscription

#pylint: disable=unused-argument

class DataUploadPipeline:
    '''Interface for implementing dataupload tech stack'''

    def __init__(self,
        file_processor: FileProcessorInterface=LangchainLoader,
        embedding: EmbeddingInterface=SentenceTransformerEmbedding(),
        vectordb: VectordbInterface=Chroma()) -> None:
        '''Define the stack with defaults, in the constructor'''
        self.file_processor = file_processor()
        self.embedding = embedding
        self.vectordb = vectordb

    def set_file_processor(self,
        choice: schema.FileProcessorType,
        **kwargs) -> None:
        '''Change the default tech with one of our choice'''
        if choice == schema.FileProcessorType.LANGCHAIN:
            self.file_processor = LangchainLoader()
        elif choice == schema.FileProcessorType.VANILLA:
            self.file_processor = VanillaLoader()
        else:
            raise GenericException("This technology type is not supported (yet)!")

    def set_embedding(self,
        choice:schema.EmbeddingType,
        api_key: Optional[str]=None,
        model: Optional[str]=None,
        **kwargs) -> None:
        '''Change the default tech with one of our choice'''
        if choice == schema.EmbeddingType.OPENAI:
            args = {}
            if not api_key is None:
                args['key'] = api_key
            if not model is None:
                args['model'] = model
            self.embedding = OpenAIEmbedding(**args)
        
        elif choice == schema.EmbeddingType.HUGGINGFACE_DEFAULT:
            args = {}
            if not model is None:
                args['model'] = model
            self.embedding = SentenceTransformerEmbedding(**args)
        
        else:
            raise GenericException("This technology type is not supported (yet)!")

    def set_vectordb(self,
        choice:schema.DatabaseType,
        host_n_port:schema.HostnPortPattern=None,
        path: Optional[str]=None,
        collection_name: Optional[str]=None,
        embedding_function=SentenceTransformerEmbedding(),
        **kwargs) -> None:
        '''Change the default tech with one of our choice'''
        args = {}
        if not host_n_port is None:
            parts = host_n_port.split(":")
            args['host'] = "".join(parts[:-1])
            args['port'] = parts[-1]
        if not path is None:
            args['path'] = path
        if not collection_name is None:
            args['collection_name'] = collection_name
        if choice == schema.DatabaseType.CHROMA:
            self.vectordb = Chroma(**args)
        elif choice == schema.DatabaseType.POSTGRES:
            args['user'] = kwargs.get("user")
            args['password'] = kwargs.get('password')
            args['embedding'] = kwargs.get('embedding')
            args['labels'] = kwargs.get('labels')
            self.vectordb = Postgres(**args)
        else:
            raise GenericException("This technology type is not supported (yet)!")

class ConversationPipeline(DataUploadPipeline):
    '''The tech stack for implementing chat bot'''
    def __init__(self, #pylint: disable=too-many-arguments,dangerous-default-value
        user,
        labels:List[str] = ["ESV-Bible"],
        file_processor: FileProcessorInterface=LangchainLoader,
        embedding: EmbeddingInterface=SentenceTransformerEmbedding(),
        vectordb: VectordbInterface=Chroma(),
        llm_framework: LLMFrameworkInterface=LangchainOpenAI(),
        transcription_framework: AudioTranscriptionInterface=WhisperAudioTranscription) -> None:
        '''Instantiate with default tech stack'''
        super().__init__(file_processor, embedding, vectordb)
        self.user = user
        if labels is not None:
            self.labels = labels
        self.chat_history = []
        self.embedding = embedding
        self.vectordb = vectordb
        self.llm_framework = llm_framework
        self.transcription_framework = transcription_framework()

    def set_llm_framework(self,
        choice:schema.LLMFrameworkType,
        api_key: Optional[str]=None,
        model_name: Optional[str]=None,
        vectordb:VectordbInterface=Chroma,
        **kwargs) -> None:
        '''Change the default tech with one of our choice'''
        self.llm_framework.api_key = api_key
        self.llm_framework.model_name = model_name
        if choice == schema.LLMFrameworkType.LANGCHAIN:
            if isinstance(vectordb, Chroma):
                vectordb = ChromaLC(host=vectordb.db_host, port=vectordb.db_port,
                    path=vectordb.db_path, collection_name=vectordb.collection_name)
            self.llm_framework = LangchainOpenAI(vectordb=vectordb)

    def set_transcription_framework(self,
        choice:schema.AudioTranscriptionType,
        api_key: Optional[str]=None,
        model_name: Optional[str]=None,
        **kwargs) -> None:
        '''Change the default tech with one of our choice'''
        self.transcription_framework.api_key = api_key
        self.transcription_framework.model_name = model_name
        if choice == schema.AudioTranscriptionType.WHISPER:
            self.transcription_framework = WhisperAudioTranscription()
