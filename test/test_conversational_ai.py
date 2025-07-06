import pytest
import asyncio
from services.conversational_ai_service import ConversationalAIService
from unittest.mock import Mock, patch

class TestConversationalAIService:
    """Test cases for ConversationalAIService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = ConversationalAIService()
    
    def test_reset_conversation(self):
        """Test conversation reset functionality"""
        # Add some messages to history
        self.service.conversation_history.append({"role": "user", "content": "test"})
        self.service.conversation_history.append({"role": "assistant", "content": "response"})
        
        # Reset conversation
        self.service.reset_conversation()
        
        # Check that only system message remains
        assert len(self.service.conversation_history) == 1
        assert self.service.conversation_history[0]["role"] == "system"
    
    @pytest.mark.asyncio
    async def test_generate_response_with_mock(self):
        """Test response generation with mocked OpenAI client"""
        with patch.object(self.service.openai_client, 'client') as mock_client:
            # Mock the OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Hello! How can I help you?"
            mock_client.chat.completions.create.return_value = mock_response
            
            # Test response generation
            response = await self.service.generate_response("Hello")
            
            assert response == "Hello! How can I help you?"
            assert len(self.service.conversation_history) == 3  # system + user + assistant
    
    @pytest.mark.asyncio
    async def test_generate_response_without_client(self):
        """Test response generation when OpenAI client is not available"""
        # Remove the client
        self.service.openai_client.client = None
        
        response = await self.service.generate_response("Hello")
        
        assert "trouble connecting" in response.lower()
    
    @pytest.mark.asyncio
    async def test_text_to_speech_without_client(self):
        """Test TTS when ElevenLabs client is not available"""
        # Remove the client
        self.service.elevenlabs_client.client = None
        
        result = await self.service.text_to_speech("Hello")
        
        assert result == ""
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_without_client(self):
        """Test transcription when OpenAI client is not available"""
        # Remove the client
        self.service.openai_client.client = None
        
        result = await self.service.transcribe_audio(b"fake_audio_data")
        
        assert result == ""

if __name__ == "__main__":
    pytest.main([__file__]) 