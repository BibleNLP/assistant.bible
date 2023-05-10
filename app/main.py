"""The entrypoint for the server app."""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain.vectorstores import VectorStore
import chromadb
from chromadb.config import Settings

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
    
    # Option 1
    # This method connects to the DB that get stored on the server itself where the app is running
    chroma_client = chromadb.Client(Settings(
        chroma_db_impl='duckdb+parquet',
        persist_directory="../chromadb"))

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
    # * how authentication for chorma DB access will work in that case
    # * how the connection can be handled like session that is started upon each user's API request

    collection = chroma_client.get_or_create_collection(
        name="adotb_collection",
        # avoid having to create embeddings in two steps before storing and querying
        # embedding_function=custom_openai_emb_fn,
        )
    DB_COLLECTION = collection

@app.get("/")
async def get_root(request: Request):
    '''Landing page with basic info about the App'''
    return {"message": "App is up and running"}

