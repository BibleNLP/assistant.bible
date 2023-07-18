import io
import openai

class Whisper:
    def __init__(self):
        self.audio_file = io.BytesIO()
    
    def transcribe_audio(self, audio_data):
        self.audio_file.write(audio_data)
        self.audio_file.seek(0)
        self.audio_file.name = 'recorded_audio.wav'
        transcript = openai.Audio.transcribe("whisper-1", self.audio_file)
        
        return transcript['text']