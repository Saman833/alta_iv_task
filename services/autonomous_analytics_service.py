from services.analytics_service import AnalyticsService
from services.agent_service import AgentService
from services.sqlite_query_service import SQLiteQueryService
from sqlalchemy.orm import Session
import json
import time
from typing import List, Dict, Any

class AutonomousAnalyticsService(AnalyticsService):
    """
    Autonomous analytics service that executes multiple queries automatically
    to provide comprehensive answers to user questions
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.agent_service = AgentService()
        self.query_service = SQLiteQueryService(db)
        self.execution_results = []
        self.comprehensive_insights = []
    
    def analyze_user_request_autonomously(self, user_input: str, max_queries: int = 5, max_retries: int = 3):
        """
        Analyze user request autonomously with retry logic for database errors
        """
        for attempt in range(max_retries):
            try:
                print(f'\n🔄 Attempt {attempt + 1}/{max_retries} for autonomous analysis')
                
                # Clear previous results
                self.execution_results = []
                self.comprehensive_insights = []
                
                # Get file summaries
                file_summaries = self._get_all_file_summaries()
                
                # Step 1: Generate research plan and multiple queries
                print('\n📋 Step 1: Generating Research Plan...')
                research_plan = self._generate_autonomous_analysis_plan(user_input, file_summaries)
                
                if not research_plan or not research_plan.get("five_step_research_plan"):
                    if attempt < max_retries - 1:
                        print(f'❌ Failed to generate research plan, retrying... (attempt {attempt + 1}/{max_retries})')
                        time.sleep(1)  # Wait before retry
                        continue
                    else:
                        return {
                            "error": "Failed to generate research plan after all retries",
                            "user_input": user_input
                        }
                
                queries = research_plan["five_step_research_plan"]
                print(f'✅ Generated {len(queries)} research steps to execute')
                
                # Step 2: Execute queries in order
                print('\n🔍 Step 2: Executing Research Steps...')
                for i, query_info in enumerate(queries[:max_queries], 1):
                    print(f'\n📊 Step {i}/{len(queries[:max_queries])}: {query_info["step_name"]} - {query_info["step_purpose"]}')
                    
                    try:
                        # Execute query
                        query_result = self._execute_query(query_info["query"])
                        
                        # Store result
                        execution_result = {
                            "step_number": i,
                            "step_name": query_info["step_name"],
                            "query": query_info["query"],
                            "purpose": query_info["step_purpose"],
                            "rationale": query_info["step_rationale"],
                            "deepening_strategy": query_info["deepening_strategy"],
                            "expected_insights": query_info["expected_insights"],
                            "analysis_phase": query_info.get("research_phase", "targeted_analysis"),
                            "result": query_result,
                            "success": query_result.get("success", False)
                        }
                        
                        self.execution_results.append(execution_result)
                        
                        # Extract insights from result
                        if query_result.get("success") and query_result.get("data", {}).get("rows"):
                            insight = self._extract_insight_from_execution(execution_result)
                            if insight:
                                self.comprehensive_insights.append(insight)
                                print(f'💡 Insight: {insight}')
                        
                        print(f'✅ Step {i} completed successfully')
                        
                        # Small delay between queries
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f'❌ Error executing step {i}: {e}')
                        execution_result = {
                            "step_number": i,
                            "step_name": query_info["step_name"],
                            "query": query_info["query"],
                            "purpose": query_info["step_purpose"],
                            "error": str(e),
                            "success": False
                        }
                        self.execution_results.append(execution_result)
                
                # Step 3: Generate comprehensive answer
                print('\n📝 Step 3: Generating Comprehensive Answer...')
                comprehensive_answer = self._generate_comprehensive_answer(user_input, research_plan, self.execution_results)
                
                # Step 4: Generate final user response
                print('\n📋 Step 4: Generating Final User Response...')
                final_user_response = self._generate_final_user_response(user_input, research_plan, self.execution_results, comprehensive_answer)
                
                # Step 5: Prepare final response
                final_response = {
                    "user_question": user_input,
                    "research_plan": research_plan["research_analysis"],
                    "queries_executed": len([r for r in self.execution_results if r.get("success", False)]),
                    "total_queries": len(self.execution_results),
                    "comprehensive_insights": self.comprehensive_insights,
                    "comprehensive_answer": comprehensive_answer,
                    "final_user_response": final_user_response,
                    "execution_details": self.execution_results
                }
                
                print(f'\n✅ Autonomous Analysis Complete (attempt {attempt + 1})')
                print(f'📊 Executed {len(self.execution_results)} queries')
                print(f'💡 Generated {len(self.comprehensive_insights)} insights')
                
                return final_response
                
            except Exception as e:
                print(f'❌ Error in autonomous analysis attempt {attempt + 1}: {e}')
                if attempt < max_retries - 1:
                    print(f'🔄 Retrying in 2 seconds... (attempt {attempt + 1}/{max_retries})')
                    time.sleep(2)  # Wait before retry
                else:
                    print(f'❌ All {max_retries} attempts failed')
                    return {
                        "error": f"Failed to complete analysis after {max_retries} attempts: {str(e)}",
                        "user_input": user_input,
                        "final_user_response": "Unable to generate answer due to database errors. Please try again later."
                    }
    
    def _generate_autonomous_analysis_plan(self, user_input: str, file_summaries: list):
        """
        Generate research plan and multiple queries using the analytics agent
        """
        try:
            # Prepare input for analytics agent with previous query results
            input_data = {
                "original_user_input": user_input,
                "file_summaries": file_summaries,
                "previous_queries": self.execution_results,  # Pass previous query results
                "analysis_context": {
                    "analysis_goal": "comprehensive_database_research",
                    "constraints": {"max_rows": 100},
                    "autonomous_mode": True,
                    "research_mode": True
                }
            }
            
            # Call analytics agent
            print('🤖 Calling analytics agent for database research plan...')
            agent_response = self.agent_service.run_agent("analytics_agent", input_data)
            
            print(f'📊 Agent response type: {type(agent_response)}')
            print(f'📊 Agent response keys: {list(agent_response.keys()) if isinstance(agent_response, dict) else "Not a dict"}')
            print(f'📊 Agent response preview: {str(agent_response)[:200] if agent_response else "None"}')
            
            if not agent_response:
                print('❌ Analytics agent returned empty response')
                return None
            
            # Check if the response has the expected structure
            if not isinstance(agent_response, dict):
                print(f'❌ Analytics agent returned non-dict response: {type(agent_response)}')
                return None
                
            if "five_step_research_plan" not in agent_response:
                print(f'❌ Analytics agent response missing five_step_research_plan key. Available keys: {list(agent_response.keys())}')
                return None
            
            print('✅ Research plan generated successfully')
            return agent_response
            
        except Exception as e:
            print(f'❌ Error generating analysis plan: {e}')
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_insight_from_execution(self, execution_result: dict):
        """
        Extract meaningful insight from query execution result
        """
        try:
            result = execution_result["result"]
            if not result.get("success") or not result.get("data", {}).get("rows"):
                return None
            
            data = result["data"]
            row_count = data.get("row_count", 0)
            columns = data.get("columns", [])
            purpose = execution_result["purpose"]
            
            # Create insight based on query purpose and results
            insight = f"Step {execution_result['step_number']}: {purpose} - Found {row_count} records"
            
            # Add specific insights based on data patterns
            if row_count > 0:
                if any("count" in col.lower() for col in columns):
                    insight += " with count analysis"
                elif any("sum" in col.lower() or "total" in col.lower() for col in columns):
                    insight += " with aggregation analysis"
                elif any("avg" in col.lower() or "average" in col.lower() for col in columns):
                    insight += " with average analysis"
                elif any("category" in col.lower() for col in columns):
                    insight += " with category analysis"
                elif any("date" in col.lower() or "time" in col.lower() for col in columns):
                    insight += " with temporal analysis"
            
            return insight
            
        except Exception as e:
            print(f'⚠️ Error extracting insight: {e}')
            return None
    
    def _generate_comprehensive_answer(self, user_input: str, analysis_plan: dict, execution_results: list):
        """
        Generate comprehensive answer based on all executed queries
        """
        try:
            # Prepare input for question answering agent
            successful_results = [r for r in execution_results if r.get("success", False)]
            
            if not successful_results:
                return "Unable to generate comprehensive answer due to query execution failures."
            
            # Format results for question answering agent
            analytics_history = []
            for result in successful_results:
                analytics_history.append({
                    "query": result["query"],
                    "purpose": result["purpose"],
                    "result": {
                        "success": result["success"],
                        "rows": result["result"].get("data", {}).get("rows", []),
                        "columns": result["result"].get("data", {}).get("columns", []),
                        "row_count": result["result"].get("data", {}).get("row_count", 0)
                    }
                })
            
            # Call question answering agent
            qa_input = {
                "client_question": user_input,
                "analytics_history": analytics_history,
                "file_summaries": self._get_all_file_summaries(),
                "conversation_context": {
                    "total_queries": len(execution_results),
                    "successful_queries": len(successful_results),
                    "analysis_depth": "comprehensive"
                }
            }
            
            print('🧠 Generating comprehensive answer...')
            qa_response = self.agent_service.run_agent("question_answering_agent", qa_input)
            
            if qa_response and "answer_response" in qa_response:
                return qa_response["answer_response"]["direct_answer"]
            else:
                return "Generated comprehensive analysis based on multiple data queries."
                
        except Exception as e:
            print(f'❌ Error generating comprehensive answer: {e}')
            return f"Comprehensive analysis completed with {len(self.comprehensive_insights)} insights discovered."
    
    def _generate_final_user_response(self, user_input: str, research_plan: dict, execution_results: list, comprehensive_answer: str):
        """
        Generate final user response using the final user response agent
        """
        try:
            # Prepare input for final user response agent
            successful_results = [r for r in execution_results if r.get("success", False)]
            
            # Calculate data quality metrics
            total_records = sum(r["result"].get("data", {}).get("row_count", 0) for r in successful_results)
            data_completeness = "High" if len(successful_results) > 0 else "Low"
            confidence_level = "High" if len(successful_results) >= 2 else "Medium"
            
            # Format all available data for the final user response agent
            final_user_response_input = {
                "user_question": user_input,
                "analytics_results": {
                    "total_queries_executed": len(execution_results),
                    "successful_queries": len(successful_results),
                    "query_results": [
                        {
                            "query": r["query"],
                            "purpose": r["purpose"],
                            "result": {
                                "success": r["success"],
                                "rows": r["result"].get("data", {}).get("rows", []),
                                "columns": r["result"].get("data", {}).get("columns", []),
                                "row_count": r["result"].get("data", {}).get("row_count", 0),
                                "data_summary": f"Query {i+1}: {r['purpose']} - {r['result'].get('data', {}).get('row_count', 0)} records"
                            }
                        }
                        for i, r in enumerate(successful_results)
                    ],
                    "key_insights": self.comprehensive_insights,
                    "data_quality_metrics": {
                        "total_records_analyzed": total_records,
                        "data_completeness": data_completeness,
                        "confidence_level": confidence_level
                    }
                },
                "question_answering_response": comprehensive_answer,
                "research_plan": research_plan.get("research_analysis", ""),
                "file_summaries": self._get_all_file_summaries()
            }
            
            print('📋 Calling final user response agent...')
            print(f'📊 Input data keys: {list(final_user_response_input.keys())}')
            print(f'📊 Analytics results keys: {list(final_user_response_input["analytics_results"].keys())}')
            print(f'📊 Query results count: {len(final_user_response_input["analytics_results"]["query_results"])}')
            print(f'📊 Comprehensive answer length: {len(comprehensive_answer)}')
            
            final_user_response = self.agent_service.run_agent("final_user_response_agent", final_user_response_input)
            
            print(f'📊 Final user response agent returned: {type(final_user_response)}')
            print(f'📊 Final user response keys: {list(final_user_response.keys()) if isinstance(final_user_response, dict) else "Not a dict"}')
            
            if final_user_response and "final_user_response" in final_user_response:
                response_text = final_user_response["final_user_response"]
                print(f'✅ Final user response generated successfully, length: {len(response_text)}')
                return response_text
            else:
                print('⚠️ Final user response agent did not return expected format, using fallback')
                # Fallback user response
                return f"""## Analysis Results

