"""API endpoint definitions"""
import os
from typing import List

from fastapi import (
    APIRouter,
    Request,
    Body,
    Path,
    Query,
    Depends,
    UploadFile,
    Form,
    HTTPException,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import SecretStr
import gotrue.errors

import schema
from log_configs import log

from core.auth import admin_auth_check_decorator
from core.pipeline import DataUploadPipeline
from core.vectordb.chroma import Chroma
from core.vectordb.postgres4langchain import Postgres
from core.embedding.openai import OpenAIEmbedding
from core.embedding.sentence_transformers import SentenceTransformerEmbedding
from core.auth.supabase import supa
from custom_exceptions import PermissionException, GenericException


router = APIRouter()
templates = Jinja2Templates(directory="templates")

WS_URL = os.getenv("WEBSOCKET_URL", "ws://localhost:8000/chat")
DOMAIN = os.getenv("DOMAIN", "localhost:8000")
POSTGRES_DB_USER = os.getenv("POSTGRES_DB_USER", "admin")
POSTGRES_DB_PASSWORD = os.getenv("POSTGRES_DB_PASSWORD", "secret")
POSTGRES_DB_HOST = os.getenv("POSTGRES_DB_HOST", "localhost")
POSTGRES_DB_PORT = os.getenv("POSTGRES_DB_PORT", "5432")
POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME", "adotbcollection")
CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH", "chromadb_store")
CHROMA_DB_COLLECTION = os.environ.get("CHROMA_DB_COLLECTION", "adotbcollection")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

UPLOAD_PATH = "./uploaded-files/"


@router.get(
    "/",
    response_class=HTMLResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse},
    },
    status_code=200,
    tags=["General", "UI"],
)
async def index(request: Request):
    """Landing page"""
    log.info("In index router")
    return templates.TemplateResponse(
        "index.html", {"request": request, "demo_url": f"http://{DOMAIN}/app"}
    )


@router.get(
    "/test",
    response_model=schema.APIInfoResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse},
    },
    status_code=200,
    tags=["General"],
)
async def get_root():
    """Landing page with basic info about the App"""
    log.info("In root endpoint")
    return {"message": "App is up and running"}


# @router.get("/ui",
#     response_class=HTMLResponse,
#     responses={
#         422: {"model": schema.APIErrorResponse},
#         403: {"model": schema.APIErrorResponse},
#         500: {"model": schema.APIErrorResponse}},
#     status_code=200, tags=["UI"])
# async def get_ui(request: Request):
#     '''The development UI using http for chat'''
#     log.info("In ui endpoint!!!")
#     return templates.TemplateResponse("chat-demo.html",
#         {"request": request, "ws_url": WS_URL, "demo_url":f"http://{DOMAIN}/ui",
#         "demo_url2":f"http://{DOMAIN}/ui2", "login_url":f"http://{DOMAIN}/login"})


@router.get(
    "/app",
    response_class=HTMLResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse},
    },
    status_code=200,
    tags=["UI"],
)
# @chatbot_auth_check_decorator
async def get_ui2(request: Request):
    """The development UI using http for chat"""
    log.info("In ui endpoint!!!")
    return templates.TemplateResponse(
        "chat-demo-postgres.html",
        {
            "request": request,
            "ws_url": WS_URL,
            "demo_url": f"http://{DOMAIN}/app",
            "login_url": f"http://{DOMAIN}/login",
        },
    )


@router.get(
    "/login",
    response_class=HTMLResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse},
    },
    status_code=200,
    tags=["UI"],
)
async def get_login(request: Request):
    """The development login UI"""
    log.info("In login endpoint!!!")
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "ws_url": WS_URL,
            "demo_url": f"http://{DOMAIN}/ui",
            "demo_url2": f"http://{DOMAIN}/ui2",
        },
    )


