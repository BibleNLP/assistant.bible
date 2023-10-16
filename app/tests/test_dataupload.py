'''Test connecting to test DB and uploading different types of documents'''
import os
import pytest
from unittest.mock import patch, Mock
from functools import wraps

from . import client
from app import schema
from app import routers
from app.core.auth.supabase import Supabase


# patch('app.routers.auth_service.check_token', return_value={'user':{'id':'1111111111'}}).start()
# patch('app.routers.auth_service.check_role', return_value=True).start()



ADMIN_TOKEN = "dummy-admin-token"

SENT_DATA =  [
    {
      "docId": "NIV GEN 1:1",
      "text": "In the beginning God created the heavens and the earth.",
      "label": "NIV bible"
    },
    {
      "docId": "NIV GEN 1:2",
      "text": "Now the earth was formless and empty, darkness was over the "+\
      "surface of the deep, and the Spirit of God was hovering over the waters.",
      "label": "NIV bible"
    },
    {
      "docId": "NIV GEN 1:3",
      "text": "And God said, “Let there be light,” and there was light.",
      "label": "NIV bible"
    },
    {
      "docId": "NIV GEN 1:4",
      "text": "God saw that the light was good, and he separated the light from the darkness.",
      "label": "NIV bible"
    },
    {
      "docId": "NIV GEN 1:5",
      "text": "God called the light “day,” and the darkness he called “night.” "+\
      "And there was evening, and there was morning —the first day.",
      "label": "NIV bible"
    }
  ]

MD_FILES = [
    "../recipes/data/translationwords/amen.md",
    "../recipes/data/translationwords/angel.md"
    ]

CSV_FILE = "../recipes/data/dataupload.tsv"



@pytest.mark.parametrize('vectordb', [schema.DatabaseType.CHROMA, schema.DatabaseType.POSTGRES])
def test_data_upload_processed_sentences(mocker, vectordb, fresh_db, clear_loggers):
    '''Test uploading documents to the vector DB'''
    mocker.patch('app.routers.Supabase.check_token',return_value={'user':{'id':'1111'}})
    mocker.patch('app.routers.Supabase.check_role',return_value=True)
    response = client.post("/upload/sentences",
                    params={"vectordb_type": vectordb.value,
                            "token":ADMIN_TOKEN,
                            "dbPath":fresh_db['dbPath'],
                            "collectionName":fresh_db['collectionName'],
                            "embeddingType":schema.EmbeddingType.HUGGINGFACE_DEFAULT.value},
                    json=SENT_DATA
                    )
    assert response.status_code == 201, response.json()
    assert response.json() == {"message": "Documents added to DB"}

@pytest.mark.parametrize('vectordb', [schema.DatabaseType.CHROMA, schema.DatabaseType.POSTGRES])
@pytest.mark.parametrize('chunker', [schema.FileProcessorType.LANGCHAIN,
    # schema.FileProcessorType.VANILLA
    ])
def test_data_upload_markdown(mocker, vectordb, chunker, fresh_db, clear_loggers):
    '''Test uploading documents to the vector DB'''
    mocker.patch('app.routers.Supabase.check_token',return_value={'user':{'id':'1111'}})
    mocker.patch('app.routers.Supabase.check_role',return_value=True)
    for md_file in MD_FILES:
        with open(md_file, 'rb') as input_file:

            response = client.post("/upload/text-file",
                        files={"file_obj": (md_file.rsplit('/', maxsplit=1)[-1],
                                                    input_file, "text/markdown")},
                        params={
                            "label":"translationwords",
                            "file_processor_type": chunker.value,
                            "vectordb_type": vectordb.value,
                            "dbPath":fresh_db["dbPath"],
                            "collectionName":fresh_db["collectionName"],
                            "token":ADMIN_TOKEN
                            }
                        # json={"vectordb_config": fresh_db}
                        )
            assert response.status_code == 201, response.json()
            assert response.json() == {"message": "Documents added to DB"}

@pytest.mark.parametrize('vectordb', [schema.DatabaseType.CHROMA, schema.DatabaseType.POSTGRES])
def test_data_upload_csv(mocker, vectordb, fresh_db, clear_loggers):
    '''Test uploading documents to the vector DB'''
    mocker.patch('app.routers.Supabase.check_token',return_value={'user':{'id':'1111'}})
    mocker.patch('app.routers.Supabase.check_role',return_value=True)
    with open(CSV_FILE, 'rb') as input_file:
        response = client.post("/upload/csv-file",
                    files={"file_obj": (CSV_FILE.rsplit('/', maxsplit=1)[-1],
                                                input_file, "text/csv")},
                    params={
                        "col_delimiter":"tab",
                        "vectordb_type": vectordb.value,
                        "dbPath":fresh_db["dbPath"],
                        "collectionName":fresh_db["collectionName"],
                        "token":ADMIN_TOKEN
                        },
                    json={"vectordb_config": fresh_db}
                    )
        assert response.status_code == 201, response.json()
        assert response.json() == {"message": "Documents added to DB"}

@pytest.mark.parametrize('vectordb', [schema.DatabaseType.CHROMA, schema.DatabaseType.POSTGRES])
def test_get_lables(mocker, vectordb, fresh_db, clear_loggers):
    '''Check available labels in the vector db, before and after data upload'''
    mocker.patch('app.routers.Supabase.check_token',return_value={'user':{'id':'1111'}})
    mocker.patch('app.routers.Supabase.check_role',return_value=True)
    param_args = {
                    "db_type": vectordb.value,
                    "dbPath": fresh_db["dbPath"],
                    "collectionName": fresh_db["collectionName"],
                    "token":ADMIN_TOKEN
                }

    # Before upload
    response = client.get("/source-labels",params=param_args)
    assert response.status_code == 200
    assert response.json() == []

    # Upload set 1
    test_data_upload_processed_sentences(mocker, vectordb, fresh_db, clear_loggers)
    response = client.get("/source-labels",params=param_args)
    assert response.status_code == 200
    for label in ['NIV bible']:
        assert label in response.json()

    # Upload set 2
    test_data_upload_markdown(
        mocker, vectordb, schema.FileProcessorType.LANGCHAIN, fresh_db, clear_loggers)
    response = client.get("/source-labels",params=param_args)
    assert response.status_code == 200
    for label in ['NIV bible', 'translationwords']:
        assert label in response.json()

    # Upload set 3
    test_data_upload_csv(mocker, vectordb, fresh_db, clear_loggers)
    response = client.get("/source-labels",params=param_args)
    assert response.status_code == 200
    for label in ['NIV bible', 'translationwords', "ESV-Bible"]:
        assert label in response.json()
