import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.agent_service import AgentService
from utils.function_loader import FunctionLoader


class FunctionManagerService:
    """
    Service that manages function selection and execution using the function_manager agent.
    Integrates with the function loader to provide available functions to the agent.
    """
    
    def __init__(self):
        self.agent_service = AgentService()
        self.function_loader = FunctionLoader()
   
    

# Example usage
def main():
    service = FunctionManagerService()
    result = service.function_manager("I want to know summary of the messages")
    print(result)

if __name__ == "__main__":
    main()
        