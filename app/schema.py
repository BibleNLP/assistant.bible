'''Defines all input and output classes for API endpoints'''
#pylint: disable=too-many-lines
from typing import List
from enum import Enum
from pydantic import BaseModel, Field, AnyUrl, constr, SecretStr#, validator

class APIInfoResponse(BaseModel):
    '''Response with only a message'''
    message : str = Field(...,example="App is up and running")

class APIErrorResponse(BaseModel):
    '''Common error response format'''
    error: str = Field(...,example="Database Error")
    details: str = Field(...,example="Violation of unique constraint blah blah blah")

class FileProcessorType(str, Enum):
    '''Available file processor technology choices'''
    LANGCHAIN = "Langchain-loaders"
    VANILLA = "Vanilla-Python-loaders"

class EmbeddingType(str, Enum):
    '''Available text embedding technology choices'''
    HUGGINGFACE_DEFAULT = "huggingface" # TODO: add support for multiple models ?
    OPENAI = "OpenAI"

class DatabaseType(str, Enum):
    '''Available Database type choices'''
    CHROMA = "chroma-db"
    POSTGRES = "postgres-with-pgvector"

class LLMFrameworkType(str, Enum):
    '''Available framework types'''
    LANGCHAIN = "openai-langchain"

class AudioTranscriptionType(str, Enum):
    '''The type fo text-to-speech audio transcription'''
    WHISPER = "whisper"

class FileType(str, Enum):
    '''Supported file/content types for populating DB'''
    TEXT = "Continuous text"
    MD = "Generic markdown"
    CSV = "CSV with fields (id, text, label, links, medialinks)"
    # USFM = "Bible book in USFM format"
    # USX = "Bible book in USFM format"

class CsvColDelimiter(str, Enum):
    '''Delimiter for the uploaded CSV file'''
    COMMA = "comma"
    TAB = "tab"

HostnPortPattern = constr(regex=r"^.*:\d+$")

class DBSelector(BaseModel):
    '''The credentials to connect to a remotely hosted chorma DB'''
    # dbTech: str = Field(DatabaseTech.CHROMA, desc="Technology choice like chroma, pinecone etc")
    dbHostnPort: HostnPortPattern = Field(None,
                            example="api.vachanengine.org:6000",
                            desc="Host and port name to connect to a remote DB deployment")
    dbPath: str= Field("chromadb_store",
                            desc="Local DB's folder path. Dont use path with slash!!!")
    collectionName:str = Field("adotbcollection",
                            desc="Collection to connect to in a local/remote DB."+\
                            "One collection should use single embedding type for all docs")
    dbUser:str = Field(None, desc="Creds to connect to the server or remote db")
    dbPassword:SecretStr = Field(None, desc="Creds to connect to the server or remote db")

class EmbeddingSelector(BaseModel):
    '''The credentials to connect to an Embedding creation service'''
    embeddingApiKey: str = Field(None,
                    desc="If using a cloud service, like OpenAI, the key obtained from them")
    embeddingModelName: str = Field(None,
                    desc="If there is a model we can choose to use from the available")

class LLMFrameworkSelector(BaseModel):
    '''The credentials and configs to be used in the LLM and its framework'''
    llmApiKey: str = Field(None, desc="If using a cloud service, like OpenAI, the key from them")
    llmModelName: str = Field(None, desc="The model to be used for chat completion")

