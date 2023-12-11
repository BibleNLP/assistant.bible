"""Test the chat websocket"""
import os
import json
import pytest
from app import schema
from . import client

from .test_dataupload import test_data_upload_markdown
from .test_dataupload import test_data_upload_processed_sentences

admin_token = os.getenv("ADMIN_ACCESS_TOKEN", "chatchatchat")

# pylint: disable=too-many-function-args
COMMON_CONNECTION_ARGS = {
    "user": "xxx",
    "llmFrameworkType": schema.LLMFrameworkType.VANILLA.value,
    "vectordbType": schema.DatabaseType.POSTGRES.value,
    "collectionName": "adotdcollection_test",
    "labels": ["NIV bible", "ESV-Bible", "translationwords", "open-access"],
    "token": admin_token,
    "transcriptionApiKey":"dummy-key-for-openai",
    "llmApiKey":"dummy-key-for-openai",
}


def assert_positive_bot_response(resp_json):
    """Common things to check in any bot response"""
    assert "message" in resp_json
    assert len(resp_json["message"]) > 0
    assert "sources" in resp_json
    assert "media" in resp_json
    assert "type" in resp_json
    assert resp_json["type"] in ["answer", "question", "error"]
    assert "sender" in resp_json
    assert resp_json["sender"] in ["Bot", "You"]


def test_chat_websocket_connection(mocker, fresh_db, monkeypatch):
    """Check if websocket is connecting to and is bot responding"""
    mocker.patch("app.routers.Supabase.check_token",
                 return_value={"user_id": "1111"})
    mocker.patch("app.routers.Supabase.check_role", return_value=True)
    mocker.patch("app.routers.Supabase.get_accessible_labels", return_value=["mock-label"])
    mocker.patch("app.core.llm_framework.openai_vanilla.ChatCompletion.create",
                            return_value={"choices":[{"message":{"content":"Mock response"}}]})
    args = COMMON_CONNECTION_ARGS.copy()
    args["dbPath"] = fresh_db["dbPath"]
    args["collectionName"] = fresh_db["collectionName"]
    with client.websocket_connect("/chat", params=args) as websocket:
        websocket.send_bytes(json.dumps({"message":"Hello"}).encode('utf-8'))
        data = websocket.receive_json()
        assert_positive_bot_response(data)
        assert "Mock" in data['message']

@pytest.mark.with_llm
def test_chat_based_on_data_in_db(mocker, fresh_db):
    """Add some docs and ask questions on it, with default configs"""
    mocker.patch("app.routers.Supabase.check_token",
                 return_value={"user_id": "1111"})
    mocker.patch("app.routers.Supabase.check_role", return_value=True)
    mocker.patch("app.routers.Supabase.get_accessible_labels",
                        return_value=COMMON_CONNECTION_ARGS['labels'])
    args = COMMON_CONNECTION_ARGS.copy()
    args["dbPath"] = fresh_db["dbPath"]
    args["collectionName"] = fresh_db["collectionName"]

    test_data_upload_markdown(mocker, schema.DatabaseType.POSTGRES,
                                schema.FileProcessorType.LANGCHAIN, fresh_db)
    test_data_upload_processed_sentences(mocker, schema.DatabaseType.POSTGRES, fresh_db)

    with client.websocket_connect("/chat", params=args) as websocket:
        websocket.send_text("Hello")
        data = websocket.receive_json()
        assert_positive_bot_response(data)

        websocket.send_bytes(
            json.dumps({"message":"Can you tell me about angels?"}).encode('utf-8'))
        data = websocket.receive_json()
        assert_positive_bot_response(data)
        assert "angel" in data["message"].lower()
        assert "spirit" in data["message"].lower()
        assert "god" in data["message"].lower()

        # websocket.send_bytes(
        #    json.dumps({"message":"How was earth in the beginning?"}).encode('utf-8'))
        # data = websocket.receive_json()
        # assert_positive_bot_response(data)
        # assert "heaven" in data["message"].lower()
        # assert "god" in data["message"].lower()
        # assert "earth" in data["message"].lower()