def compose_vector_db_args(db_type, settings, embedding_config):
    """Convert the API params or default values to args for initializing the DB."""
    vectordb_args = {}

    if settings.dbHostnPort:
        parts = settings.dbHostnPort.split(":")
        vectordb_args.update({
            "host_n_port": settings.dbHostnPort,
            "host": "".join(parts[:-1]),
            "port": parts[-1]
        })
    elif db_type == schema.DatabaseType.POSTGRES:
        vectordb_args.update({
            "host_n_port": f"{POSTGRES_DB_HOST}:{POSTGRES_DB_PORT}",
            "host": POSTGRES_DB_HOST,
            "port": POSTGRES_DB_PORT
        })

    vectordb_args["user"] = (
        settings.dbUser
        or (POSTGRES_DB_USER if db_type == schema.DatabaseType.POSTGRES else None)
    )
    vectordb_args["password"] = (
        settings.dbPassword.get_secret_value()
        if settings.dbPassword
        else (
            POSTGRES_DB_PASSWORD
            if db_type == schema.DatabaseType.POSTGRES
            else None
        )
    )
    vectordb_args["path"] = (
        settings.dbPath
        or (CHROMA_DB_PATH if db_type == schema.DatabaseType.CHROMA else None)
    )
    vectordb_args["collection_name"] = (
    settings.collectionName
    or CHROMA_DB_COLLECTION if db_type == schema.DatabaseType.CHROMA
    else POSTGRES_DB_NAME if db_type == schema.DatabaseType.POSTGRES
    else None
    )

    if db_type == schema.DatabaseType.POSTGRES:
        log.info(
            "Because the db is Postgres, and embedding dimension size must be hard-coded, "
            + "setting embedding type to %s",
            embedding_config.embeddingType,
        )
        if embedding_config.embeddingType == schema.EmbeddingType.HUGGINGFACE_DEFAULT:
            vectordb_args["embedding"] = SentenceTransformerEmbedding()
        elif (
            embedding_config.embeddingType
            == schema.EmbeddingType.HUGGINGFACE_MULTILINGUAL
        ):
            vectordb_args["embedding"] = SentenceTransformerEmbedding(
                model="sentence-transformers/LaBSE"
            )
        elif embedding_config.embeddingType == schema.EmbeddingType.OPENAI:
            vectordb_args["embedding"] = OpenAIEmbedding()
        else:
            raise GenericException("This embedding type is not supported (yet)!")

    return vectordb_args


@router.post(
    "/upload/sentences",
    response_model=schema.APIInfoResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse},
    },
    status_code=201,
    tags=["Data Management"],
)
@admin_auth_check_decorator
async def upload_sentences(
    document_objs: List[schema.Document] = Body(
        ..., desc="List of pre-processed sentences"
    ),
    vectordb_type: schema.DatabaseType = Query(schema.DatabaseType.CHROMA),
    vectordb_config: schema.DBSelector = Depends(schema.DBSelector),
    embedding_config: schema.EmbeddingSelector = Depends(schema.EmbeddingSelector),
    token: SecretStr = Query(
        None, desc="Optional access token to be used if user accounts not present"
    ),
):
    """* Upload of any kind of data that has been pre-processed as list of sentences.
    * Vectorises the text using OpenAI embdedding (or the one set in chroma DB settings).
    * Keeps other details, sourceTag, link, and media as metadata in vector store
    * embedding_type: optional for ChromaDB. For Postgres, if none, will use OpenAIEmbedding
    """
    log.info("Access token used:%s", token)
    data_stack = DataUploadPipeline()
    vectordb_args = compose_vector_db_args(
        vectordb_type, vectordb_config, embedding_config
    )
    data_stack.set_vectordb(vectordb_type, **vectordb_args)
    data_stack.set_embedding(
        embedding_config.embeddingType,
        embedding_config.embeddingApiKey,
        embedding_config.embeddingModelName,
    )
    # FIXME: This may have to be a background job!!! # pylint: disable=W0511#
    data_stack.embedding.get_embeddings(doc_list=document_objs)

    # FIXME: This may have to be a background job!!! # pylint: disable=W0511
    data_stack.vectordb.add_to_collection(docs=document_objs)
    return {"message": "Documents added to DB"}


