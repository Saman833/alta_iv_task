from config import config
import io
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def transcribe_audio(self, mp3_bytes: bytes) -> str:
        audio = io.BytesIO(mp3_bytes)
        audio.name = "voice.mp3"

        resp = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
            response_format="text"
        )
        return resp  
    def request_agent(self, system_prompt: str, user_message: str , output_schema: dict):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
        