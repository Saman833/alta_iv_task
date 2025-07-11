from db import SessionLocal
from services.question_answering_service import QuestionAnsweringService
import json

def main():
    """
    Debug the question answering agent to see why it's failing
    """
    print('🔍 DEBUGGING QUESTION ANSWERING AGENT')
    print('=' * 50)
    
    db = None
    try:
        # Initialize service
        print('🔧 Initializing services...')
        db = SessionLocal()
        qa_service = QuestionAnsweringService(db)
        print('✅ Services ready!')
        print()
        
        # Create minimal test data
        print('📝 Creating test analytics data...')
        test_analytics_data = {
            "full_history": [
                {
                    "query": "SELECT category, COUNT(*) as total FROM test_table GROUP BY category",
                    "result": {
                        "success": True,
                        "rows": [["Electronics", 10], ["Books", 5]],
                        "columns": ["category", "total"],
                        "row_count": 2
                    },
                    "purpose": "Test query to count items by category"
                }
            ],
            "context": {
                "insights_discovered": ["Electronics has more items than Books"],
                "successful_queries": 1,
                "total_queries": 1
            }
        }
        
        # Test simple question
        print('🤔 Testing simple question...')
        test_question = "What are the main categories in the data?"
        
        result = qa_service.answer_question_from_analytics_data(test_question, test_analytics_data)
        
        print(f'📊 Result success: {result.get("success", False)}')
        if result.get("success"):
            print(f'✅ Answer: {result["direct_answer"]}')
        else:
            print(f'❌ Error: {result.get("error", "Unknown error")}')
            if "agent_response" in result:
                print(f'🔍 Agent response: {json.dumps(result["agent_response"], indent=2)}')
        
    except Exception as e:
        print(f'❌ Debug error: {str(e)}')
        import traceback
        traceback.print_exc()
    
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 