@router.post(
    "/upload/text-file",
    response_model=schema.APIInfoResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse},
    },
    status_code=201,
    tags=["Data Management"],
)
@admin_auth_check_decorator
async def upload_text_file(  # pylint: disable=too-many-arguments
    file_obj: UploadFile,
    label: str = Query(
        ..., desc="The label for the set of documents for access based filtering"
    ),
    file_processor_type: schema.FileProcessorType = Query(
        schema.FileProcessorType.LANGCHAIN
    ),
    vectordb_type: schema.DatabaseType = Query(schema.DatabaseType.CHROMA),
    vectordb_config: schema.DBSelector = Depends(schema.DBSelector),
    embedding_config: schema.EmbeddingSelector = Depends(schema.EmbeddingSelector),
    token: SecretStr = Query(
        None, desc="Optional access token to be used if user accounts not present"
    ),
):
    """* Upload of any kind text files like .md, .txt etc.
    * Splits the whole document into smaller chunks using the selected file_processor
    * Vectorises the text using OpenAI embdedding (or the one set in chroma DB settings).
    * Keeps other details, sourceTag, link, and media as metadata in vector store
    * embedding_type: optional for ChromaDB. For Postgres, if none, will use OpenAIEmbedding
    """
    log.info("Access token used: %s", token)
    vectordb_args = compose_vector_db_args(
        vectordb_type, vectordb_config, embedding_config
    )
    data_stack = DataUploadPipeline()
    data_stack.set_vectordb(vectordb_type, **vectordb_args)

    data_stack.set_file_processor(file_processor_type)

    if not os.path.exists(UPLOAD_PATH):
        os.mkdir(UPLOAD_PATH)
    with open(f"{UPLOAD_PATH}{file_obj.filename}", "w", encoding="utf-8") as tfp:
        tfp.write(file_obj.file.read().decode("utf-8"))

    # FIXME: This may have to be a background job!!! # pylint: disable=W0511
    docs = data_stack.file_processor.process_file(
        file=f"{UPLOAD_PATH}{file_obj.filename}",
        file_type=schema.FileType.TEXT,
        label=label,
        name="".join(file_obj.filename.split(".")[:-1]),
    )
    data_stack.set_embedding(
        embedding_config.embeddingType,
        embedding_config.embeddingApiKey,
        embedding_config.embeddingModelName,
    )
    # FIXME: This may have to be a background job!!!
    data_stack.embedding.get_embeddings(doc_list=docs)
    data_stack.vectordb.add_to_collection(docs=docs)
    return {"message": "Documents added to DB"}


@router.post(
    "/upload/csv-file",
    response_model=schema.APIInfoResponse,
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse},
    },
    status_code=201,
    tags=["Data Management"],
)
@admin_auth_check_decorator
async def upload_csv_file(  # pylint: disable=too-many-arguments
    file_obj: UploadFile,
    col_delimiter: schema.CsvColDelimiter = Query(
        schema.CsvColDelimiter.COMMA, desc="Seperator used in input file"
    ),
    vectordb_type: schema.DatabaseType = Query(schema.DatabaseType.CHROMA),
    vectordb_config: schema.DBSelector = Depends(schema.DBSelector),
    embedding_config: schema.EmbeddingSelector = Depends(schema.EmbeddingSelector),
    token: SecretStr = Query(
        None, desc="Optional access token to be used if user accounts not present"
    ),
):
    """* Upload CSV with fields (id, text, label, links, medialinks).
    * Vectorises the text using OpenAI embdedding (or the one set in chroma DB settings).
    * Keeps other details, sourceTag, link, and media as metadata in vector store
    * embedding_type: optional for ChromaDB. For Postgres, if none, will use OpenAIEmbedding
    """
    log.info("Access token used: %s", token)
    vectordb_args = compose_vector_db_args(
        vectordb_type, vectordb_config, embedding_config
    )
    data_stack = DataUploadPipeline()
    data_stack.set_vectordb(vectordb_type, **vectordb_args)
    if not os.path.exists(UPLOAD_PATH):
        os.mkdir(UPLOAD_PATH)
    with open(f"{UPLOAD_PATH}{file_obj.filename}", "w", encoding="utf-8") as tfp:
        tfp.write(file_obj.file.read().decode("utf-8"))

    # FIXME: This may have to be a background job!!! # pylint: disable=W0511
    if col_delimiter == schema.CsvColDelimiter.COMMA:
        col_delimiter = ","
    elif col_delimiter == schema.CsvColDelimiter.TAB:
        col_delimiter = "\t"
    docs = data_stack.file_processor.process_file(
        file=f"{UPLOAD_PATH}{file_obj.filename}",
        file_type=schema.FileType.CSV,
        col_delimiter=col_delimiter,
    )
    data_stack.set_embedding(
        embedding_config.embeddingType,
        embedding_config.embeddingApiKey,
        embedding_config.embeddingModelName,
    )
    # FIXME: This may have to be a background job!!!
    data_stack.embedding.get_embeddings(doc_list=docs)
    data_stack.vectordb.add_to_collection(docs=docs)
    return {"message": "Documents added to DB"}


