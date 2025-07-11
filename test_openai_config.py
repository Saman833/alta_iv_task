from config import config
import os

print('OpenAI Configuration Check:')
print('=' * 40)

# Check if API key is set
api_key = config.OPENAI_API_KEY
print(f'API Key present: {"Yes" if api_key else "No"}')

if api_key:
    print(f'API Key length: {len(api_key)}')
    print(f'API Key starts with: {api_key[:7]}...')
else:
    print('❌ OPENAI_API_KEY is not set in environment variables')
    print('Available environment variables:')
    for key in os.environ:
        if 'OPENAI' in key.upper():
            print(f'  {key}')

# Test agent service initialization
print('\nAgent Service Test:')
print('=' * 40)

try:
    from services.agent_service import AgentService
    agent_service = AgentService()
    print('✅ AgentService initialized successfully')
    
    # Try to access the OpenAI client
    if hasattr(agent_service.openai_client, 'client'):
        print('✅ OpenAI client accessible')
    else:
        print('❌ OpenAI client not accessible')
        
except Exception as e:
    print(f'❌ Error initializing AgentService: {e}')

# Try a minimal test
print('\nMinimal Agent Test:')
print('=' * 40)

try:
    from clients.openai_client import OpenAIClient
    client = OpenAIClient()
    print('✅ OpenAIClient initialized')
    
    if api_key:
        # Try a very simple call
        try:
            response = client.client.models.list()
            print('✅ OpenAI API connection successful')
        except Exception as e:
            print(f'❌ OpenAI API call failed: {e}')
    else:
        print('⏸️  Skipping API test - no API key')
        
except Exception as e:
    print(f'❌ Error testing OpenAI client: {e}')

print('\n' + '=' * 40) 