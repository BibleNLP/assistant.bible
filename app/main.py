"""The entrypoint for the server app."""
import os
import string
import random
import time
from functools import wraps

from typing import List
from fastapi import FastAPI, Request, Body, Path, Query#, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from log_configs import log
import schema

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

templates = Jinja2Templates(directory="templates")

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


def auth_check_decorator(func):
    '''checks a predefined token in request header'''
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # To be implemented.
        # Uses Supabase, gets user roles
        # Verify the DB requesting to connect to and sources listed for querying are permissible
        # Raises 403 error for unauthorized access
        # Passes the list of accessible sources to the calling function
        return await func(*args, **kwargs)
    return wrapper

@app.get("/",
    response_class=HTMLResponse,
    responses={
        422: {"model": schema.ErrorResponse},
        500: {"model": schema.ErrorResponse}},
    status_code=200, tags=["General", "UI"])
async def index(request:Request):
    '''Landing page'''
    log.info("In index router")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/test",
    response_model=schema.NormalResponse,
    responses={
        422: {"model": schema.ErrorResponse},
        500: {"model": schema.ErrorResponse}},
    status_code=200, tags=["General"])
async def get_root():
    '''Landing page with basic info about the App'''
    log.info("In root endpoint")
    return {"message": "App is up and running"}

@app.get("/ui",
    response_class=HTMLResponse,
    responses={
        422: {"model": schema.ErrorResponse},
        403: {"model": schema.ErrorResponse},
        500: {"model": schema.ErrorResponse}},
    status_code=200, tags=["UI"])
@auth_check_decorator
async def get_ui(request: Request):
    '''The development UI using http for chat'''
    log.info("In ui endpoint!!!")
    return templates.TemplateResponse("chat-demo.html", {"request": request, "http_url": ""})

@app.post("/chat",
    response_model=schema.ChatOut,
    responses={
        422: {"model": schema.ErrorResponse},
        403: {"model": schema.ErrorResponse},
        500: {"model": schema.ErrorResponse}},
    status_code=200, tags=["ChatBot"])
@auth_check_decorator
async def http_chat_endpoint(input_obj: schema.ChatIn):
    '''The http chat endpoint'''
    new_response = ""
    sources_list = []
    chat_id = 000
    if input_obj.chatId is not None:
        chat_id = input_obj.chatId
    # get chat history+question embedding
    # get matched documents from vector store, using filters for permissible sources
    # get new response from LLM
    # post process the response(
        # filter out of context answers,
        # add links, images, etc
        # translate )
    return {"text": new_response, "chatId": chat_id, "sources": sources_list}

@app.post("/documents/sentences",
    response_model=schema.Job,
    responses={
        422: {"model": schema.ErrorResponse},
        403: {"model": schema.ErrorResponse},
        500: {"model": schema.ErrorResponse}},
    status_code=200, tags=["Data Management"])
@auth_check_decorator
async def upload_documents(
    document_objs:List[schema.SourceSentence]=Body(..., desc="List of pre-processed sentences"),
    db_config:schema.DBSelector = Body(None, desc="If not provided, local db of server is used")):
    '''* Upload of any kind of data that has been pre-processed as list of sentences.
    * Vectorises the text using OpenAI embdedding (or the one set in chroma DB settings).
    * Keeps other details, sourceTag, link, and media as metadata in vector store'''
    print(document_objs)
    # Get openAI embeddings
    # documents = [item['text'] for item in document_objs]
    # embeddings = OpenAIEmbeddings()
    # Add the data to vetcorstore (ChromaDB)
    # DB_COLLECTION.add(
    #     embeddings=embeddings,
    #     documents=documents,
    #     metadatas=[{
    #                "sourceTag":item['sourceTag']
    #                "link": item['link'],
    #                "media": item['media'],
    #                } for item in documents],
    #     ids=[item["senId"] for item in raw_documents]
    # )

    # This may have to be a background job!!!

    return {"jobId":"10001", "status":schema.JobStatus.QUEUED}

@app.get("/job/{job_id}",
    response_model=schema.Job,
    responses={
        404: {"model": schema.ErrorResponse},
        422: {"model": schema.ErrorResponse},
        403: {"model": schema.ErrorResponse},
        500: {"model": schema.ErrorResponse}},
    status_code=200, tags=["Data Management"])
@auth_check_decorator
async def check_job_status(job_id:int = Path(...)):
    '''Returns the status of background jobs like upload-documemts'''
    print(job_id)
    return {"jobId":"10001", "status":schema.JobStatus.QUEUED}

@app.get("/source-tags",
    response_model=List[str],
    responses={
        422: {"model": schema.ErrorResponse},
        403: {"model": schema.ErrorResponse},
        500: {"model": schema.ErrorResponse}},
    status_code=200, tags=["Data Management"])
@auth_check_decorator
async def get_source_tags(
    dbHost: str = Query(None, desc="Host name to connect to a remote chroma DB deployment"),
    dbPort: str = Query(None, desc="Port to connect to a remote chroma DB deployment"),
    collectionName:str = Query(None, desc="Collection to connect to a remote chroma DB deployment")
):
    '''Returns the distinct set of source tags available in chorma DB'''
    print(dbHost, dbPort, collectionName)
    source_tags = []
    # metas = DB_COLLECTION.get(
    #         include=["metadatas"]
    #     )
    # source_tags = [item['sourceTag'] for item in metas]

    # Then filter these tags based on requesting users access rights
    return source_tags
