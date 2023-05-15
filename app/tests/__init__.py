'''Initializes a test client'''

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
