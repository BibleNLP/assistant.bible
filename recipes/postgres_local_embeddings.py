'''This script inputs text data into a vector database.
Content type: text/markdown files
File processor: Langchain loaders and splitters
Embedding: Local Sentence Transformers
Database: Postgres with pgvector extension
'''

import os
import glob
import sys

# Add application directory to system path
sys.path.append('../app')

from core.pipeline import DataUploadPipeline
from core.vectordb.postgres4langchain import Postgres
from core.vectordb import VectordbInterface
from core.embedding.sentence_transformers import SentenceTransformerEmbedding
import schema

# Initialize the data upload pipeline
data_stack = DataUploadPipeline(
    vectordb = Postgres(
            host_n_port="localhost:5435",
            collection_name='adotbcollection',
            user='admin',
            password="secret",
            embedding=SentenceTransformerEmbedding() # Set the embedding to local Sentence Transformers
            # With PGVector, the embedding dimension size is always hard-coded on init, so we have to set it here.
        )
    )

# Set the file processor
data_stack.set_file_processor(schema.FileProcessorType.LANGCHAIN)

# Process input files
input_files = glob.glob("./data/translationwords/*.md")
processed_documents = []
for path in input_files:
    docs = data_stack.file_processor.process_file(
        file=path,
        file_type=schema.FileType.MD,
        label="TranslationWords",
        name=f"tw-en-{path.split('/')[-1]}")
    processed_documents += docs

# Generate embeddings for the processed documents
data_stack.embedding.get_embeddings(doc_list=processed_documents)

# Add the processed documents to the database
data_stack.vectordb.add_to_collection(docs=processed_documents)

# Print some information about the data in the database
cur = data_stack.vectordb.db_conn.cursor()
cur.execute("SELECT * FROM embeddings")
rows = cur.fetchall()
print("First Row meta from DB", str(rows[0])[:80] + '...')
print("Last Row meta from DB:", str(rows[-1])[:80] + '...')
print("Total rows: ", len(rows))
print("Data upload complete.")
cur.close()
