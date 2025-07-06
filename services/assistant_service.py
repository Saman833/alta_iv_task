from clients.openai_client import OpenAIClient
from services.agent_service import AgentService
from services.message_service import MessageService
from sqlalchemy.orm import Session
from services.content_table_service import ContentTableService

class AssistantService:
    def __init__(self, db: Session):
        self.agent_service = AgentService()
        self.content_table_service = ContentTableService(db)
    def get_assistant_response(self, user_message: str) -> str:
        return self.openai_client.get_assistant_response(user_message)
    def search_on_database(self, user_request: str) -> str:
        messages = self.content_table_service.get_public_summary()
        prompt={
            "user_request": user_request,
            "messages": messages
        }
        response=self.agent_service.run_agent("collect_requested_messages",prompt)
        messages_to_return=[messages[index] for index in response["matching_indices"]]
        return messages_to_return
    def handle_new_chat(self, chat:str) -> str:
        
