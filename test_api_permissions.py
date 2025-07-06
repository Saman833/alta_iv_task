#!/usr/bin/env python3
"""
Test script to check ElevenLabs API key permissions
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clients.elevenlabs_client import ElevenLabsClient, ELEVENLABS_AVAILABLE

def test_api_permissions():
    """Test ElevenLabs API key permissions"""
    print("🔧 Testing ElevenLabs API Key Permissions")
    print("=" * 50)
    
    if not ELEVENLABS_AVAILABLE:
        print("❌ ElevenLabs is not available")
        return False
    
    try:
        client = ElevenLabsClient()
        
        if client.client is None:
            print("❌ ElevenLabs client is None")
            return False
        
        print("✅ ElevenLabs client created successfully")
        
        # Test 1: Try to get voices (requires voices_read permission)
        print("\n1️⃣ Testing voices_read permission...")
        try:
            voices = client.client.voices.get_all()
            print(f"✅ voices_read permission: OK - Found {len(voices)} voices")
        except Exception as e:
            print(f"❌ voices_read permission: FAILED - {e}")
        
        # Test 2: Try to generate audio (requires text_to_speech permission)
        print("\n2️⃣ Testing text_to_speech permission...")
        try:
            audio = client.client.text_to_speech.generate(
                text="Hello, this is a test.",
                voice="21m00Tcm4TlvDq8ikWAM",
                model="eleven_multilingual_v1"
            )
            print(f"✅ text_to_speech permission: OK - Generated {len(audio)} bytes")
        except Exception as e:
            print(f"❌ text_to_speech permission: FAILED - {e}")
        
        # Test 3: Check available methods
        print("\n3️⃣ Available API methods:")
        methods = [method for method in dir(client.client) if not method.startswith('_')]
        for method in methods:
            print(f"   - {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API permissions: {e}")
        return False

if __name__ == "__main__":
    success = test_api_permissions()
    
    if success:
        print("\n🎉 API permission test completed!")
    else:
        print("\n💥 API permission test failed!")
    
    sys.exit(0 if success else 1) 