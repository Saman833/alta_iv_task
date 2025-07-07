import json
import os
from typing import List, Dict, Any

class FunctionLoader:
    """
    Utility class to load function definitions from JSON files.
    Each function is defined in a separate JSON file in the functions/ directory.
    """
    
    def __init__(self, functions_dir: str = "functions"):
        self.functions_dir = functions_dir
    
    def load_function(self, function_name: str) -> Dict[str, Any]:
        """
        Load a single function definition from its JSON file.
        
        Args:
            function_name: Name of the function (without .json extension)
            
        Returns:
            Function definition dictionary
            
        Raises:
            FileNotFoundError: If the function file doesn't exist
            json.JSONDecodeError: If the JSON is invalid
        """
        file_path = os.path.join(self.functions_dir, f"{function_name}.json")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Function definition not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_all_functions(self) -> List[Dict[str, Any]]:
        """
        Load all function definitions from the functions directory.
        
        Returns:
            List of function definition dictionaries
        """
        functions = []
        
        if not os.path.exists(self.functions_dir):
            return functions
        
        for filename in os.listdir(self.functions_dir):
            if filename.endswith('.json'):
                function_name = filename[:-5]  # Remove .json extension
                try:
                    function_def = self.load_function(function_name)
                    functions.append(function_def)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Warning: Could not load function {function_name}: {e}")
                    continue
        
        return functions
    
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """
        Get a list of available functions in the format expected by the function_manager agent.
        
        Returns:
            List of function definitions with function_name, description, and parameters
        """
        all_functions = self.load_all_functions()
        
        # Format for function_manager agent input
        available_functions = []
        for func in all_functions:
            available_functions.append({
                "function_name": func["function_name"],
                "description": func["description"],
                "parameters": func["parameters"]
            })
        
        return available_functions
    
    def get_function_names(self) -> List[str]:
        """
        Get a list of all available function names.
        
        Returns:
            List of function names
        """
        all_functions = self.load_all_functions()
        return [func["function_name"] for func in all_functions]
    
    def function_exists(self, function_name: str) -> bool:
        """
        Check if a function definition exists.
        
        Args:
            function_name: Name of the function to check
            
        Returns:
            True if the function exists, False otherwise
        """
        file_path = os.path.join(self.functions_dir, f"{function_name}.json")
        return os.path.exists(file_path) 