@router.get(
    "/job/{job_id}",
    response_model=schema.Job,
    responses={
        404: {"model": schema.APIErrorResponse},
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse},
    },
    status_code=200,
    tags=["Data Management"],
)
@admin_auth_check_decorator
async def check_job_status(
    job_id: int = Path(...),
    token: SecretStr = Query(
        None, desc="Optional access token to be used if user accounts not present"
    ),
):
    """Returns the status of background jobs like upload-documemts"""
    log.info("Access token used:%s", token)
    print(job_id)
    return {"jobId": "10001", "status": schema.JobStatus.QUEUED}


@router.get(
    "/source-labels",
    response_model=List[str],
    responses={
        422: {"model": schema.APIErrorResponse},
        403: {"model": schema.APIErrorResponse},
        500: {"model": schema.APIErrorResponse},
    },
    status_code=200,
    tags=["Data Management"],
)
@admin_auth_check_decorator
async def get_source_tags(
    db_type: schema.DatabaseType = schema.DatabaseType.CHROMA,
    settings: schema.DBSelector = Depends(schema.DBSelector),
    embedding_config: schema.EmbeddingSelector = Depends(schema.EmbeddingSelector),
    token: SecretStr = Query(
        None, desc="Optional access token to be used if user accounts not present"
    ),
):
    """Returns the distinct set of source tags available in chorma DB"""
    log.debug(
        "host:port:%s, path:%s, collection:%s",
        settings.dbHostnPort,
        settings.dbPath,
        settings.collectionName,
    )
    log.info("Access token used: %s", token)
    args = compose_vector_db_args(db_type, settings, embedding_config)

    if db_type == schema.DatabaseType.CHROMA:
        vectordb = Chroma(**args)
    elif db_type == schema.DatabaseType.POSTGRES:
        vectordb = Postgres(**args)
    else:
        raise GenericException("This database type is not supported (yet)!")

    return vectordb.get_available_labels()


@router.post("/login")
async def login(
    email=Form(..., desc="Email of the user"),
    password=Form(..., desc="Password of the user"),
):
    """Signs in a user"""
    try:
        data = supa.auth.sign_in_with_password({"email": email, "password": password})
    except gotrue.errors.AuthApiError as error:
        log.info(f"We have an error: {error}")
        print(error)
        if str(error) == "Email not confirmed":
            print("It's an email not confirmed error")
            raise HTTPException(
                status_code=401,
                detail="The user email hasn't been confirmed. "
                "Please confirm your email and then try to log in again.",
            ) from error

        raise PermissionException("Unauthorized access. Invalid token.") from error

    return {
        "message": "User logged in successfully",
        "access_token": data.session.access_token,
    }


@router.post("/logout")
async def logout():
    """Signs out a user"""
    auth_service.conn.auth.sign_out()

    return {
        "message": "User logged out successfully",
        "next_url": f"http://{DOMAIN}/login",
    }


@router.post("/signup")
async def signup(
    email=Form(..., desc="Email of the user"),
    password=Form(..., desc="Password of the user"),
):
    """Signs up a new user"""
    try:
        supa.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )
    except gotrue.errors.AuthApiError as error:
        raise PermissionException("Sign up error") from error

    return {
        "message": "Please check your email to confirm your account.",
        "access_token": None,
    }
