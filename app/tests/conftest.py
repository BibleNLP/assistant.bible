''' Test fixtures and stuff'''

import os
import shutil
import pytest


@pytest.fixture
def fresh_db():
    '''Deletes the chroma db folder if one existed and 
    returns the DB_config to be used in all APIs'''
    chroma_db_path = "chromadb_store_test"
    chroma_db_collection = "aDotBCollection_test"
    if os.path.exists(chroma_db_path):
        shutil.rmtree(chroma_db_path)
    try:
        yield {
                "dbPath": chroma_db_path,
                "collectionName": chroma_db_collection
              }
    finally:
        if os.path.exists(chroma_db_path):
            shutil.rmtree(chroma_db_path)
