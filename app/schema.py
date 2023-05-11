'''Defines all input and output classes for API endpoints'''
#pylint: disable=too-many-lines
from typing import Optional, List
# from enum import Enum
from pydantic import BaseModel, Field, AnyUrl#, constr, validator

class NormalResponse(BaseModel):
    '''Response with only a message'''
    message : str = Field(...,example="App is up and running")

class ErrorResponse(BaseModel):
    '''Common error response format'''
    error: str = Field(...,example="Database Error")
    details: str = Field(...,example="Violation of unique constraint blah blah blah")

class TextIn(BaseModel):
    '''Input chat text from the user'''
    text: str = Field(...,example="Who is Jesus?")
    chatId: Optional[str] = Field(None, example=10001)
    sources: List[str] = Field(None,
        desc = "The list of documents to be used for answering",
        example=["tyndale", "Open Bible Stories", "Paratext User Manual", "The Bible"])
    dbHost: str = Field(None, desc="host name to connect to a remote chroma DB deployment")
    dbHost: str = Field(None, desc="port to connect to a remote chroma DB deployment")

class TextOut(BaseModel):
    '''Chat response from bot to user'''
    text: str = Field(...,example="Good Morning to you too!")
    chatId: str = Field(...,example=10001)
    sources: List[AnyUrl] = Field(None,
        example=["https://www.biblegateway.com/passage/?search=Genesis+1%3A1&version=NIV",
                 "https://git.door43.org/Door43-Catalog/en_tw/src/branch/master/"+\
                 "bible/other/creation.md"])
    media: List[AnyUrl] = Field(None,
        example=["https://www.youtube.com/watch?v=teu7BCZTgDs"])
