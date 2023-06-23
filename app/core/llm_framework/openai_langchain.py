'''Implemetations for lmm_framework interface using langchain'''
import os
from typing import List, Tuple
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory

from core.llm_framework import LLMFrameworkInterface
from core.vectordb import VectordbInterface
from core.vectordb.chroma4langchain import Chroma

from custom_exceptions import AccessException, OpenAIException


#pylint: disable=too-few-public-methods

class LangchainOpenAI(LLMFrameworkInterface):
    '''Uses OpenAI APIs to create vectors for text'''
    api_key: str = None
    model_name: str = None
    api_object = None
    llm = None
    chain = None
    vectordb = None
    def __init__(self, #pylint: disable=super-init-not-called
                key:str=os.getenv("OPENAI_API_KEY"),
                model_name:str = 'gpt-3.5-turbo',
                vectordb:VectordbInterface = Chroma()) -> None:
        '''Sets the API key and initializes library objects if any'''
        if key is None:
            raise AccessException("OPENAI_API_KEY needs to be provided."+\
                "Visit https://platform.openai.com/account/api-keys")
        self.api_key = key
        self.model_name = model_name
        self.vectordb = vectordb
        self.api_object = OpenAI
        self.api_object.api_key = self.api_key
        self.llm = self.api_object(temperature=0, model_name=self.model_name)
        # memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        self.chain = ConversationalRetrievalChain.from_llm(self.llm,
			self.vectordb,
			# memory = memory,
        	return_source_documents=True)

    def generate_text(self,
    	query:str,
    	chat_history:List[Tuple[str,str]]) -> str:
        '''Prompt completion for QA or Chat reponse, based on specific documents, if provided'''
        try:
            return self.chain({"question": query, "chat_history": chat_history})
        except Exception as exe:
            raise OpenAIException("While generating answer: "+str(exe)) from exe
