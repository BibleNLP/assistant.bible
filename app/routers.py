'''API endpoint definitions'''
from typing import List
from pydantic import Field
from fastapi import (
                    APIRouter,
                    Request,
                    Body, Path, Query,
                    WebSocket, WebSocketDisconnect,
                    Depends)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import schema
from log_configs import log
from core.auth import auth_check_decorator
from core.pipeline import ConversationPipeline
from core.vectordb.chroma import Chroma
from custom_exceptions import GenericException

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/",
    response_class=HTMLResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse}},
    status_code=200, tags=["General", "UI"])
async def index(request:Request):
    '''Landing page'''
    log.info("In index router")
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/test",
    response_model=schema.APIInfoResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse}},
    status_code=200, tags=["General"])
async def get_root():
    '''Landing page with basic info about the App'''
    log.info("In root endpoint")
    return {"message": "App is up and running"}

@router.get("/ui",
    response_class=HTMLResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse}},
    status_code=200, tags=["UI"])
@auth_check_decorator
async def get_ui(request: Request):
    '''The development UI using http for chat'''
    log.info("In ui endpoint!!!")
    return templates.TemplateResponse("chat-demo.html", {"request": request, "http_url": ""})

@router.websocket("/chat")
@auth_check_decorator
async def websocket_chat_endpoint(websocket: WebSocket,
    settings=Depends(schema.ChatPipelineSelector),
    user:str=Query(..., desc= "user id of the end user accessing the chat bot"),
    labels:List[str]=Query(["open-access"],
        desc="The document sets to be used for answering questions")):
    '''The http chat endpoint'''
    await websocket.accept()

    chat_stack = ConversationPipeline(user=user, labels=labels)

    vectordb_args = {}
    if settings.vectordbConfig is not None:
        vectordb_args['path'] = settings.vectordbConfig.dbPath
        vectordb_args['collection_name']=settings.vectordbConfig.collectionName
    # else:
    #     vectordb_args['path'] = "chromadb_store"
    #     vectordb_args['collection_name']='aDotBCollection_chromaDefaultEmbeddings'
    chat_stack.set_vectordb(settings.vectordbType,**vectordb_args)
    llm_args = {}
    if settings.llmConfig is not None:
        llm_args['api_key']=settings.llmConfig.llmApiKey
        llm_args['model']=settings.llmConfig.lllModelName

    chat_stack.set_llm_framework(settings.llmFrameworkType,
        vectordb=chat_stack.vectordb, **llm_args)
    while True:
        try:
            # Receive and send back the client message
            question = await websocket.receive_text()

            # # send back the response
            # resp = schema.BotResponse(sender=schema.SenderType.USER,
            #     message=question, type=schema.ChatResponseType.QUESTION)
            # await websocket.send_json(resp.dict())


            bot_response = chat_stack.llm_framework.generate_text(
                            query=question, chat_history=chat_stack.chat_history)
            log.debug(f"Human: {question}\nBot:{bot_response['answer']}\n"+\
                "Sources:"+\
                f"{[item.metadata['source'] for item in bot_response['source_documents']]}\n\n")
            chat_stack.chat_history.append((bot_response['question'], bot_response['answer']))

            # Construct a response
            start_resp = schema.BotResponse(sender=schema.SenderType.BOT,
                    message=bot_response['answer'], type=schema.ChatResponseType.ANSWER,
                    sources=[item.metadata['source'] for item in bot_response['source_documents']],
                    media=[])
            await websocket.send_json(start_resp.dict())

        except WebSocketDisconnect:
            chat_stack.vectordb.db_client.persist()
            log.info("websocket disconnect")
            break
        except Exception as exe: #pylint: disable=broad-exception-caught
            log.exception(exe)
            resp = schema.BotResponse(
                sender=schema.SenderType.BOT,
                message="Sorry, something went wrong. Try again.",
                type=schema.ChatResponseType.ERROR,
            )
            await websocket.send_json(resp.dict())

@router.post("/upload/sentences",
    response_model=schema.Job,
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse}},
    status_code=200, tags=["Data Management"])
@auth_check_decorator
async def upload_sentences(
    document_objs:List[schema.Document]=Body(..., desc="List of pre-processed sentences"),
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
        404: {"model": schema.APIErrorResponse},
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse}},
    status_code=200, tags=["Data Management"])
@auth_check_decorator
async def check_job_status(job_id:int = Path(...)):
    '''Returns the status of background jobs like upload-documemts'''
    print(job_id)
    return {"jobId":"10001", "status":schema.JobStatus.QUEUED}

@router.get("/source-labels",
    response_model=List[str],
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse}},
    status_code=200, tags=["Data Management"])
@auth_check_decorator
async def get_source_tags(
    db_type:schema.DatabaseType=schema.DatabaseType.CHROMA,
    settings=Depends(schema.DBSelector)
    ):
    '''Returns the distinct set of source tags available in chorma DB'''
    log.debug("host:%s, port:%s, path:%s, collection:%s", 
        settings.dbHostnPort, settings.dbPath, settings.collectionName)
    if db_type == schema.DatabaseType.CHROMA:
        args = {}
        if settings.dbHostnPort is not None:
            parts = settings.dbHostnPort.split(":")
            args['path'] = parts[0]
            args['host'] = parts[0]
        if settings.dbPath is not None:
            args['path'] = settings.dbPath
        if settings.collectionName is not None:
            args['collection_name'] = settings.collectionName
        vectordb = Chroma(**args)
    else:
        raise GenericException("This database type is not supported (yet)!")

    return vectordb.get_available_labels()
