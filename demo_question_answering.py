from db import SessionLocal
from services.iterative_analytics_service import IterativeAnalyticsService
from services.question_answering_service import QuestionAnsweringService
import json

def main():
    """
    Demonstrate the question answering agent that answers client questions
    based on analytics data with detailed reasoning
    """
    print('🤖 QUESTION ANSWERING AGENT DEMONSTRATION')
    print('=' * 60)
    print('This demo shows how to answer client questions using collected analytics data')
    print()
    
    db = None
    try:
        # Initialize services
        print('🔧 Initializing services...')
        db = SessionLocal()
        analytics_service = IterativeAnalyticsService(db)
        qa_service = QuestionAnsweringService(db)
        print('✅ Services ready!')
        print()
        
        # Step 1: Run some analytics to collect data
        print('📊 STEP 1: Collecting Analytics Data')
        print('-' * 40)
        print('Running analytics queries to collect data for answering questions...')
        
        # Run analytics conversation
        initial_result = analytics_service.start_analytics_conversation("Analyze the data patterns and trends")
        follow_up1 = analytics_service.continue_analytics_conversation("Show me category breakdowns")
        follow_up2 = analytics_service.continue_analytics_conversation("What are the key metrics?")
        
        print(f'✅ Completed {len(analytics_service.query_history)} analytics queries')
        print()
        
        # Step 2: Export analytics data
        print('💾 STEP 2: Exporting Analytics Data')
        print('-' * 40)
        analytics_file = analytics_service.export_conversation("saman_test1.json")
        print(f'Analytics data saved to: {analytics_file}')
        print()
        
        # Step 3: Load analytics data for question answering
        print('📖 STEP 3: Loading Analytics Data for Q&A')
        print('-' * 40)
        with open(analytics_file, 'r', encoding='utf-8') as f:
            analytics_data = json.load(f)
        
        print(f'Loaded analytics data with:')
        print(f'  - {len(analytics_data["full_history"])} queries')
        print(f'  - {analytics_data["context"]["successful_queries"]} successful queries')
        print(f'  - {len(analytics_data["context"]["insights_discovered"])} insights discovered')
        print()
        
        # Step 4: Answer client questions
        print('🔍 STEP 4: Answering Client Questions')
        print('-' * 40)
        
        # Example client questions
        client_questions = [
            "What are the main patterns in our data?",
            "What insights can you provide about our business performance?",
            "Are there any concerning trends we should be aware of?",
            "What recommendations do you have based on the analysis?"
        ]
        
        print('Client questions to answer:')
        for i, question in enumerate(client_questions, 1):
            print(f'  {i}. {question}')
        print()
        
        # Answer each question
        qa_results = qa_service.answer_multiple_questions(client_questions, analytics_data)
        
        # Step 5: Display results
        print('📋 STEP 5: Question Answering Results')
        print('-' * 40)
        
        for i, answer in enumerate(qa_results["answers"], 1):
            if answer.get("success", False):
                print(f'\n🔍 Question {i}: {answer["client_question"]}')
                print(f'📝 Answer: {answer["direct_answer"]}')
                print(f'🧠 Reasoning: {answer["detailed_reasoning"][:200]}...')
                print(f'🎯 Confidence: {answer["confidence_level"]}')
                print(f'📊 Evidence sources: {len(answer["supporting_evidence"])}')
                
                # Show supporting evidence
                if answer["supporting_evidence"]:
                    print(f'🔗 Key Evidence:')
                    for evidence in answer["supporting_evidence"][:2]:  # Show first 2 pieces of evidence
                        print(f'   • {evidence["data_source"]}: {evidence["evidence"][:100]}...')
                
                if answer.get("additional_analysis_suggestions"):
                    print(f'💡 Suggestions: {len(answer["additional_analysis_suggestions"])} recommendations for further analysis')
                
            else:
                print(f'\n❌ Question {i}: Failed to answer')
                print(f'   Error: {answer.get("error", "Unknown error")}')
                if answer.get("fallback_answer"):
                    print(f'   Fallback: {answer["fallback_answer"]["answer"]}')
        
        # Step 6: Export Q&A session
        print('\n💾 STEP 6: Exporting Q&A Session')
        print('-' * 40)
        qa_export_file = qa_service.export_qa_session(qa_results, "client_qa_session.json")
        print(f'Q&A session saved to: {qa_export_file}')
        
        # Summary
        session_info = qa_results["session_info"]
        print(f'\n✅ SESSION SUMMARY')
        print(f'📊 Questions answered: {session_info["successful_answers"]}/{session_info["total_questions"]}')
        print(f'🎯 Success rate: {session_info["success_rate"]}%')
        print(f'🏆 High confidence answers: {session_info["high_confidence_answers"]}')
        print(f'📈 Analytics queries used: {session_info["analytics_queries_used"]}')
        
        print('\n🎉 Question Answering Agent demonstration completed!')
        print('The agent successfully used analytics data to provide data-backed answers with reasoning!')
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()
    
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 