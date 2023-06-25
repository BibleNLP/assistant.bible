'''Implemetations for lmm_framework interface using vanilla'''
import os
from typing import List, Tuple

import openai

from core.llm_framework import LLMFrameworkInterface
from core.vectordb import VectordbInterface
from core.vectordb.chroma4langchain import Chroma

from custom_exceptions import AccessException, OpenAIException
from log_configs import log


def get_context(results):
    context = '['
    # *** This will need to be adjusted, based on what the returned results look like ***
    for i in range(len(results['documents'][0])):
        context += "{source:" + results['metadatas'][0][i]['citation'] + ', text: ' + results['documents'][0][i] + '}' + ','
    context += ']' + '\n'
    
    return context


def get_pre_prompt(context):
    chat_prefix = "The following is a conversation with an AI assistant for Bible translators. The assistant is"
    chat_prefix += f" helpful, creative, clever, and very friendly.\n"
    prompt = (
        chat_prefix +
        f'Read the paragraph below and answer the question, using only the information in the context delimited by triple backticks.'
        f'At the end of your answer, include the source of each context text that you used. You may use more than one, and include the sources of all those you used. '
        f'If the question cannot be answered based on the context alone, write "Sorry, I had trouble answering this question based on the information i found\n'
        f"\n"
        f"Context:\n"
        f"```{ context }```\n"
        f"\n"
    )

    return prompt


def append_query_to_prompt(prompt, query, chat_history):
    if len(chat_history) > 0:
        if len(chat_history) > 3:
            chat_history = chat_history[-3:]
        for exchange in chat_history:
            prompt += "\nHuman: " + exchange[0] + "\nAI: " + exchange[1]
    prompt += "\nHuman: " + query + "\nAI: "

    return prompt


class LangchainOpenAI(LLMFrameworkInterface):
    '''Uses OpenAI APIs to create vectors for text'''
    api_key: str = None
    model_name: str = None
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
        openai.api_key = self.api_key
        self.model_name = model_name
        self.vectordb = vectordb


    def generate_text(self,
        query:str,
        chat_history:List[Tuple[str,str]],
        **kwargs) -> dict:
        '''Prompt completion for QA or Chat reponse, based on specific documents, if provided'''
        if len(kwargs) > 0:
            log.warning("Unused arguments in LangchainOpenAI.generate_text(): ",**kwargs)

        # Vectordb results are currently returned based on the whole chat history. We'll need to figure out if this is optimal or not.
        query_text = '\n'.join([x[0] + '/n' + x[1][:50] + '\n' for x in chat_history]) + '\n' + query
        results = self.vectordb.get_relevant_documents(query_text)
        context = get_context(results)
        pre_prompt = get_pre_prompt(context)
        prompt = append_query_to_prompt(pre_prompt, query, chat_history)

        try:
            response = openai.ChatCompletion.create(
                                model=self.model_name,
                                temperature=0,
                    messages=[{"role": "user", "content": prompt}]
                )
            return response['choices'][0]["message"]["content"]
        
        except Exception as exe:
            raise OpenAIException("While generating answer: "+str(exe)) from exe
