'''Test connecting to test DB and uploading different types of documents'''
from . import client


SENT_DATA =  [
    {
      "docId": "NIV GEN 1:1",
      "text": "In the beginning God created the heavens and the earth.",
      "label": "NIV bible"
    },
    {
      "docId": "NIV GEN 1:2",
      "text": "Now the earth was formless and empty, darkness was over the surface of the deep, and the Spirit of God was hovering over the waters.",
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
      "text": "God called the light “day,” and the darkness he called “night.” And there was evening, and there was morning —the first day.",
      "label": "NIV bible"
    }
  ]

MD_FILES = [
    "../recipes/data/translationwords/amen.md",
    "../recipes/data/translationwords/angel.md"
    ]

CSV_FILE = "../recipes/data/dataupload.tsv"

def test_data_upload_processed_sentences(fresh_db):
    '''Test uploading documents to the vector DB'''
    response = client.post("/upload/sentences",
                    params={"vectordb_type": "chroma-db"},
                    json={"document_objs":SENT_DATA, "vectordb_config": fresh_db}
                    )
    assert response.status_code == 201
    assert response.json() == {"message": "Documents added to DB"}

def test_data_upload_markdown(fresh_db):
    '''Test uploading documents to the vector DB'''
    for md_file in MD_FILES:
        with open(md_file, 'rb') as input_file:

            response = client.post("/upload/text-file",
                        files={"file_obj": (md_file.rsplit('/', maxsplit=1)[-1],
                                                    input_file, "text/markdown")},
                        params={
                            "label":"translationwords",
                            "file_processor_type": "Langchain-loaders",
                            "vectordb_type": "chroma-db",
                            "dbPath":fresh_db["dbPath"],
                            "collectionName":fresh_db["collectionName"],
                            }
                        # json={"vectordb_config": fresh_db}
                        )
            assert response.status_code == 201
            assert response.json() == {"message": "Documents added to DB"}

def test_data_upload_csv(fresh_db):
    '''Test uploading documents to the vector DB'''
    with open(CSV_FILE, 'rb') as input_file:
        response = client.post("/upload/csv-file",
                    files={"file_obj": (CSV_FILE.rsplit('/', maxsplit=1)[-1],
                                                input_file, "text/csv")},
                    params={
                        "col_delimiter":"tab",
                        "vectordb_type": "chroma-db",
                        "dbPath":fresh_db["dbPath"],
                        "collectionName":fresh_db["collectionName"],
                        },
                    json={"vectordb_config": fresh_db}
                    )
        assert response.status_code == 201
        assert response.json() == {"message": "Documents added to DB"}

def test_get_lables(fresh_db):
    '''Check available labels in the vector db, before and after data upload'''
    param_args = {
                    "db_type": "chroma-db",
                    "dbPath": fresh_db["dbPath"],
                    "collectionName": fresh_db["collectionName"]
                }

    # Before upload
    response = client.get("/source-labels",params=param_args)
    assert response.status_code == 200
    assert response.json() == []

    # Upload set 1
    test_data_upload_processed_sentences(fresh_db)
    response = client.get("/source-labels",params=param_args)
    assert response.status_code == 200
    for label in ['NIV bible']:
        assert label in response.json()

    # Upload set 2
    test_data_upload_markdown(fresh_db)
    response = client.get("/source-labels",params=param_args)
    assert response.status_code == 200
    for label in ['NIV bible', 'translationwords']:
        assert label in response.json()

    # Upload set 3
    test_data_upload_csv(fresh_db)
    response = client.get("/source-labels",params=param_args)
    assert response.status_code == 200
    for label in ['NIV bible', 'translationwords', "ESV-Bible"]:
        assert label in response.json()
