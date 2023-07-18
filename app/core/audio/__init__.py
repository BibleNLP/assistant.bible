import schema
from core.audio.whisper import Whisper
from custom_exceptions import GenericException


class AudioTranscriptionInterface:
    '''Interface for audio transcription technology and its use'''
    api_key: str
    api_object = None
    def __init__(self, key:str, **kwargs) -> None:
        '''Sets the API key and initializes library objects if any'''
        self.api_key = key
    def transcribe_audio(self, audio_data) -> str:
        '''Generate transcription for the audio data'''
        return