class ChatPipelineSelector(BaseModel):
    '''Construct the Conversation Pipeline at the start of a connection from UI app'''
    llmFrameworkType: LLMFrameworkType = Field(LLMFrameworkType.LANGCHAIN,
                    desc="The framework through which LLM access is handled")
    llmApiKey: str = Field(None, desc="If using a cloud service, like OpenAI, the key from them")
    llmModelName: str = Field(None, desc="The model to be used for chat completion")
    vectordbType: DatabaseType = Field(DatabaseType.POSTGRES,
                    desc="The Database to be connected to. Same one used for dataupload")
    dbHostnPort: HostnPortPattern = Field(None,
                            example="api.vachanengine.org:6000",
                            desc="Host and port name to connect to a remote DB deployment")
    dbPath: str= Field("chromadb_store",
                            desc="Local DB's folder path. Dont use path with slash!!!")
    collectionName:str = Field("adotbcollection",
                            desc="Collection to connect to in a local/remote DB."+\
                            "One collection should use single embedding type for all docs")
    dbUser:str = Field(None, desc="Creds to connect to the server or remote db")
    dbPassword:SecretStr = Field(None, desc="Creds to connect to the server or remote db")
    embeddingType:EmbeddingType = Field(EmbeddingType.HUGGINGFACE_DEFAULT,
                    desc="EmbeddingType used for storing and searching documents in vectordb")
    embeddingApiKey: str = Field(None,
                    desc="If using a cloud service, like OpenAI, the key obtained from them")
    embeddingModelName: str = Field(None,
                    desc="If there is a model we can choose to use from the available")
    transcriptionFrameworkType: AudioTranscriptionType = Field(AudioTranscriptionType.WHISPER,
                    desc="The framework through which audio transcription is handled")

# class UserPrompt(BaseModel): # not using this as we recieve string from websocket
#     '''Input chat text from the user'''
#     text: str = Field(...,example="Who is Jesus?")

class SenderType(str, Enum):
    '''Supported file/content types for populating DB'''
    USER = "You"
    BOT = "Bot"

class ChatResponseType(str, Enum):
    '''The type field values for a botResponse'''
    QUESTION = "question"
    ANSWER = "answer"
    ERROR = "error"


class BotResponse(BaseModel):
    '''Chat response from server to UI or user app'''
    message: str = Field(...,example="Good Morning to you too!")
    sender: SenderType = Field(...,example="You or BOT")
    sources: List[str] = Field(None,
        example=["https://www.biblegateway.com/passage/?search=Genesis+1%3A1&version=NIV",
                 "https://git.door43.org/Door43-Catalog/en_tw/src/branch/master/"+\
                 "bible/other/creation.md"])
    media: List[AnyUrl] = Field(None,
        example=["https://www.youtube.com/watch?v=teu7BCZTgDs"])
    type: ChatResponseType = Field(..., example="answer or error")

class JobStatus(str, Enum):
    '''Valid values for Background Job Status'''
    QUEUED = 'queued'
    STARTED = 'started'
    FINISHED = 'finished'
    FAILED = 'failed'

class Job(BaseModel):
    '''Response object of Background Job status check'''
    jobId: int = Field(..., example=100000)
    status: JobStatus = Field(..., example="started")
    output: dict = Field(None, example={
        'error': 'Gateway Error',
        'details': 'Connect to OpenAI terminated unexpectedly'
        })

class Document(BaseModel):
    '''List of sentences to be vectorised and stored for later querying'''
    docId: str = Field(...,
                        example="NIV Bible Mat 1:1-20",
                        desc="Unique for a sentence. Used by the LLM to specify which document "+\
                        "it answers from. Better to combine the source tag and a serial number.")
    text: str = Field(..., desc="The sentence to be vectorised and used for question answering")
    embedding: List[float] = Field(None, desc="vector embedding for the text field")
    label: str = Field("open-access",
                        example="paratext user manual or bible or door-43-users",
                        desc="The common tag for all sentences under a set. "+\
                        "Used for specifying access rules and filtering during querying")
    links: List[AnyUrl] = Field([], desc="The links to fetch the actual resource. "+\
                        "To be used by end user like a search result")
    media: List[AnyUrl] = Field([], desc="Additional media links, like images, videos etc "+\
                        "to be used in output to make the chat interface multimodel")
    metadata: dict = Field({}, desc="Any additional data that needs to go along with the text,"+\
                        " as per usecases. Could help in pre- and/or post-processing",
                        example={"displayimages": True})

class SupabaseKeys(BaseModel):
    supabaseUrl: str
    supabaseKey: str