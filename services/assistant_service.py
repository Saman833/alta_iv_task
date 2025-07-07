from clients.openai_client import OpenAIClient
from services.agent_service import AgentService
from services.message_service import MessageService
from sqlalchemy.orm import Session
from services.content_table_service import ContentTableService
from utils.function_loader import FunctionLoader

class AssistantService:
    def __init__(self, db: Session):
        self.agent_service = AgentService()
        self.content_table_service = ContentTableService(db)
        self.function_loader = FunctionLoader()
    def get_assistant_response(self, user_message: str) -> str:
        return self.openai_client.get_assistant_response(user_message)
    def search_on_database(self, user_request: str) -> str:
        print(f"🔍 Search request: '{user_request}'")
        messages = self.content_table_service.get_public_summary()
        print(f"📊 Total messages available: {len(messages)}")
        
        prompt={
            "user_request": user_request,
            "messages": messages
        }
        
        print(f"🤖 Calling collect_requested_messages agent...")
        response=self.agent_service.run_agent("collect_requested_messages",prompt)
        print(f"📋 Agent response: {response}")
        
        if "matching_indices" in response:
            matching_indices = response["matching_indices"]
            print(f"🎯 Found {len(matching_indices)} matching indices: {matching_indices}")
            messages_to_return=[messages[index] for index in matching_indices]
            print(f"📤 Returning {len(messages_to_return)} messages")
            return messages_to_return
        else:
            print(f"❌ No matching_indices in response: {response}")
            return []
    def get_summary_of_messages(self,user_request:str) -> str:
        messages=self.content_table_service.get_public_summary()
        prompt={
            "user_request": user_request,
            "messages": messages
        }
        response=self.agent_service.run_agent("summary_agent",prompt)
        return response["summary"]
    def agent_manager(self, user_request: str) -> dict:
        """
        Smart assistant manager that decides whether to call functions or respond conversationally.
        Returns a dictionary with response type and content.
        """
        available_functions = self.function_loader.get_available_functions()
        prompt = {
            "user_request": user_request,
            "available_functions": available_functions
        }
        
        try:
            run_agent_response = self.agent_service.run_agent("function_manager", prompt)
            
            # Check if functions were selected
            if "selected_functions" in run_agent_response and run_agent_response["selected_functions"]:
                # Function-based response
                function_results = []
                for function in run_agent_response["selected_functions"]:
                    result = self.run_function(function["function_name"], function["parameters"])
                    if result:
                        function_results.append({
                            "function_name": function["function_name"],
                            "result": result,
                            "reasoning": function.get("reasoning", "")
                        })
                
                if function_results:
                    return {
                        "type": "function_response",
                        "content": self._format_function_response(function_results, user_request),
                        "function_results": function_results
                    }
            
            # No functions selected or no results - fallback to conversational response
            return {
                "type": "conversational",
                "content": "I understand your request, but I don't have specific functions to handle it. Let me respond conversationally.",
                "function_results": []
            }
            
        except Exception as e:
            return {
                "type": "error",
                "content": f"I encountered an error processing your request: {str(e)}",
                "function_results": []
            }
    
    def _format_function_response(self, function_results: list, original_request: str) -> str:
        """Format function results into a natural language, friendly response"""
        if not function_results:
            return "I looked through your messages, but didn't find anything matching your request right now. If you want to look for something else, just let me know!"
        
        response_parts = []
        
        for result in function_results:
            if result["function_name"] == "search_on_database":
                messages = result["result"]
                if messages:
                    response_parts.append(f"I found {len(messages)} messages related to your search:")
                    for i, msg in enumerate(messages[:3], 1):  # Show first 3 messages
                        content = msg.get('content_data', msg.get('content', 'No content'))
                        response_parts.append(f"{i}. {content[:100]}...")
                    if len(messages) > 3:
                        response_parts.append(f"... and {len(messages) - 3} more messages.")
                else:
                    response_parts.append("I checked your messages, but didn't spot anything urgent or matching your search right now. If you want to look for something else, just let me know!")
                    
            elif result["function_name"] == "get_summary_of_messages":
                summary = result["result"]
                response_parts.append(f"Here's a summary based on your request: {summary}")
        
        return " ".join(response_parts)

    def run_function(self, function_name: str, function_input: dict) -> str:
        """
        Execute a function based on the function name and input parameters.
        
        Args:
            function_name: Name of the function to execute
            function_input: Dictionary containing the function parameters
            
        Returns:
            Result of the function execution
        """
        if function_name == "search_on_database":
            user_request = function_input.get("user_request")
            if user_request:
                return self.search_on_database(user_request)
            else:
                return "Error: user_request parameter is required for search_on_database function"
                
        elif function_name == "get_summary_of_messages":
            user_request = function_input.get("user_request")
            if user_request:
                return self.get_summary_of_messages(user_request)
            else:
                return "Error: user_request parameter is required for get_summary_of_messages function"
                
        else:
            return f"Error: Unknown function '{function_name}'" 
       

        
        