**Direct Answer:** {comprehensive_answer}

**Key Findings:**
- Analyzed {len(successful_results)} queries with {total_records} total records
- {len(self.comprehensive_insights)} key insights discovered
- Data quality: {data_completeness} completeness, {confidence_level} confidence

**Recommendations:**
- Review the comprehensive insights generated
- Consider additional analysis if needed
- Use findings for data-driven decision making

**Limitations:** Analysis based on available data only."""
                
        except Exception as e:
            print(f'❌ Error generating final user response: {e}')
            import traceback
            traceback.print_exc()
            return f"""## Analysis Complete

**Answer:** {comprehensive_answer}

**Summary:** Analysis completed with {len(self.comprehensive_insights)} insights from {len(execution_results)} queries.

**Data Quality:** Based on {len([r for r in execution_results if r.get("success", False)])} successful queries."""
    
    def get_execution_summary(self):
        """
        Get summary of autonomous execution
        """
        if not self.execution_results:
            return {"error": "No execution results available"}
        
        successful_queries = sum(1 for r in self.execution_results if r.get("success", False))
        total_queries = len(self.execution_results)
        
        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "success_rate": round(successful_queries / total_queries * 100, 2) if total_queries > 0 else 0,
            "insights_generated": len(self.comprehensive_insights),
            "execution_time": "N/A"  # Could be enhanced with timing
        } 