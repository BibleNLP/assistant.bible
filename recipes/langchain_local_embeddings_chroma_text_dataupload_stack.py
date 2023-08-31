'''This script inputs text data into a vector database.
Content type: text/markdown files
File processor: Langchain loaders and splitters
Embedding: Huggingface Sentence Transformers 
Database: Chroma
'''

import os
import glob
import sys

sys.path.append('../app')  # Add application directory to system path

from core.pipeline import DataUploadPipeline
import schema

# Initialize the data upload pipeline
data_stack = DataUploadPipeline()

# Set the file processor, embedding, and database
data_stack.set_file_processor(schema.FileProcessorType.LANGCHAIN)
data_stack.set_embedding(schema.EmbeddingType.HUGGINGFACE_DEFAULT)
print(f"Embedding documents with model: {schema.EmbeddingType.HUGGINGFACE_DEFAULT}")
data_stack.set_vectordb(schema.DatabaseType.CHROMA, path="chromadb_store", collection_name='aDotBCollection')

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

# Print the number of processed files and documents
print(f"Processed {len(input_files)} files and created {len(processed_documents)} documents")

# Generate embeddings for the processed documents
data_stack.embedding.get_embeddings(doc_list=processed_documents)

# Add the processed documents to the database
data_stack.vectordb.add_to_collection(docs=processed_documents)
rows = data_stack.vectordb.db_conn.get(include=["metadatas"])

# Print some information about the data in the database
print("First Row meta from DB",rows['metadatas'][0])
print("Last Row meta from DB:", rows['metadatas'][-1])
print("Total rows: ", len(rows['metadatas']))
print("Data upload complete.")
