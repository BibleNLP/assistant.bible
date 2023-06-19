'''Inputs text data into vector db.
Content type: CSV/TSV with following header(id,text,label,links,medialinks)
File processor: the Common CSV processor inherited into the LangchainLoader class
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
data_stack.set_vectordb(schema.DatabaseType.CHROMA,
    path="../chromadb",
    collection_name='aDotBCollection_fromTSV')


######## File Processor #############
INPUTFILE = "./data/dataupload.tsv"

processed_documents = data_stack.file_processor.process_file(
        file=INPUTFILE,
        file_type=schema.FileType.CSV,
        col_delimiter="\t")
print(f"Created {len(processed_documents)} documents")
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
