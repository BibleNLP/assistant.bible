"""Implemetations for lmm_framework interface using vanilla"""
import os
from typing import List, Tuple

import openai

from core.llm_framework import LLMFrameworkInterface
from core.vectordb import VectordbInterface

from custom_exceptions import AccessException, OpenAIException
from log_configs import log

# pylint: disable=too-few-public-methods, unused-argument, too-many-arguments, R0801


def get_context(source_documents):
    """Constructs a context string based on the provided results."""
    context = "["
    # ** This will need to be adjusted, based on what the returned results look like **
    for i in range(len(source_documents)):
        if (
            len(source_documents[i].page_content) + len(context) > 11000
        ):  # FIXME: use tiktoken library to count tokens
            break
        context += "{source:" + source_documents[i].metadata.get("source", "")
        context += ", text: " + source_documents[i].page_content + "}" + ","
    context += "]" + "\n"

    return context


def get_pre_prompt(context):
    """Constructs a pre-prompt for the conversation, including the context"""
    chat_prefix = "The following is a conversation with an AI assistant for "
    chat_prefix += "Bible translators. The assistant is"
    chat_prefix += " helpful, creative, clever, very friendly and follows instructions carefully.\n"
    prompt = (
        chat_prefix
        + "Read the paragraph below and answer the question, using only the information"
        " in the context delimited by triple backticks. "
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
            chat_history = chat_history[
                -15:
            ]  # FIXME: use tiktoken library to check overall token count and ensure context window is not exceeded
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
        model_name: str = "gpt-3.5-turbo",
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
        self, query: str, chat_history: List[Tuple[str, str]], **kwargs
    ) -> dict:
        """Prompt completion for QA or Chat reponse, based on specific documents,
        if provided"""
        if len(kwargs) > 0:
            log.warning(
                "Unused arguments in VanillaOpenAI.generate_text(): ", **kwargs)

        # Vectordb results are currently returned based on the whole chat history.
        # We'll need to figure out if this is optimal or not.
        query_text = "\n".join(
            [x[0] + "/n" + x[1][:50] + "\n" for x in chat_history])
        query_text += "\n" + query
        source_documents = self.vectordb.get_relevant_documents(query_text)
        context = get_context(source_documents)
        pre_prompt = get_pre_prompt(context)
        prompt = append_query_to_prompt(pre_prompt, query, chat_history)
        print(f"{prompt=}")

        try:
            response = openai.ChatCompletion.create(
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
            raise OpenAIException(
                "While generating answer: " + str(exe)) from exe
