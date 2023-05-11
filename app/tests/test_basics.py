'''Basic tests to check App is working'''
from . import client

def test_default_api():
    '''test the default API endpoint and check if App is up'''
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "App is up and running"}
