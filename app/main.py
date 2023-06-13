"""The entrypoint for the server app."""
import os
import string
import random
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from log_configs import log
import routers

import chromadb
from chromadb.config import Settings

CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH", "../chromadb")
CHROMA_DB_COLLECTION = os.environ.get("CHROMA_DB_COLLECTION", "a_dot_b_collection")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

app = FastAPI(title="Assistant.Bible  APIs", version="0.0.1-alpha.1",
    description="The server application that provides APIs to interact \
with the Assistant.Bible Chatbot App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DB_COLLECTION = None

@app.on_event("startup")
async def startup_event():
    '''Set up ChromaDB connection'''
    log.info("Connecting to vector DB...")
    global DB_COLLECTION # pylint: disable=W0603
    # Option 1
    # This method connects to the DB that get stored on the server itself where the app is running
    chroma_client = chromadb.Client(Settings(
        chroma_db_impl='duckdb+parquet',
        persist_directory=CHROMA_DB_PATH))

    # Option 2
    # This method requires us to run the chroma DB as a separate service (say in docker-compose).
    # In future this would allow us to keep multiple options for DB connection,
    # letting different users set up and host their own chroma DBs where ever they please
    # and just use the correct host and port.
    # chroma_client = chromadb.Client(Settings(chroma_api_impl="rest",
    #         chroma_server_host="localhost",
    #         chroma_server_http_port="8000"
    #     ))
    # Also need to sort out the following
    # * Let the connection details, host, port and collection name be passed in requests
    # * how authentication for chorma DB access will work in that case
    # * how the connection can be handled like session that is started upon each user's API request
    #   to let each user connect to the DB that he prefers and has rights for(fastapi's Depends())

    collection = chroma_client.get_or_create_collection(
        name=CHROMA_DB_COLLECTION,
        # avoid having to create embeddings in two steps before storing and querying
        # embedding_function=custom_openai_emb_fn,
        )
    DB_COLLECTION = collection

@app.middleware("http")
async def log_requests(request: Request, call_next):
    '''Place to define common logging for all API calls'''
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    log.info("rid=%s start request: %s %s",idem, request.method, request.url.path)
    start_time = time.time()
    log.debug("rid=%s request headers: %s",idem, request.headers)
    log.debug("rid=%s request parameters: %s %s",
        idem, request.path_params, request.query_params)

    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_time = f"{process_time:.2f}"
    log.info("rid=%s completed_in=%sms status_code=%s",
        idem, formatted_time, response.status_code)

    return response

app.include_router(routers.router)
