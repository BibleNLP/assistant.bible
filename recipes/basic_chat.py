'''Create a conversationPipeline
Embedding: chromadb's default
DB: chroma, no filtering
framework: langchain
'''

import os
import glob
import sys
 
# setting path
sys.path.append('../app')

from core.pipeline import ConversationPipeline, DataUploadPipeline
import schema

######## Configure the pipeline's tech stack ############
chat_stack = ConversationPipeline(user="test_user")
chat_stack.set_vectordb(schema.DatabaseType.CHROMA,
    path="chromadb_store",
    collection_name="aDotBCollection_chromaDefaultEmbeddings",
    # collection_name='aDotBCollection_chromaDefaultEmbeddings'
    )
chat_stack.set_llm_framework(schema.LLMFrameworkType.LANGCHAIN,
    api_key=os.getenv('OPENAI_API_KEY'),
    model='gpt-3.5-turbo',
    vectordb=chat_stack.vectordb)

##### Checking DB has content ##########

# print(chat_stack.vectordb.db_conn.get(
#     include=["metadatas"]
# ))


########### Talk #################

QUERY = "Who are angels?"
bot_response = chat_stack.llm_framework.generate_text(
                query=QUERY, chat_history=chat_stack.chat_history)
print(f"Human: {QUERY}\nBot:{bot_response['answer']}\n"+\
    f"Sources:{[item.metadata['source'] for item in bot_response['source_documents']]}\n\n")
chat_stack.chat_history.append((bot_response['question'], bot_response['answer']))

QUERY = "Are they like humans?"
bot_response = chat_stack.llm_framework.generate_text(
                query=QUERY, chat_history=chat_stack.chat_history)
print(f"Human: {QUERY}\nBot:{bot_response['answer']}\n"+\
    f"Sources:{[item.metadata['source'] for item in bot_response['source_documents']]}\n\n")
chat_stack.chat_history.append((bot_response['question'], bot_response['answer']))


QUERY = "Can they perform actions that impact our life, future etc?"
bot_response = chat_stack.llm_framework.generate_text(
                query=QUERY, chat_history=chat_stack.chat_history)
print(f"Human: {QUERY}\nBot:{bot_response['answer']}\n"+\
    f"Sources:{[item.metadata['source'] for item in bot_response['source_documents']]}\n\n")
chat_stack.chat_history.append((bot_response['question'], bot_response['answer']))

print("!!!!!!!!!!!!!! Finished !!!!!!!!!!!!!!!!")
