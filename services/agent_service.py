from clients.openai_client import OpenAIClient
import json
from typing import Tuple
from utils.text_utils import clean_text, safe_json_string

class AgentService:
    def __init__(self):
        self.openai_client = OpenAIClient()
    
    def run_agent(self, agent_name: str, input_data: dict):
        # Clean the input data to handle encoding issues
        cleaned_input_data = self._clean_input_data(input_data)
        
        system_prompt, user_message , output_schema = self.create_agent_prompt(agent_name, cleaned_input_data)
        response = self.openai_client.request_agent(system_prompt, user_message, output_schema)
        # Parse the JSON response string into a dictionary
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse agent response as JSON: {e}. Response: {response}")
    
    def _clean_input_data(self, input_data: dict) -> dict:
        """Clean input data to handle encoding issues."""
        cleaned_data = {}
        for key, value in input_data.items():
            if isinstance(value, str):
                cleaned_data[key] = clean_text(value)
            elif isinstance(value, dict):
                cleaned_data[key] = self._clean_input_data(value)
            elif isinstance(value, list):
                cleaned_data[key] = [clean_text(item) if isinstance(item, str) else item for item in value]
            else:
                cleaned_data[key] = value
        return cleaned_data
     
    def create_agent_prompt(self, agent_name: str, input_data: dict) -> Tuple[str, str]:
        """
        this function will create the system prompt , user message and output schema for the agent based
        on the files in the ai_agents folder and the specific agent name 
        """
        try:
            with open(f"ai_agents/{agent_name}/instruction.json", "r", encoding='utf-8') as f:
                instruction = json.load(f)
            
            with open(f"ai_agents/{agent_name}/input_schema.json", "r", encoding='utf-8') as f:
                input_schema = json.load(f)
            
            with open(f"ai_agents/{agent_name}/output_schema.json", "r", encoding='utf-8') as f:
                output_schema = json.load(f)
            
            with open(f"ai_agents/{agent_name}/examples.json", "r", encoding='utf-8') as f:
                examples = json.load(f)
            
             
            system_prompt = f"""
            you are {agent_name}
            fololow instruction below : 
            {instruction}
            the input schema is {input_schema}
            the output schema you is {output_schema}
            
            IMPORTANT: You must respond with valid JSON format only. Do not include any other text.
            """
            
            example_sentence=f"consider the following examples : {examples} to know better about the task . " if examples else ""
            user_message = f"""
            {example_sentence}
            my inputis : 
            {safe_json_string(str(input_data))}
            """
            
            return system_prompt, user_message , output_schema
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Agent configuration file not found: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in agent configuration: {e}")

    

 
        
         
    