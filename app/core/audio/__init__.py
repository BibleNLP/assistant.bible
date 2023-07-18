import schema
from core.audio.whisper import Whisper
from custom_exceptions import GenericException


async def handle_audio_data(
    audio_data, 
    transcription_type:schema.AudioTranscriptionType=schema.AudioTranscriptionType.WHISPER) -> str:
    '''Takes audio input and returns the transcribed text as a string'''

    if transcription_type == schema.AudioTranscriptionType.WHISPER:
        whisper = Whisper()
        user_message = whisper.transcribe_audio(audio_data)
    
    else:
        raise GenericException("This audio transcription type is not supported (yet)!")

    return user_message