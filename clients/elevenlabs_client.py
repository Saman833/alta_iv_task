from config import config
from fastapi import HTTPException
import requests

class ElevenLabsClient:
    def __init__(self):
        self.elevenlabs_api_key = config.ELEVENLABS_API_KEY
        
    def start_a_call(self, agent_id : str , phone_number_id : str , to_number : str):
        call_payload = {
                "agent_id": agent_id,
                "agent_phone_number_id": phone_number_id,
                "to_number": to_number
            }
        try:
                resp = requests.post(
                    "https://api.elevenlabs.io/v1/convai/twilio/outbound-call",
                    headers={
                        "xi-api-key": self.elevenlabs_api_key,
                        "Content-Type": "application/json"
                    },
                    json=call_payload,
                )
                return resp.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error starting a call: {str(e)}")

    def connect_phone_number_to_agent_elevenlabs(self, elevenlabs_phone_number_id: str, elevenlabs_agent_id: str) -> str | None:
            print(f"Making ElevenLabs API call: phone_number_id={elevenlabs_phone_number_id}, agent_id={elevenlabs_agent_id}")
            response = requests.patch(
                f"https://api.elevenlabs.io/v1/convai/phone-numbers/{elevenlabs_phone_number_id}",
                headers={
                    "xi-api-key": f"{self.elevenlabs_api_key}"
                },
                json={
                    "agent_id": f"{elevenlabs_agent_id}"
                },
                timeout=10
            )
            print(f"ElevenLabs API response status: {response.status_code}")
            print(f"ElevenLabs API response body: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data.get("phone_number_id")
            else:
                print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
    def create_elevenlabs_agent(self, agent_prompt: str) -> str:
        """
        Create an ElevenLabs agent using the provided configuration.
        Returns the ElevenLabsAgent if successful.
        """
        
        try:    # Use the correct ElevenLabs API request structure
            request_data = {
                "conversation_config": {                     
                    "agent": {
                        "first_message": "hello saman an urgenc",
                    
                        "prompt": {
                            "prompt": agent_prompt
                        }
                    }
                },
                "name": "urgency_detector",
                "tags": ["urgency_detector"]
            }
            
            # Log the request data for debugging
            print(f"ElevenLabs API Request Data: {request_data}")
            
            # Make the API request
            response = requests.post(
                "https://api.elevenlabs.io/v1/convai/agents/create",
                headers={
                    "xi-api-key": self.elevenlabs_api_key
                },
                json=request_data
            )
            
            # Log the response for debugging
            print(f"ElevenLabs API Response: {response.status_code}")
            print(f"Response body: {response.text}")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error creating ElevenLabs agent: {response.text}"
                )
            
            # Parse the response
            response_data = response.json()
            
            # Check if we have a valid response with an agent_id
            if not response_data or "agent_id" not in response_data:
                raise HTTPException(
                    status_code=500,
                    detail=f"Invalid response from ElevenLabs API: missing agent_id. Response: {response_data}"
                )
            
            return response_data["agent_id"] 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating ElevenLabs agent: {str(e)}")
        
    def get_agent_id(self, agent_name: str) -> str:
        response = requests.get(
            f"https://api.elevenlabs.io/v1/convai/agents/{agent_name}",
            headers={"xi-api-key": self.elevenlabs_api_key}
        )
        return response.json()["agent_id"]
    