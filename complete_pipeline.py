from db import SessionLocal
from services.autonomous_analytics_service import AutonomousAnalyticsService
from services.question_answering_service import QuestionAnsweringService
import json

def main():
    """
    Complete pipeline: User input → Analytics → Question Answering → saman_test_1.json
    """
    print('🚀 COMPLETE ANALYTICS + Q&A PIPELINE')
    print('=' * 50)
    
    # Get user input
    print('Please provide your initial request for analysis:')
    user_input = input('👤 Your request: ').strip()
    
    if not user_input:
        user_input = "Analyze the data and show me key insights and patterns"
        print(f'Using default: "{user_input}"')
    
    print(f'\n🎯 Processing: "{user_input}"')
    print('=' * 50)
    
    db = None
    try:
        # Initialize services
        print('🔧 Initializing services...')
        db = SessionLocal()
        analytics_service = AutonomousAnalyticsService(db)
        qa_service = QuestionAnsweringService(db)
        print('✅ Services ready!')
        print()
        
        # Step 1: Run Autonomous Analytics
        print('📊 STEP 1: Running Autonomous Analytics...')
        print('-' * 30)
        
        # Run autonomous analytics (agent plans and executes multiple queries)
        autonomous_result = analytics_service.analyze_user_request_autonomously(user_input, max_queries=5)
        
        print(f'✅ Completed autonomous analysis with {autonomous_result["queries_executed"]} successful queries')
        
        # Get analytics data from autonomous results
        analytics_data = {
            "autonomous_summary": analytics_service.get_execution_summary(),
            "full_history": autonomous_result["execution_details"],
            "comprehensive_insights": autonomous_result["comprehensive_insights"],
            "comprehensive_answer": autonomous_result["comprehensive_answer"]
        }
        print()
        
        # Step 2: Generate Questions and Answers
        print('🤔 STEP 2: Answering Key Questions...')
        print('-' * 30)
        
        # The autonomous analysis already provides comprehensive answers
        # We can ask follow-up questions based on the comprehensive answer
        client_questions = [
            "What are the main insights from this analysis?",
            "What patterns or trends should we be aware of?", 
            "What are the key findings and their business implications?",
            "What recommendations do you have based on this data?"
        ]
        
        # Answer all questions using the comprehensive analysis
        qa_results = qa_service.answer_multiple_questions(client_questions, analytics_data)
        print()
        
        # Step 3: Prepare Final Output
        print('📝 STEP 3: Preparing Final Output...')
        print('-' * 30)
        
        # Create comprehensive final output
        final_output = {
            "pipeline_info": {
                "user_request": user_input,
                "pipeline_type": "Complete Analytics + Question Answering",
                "timestamp": qa_service._get_timestamp(),
                "analytics_queries_executed": len(analytics_service.query_history),
                "questions_answered": len(client_questions),
                "success_rate": qa_results["session_info"]["success_rate"]
            },
            "analytics_summary": {
                "total_queries": analytics_data["context"]["total_queries"],
                "successful_queries": analytics_data["context"]["successful_queries"], 
                "insights_discovered": analytics_data["context"]["insights_discovered"],
                "query_history": analytics_data["full_history"]
            },
            "question_answers": {
                "session_info": qa_results["session_info"],
                "answers": qa_results["answers"]
            },
            "key_insights": [],
            "business_recommendations": []
        }
        
        # Extract key insights and recommendations from Q&A results
        for answer in qa_results["answers"]:
            if answer.get("success", False):
                # Add insights
                insight = {
                    "question": answer["client_question"],
                    "key_finding": answer["direct_answer"],
                    "confidence": answer["confidence_level"]
                }
                final_output["key_insights"].append(insight)
                
                # Add recommendations from additional analysis suggestions
                for suggestion in answer.get("additional_analysis_suggestions", []):
                    recommendation = {
                        "analysis": suggestion["suggested_analysis"],
                        "benefit": suggestion["expected_benefit"],
                        "source_question": answer["client_question"]
                    }
                    final_output["business_recommendations"].append(recommendation)
        
        # Step 4: Save to saman_test_1.json
        print('💾 STEP 4: Saving Final Output...')
        print('-' * 30)
        
        output_filename = "saman_test_1.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, default=str)
        
        print(f'✅ Final output saved to: {output_filename}')
        
        # Show summary
        print('\n🎉 PIPELINE COMPLETED SUCCESSFULLY!')
        print('=' * 50)
        print(f'📊 Analytics Queries: {final_output["pipeline_info"]["analytics_queries_executed"]}')
        print(f'🤔 Questions Answered: {final_output["pipeline_info"]["questions_answered"]}')
        print(f'🎯 Success Rate: {final_output["pipeline_info"]["success_rate"]}%')
        print(f'💡 Key Insights: {len(final_output["key_insights"])}')
        print(f'📈 Business Recommendations: {len(final_output["business_recommendations"])}')
        print(f'📁 Output File: {output_filename}')
        
        # Show sample insights
        if final_output["key_insights"]:
            print('\n🔍 Sample Key Insights:')
            for i, insight in enumerate(final_output["key_insights"][:2], 1):
                print(f'  {i}. {insight["key_finding"][:100]}...')
        
        print(f'\n💾 Complete results saved in {output_filename}')
        
    except Exception as e:
        print(f'❌ Error in pipeline: {str(e)}')
        import traceback
        traceback.print_exc()
    
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 