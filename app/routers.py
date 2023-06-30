'''API endpoint definitions'''
import os
from typing import List
from fastapi import (
                    APIRouter,
                    Request,
                    Body, Path, Query,
                    WebSocket, WebSocketDisconnect,
                    Depends,
                    UploadFile)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import schema
from log_configs import log
from core.auth import auth_check_decorator
from core.pipeline import ConversationPipeline, DataUploadPipeline
from core.vectordb.chroma import Chroma
from custom_exceptions import GenericException

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UPLOAD_PATH = "./uploaded-files/"

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
    labels:List[str]=Query(["open-access"], # filtering with labels not implemented yet
        desc="The document sets to be used for answering questions")):
    '''The http chat endpoint'''
    await websocket.accept()

    chat_stack = ConversationPipeline(user=user, labels=labels)

    vectordb_args = {}
    if settings.dbHostnPort:
        parts = settings.vectordbConfig.dbHostnPort.split(":")
        vectordb_args['host'] = "".join(parts[:-1])
        vectordb_args['port'] = parts[-1]
    vectordb_args['path'] = settings.dbPath
    vectordb_args['collection_name']=settings.collectionName
    chat_stack.set_vectordb(settings.vectordbType,**vectordb_args)
    llm_args = {}
    if settings.llmApiKey:
        llm_args['api_key']=settings.llmApiKey
    if settings.llmModelName:
        llm_args['model']=settings.llmModelName
    chat_stack.set_llm_framework(settings.llmFrameworkType,
        vectordb=chat_stack.vectordb, **llm_args)

    ### Not implemented using custom embeddings

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
    response_model=schema.APIInfoResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse}},
    status_code=201, tags=["Data Management"])
@auth_check_decorator
async def upload_sentences(
    document_objs:List[schema.Document]=Body(...,
        desc="List of pre-processed sentences"),
    vectordb_type:schema.DatabaseType=Query(schema.DatabaseType.CHROMA),
    vectordb_config:schema.DBSelector = Body(None,
        desc="If not provided, the default, local db of server is used")):
    '''* Upload of any kind of data that has been pre-processed as list of sentences.
    * Vectorises the text using OpenAI embdedding (or the one set in chroma DB settings).
    * Keeps other details, sourceTag, link, and media as metadata in vector store'''
    data_stack = DataUploadPipeline()
    if vectordb_config is not None:
        vectordb_args = {}
        if vectordb_config.dbHostnPort:
            parts = vectordb_config.dbHostnPort.split(":")
            vectordb_args['host'] = "".join(parts[:-1])
            vectordb_args['port'] = parts[-1]
        vectordb_args['path'] = vectordb_config.dbPath
        vectordb_args['collection_name']=vectordb_config.collectionName
        data_stack.set_vectordb(vectordb_type,**vectordb_args)

    # This may have to be a background job!!!
    data_stack.vectordb.add_to_collection(docs=document_objs)
    return {"message": "Documents added to DB"}

@router.post("/upload/text-file",
    response_model=schema.APIInfoResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse}},
    status_code=201, tags=["Data Management"])
