#!/usr/bin/env python3
"""
Quick test script to verify ElevenLabs integration
Run this to check if ElevenLabs is working correctly
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.conversational_ai_service import ConversationalAIService
from clients.elevenlabs_client import ElevenLabsClient, ELEVENLABS_AVAILABLE

async def test_elevenlabs():
    """Test ElevenLabs functionality"""
    print("🔧 Testing ElevenLabs Integration")
    print("=" * 50)
    
    # Test 1: Check availability
    print("1️⃣ Checking ElevenLabs availability...")
    print(f"   - ELEVENLABS_AVAILABLE: {ELEVENLABS_AVAILABLE}")
    
    if not ELEVENLABS_AVAILABLE:
        print("❌ ElevenLabs is not available")
        return False
    
    # Test 2: Check client initialization
    print("\n2️⃣ Testing client initialization...")
    try:
        client = ElevenLabsClient()
        print(f"   - Client created: {client is not None}")
        print(f"   - Client object: {client.client is not None}")
        
        if client.client is None:
            print("❌ ElevenLabs client is None")
            return False
            
    except Exception as e:
        print(f"❌ Error creating client: {e}")
        return False
    
    # Test 3: Check available methods
    print("\n3️⃣ Checking available methods...")
    try:
        methods = [method for method in dir(client.client) if not method.startswith('_')]
        print(f"   - Available methods: {methods}")
        
        has_generate = hasattr(client.client, 'generate')
        has_voices = hasattr(client.client, 'voices')
        
        print(f"   - Has generate method: {'✅ Yes' if has_generate else '❌ No'}")
        print(f"   - Has voices attribute: {'✅ Yes' if has_voices else '❌ No'}")
        
    except Exception as e:
        print(f"❌ Error checking methods: {e}")
        return False
    
    # Test 4: Test voice generation
    print("\n4️⃣ Testing voice generation...")
    try:
        service = ConversationalAIService()
        test_text = "Hello, this is a test message from ElevenLabs."
        
        print(f"   - Testing with text: '{test_text}'")
        result = await service.text_to_speech(test_text)
        
        if result:
            print(f"   - ✅ Voice generation successful!")
            print(f"   - Base64 length: {len(result)}")
            print(f"   - First 50 chars: {result[:50]}...")
        else:
            print("   - ❌ Voice generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in voice generation: {e}")
        return False
    
    print("\n✅ All tests passed! ElevenLabs is working correctly.")
    return True

if __name__ == "__main__":
    print("🚀 Starting ElevenLabs test...")
    success = asyncio.run(test_elevenlabs())
    
    if success:
        print("\n🎉 ElevenLabs integration is working!")
        sys.exit(0)
    else:
        print("\n💥 ElevenLabs integration has issues!")
        sys.exit(1) 