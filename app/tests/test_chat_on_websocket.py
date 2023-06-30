'''Test the chat websocket'''

from . import client
from .test_dataupload import test_data_upload_markdown
from .test_dataupload import test_data_upload_processed_sentences

COMMON_CONNECTION_ARGS = {
                "user": "xxx",
                "llmFrameworkType":"openai-langchain",
                "vectordbType": "chroma-db",
                "dbPath":"chromadb_store_test",
                "collectionName": "aDotBCollection_test",
                "labels": ["NIV bible", "ESV-Bible", "translationwords"]
                }

def assert_positive_bot_response(resp_json):
    '''Common things to check in any bot response'''
    assert "message" in resp_json
    assert len(resp_json['message']) > 0
    assert "sources" in resp_json
    assert "media" in resp_json
    assert "type" in resp_json
    assert resp_json['type'] in ['answer', 'question', 'error']
    assert "sender" in resp_json
    assert resp_json['sender'] in ['Bot', 'You']

def test_chat_websocket_connection(fresh_db):
    '''Check if websocket is connecting to and is bot responding'''
    args = COMMON_CONNECTION_ARGS.copy()
    args['dbPath'] = fresh_db['dbPath']
    args['collectionName'] = fresh_db['collectionName']
    with client.websocket_connect("/chat",
            params=args
        ) as websocket:

        websocket.send_text("Hello")
        data = websocket.receive_json()
        assert_positive_bot_response(data)

def test_chat_based_on_translationwords(fresh_db):
    '''Add some docs and ask questions on it, with default configs'''
    args = COMMON_CONNECTION_ARGS.copy()
    args['dbPath'] = fresh_db['dbPath']
    args['collectionName'] = fresh_db['collectionName']

    test_data_upload_markdown(fresh_db)
    test_data_upload_processed_sentences(fresh_db)

    with client.websocket_connect("/chat",
            params=args
        ) as websocket:

        websocket.send_text("Hello")
        data = websocket.receive_json()
        assert_positive_bot_response(data)

        websocket.send_text("Can you tell me about angels?")
        data = websocket.receive_json()
        assert_positive_bot_response(data)
        assert "angel" in data['message'].lower()
        assert "spirit" in data['message'].lower()
        assert "god" in data['message'].lower()

        websocket.send_text("What happended in the beginning?")
        data = websocket.receive_json()
        assert_positive_bot_response(data)
        assert "heaven" in data['message'].lower()
        assert "god" in data['message'].lower()
        assert "earth" in data['message'].lower()
