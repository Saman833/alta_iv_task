from sqlalchemy.orm import Session
from services.agent_service import AgentService
from services.analytics_service import AnalyticsService
import json
import traceback

class QuestionAnsweringService:
    """
    Service that answers client questions based on analytics data collected
    from previous queries, providing detailed reasoning and data-backed responses
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.agent_service = AgentService()
        self.analytics_service = AnalyticsService(db)
    
    def answer_question_from_analytics_data(self, client_question: str, analytics_data: dict):
        """
        Answer a client question using data from analytics queries
        
        Args:
            client_question: The question the client wants answered
            analytics_data: Complete analytics data including query history, file summaries, context
            
        Returns:
            Dict with structured answer, reasoning, evidence, and confidence level
        """
        try:
            print(f'🤔 Processing client question: "{client_question}"')
            print('=' * 60)
            
            # Extract analytics components
            query_history = analytics_data.get("full_history", [])
            file_summaries = self._get_file_summaries_for_agent()
            conversation_context = analytics_data.get("context", {})
            
            print(f'📊 Using data from {len(query_history)} analytics queries')
            print(f'📁 Analyzing {len(file_summaries)} data sources')
            
            # Prepare input for the question answering agent
            agent_input = {
                "client_question": client_question,
                "analytics_history": query_history,
                "file_summaries": file_summaries,
                "conversation_context": conversation_context
            }
            
            # Call the question answering agent
            print('🧠 Generating data-backed answer...')
            agent_response = self.agent_service.run_agent(
                agent_name="question_answering_agent",
                input_data=agent_input
            )
            
            print(f'🔍 Agent response type: {type(agent_response)}')
            print(f'🔍 Agent response keys: {list(agent_response.keys()) if isinstance(agent_response, dict) else "Not a dict"}')
            
            # The agent response format is different - it directly contains answer_response
            if not isinstance(agent_response, dict):
                return {
                    "success": False,
                    "error": f"Agent returned non-dict response: {type(agent_response)}",
                    "agent_response": agent_response,
                    "fallback_answer": self._generate_fallback_answer(client_question, query_history)
                }
            
            # Check if we have answer_response directly (new format)
            if "answer_response" in agent_response:
                answer_data = agent_response["answer_response"]
                print('✅ Found answer_response in agent output')
            # Check old format with nested response
            elif "response" in agent_response and "answer_response" in agent_response["response"]:
                answer_data = agent_response["response"]["answer_response"]
                print('✅ Found answer_response in nested response')
            else:
                print(f'❌ No answer_response found in agent output:')
                print(f'   Available fields: {list(agent_response.keys())}')
                return {
                    "success": False,
                    "error": "Agent response missing 'answer_response' field",
                    "agent_response": agent_response,
                    "fallback_answer": self._generate_fallback_answer(client_question, query_history)
                }
            
            result = {
                "success": True,
                "client_question": client_question,
                "direct_answer": answer_data["direct_answer"],
                "detailed_reasoning": answer_data["detailed_reasoning"],
                "supporting_evidence": answer_data["supporting_evidence"],
                "confidence_level": answer_data["confidence_level"],
                "confidence_reasoning": answer_data["confidence_reasoning"],
                "data_limitations": answer_data.get("data_limitations", []),
                "additional_analysis_suggestions": answer_data.get("additional_analysis_suggestions", []),
                "data_sources_used": len(query_history),
                "timestamp": self._get_timestamp()
            }
            
            print(f'✅ Question answered with {answer_data["confidence_level"]} confidence')
            print(f'📋 Answer: {answer_data["direct_answer"][:100]}...')
            
            return result
            
        except Exception as e:
            print(f'❌ Error answering question: {str(e)}')
            return {
                "success": False,
                "error": str(e),
                "fallback_answer": self._generate_fallback_answer(client_question, analytics_data.get("full_history", []))
            }
    
    def answer_question_from_file(self, client_question: str, analytics_file_path: str):
        """
        Answer a client question using analytics data loaded from a JSON file
        
        Args:
            client_question: The question the client wants answered
            analytics_file_path: Path to the JSON file containing analytics data
            
        Returns:
            Dict with structured answer, reasoning, evidence, and confidence level
        """
        try:
            print(f'📁 Loading analytics data from: {analytics_file_path}')
            
            with open(analytics_file_path, 'r', encoding='utf-8') as f:
                analytics_data = json.load(f)
            
            print(f'✅ Analytics data loaded successfully')
            
            return self.answer_question_from_analytics_data(client_question, analytics_data)
            
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Analytics file not found: {analytics_file_path}",
                "suggestion": "Please run analytics first to generate the data file"
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in analytics file: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error loading analytics file: {str(e)}"
            }
    
    def answer_multiple_questions(self, questions: list, analytics_data: dict):
        """
        Answer multiple client questions using the same analytics data
        
        Args:
            questions: List of questions to answer
            analytics_data: Analytics data to use for all questions
            
        Returns:
            Dict with results for all questions
        """
        print(f'📝 Answering {len(questions)} questions using collected analytics data')
        print('=' * 70)
        
        results = {
            "session_info": {
                "total_questions": len(questions),
                "analytics_queries_used": len(analytics_data.get("full_history", [])),
                "timestamp": self._get_timestamp()
            },
            "answers": []
        }
        
        for i, question in enumerate(questions, 1):
            print(f'\n🔍 Question {i}/{len(questions)}')
            answer_result = self.answer_question_from_analytics_data(question, analytics_data)
            
            answer_result["question_number"] = i
            results["answers"].append(answer_result)
            
            # Add small delay between questions to avoid overwhelming the AI
            import time
            time.sleep(1)
        
        # Calculate summary statistics
        successful_answers = sum(1 for ans in results["answers"] if ans.get("success", False))
        high_confidence_answers = sum(1 for ans in results["answers"] if ans.get("confidence_level") == "high")
        
        results["session_info"]["successful_answers"] = successful_answers
        results["session_info"]["high_confidence_answers"] = high_confidence_answers
        results["session_info"]["success_rate"] = round(successful_answers / len(questions) * 100, 2)
        
        print(f'\n✅ Completed answering all questions')
        print(f'📊 Success rate: {results["session_info"]["success_rate"]}%')
        print(f'🎯 High confidence answers: {high_confidence_answers}/{len(questions)}')
        
        return results
    
    def _get_file_summaries_for_agent(self):
        """
        Get file summaries in the format expected by the question answering agent
        """
        try:
            file_summaries = self.analytics_service._get_all_file_summaries()
            
            # Convert to the format expected by the agent
            formatted_summaries = []
            for summary in file_summaries:
                formatted_summaries.append({
                    "table_name": summary["table_name"],
                    "original_file_name": summary["original_file_name"],
                    "file_summary": {
                        "overview": summary["file_summary"]["overview"],
                        "business_domain": summary["file_summary"]["business_domain"]
                    }
                })
            
            return formatted_summaries
            
        except Exception as e:
            print(f'⚠️  Warning: Could not get file summaries: {e}')
            return []
    
    def _generate_fallback_answer(self, question: str, query_history: list):
        """
        Generate a basic fallback answer when the AI agent fails
        """
        successful_queries = [q for q in query_history if q.get("result", {}).get("success", False)]
        
        if not successful_queries:
            return {
                "answer": "I don't have sufficient data to answer this question reliably.",
                "reason": "No successful analytics queries found in the provided data."
            }
        
        # Try to provide a basic data summary
        total_rows = sum(q["result"].get("row_count", 0) for q in successful_queries)
        data_sources = len(set(q.get("purpose", "") for q in successful_queries))
        
        return {
            "answer": f"Based on the available data from {len(successful_queries)} queries analyzing {total_rows} total records, I need more specific analytics to answer '{question}' accurately.",
            "reason": "Fallback response due to AI agent failure. Additional analysis may be needed.",
            "data_available": f"{len(successful_queries)} successful queries, {total_rows} total records, {data_sources} different analysis types"
        }
    
    def _get_timestamp(self):
        """
        Get current timestamp
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def export_qa_session(self, qa_results: dict, filename: str = "qa_session.json"):
        """
        Export question answering session results to a JSON file
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(qa_results, f, indent=2, default=str)
            
            print(f'💾 Q&A session exported to {filename}')
            return filename
            
        except Exception as e:
            print(f'❌ Error exporting Q&A session: {e}')
            return None 