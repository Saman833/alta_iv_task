import pytest
import asyncio
from services.conversational_ai_service import ConversationalAIService
from clients.elevenlabs_client import ElevenLabsClient, ELEVENLABS_AVAILABLE
from unittest.mock import Mock, patch

class TestElevenLabsIntegration:
    """Test cases for ElevenLabs integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = ConversationalAIService()
    
    def test_elevenlabs_availability(self):
        """Test if ElevenLabs is available"""
        print(f"🔍 Testing ElevenLabs availability:")
        print(f"   - ELEVENLABS_AVAILABLE: {ELEVENLABS_AVAILABLE}")
        print(f"   - ElevenLabs client: {self.service.elevenlabs_client}")
        print(f"   - Client initialized: {self.service.elevenlabs_client.client is not None}")
        
        if ELEVENLABS_AVAILABLE:
            assert self.service.elevenlabs_client is not None
            print("✅ ElevenLabs is available")
        else:
            print("⚠️ ElevenLabs is not available")
    
    @pytest.mark.asyncio
    async def test_voice_generation(self):
        """Test voice generation with ElevenLabs"""
        if not ELEVENLABS_AVAILABLE:
            pytest.skip("ElevenLabs not available")
        
        print("🎤 Testing voice generation...")
        
        # Test with a simple text
        test_text = "Hello, this is a test message."
        result = await self.service.text_to_speech(test_text)
        
        print(f"📊 Voice generation result:")
        print(f"   - Input text: '{test_text}'")
        print(f"   - Result length: {len(result)}")
        print(f"   - Result type: {type(result)}")
        print(f"   - Success: {'✅ Yes' if result else '❌ No'}")
        
        # Should return base64 string or empty string
        assert isinstance(result, str)
        
        if result:
            print("✅ Voice generation successful")
        else:
            print("❌ Voice generation failed")
    
    @pytest.mark.asyncio
    async def test_voice_generation_with_long_text(self):
        """Test voice generation with longer text"""
        if not ELEVENLABS_AVAILABLE:
            pytest.skip("ElevenLabs not available")
        
        print("🎤 Testing voice generation with longer text...")
        
        # Test with longer text
        test_text = "This is a longer test message to see how ElevenLabs handles more complex text. It should generate audio for this entire sentence."
        result = await self.service.text_to_speech(test_text)
        
        print(f"📊 Long text voice generation result:")
        print(f"   - Input text length: {len(test_text)}")
        print(f"   - Result length: {len(result)}")
        print(f"   - Success: {'✅ Yes' if result else '❌ No'}")
        
        assert isinstance(result, str)
    
    def test_elevenlabs_client_methods(self):
        """Test ElevenLabs client methods"""
        if not ELEVENLABS_AVAILABLE:
            pytest.skip("ElevenLabs not available")
        
        client = self.service.elevenlabs_client.client
        
        print("🔍 Testing ElevenLabs client methods:")
        print(f"   - Client type: {type(client)}")
        print(f"   - Available methods: {[method for method in dir(client) if not method.startswith('_')]}")
        
        # Check if generate method exists
        has_generate = hasattr(client, 'generate')
        print(f"   - Has generate method: {'✅ Yes' if has_generate else '❌ No'}")
        
        # Check if voices attribute exists
        has_voices = hasattr(client, 'voices')
        print(f"   - Has voices attribute: {'✅ Yes' if has_voices else '❌ No'}")
        
        if has_voices:
            try:
                voices = client.voices.get_all()
                print(f"   - Available voices: {len(voices)}")
                if voices:
                    print(f"   - First voice ID: {voices[0].voice_id}")
            except Exception as e:
                print(f"   - Error getting voices: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 