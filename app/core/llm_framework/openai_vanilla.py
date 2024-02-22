"""Implemetations for lmm_framework interface using vanilla"""
import os
from typing import List, Tuple

import openai
from openai import ChatCompletion

from core.llm_framework import LLMFrameworkInterface
from core.vectordb import VectordbInterface

from custom_exceptions import AccessException, OpenAIException
from log_configs import log

# pylint: disable=too-few-public-methods, unused-argument, too-many-arguments, R0801,super-init-not-called,
# pylint: disable=fixme


def get_context(source_documents):
    """Constructs a context string based on the provided results."""
    context = "["
    # ** This will need to be adjusted, based on what the returned results look like **
    for _, source_document in enumerate(source_documents):
        if (
            len(source_document.page_content) + len(context) > 44000
        ):  # FIXME: use tiktoken library to count tokens
            break
        if source_document.metadata.get("source", "") is not None:
            context += "{source:" + source_document.metadata.get("source", "")
            context += ", text: " + source_document.page_content + "}" + ","
    context += "]" + "\n"

    return context


def get_pre_prompt(context, response_language="English"):
    """Constructs a pre-prompt for the conversation, including the context"""
    chat_prefix = "The following is a conversation with an AI assistant for "
    chat_prefix += "Bible translators. The assistant is"
    chat_prefix += "verbose, helpful, creative, clever, very friendly "
    chat_prefix += "and follows instructions carefully,"
    chat_prefix += "giving as much information as possible.\n"
    prompt = (
        chat_prefix
        + "Read the paragraph below and answer the question, using only the information"
        " in the context delimited by triple backticks. "
        f" Your response should be in the {response_language} language."
        "If the question cannot be answered based on the context alone, "
        'write "Sorry, I had trouble answering this question based on the '
        "information I found\n"
        "\n"
        "Context:\n"
        f"```{ context }```\n"
        "\n"
    )

    return prompt


def append_query_to_prompt(prompt, query, chat_history):
    """Appends the provided query and chat history to the given prompt."""
    if len(chat_history) > 0:
        if len(chat_history) > 15:
            # FIXME: use tiktoken library to check overall token count
            # and ensure context window is not exceeded
            chat_history = chat_history[-15:]
        for exchange in chat_history:
            prompt += "\nHuman: " + exchange[0] + "\nAI: " + exchange[1]
    prompt += "\nHuman: " + query + "\nAI: "

    return prompt


class OpenAIVanilla(LLMFrameworkInterface):  # pylint: disable=too-few-public-methods
    """Uses OpenAI APIs to create vectors for text"""

    api_key: str = None
    model_name: str = None
    vectordb = None

    def __init__(
        self,  # pylint: disable=super-init-not-called
        key: str = os.getenv("OPENAI_API_KEY"),
        model_name: str = os.getenv("OPENAI_LLM_NAME", "gpt-3.5-turbo"),
        vectordb: VectordbInterface = None,  # What should this be by default?
    ) -> None:
        """Sets the API key and initializes library objects if any"""
        if key is None:
            raise AccessException(
                "OPENAI_API_KEY needs to be provided."
                + "Visit https://platform.openai.com/account/api-keys"
            )
        self.api_key = key
        openai.api_key = self.api_key
        self.model_name = model_name
        self.vectordb = vectordb

    def generate_text(
        self,
        query: str,
        chat_history: List[Tuple[str, str]],
        response_language: str = "English",
        **kwargs,
    ) -> dict:
        """Prompt completion for QA or Chat reponse, based on specific documents,
        if provided"""
        if len(kwargs) > 0:
            log.warning("Unused arguments in VanillaOpenAI.generate_text(): ", **kwargs)

        # Vectordb results are currently returned based on the whole chat history.
        # We'll need to figure out if this is optimal or not.
        query_text = "\n".join([x[0] + "/n" + x[1][:50] + "\n" for x in chat_history])
        query_text += "\n" + query
        source_documents = self.vectordb._get_relevant_documents(query_text)  # pylint: disable=protected-access
        context = get_context(source_documents)
        pre_prompt = get_pre_prompt(context, response_language=response_language)
        prompt = append_query_to_prompt(pre_prompt, query, chat_history)
        print(f"{prompt=}")

        try:
            response = ChatCompletion.create(
                model=self.model_name,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )
            return {
                "question": query,
                "answer": response["choices"][0]["message"]["content"],
                "source_documents": source_documents,
            }

        except Exception as exe:
            raise OpenAIException("While generating answer: " + str(exe)) from exe
