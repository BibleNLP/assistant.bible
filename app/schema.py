'''Defines all input and output classes for API endpoints'''
#pylint: disable=too-many-lines
from typing import Optional#, List
# from enum import Enum
from pydantic import BaseModel, Field#, constr, validator

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

class TextOut(BaseModel):
    '''Chat response from bot to user'''
    text: str = Field(...,example="Good Morning to you too!")
    chatId: str = Field(...,example=10001)
