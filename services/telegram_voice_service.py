from models import Source
from clients.telegram_voice_client import TelegramVoiceClient
from clients.openai_client import OpenAIClient
import ffmpeg
import imageio_ffmpeg

class TelegramVoiceService:
    def __init__(self):
        self.telegram_voice_client = TelegramVoiceClient()
        self.openai_client = OpenAIClient()

    def process_voice_message(self, parsed_data: dict):
        if not parsed_data['content_data']['source'] == Source.TELEGRAM:
            raise ValueError(f"Unsupported source: {parsed_data['content_data']['source']}")
        
        # First get the file path from file_id
        file_path = self.telegram_voice_client.get_telegram_file_path(parsed_data['voice_file_id'])
        
        # Then download the voice message using the file path
        voice_message = self.telegram_voice_client.get_voice_message(file_path)
       
        if not voice_message:
            raise ValueError(f"Voice message not found: {parsed_data['voice_file_id']}")
        formated_voice_message = self.convert_ogg_to_mp3_bytes(voice_message)
        voice_message_text = self.openai_client.transcribe_audio(formated_voice_message)

        parsed_data['content_data']['content_data'] = voice_message_text
        return parsed_data
        
    def convert_ogg_to_mp3_bytes(self, ogg_bytes: bytes) -> bytes:
        ff_path = imageio_ffmpeg.get_ffmpeg_exe()
        proc = (
            ffmpeg
            .input("pipe:0")
            .output("pipe:1", format="mp3", ac=1)
            .run_async(cmd=ff_path, pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )
        mp3_bytes, _ = proc.communicate(input=ogg_bytes)
        return mp3_bytes
    
    
    
        
             
    
    