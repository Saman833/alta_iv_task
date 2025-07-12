import asyncio
import json
import base64
import tempfile
import os
from typing import List, Dict, Any
from fastapi import WebSocket
from clients.openai_client import OpenAIClient
from config import config
from services.assistant_service import AssistantService
from db import SessionLocal

class ConversationalAIService:
    """
    Service for handling conversational AI with voice capabilities.
    Integrates with existing OpenAI and ElevenLabs clients.
    """
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        
        # Initialize AssistantService for smart function handling
        self.db = SessionLocal()
        self.assistant_service = AssistantService(self.db)
        
        # Global conversation history
        self.conversation_history = [
            {
                "role": "system", 
                "content": "You are a helpful, friendly AI assistant having a voice conversation. Keep your responses conversational, natural, and concise (1-2 sentences max)."
            }
        ]
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = [
            {
                "role": "system", 
                "content": "You are a helpful, friendly AI assistant having a voice conversation. Keep your responses conversational, natural, and concise (1-2 sentences max)."
            }
        ]
        print("🔄 Conversation history reset")
    
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio using OpenAI Whisper"""
        try:
            # Check if OpenAI client is available
            if not hasattr(self.openai_client, 'client') or not self.openai_client.client:
                print("❌ OpenAI client not initialized for transcription")
                return ""
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Use OpenAI Whisper API
            with open(temp_file_path, "rb") as audio_file:
                transcript = self.openai_client.transcribe_audio(audio_file.read())
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return transcript
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    async def generate_response(self, text: str) -> str:
        """Generate AI response using smart assistant manager with function capabilities"""
        try:
            print(f"🤖 Processing user request: '{text}'")
            
            # First, try to use the smart assistant manager
            assistant_response = self.assistant_service.agent_manager(text)
            
            if assistant_response["type"] == "function_response":
                # Function was called successfully
                response_content = assistant_response["content"]
                print(f"🔧 Function response: '{response_content}'")
                
                # Add to conversation history
                self.conversation_history.append({"role": "user", "content": text})
                self.conversation_history.append({"role": "assistant", "content": response_content})
                
                return response_content
                
            elif assistant_response["type"] == "conversational":
                # No functions matched, fallback to conversational response
                print("💬 No functions matched, using conversational fallback")
                
                # Add user message to history
                self.conversation_history.append({"role": "user", "content": text})
                
                # Keep only last 10 messages to prevent context from getting too long
                if len(self.conversation_history) > 11:  # 1 system + 10 conversation messages
                    # Keep system message and last 10 conversation messages
                    self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-10:]
                
                # Check if OpenAI client is available
                if not hasattr(self.openai_client, 'client') or not self.openai_client.client:
                    print("❌ OpenAI client not initialized")
                    return "I'm having trouble connecting to my AI services right now."
                
                response = self.openai_client.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=self.conversation_history,
                    max_tokens=100,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content.strip()
                
                # Add AI response to history
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                print(f"💬 Conversational response: '{ai_response}'")
                return ai_response
                
            else:
                # Error occurred
                error_message = assistant_response["content"]
                print(f"❌ Assistant error: {error_message}")
                return f"I encountered an issue: {error_message}"
                
        except Exception as e:
            print(f"❌ Generate response error: {e}")
            return "I'm having some trouble right now, but I'm here to chat!"
    
    async def text_to_speech(self, text: str) -> str:
        """Convert text to speech using ElevenLabs"""
        try:
            print(f"🎤 Generating TTS for: '{text}'")
            
            # Check if ElevenLabs is available
            # if not ELEVENLABS_AVAILABLE:
            #     print("❌ ElevenLabs not available")
            #     return ""
            
            # Check if client is available
            # if not self.elevenlabs_client.client:
            #     print("❌ ElevenLabs client not initialized")
            #     return ""
            
            # Use ElevenLabs text-to-speech with correct API
            print("🔧 Using ElevenLabs TTS API...")
            
            # Use the working approach from the tested code
            # audio_generator = self.elevenlabs_client.client.generate(
            #     text=text,
            #     voice="Rachel",
            #     model="eleven_multilingual_v1"
            # )
            
            # Collect all audio chunks from the generator
            # audio_chunks = []
            # chunk_count = 0
            # for chunk in audio_generator:
            #     audio_chunks.append(chunk)
            #     chunk_count += 1
            
            # print(f"📦 Collected {chunk_count} audio chunks")
            
            # Combine all chunks into a single bytes object
            # audio = b''.join(audio_chunks)
            # print(f"🔊 Total audio size: {len(audio)} bytes")
            
            # Convert to base64
            # audio_base64 = base64.b64encode(audio).decode()
            # print(f"✅ TTS generation successful, base64 length: {len(audio_base64)}")
            # return audio_base64
            
            # Fallback to OpenAI TTS if ElevenLabs is not available
            print("🔧 Falling back to OpenAI TTS...")
            if not hasattr(self.openai_client, 'client') or not self.openai_client.client:
                print("❌ OpenAI client not initialized for TTS")
                return ""
            
            response = self.openai_client.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history + [{"role": "user", "content": text}],
                max_tokens=100,
                temperature=0.7,
                response_format={"type": "text"}
            )
            
            ai_response = response.choices[0].message.content.strip()
            print(f"💬 Conversational response for TTS: '{ai_response}'")
            
            # Add AI response to history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Convert to speech (OpenAI TTS is text-to-text, so no audio generation here)
            return "" # No audio generated for OpenAI TTS
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            print(f"Error details: {type(e).__name__}: {e}")
            return ""
    
    async def handle_websocket_conversation(self, websocket: WebSocket):
        """Handle WebSocket conversation with voice capabilities"""
        await websocket.accept()
        
        try:
            while True:
                # Receive message from client
                message = await websocket.receive_text()
                data = json.loads(message)
                
                if data["type"] == "realtime_audio":
                    # Handle real-time audio for live transcription
                    audio_data = base64.b64decode(data["data"])
                    
                    # Transcribe audio chunk
                    transcript = await self.transcribe_audio(audio_data)
                    if transcript:
                        await websocket.send_text(json.dumps({
                            "type": "realtime_transcription",
                            "text": transcript
                        }))
                        
                elif data["type"] == "final_transcript":
                    # Handle final transcript from real-time speech recognition
                    transcript = data["data"]
                    print(f"📝 Received final transcript: '{transcript}'")
                    
                    await websocket.send_text(json.dumps({
                        "type": "transcription",
                        "text": transcript
                    }))
                    
                    # Check for reset command
                    if transcript.lower().strip() in ["reset", "clear", "start over", "new conversation"]:
                        self.reset_conversation()
                        ai_response = "Conversation reset! How can I help you?"
                    else:
                        # Generate AI response
                        ai_response = await self.generate_response(transcript)
                    
                    await websocket.send_text(json.dumps({
                        "type": "response",
                        "text": ai_response
                    }))
                    
                    # Convert to speech
                    print(f"🎵 Converting response to speech: '{ai_response}'")
                    audio_base64 = await self.text_to_speech(ai_response)
                    if audio_base64:
                        print(f"📤 Sending audio to browser (length: {len(audio_base64)})")
                        await websocket.send_text(json.dumps({
                            "type": "audio",
                            "audio": audio_base64
                        }))
                        print("✅ Audio sent successfully")
                    else:
                        print("❌ No audio generated")
                        
                elif data["type"] == "final_audio":
                    # Handle final audio for complete processing (fallback)
                    audio_data = base64.b64decode(data["data"])
                    
                    # Transcribe final audio
                    transcript = await self.transcribe_audio(audio_data)
                    if transcript:
                        await websocket.send_text(json.dumps({
                            "type": "transcription",
                            "text": transcript
                        }))
                        
                        # Check for reset command
                        if transcript.lower().strip() in ["reset", "clear", "start over", "new conversation"]:
                            self.reset_conversation()
                            ai_response = "Conversation reset! How can I help you?"
                        else:
                            # Generate AI response
                            ai_response = await self.generate_response(transcript)
                        
                        await websocket.send_text(json.dumps({
                            "type": "response",
                            "text": ai_response
                        }))
                        
                        # Convert to speech
                        print(f"🎵 Converting response to speech: '{ai_response}'")
                        audio_base64 = await self.text_to_speech(ai_response)
                        if audio_base64:
                            print(f"📤 Sending audio to browser (length: {len(audio_base64)})")
                            await websocket.send_text(json.dumps({
                                "type": "audio",
                                "audio": audio_base64
                            }))
                            print("✅ Audio sent successfully")
                        else:
                            print("❌ No audio generated")
                    else:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Could not transcribe audio"
                        }))
                
        except Exception as e:
            print(f"WebSocket error: {e}")
            await websocket.close() 