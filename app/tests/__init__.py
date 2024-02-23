"""Initializes a test client"""
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

mock_supabase = Mock()

mock_translate_text = {'TranslatedText': 'Hello, world', 'SourceLanguageCode': 'es', 'TargetLanguageCode': 'en'}

with patch("supabase.create_client", mock_supabase), \
     patch("app.core.translation.translate_text", return_value=mock_translate_text):
    from main import app

client = TestClient(app)
