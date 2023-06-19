"""The entrypoint for the server app."""
import os
import string
import random
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from log_configs import log
import routers


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
    '''Any setup we need on start up'''
    log.info("App is starting...")

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
