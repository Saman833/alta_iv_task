from services.agent_service import AgentService
from models import Entity
from utils.text_utils import clean_text

class ClassificationService:
    def __init__(self):
        self.agent_service = AgentService()
        
    def extract_category(self, **kwargs):
        
        try:
            response = self.agent_service.run_agent("category_agent", kwargs)
            category = response.get("category")
            if not category:
                raise ValueError("Agent response missing 'category' field")
            return category
        except Exception as e:
            print(f"Classification failed: {e}. Using 'other' category.") # Fallback to 'other' category if classification fails
            return "other"
    
    def extract_entities(self, **kwargs):
        try:
            # Clean the input data to prevent encoding issues
            cleaned_kwargs = self._clean_kwargs(kwargs)
            
            response = self.agent_service.run_agent("entity_agent", cleaned_kwargs)
            entities_json: list[dict] = response.get("entities")
            if not entities_json:
                return []
            entities = [Entity(**entity) for entity in entities_json]
            return entities
        except Exception as e:
            print(f"Entity extraction failed: {e}")
            # Return empty list instead of raising error to prevent pipeline failure
            return []
    
    def _clean_kwargs(self, kwargs: dict) -> dict:
        """Clean keyword arguments to handle encoding issues."""
        cleaned_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                cleaned_kwargs[key] = clean_text(value)
            elif isinstance(value, dict):
                cleaned_kwargs[key] = self._clean_kwargs(value)
            elif isinstance(value, list):
                cleaned_kwargs[key] = [clean_text(item) if isinstance(item, str) else item for item in value]
            else:
                cleaned_kwargs[key] = value
        return cleaned_kwargs
    
    
    
    
    
    