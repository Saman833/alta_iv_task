from services.analytics_service import AnalyticsService
from sqlalchemy.orm import Session
import json
from typing import List, Dict, Any, Optional

class IterativeAnalyticsService(AnalyticsService):
    """
    Extended analytics service that maintains conversation history and context
    for iterative analysis
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.query_history = []  # This should store SQL queries and their results
        self.conversation_context = {
            "insights_discovered": [],
            "successful_queries": 0,
            "total_queries": 0,
            "current_focus": "",
            "discovered_patterns": []
        }
    
    def start_analytics_conversation(self, initial_user_input: str):
        """
        Start a new analytics conversation
        """
        print(f'🚀 Starting Analytics Conversation')
        print('=' * 60)
        
        # Clear previous history
        self.query_history = []
        self.conversation_context = {
            "insights_discovered": [],
            "successful_queries": 0,
            "total_queries": 0,
            "current_focus": initial_user_input,
            "discovered_patterns": []
        }
        
        # Run initial analysis
        result = self.analyze_user_request(initial_user_input)
        
        # Store SQL query and result in history (not user input)
        self._add_sql_query_to_history(
            query=result["generated_query"], 
            result=result["query_result"],
            purpose=result["query_purpose"]
        )
        
        return result
    
    def continue_analytics_conversation(self, follow_up_input: str):
        """
        Continue the analytics conversation with context
        """
        print(f'\n🔄 Continuing Analytics Conversation')
        print('-' * 50)
        print(f'Previous queries executed: {len(self.query_history)}')
        
        # Get file summaries
        file_summaries = self._get_all_file_summaries()
        
        # Enhanced prompt with conversation context
        enhanced_prompt = self._enhance_user_prompt(follow_up_input, file_summaries, self._get_conversation_context())
        
        # Generate query with context
        query_response = self._generate_analytics_query_with_context(
            follow_up_input, 
            enhanced_prompt, 
            file_summaries, 
            self._get_conversation_context()
        )
        
        query_result = self._execute_query(query_response["analysis_response"]["query"])
        
        result = {
            "original_input": follow_up_input,
            "enhanced_prompt": enhanced_prompt,
            "generated_query": query_response["analysis_response"]["query"],
            "query_purpose": query_response["analysis_response"]["query_purpose"],
            "query_result": query_result,
            "next_steps": query_response["analysis_response"]["anticipated_next_steps"]
        }
        
        # Store SQL query and result in history (not user input)
        self._add_sql_query_to_history(
            query=result["generated_query"], 
            result=result["query_result"],
            purpose=result["query_purpose"]
        )
        
        return result
    
    def _add_sql_query_to_history(self, query: str, result: dict, purpose: str):
        """
        Add SQL query and its execution result to history
        This matches the format expected by analytics agent examples
        """
        # Format the result according to analytics agent expectations
        formatted_result = {
            "success": result.get("success", False),
            "rows": result.get("data", {}).get("rows", []) if result.get("success") else [],
            "columns": result.get("data", {}).get("columns", []) if result.get("success") else [],
            "row_count": result.get("data", {}).get("row_count", 0) if result.get("success") else 0
        }
        
        # Add to query history in the format expected by analytics agent
        query_entry = {
            "query": query,
            "result": formatted_result,
            "purpose": purpose
        }
        
        self.query_history.append(query_entry)
        
        # Update conversation context
        self.conversation_context["total_queries"] += 1
        if result.get("success"):
            self.conversation_context["successful_queries"] += 1
        
        # Extract insights if successful
        if result.get("success") and result.get("data", {}).get("rows"):
            insight = self._extract_insight_from_result(query, result, purpose)
            if insight:
                self.conversation_context["insights_discovered"].append(insight)
        
        print(f'📝 Added to query history: {purpose}')
        print(f'   Query: {query[:100]}...')
        print(f'   Success: {formatted_result["success"]}')
        if formatted_result["success"]:
            print(f'   Rows returned: {formatted_result["row_count"]}')
    
    def _get_conversation_context(self):
        """
        Get context for the analytics agent
        """
        return {
            "previous_queries": self.query_history,  # Now contains SQL queries and results
            "previous_results": [],  # Keep empty since results are in previous_queries
            "insights_discovered": self.conversation_context["insights_discovered"],
            "successful_queries": self.conversation_context["successful_queries"],
            "total_queries": self.conversation_context["total_queries"],
            "current_focus": self.conversation_context["current_focus"]
        }
    
    def _enhance_user_prompt(self, user_input: str, file_summaries: list, context_info: dict):
        """
        Enhance user prompt with conversation history
        """
        input_data = {
            "original_user_prompt": user_input,
            "file_summaries": file_summaries,
            "conversation_context": context_info
        }
        
        try:
            result = self.agent_service.run_agent("enhanced_user_prompt_agent", input_data)
            return result["enhanced_prompt"]
        except Exception as e:
            print(f"⚠️  Enhanced prompt agent failed: {e}")
            # Fallback to basic enhancement
            return {
                "enhanced_user_request": user_input,
                "context_summary": f"Continuing analysis based on {len(context_info.get('previous_queries', []))} previous queries",
                "analysis_objectives": ["Build upon previous findings", "Explore related data patterns"]
            }
    
    def _generate_analytics_query_with_context(self, original_input: str, enhanced_prompt: dict, file_summaries: list, context_info: dict):
        """
        Generate analytics query with conversation context
        """
        input_data = {
            "original_user_input": original_input,
            "enhanced_user_prompt": enhanced_prompt,
            "file_summaries": file_summaries,
            "previous_queries": context_info.get("previous_queries", []),
            "previous_results": context_info.get("previous_results", []),
            "analysis_context": {
                "analysis_goal": "iterative_exploration",
                "constraints": {"max_rows": 100},
                "conversation_stage": len(self.query_history) + 1
            }
        }
        
        try:
            return self.agent_service.run_agent("analytics_agent", input_data)
        except Exception as e:
            print(f"⚠️  Analytics agent failed: {e}")
            # Fallback query generation
            return {
                "analysis_response": {
                    "query": "SELECT COUNT(*) as total_rows FROM " + file_summaries[0]["table_name"] if file_summaries else "SELECT 1",
                    "query_purpose": "Fallback query due to agent failure",
                    "anticipated_next_steps": ["Review query results", "Refine analysis approach"]
                }
            }
    
    def _generate_follow_up_query(self):
        """
        Generate an intelligent follow-up query based on previous results
        """
        if not self.query_history:
            return "Show me an overview of my data"
        
        last_entry = self.query_history[-1]
        last_result = last_entry["result"]
        iteration_number = len(self.query_history)
        
        # Analyze the last result to suggest follow-up
        if last_result["success"]:
            data = last_result["data"]
            columns = data.get("columns", [])
            row_count = data.get("row_count", 0)
            
            # Progressive query complexity based on iteration
            if iteration_number == 1:
                # After initial overview, go deeper into categories
                if any("category" in col.lower() for col in columns):
                    return "Show me the distribution of categories and their frequency"
                else:
                    return "Analyze the main categories and types in my data"
            
            elif iteration_number == 2:
                # After category analysis, look at relationships
                if any("category" in col.lower() for col in columns):
                    return "Show me detailed breakdown of the most populated categories with examples"
                elif any("visitor" in col.lower() or "session" in col.lower() for col in columns):
                    return "Analyze visitor session patterns and user engagement metrics"
                else:
                    return "Find relationships and correlations between different data fields"
            
            elif iteration_number == 3:
                # After relationships, look at trends
                if any("date" in col.lower() or "time" in col.lower() for col in columns):
                    return "Analyze temporal trends and patterns over time"
                elif any("content" in col.lower() for col in columns):
                    return "Analyze content patterns and common themes in the data"
                else:
                    return "Identify outliers and unusual patterns in the dataset"
            
            elif iteration_number == 4:
                # After trends, focus on insights
                if row_count > 10:
                    return "Find the most significant insights and actionable patterns"
                else:
                    return "Summarize key findings and provide business recommendations"
            
            else:
                # For later iterations, focus on specific insights
                advanced_queries = [
                    "Identify anomalies and exceptional cases in the data",
                    "Compare different segments and find performance differences",
                    "Analyze conversion patterns and success metrics",
                    "Find correlations between user behavior and outcomes"
                ]
                # Cycle through advanced queries
                return advanced_queries[(iteration_number - 5) % len(advanced_queries)]
        else:
            # If last query failed, try something simpler
            if iteration_number == 1:
                return "Show me basic statistics and row counts for all tables"
            else:
                return "Try a different approach to analyze the data structure"
    
    def _extract_insight_from_result(self, query: str, result: dict, purpose: str):
        """
        Extract a meaningful insight from the current iteration's result
        """
        if not result.get("success", False):
            return None
        
        data = result["data"]
        
        # Extract data patterns
        if data.get("rows"):
            row_count = len(data["rows"])
            if row_count > 0:
                insight = f"Iteration {len(self.query_history)}: {purpose} - Found {row_count} records"
                
                # Add more specific insights based on column patterns
                if any("category" in col.lower() for col in data.get("columns", [])):
                    insight += " with category analysis"
                elif any("count" in col.lower() for col in data.get("columns", [])):
                    insight += " with count aggregation"
                elif any("date" in col.lower() or "time" in col.lower() for col in data.get("columns", [])):
                    insight += " with temporal analysis"
                
                return insight
        
        return None
    
    def _get_timestamp(self):
        """
        Get current timestamp for history tracking
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_summary(self):
        """
        Get a summary of the entire analytics conversation
        """
        summary = {
            "total_queries": len(self.query_history),
            "successful_queries": self.conversation_context["successful_queries"],
            "insights_discovered": self.conversation_context["insights_discovered"],
            "query_history": [
                {
                    "query": entry["query"],
                    "success": entry["result"]["success"],
                    "purpose": entry["purpose"]
                }
                for entry in self.query_history
            ]
        }
        return summary
    
    def export_conversation(self, filename: str = "analytics_conversation.json"):
        """
        Export the entire conversation to a JSON file
        """
        conversation_data = {
            "conversation_summary": self.get_conversation_summary(),
            "full_history": self.query_history,
            "context": self.conversation_context
        }
        
        with open(filename, 'w') as f:
            json.dump(conversation_data, f, indent=2, default=str)
        
        print(f"💾 Conversation exported to {filename}")
        return filename 

    def run_autonomous_analytics(self, initial_user_input: str, max_iterations: int = 5, min_iterations: int = 3):
        """
        Run autonomous analytics for several iterations, automatically generating
        follow-up queries based on previous results
        
        Args:
            initial_user_input: The starting query/request
            max_iterations: Maximum number of iterations to run
            min_iterations: Minimum number of iterations to run before allowing early termination
        
        Returns:
            Dict with complete analytics session results
        """
        print('🚀 Starting Autonomous Analytics Session')
        print(f'📊 Will run {min_iterations}-{max_iterations} iterations automatically')
        print('=' * 70)
        
        # Start with initial query
        print(f'\n🎯 Iteration 1: Initial Query')
        print(f'Query: "{initial_user_input}"')
        initial_result = self.start_analytics_conversation(initial_user_input)
        
        # Show detailed information about the initial query
        print(f"\n📋 Query Details for Iteration 1:")
        self.print_last_query_details()
        
        # Track autonomous session results
        autonomous_results = {
            "session_start": self._get_timestamp(),
            "initial_query": initial_user_input,
            "iterations": [initial_result],
            "autonomous_insights": [],
            "early_termination": False,
            "termination_reason": None
        }
        
        # Continue with autonomous iterations
        for iteration in range(2, max_iterations + 1):
            print(f'\n🤖 Iteration {iteration}: Auto-Generated Query')
            
            try:
                # Check if we should continue
                should_continue = self._should_continue_autonomous_analysis(iteration, min_iterations)
                if not should_continue["continue"]:
                    autonomous_results["early_termination"] = True
                    autonomous_results["termination_reason"] = should_continue["reason"]
                    print(f'🛑 Early termination: {should_continue["reason"]}')
                    break
                
                # Generate and run next query automatically
                next_result = self.continue_analytics_conversation(initial_user_input) # Pass initial_user_input for consistency
                autonomous_results["iterations"].append(next_result)
                
                # Show detailed information about the last query
                print(f"\n📋 Query Details for Iteration {iteration}:")
                self.print_last_query_details()
                
                # Extract autonomous insights
                insight = self._extract_autonomous_insight(next_result, iteration)
                if insight:
                    autonomous_results["autonomous_insights"].append(insight)
                    print(f'💡 Insight discovered: {insight}')
                
                # Add small delay between iterations to avoid overwhelming the system
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f'❌ Error in iteration {iteration}: {e}')
                autonomous_results["iterations"].append({
                    "iteration": iteration,
                    "error": str(e),
                    "success": False
                })
                
                # If we've done minimum iterations, we can stop on error
                if iteration >= min_iterations:
                    autonomous_results["early_termination"] = True
                    autonomous_results["termination_reason"] = f"Error after {iteration-1} successful iterations: {e}"
                    break
        
        # Finalize autonomous session
        autonomous_results["session_end"] = self._get_timestamp()
        autonomous_results["total_iterations"] = len(autonomous_results["iterations"])
        autonomous_results["successful_iterations"] = sum(1 for result in autonomous_results["iterations"] if result.get("query_result", {}).get("success", False))
        
        print(f'\n✅ Autonomous Analytics Session Complete')
        print(f'📈 Completed {autonomous_results["total_iterations"]} iterations')
        print(f'✔️  {autonomous_results["successful_iterations"]} successful queries')
        print(f'🧠 {len(autonomous_results["autonomous_insights"])} insights discovered')
        
        return autonomous_results

    def _should_continue_autonomous_analysis(self, current_iteration: int, min_iterations: int):
        """
        Determine if autonomous analysis should continue based on various factors
        """
        # Always continue if we haven't hit minimum iterations
        if current_iteration <= min_iterations:
            return {"continue": True, "reason": "Below minimum iterations"}
        
        # Check if we have meaningful data to analyze
        if not self.query_history:
            return {"continue": False, "reason": "No query history available"}
        
        # Check recent success rate
        recent_queries = self.query_history[-3:]  # Last 3 queries
        recent_failures = sum(1 for entry in recent_queries if not entry["result"]["success"])
        
        if recent_failures >= 2:
            return {"continue": False, "reason": "Too many recent query failures"}
        
        # Check if we're discovering new insights
        recent_insights = self.conversation_context["insights_discovered"][-3:]
        if len(recent_insights) == 0 and current_iteration > min_iterations + 1:
            return {"continue": False, "reason": "No new insights being discovered"}
        
        # Check for repetitive queries (basic check)
        if len(self.query_history) >= 3:
            last_queries = [entry["query"].lower() for entry in self.query_history[-3:]]
            if len(set(last_queries)) <= 1:  # All recent queries are very similar
                return {"continue": False, "reason": "Queries becoming repetitive"}
        
        return {"continue": True, "reason": "Analysis progressing well"}

    def _extract_autonomous_insight(self, result: dict, iteration: int):
        """
        Extract a meaningful insight from the current iteration's result
        """
        if not result.get("query_result", {}).get("success", False):
            return None
        
        data = result["query_result"]["data"]
        query_purpose = result.get("query_purpose", "")
        
        # Create insight based on the data
        row_count = data.get("row_count", 0)
        columns = data.get("columns", [])
        
        if row_count > 0:
            insight = f"Iteration {iteration}: {query_purpose} - Found {row_count} records"
            
            # Add more specific insights based on column patterns
            if any("category" in col.lower() for col in columns):
                insight += " with category analysis"
            elif any("count" in col.lower() for col in columns):
                insight += " with count aggregation"
            elif any("date" in col.lower() or "time" in col.lower() for col in columns):
                insight += " with temporal analysis"
            
            return insight
        
        return None

    def get_autonomous_summary(self):
        """
        Get a comprehensive summary of the autonomous analytics session
        """
        if not self.query_history:
            return {"error": "No autonomous session data available"}
        
        # Calculate autonomous session metrics
        total_iterations = len(self.query_history)
        successful_queries = sum(1 for entry in self.query_history if entry["result"]["success"])
        
        # Analyze query evolution
        query_evolution = []
        for i, entry in enumerate(self.query_history, 1):
            query_evolution.append({
                "iteration": i,
                "query": entry["query"],
                "purpose": entry["purpose"],
                "success": entry["result"]["success"],
                "row_count": entry["result"]["row_count"] if entry["result"]["success"] else 0
            })
        
        # Extract key findings
        key_findings = []
        for entry in self.query_history:
            if entry["result"]["success"]:
                data = entry["result"]["data"]
                if data.get("row_count", 0) > 0:
                    key_findings.append({
                        "query": entry["query"],
                        "finding": f"Retrieved {data['row_count']} records",
                        "columns": data.get("columns", [])
                    })
        
        return {
            "session_metrics": {
                "total_iterations": total_iterations,
                "successful_queries": successful_queries,
                "success_rate": round(successful_queries / total_iterations * 100, 2) if total_iterations > 0 else 0,
                "insights_discovered": len(self.conversation_context["insights_discovered"]),
                "data_patterns_found": len(self.conversation_context["discovered_patterns"]) # Changed from data_patterns
            },
            "query_evolution": query_evolution,
            "key_findings": key_findings[-5:],  # Last 5 findings
            "conversation_context": self.conversation_context
        } 

    def get_detailed_query_history(self):
        """
        Get detailed history showing exact SQL queries and database responses
        """
        detailed_history = []
        
        for i, entry in enumerate(self.query_history, 1):
            result = entry["result"]
            
            # Extract exact SQL query
            exact_sql = entry["query"]
            
            # Extract exact database response
            query_result = result
            if query_result.get("success", False):
                exact_response = {
                    "success": True,
                    "data": query_result.get("data", {}),
                    "execution_time": "N/A", # Execution time is not tracked in the new history format
                    "row_count": query_result.get("row_count", 0),
                    "columns": query_result.get("columns", []),
                    "rows": query_result.get("rows", [])
                }
            else:
                exact_response = {
                    "success": False,
                    "error": query_result.get("error", "Unknown error"),
                    "error_details": query_result.get("error_details", "No details available")
                }
            
            detailed_entry = {
                "iteration": i,
                "timestamp": self._get_timestamp(), # Timestamp is not tracked in the new history format
                "user_input": "N/A", # User input is not tracked in the new history format
                "query_purpose": entry["purpose"],
                "exact_sql_query": exact_sql,
                "exact_db_response": exact_response
            }
            
            detailed_history.append(detailed_entry)
        
        return detailed_history

    def print_detailed_query_history(self):
        """
        Print detailed query history with exact SQL and database responses
        """
        detailed_history = self.get_detailed_query_history()
        
        print("\n" + "=" * 80)
        print("🔍 DETAILED QUERY HISTORY - EXACT SQL & DATABASE RESPONSES")
        print("=" * 80)
        
        for entry in detailed_history:
            print(f"\n📍 ITERATION {entry['iteration']} - {entry['timestamp']}")
            print("-" * 60)
            print(f"👤 User Input: {entry['user_input']}")
            print(f"🎯 Query Purpose: {entry['query_purpose']}")
            
            print(f"\n📝 EXACT SQL QUERY:")
            print(f"```sql")
            print(f"{entry['exact_sql_query']}")
            print(f"```")
            
            print(f"\n💾 EXACT DATABASE RESPONSE:")
            response = entry['exact_db_response']
            if response['success']:
                print(f"✅ Success: {response['row_count']} rows returned")
                print(f"⏱️  Execution Time: {response.get('execution_time', 'N/A')}")
                print(f"🗂️  Columns: {response['columns']}")
                
                # Show first few rows of data
                if response['rows']:
                    print(f"📊 Sample Data (first 3 rows):")
                    for i, row in enumerate(response['rows'][:3], 1):
                        print(f"   Row {i}: {row}")
                    if len(response['rows']) > 3:
                        print(f"   ... and {len(response['rows']) - 3} more rows")
                else:
                    print(f"📊 No data rows returned")
            else:
                print(f"❌ Query Failed")
                print(f"🚨 Error: {response['error']}")
                print(f"🔍 Details: {response['error_details']}")
            
            print("\n" + "-" * 60)

    def print_last_query_details(self):
        """
        Print details of the last executed query with exact SQL and response
        """
        if not self.query_history:
            print("❌ No queries in history")
            return
        
        last_entry = self.query_history[-1]
        result = last_entry["result"]
        
        print("\n" + "=" * 60)
        print("🔍 LAST QUERY DETAILS")
        print("=" * 60)
        
        print(f"👤 User Input: {last_entry['user_input']}")
        print(f"🎯 Query Purpose: {last_entry['purpose']}")
        print(f"⏰ Timestamp: {last_entry['timestamp']}")
        
        # Show exact SQL query
        exact_sql = last_entry["query"]
        print(f"\n📝 EXACT SQL QUERY:")
        print(f"```sql")
        print(f"{exact_sql}")
        print(f"```")
        
        # Show exact database response
        query_result = result
        print(f"\n💾 EXACT DATABASE RESPONSE:")
        if query_result.get("success", False):
            data = query_result.get("data", {})
            print(f"✅ Query executed successfully")
            print(f"📊 Rows returned: {data.get('row_count', 0)}")
            print(f"🗂️  Columns: {data.get('columns', [])}")
            print(f"⏱️  Execution time: {result.get('execution_time', 'N/A')}")
            
            # Show raw data
            rows = data.get("rows", [])
            if rows:
                print(f"\n📋 RAW DATA ({len(rows)} rows):")
                for i, row in enumerate(rows, 1):
                    print(f"   {i}. {row}")
            else:
                print(f"\n📋 No data rows returned")
        else:
            print(f"❌ Query failed")
            print(f"🚨 Error: {query_result.get('error', 'Unknown error')}")
            print(f"🔍 Error details: {query_result.get('error_details', 'No details available')}") 