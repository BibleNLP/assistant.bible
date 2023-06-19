'''Inputs text data into vector db.
Content type: text/markdown files
File processor: Langchain loaders and splitters
Embedding: Using the chroma db's default embedding()
DB: chroma
'''

import os
import glob
import sys
 
# setting path
sys.path.append('../app')

from core.pipeline import DataUploadPipeline
import schema

######## Configure the pipeline's tech stack ############
data_stack = DataUploadPipeline()
data_stack.set_file_processor(
    schema.FileProcessorType.LANGCHAIN)
data_stack.set_vectordb(schema.DatabaseType.CHROMA,
    path="../chromadb",
    collection_name='aDotBCollection_chromaDefaultEmbeddings')


######## File Processor #############
input_files = glob.glob(
    "./data/translationwords/*.md")

processed_documents = []
for path in input_files:
    # with open(path, 'r', encoding='utf-8') as infile:
    docs = data_stack.file_processor.process_file(
        file=path,
        file_type=schema.FileType.MD,
        label="TranslationWords",
        name=f"tw-en-{path.split('/')[-1]}")
    processed_documents += docs
print(f"Processed {len(input_files)} files and created {len(processed_documents)} documents")
print('One Sample Document: ', processed_documents[0], '\n\n')



############# Embeddings  ###############
# not done explicitly. So using chroma db's default embedding!


# ########### Adding to chroma DB #################
data_stack.vectordb.add_to_collection(docs=processed_documents[:10])
rows = data_stack.vectordb.db_conn.get(
    include=["metadatas"]
)
print("First Row meta from DB",rows['metadatas'][0])
print("Last Row meta from DB:", rows['metadatas'][-1])
print("Total rows: ", len(rows['metadatas']))
print("!!!!!!!!!!!!!! Finished !!!!!!!!!!!!!!!!")
