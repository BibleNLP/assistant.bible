'''Interface definition and common implemetations for lmm framework classes'''
import os
from typing import List, Tuple

import schema

#pylint: disable=too-few-public-methods, unused-argument

class LLMFrameworkInterface:
    '''Interface for embedding technology and its use'''
    api_key: str
    model_name: str
    api_object = None
    llm = None
    def __init__(self, key:str, **kwargs) -> None:
        '''Sets the API key and initializes library objects if any'''
        self.api_key = key
    def generate_text(self,
    	query:str,
    	chat_history:List[Tuple[str,str]]=None,
    	# context_docs: List[schema.Document]=None
        **kwargs) -> dict:
        '''Prompt completion for QA or Chat reponse, based on specific documents, if provided'''
        return {}
