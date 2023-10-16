'''Basic tests to check App is working and pages are loading'''
from . import client

def test_test_endpoint():
    '''test the default API endpoints and check if App is up'''
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "App is up and running"}

def test_index_page_load():
    '''test the default API endpoints and check if App is up'''
    response = client.get("/")
    assert response.status_code == 200

def test_chat_demo_page_load():
    '''test the default API endpoints and check if App is up'''
    response = client.get("/app")
    assert response.status_code == 200

def test_login_page_load():
    '''test the default API endpoints and check if App is up'''
    response = client.get("/login")
    assert response.status_code == 200
