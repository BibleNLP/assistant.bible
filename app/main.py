"""The entrypoint for the server app."""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain.vectorstores import VectorStore

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

@app.get("/")
async def get_root(request: Request):
    '''Landing page with basic info about the App'''
    return {"message": "App is up and running"}

