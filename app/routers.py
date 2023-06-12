'''API endpoint definitions'''
from typing import List
from fastapi import APIRouter, Request, Body, Path, Query#, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import schema
from log_configs import log
from core.auth import auth_check_decorator

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/",
    response_class=HTMLResponse,
    responses={
        422: {"model": schema.ErrorResponse},
        500: {"model": schema.ErrorResponse}},
    status_code=200, tags=["General", "UI"])
async def index(request:Request):
    '''Landing page'''
    log.info("In index router")
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/test",
    response_model=schema.NormalResponse,
    responses={
        422: {"model": schema.ErrorResponse},
        500: {"model": schema.ErrorResponse}},
    status_code=200, tags=["General"])
async def get_root():
    '''Landing page with basic info about the App'''
    log.info("In root endpoint")
    return {"message": "App is up and running"}

@router.get("/ui",
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

@router.post("/chat",
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

@router.post("/documents/sentences",
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
    print(document_objs, db_config)
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

@router.get("/job/{job_id}",
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

@router.get("/source-tags",
    response_model=List[str],
    responses={
        422: {"model": schema.ErrorResponse},
        403: {"model": schema.ErrorResponse},
        500: {"model": schema.ErrorResponse}},
    status_code=200, tags=["Data Management"])
@auth_check_decorator
async def get_source_tags(
    db_host: str = Query(None, desc="Host name to connect to a remote chroma DB deployment"),
    db_port: str = Query(None, desc="Port to connect to a remote chroma DB deployment"),
    collection_name:str = Query(None, desc="Collection to connect to a remote chroma DB deployment")
):
    '''Returns the distinct set of source tags available in chorma DB'''
    print(db_host, db_port, collection_name)
    source_tags = []
    # metas = DB_COLLECTION.get(
    #         include=["metadatas"]
    #     )
    # source_tags = [item['sourceTag'] for item in metas]

    # Then filter these tags based on requesting users access rights
    return source_tags
