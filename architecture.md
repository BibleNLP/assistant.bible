# Assistant.Bible

## Technology Stack
* Python 3.10
* FastAPI
* LangChain(?)
* OpenAI APIs
* ChromaDB
* Postgres(?)
* Supabase
* Docker

## Code Base Folder Structure

- assistant.bible
    - app (All files that need to be in docker context)
        - main.py (FastAPI app, endpoint definitions)
        - schema.py (Pydantic IO object definitions)
        - log_configs.py 
        - templates/ (HTML templates for index page, demo-ui etc)
        - tests/ (Pytest test cases)
    - logs/ 
    - chromadb/ (default location where vector db will be persisted. not pushed to git)
    - requirements.txt
    - Dockerfile
    - .pylintrc 


