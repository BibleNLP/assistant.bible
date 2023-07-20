"""The entrypoint for the server app."""
import string
import random
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from log_configs import log
import routers

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

@app.exception_handler(Exception)
async def any_exception_handler(request, exc: Exception):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",'Error', str(exc))
    if hasattr(exc, "status_code"):
        status_code=exc.status_code
    else:
        status_code = 500
    if hasattr(exc, "name"):
        error_title = exc.name
    else:
        error_title = "Error"
    if hasattr(exc, "detail"):
        details = exc.detail
    else:
        details = str(exc)
    return JSONResponse(
        status_code =status_code,
        content={"error": error_title, "details" : details},
    )

app.include_router(routers.router)
