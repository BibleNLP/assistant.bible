"""Initializes a test client"""

from fastapi.testclient import TestClient

mock = Mock()

with patch('supabase.create_client', mock):
    from main import app

client = TestClient(app)