@auth_check_decorator
async def upload_text_file(
    file_obj: UploadFile,
    label:str=Query(..., desc="The label for the set of documents for access based filtering"),
    file_processor_type: schema.FileProcessorType=Query(schema.FileProcessorType.LANGCHAIN),
    vectordb_type:schema.DatabaseType=Query(schema.DatabaseType.CHROMA),
    vectordb_config:schema.DBSelector = Depends(schema.DBSelector),
    ):
    '''* Upload of any kind text files like .md, .txt etc.
    * Splits the whole document into smaller chunks using the selected file_processor
    * Vectorises the text using OpenAI embdedding (or the one set in chroma DB settings).
    * Keeps other details, sourceTag, link, and media as metadata in vector store'''
    data_stack = DataUploadPipeline()
    data_stack.set_file_processor(file_processor_type)
    vectordb_args = {}
    if vectordb_config.dbHostnPort:
        parts = vectordb_config.dbHostnPort.split(":")
        vectordb_args['host'] = "".join(parts[:-1])
        vectordb_args['port'] = parts[-1]
    vectordb_args['path'] = vectordb_config.dbPath
    vectordb_args['collection_name']=vectordb_config.collectionName
    data_stack.set_vectordb(vectordb_type,**vectordb_args)

    if not os.path.exists(UPLOAD_PATH):
        os.mkdir(UPLOAD_PATH)
    with open(f"{UPLOAD_PATH}{file_obj.filename}", 'w', encoding='utf-8') as tfp:
        tfp.write(file_obj.file.read().decode("utf-8"))

    # This may have to be a background job!!!
    docs = data_stack.file_processor.process_file(
        file=f"{UPLOAD_PATH}{file_obj.filename}",
        file_type=schema.FileType.TEXT,
        label=label,
        name="".join(file_obj.filename.split(".")[:-1])
        )
    data_stack.vectordb.add_to_collection(docs=docs)
    return {"message": "Documents added to DB"}

@router.post("/upload/csv-file",
    response_model=schema.APIInfoResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse}},
    status_code=201, tags=["Data Management"])
@auth_check_decorator
async def upload_csv_file(
    file_obj: UploadFile,
    col_delimiter:schema.CsvColDelimiter=Query(schema.CsvColDelimiter.COMMA,
        desc="Seperator used in input file"),
    vectordb_type:schema.DatabaseType=Query(schema.DatabaseType.CHROMA),
    vectordb_config:schema.DBSelector = Depends(schema.DBSelector),
    ):
    '''* Upload CSV with fields (id, text, label, links, medialinks).
    * Vectorises the text using OpenAI embdedding (or the one set in chroma DB settings).
    * Keeps other details, sourceTag, link, and media as metadata in vector store'''
    data_stack = DataUploadPipeline()
    vectordb_args = {}
    if vectordb_config.dbHostnPort:
        parts = vectordb_config.dbHostnPort.split(":")
        vectordb_args['host'] = "".join(parts[:-1])
        vectordb_args['port'] = parts[-1]
    vectordb_args['path'] = vectordb_config.dbPath
    vectordb_args['collection_name']=vectordb_config.collectionName
    data_stack.set_vectordb(vectordb_type,**vectordb_args)

    if not os.path.exists(UPLOAD_PATH):
        os.mkdir(UPLOAD_PATH)
    with open(f"{UPLOAD_PATH}{file_obj.filename}", 'w', encoding='utf-8') as tfp:
        tfp.write(file_obj.file.read().decode("utf-8"))

    # This may have to be a background job!!!
    if col_delimiter==schema.CsvColDelimiter.COMMA:
        col_delimiter=","
    elif col_delimiter==schema.CsvColDelimiter.TAB:
        col_delimiter="\t"
    docs = data_stack.file_processor.process_file(
        file=f"{UPLOAD_PATH}{file_obj.filename}",
        file_type=schema.FileType.CSV,
        col_delimiter=col_delimiter
        )
    data_stack.vectordb.add_to_collection(docs=docs)
    return {"message": "Documents added to DB"}

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
    log.debug("host:port:%s, path:%s, collection:%s",
        settings.dbHostnPort, settings.dbPath, settings.collectionName)
    if db_type == schema.DatabaseType.CHROMA:
        args = {}
        if settings.dbHostnPort is not None:
            parts = settings.dbHostnPort.split(":")
            args['host'] = "".join(parts[:-1])
            args['port'] = parts[-1]
        if settings.dbPath is not None:
            args['path'] = settings.dbPath
        if settings.collectionName is not None:
            args['collection_name'] = settings.collectionName
        vectordb = Chroma(**args)
    else:
        raise GenericException("This database type is not supported (yet)!")

    return vectordb.get_available_labels()
