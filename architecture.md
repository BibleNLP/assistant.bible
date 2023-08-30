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
        - main.py (FastAPI app, logging settings, CORS etc)
        - schema.py (Pydantic IO object definitions)
        - routers.py (The API endpoints and websocket)
        - log_configs.py 
        - templates/ (HTML templates for index page, demo-ui etc)
        - tests/ (Pytest test cases)
        - core/ (modules, their interfaces and class implementations with different technologies)
            - auth/ 
                - supabase
            - file_processor/ 
                - langchain based
                - vanilla based
            - audio/
                - whisper
            - embedding/
                - openai
                <!-- - huggingface -->
            - vectordb/
                - chroma
                - postgres with pg_vector
            - llm_framework/
                - langchain
                - vanilla
    - logs/ 
    - chromadb/ (default location where vector db will be persisted. not pushed to git)
    - deployment/
        - Dockerfile
        - docker-compose.yml
        - Dockerfile-for-db-backup
    - requirements.txt
    - .pylintrc 


