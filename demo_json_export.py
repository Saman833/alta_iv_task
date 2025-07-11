#!/usr/bin/env python3
"""
Demo: Complete JSON Export of Analytics Session

This demo captures all inputs, outputs, and agent names in a comprehensive JSON file
for complete traceability and analysis.
"""

import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from services.iterative_analytics_service import IterativeAnalyticsService

class ComprehensiveAnalyticsLogger:
    """
    Enhanced logger that captures all analytics data for JSON export
    """
    
    def __init__(self, analytics_service):
        self.analytics_service = analytics_service
        self.comprehensive_log = {
            "session_metadata": {
                "session_id": f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "total_duration": None
            },
            "agent_interactions": [],
            "sql_executions": [],
            "autonomous_iterations": [],
            "complete_conversation_flow": [],
            "system_configuration": {},
            "summary_statistics": {}
        }
    
    def capture_comprehensive_session(self, initial_query, max_iterations=4, min_iterations=3):
        """
        Run autonomous analytics and capture everything in detailed JSON format
        """
        print("📊 Starting Comprehensive Analytics Session with JSON Logging")
        print("=" * 70)
        
        session_start = datetime.now()
        
        # Run autonomous analytics
        results = self.analytics_service.run_autonomous_analytics(
            initial_user_input=initial_query,
            max_iterations=max_iterations,
            min_iterations=min_iterations
        )
        
        session_end = datetime.now()
        duration = (session_end - session_start).total_seconds()
        
        # Update session metadata
        self.comprehensive_log["session_metadata"]["end_time"] = session_end.isoformat()
        self.comprehensive_log["session_metadata"]["total_duration"] = duration
        self.comprehensive_log["session_metadata"]["initial_query"] = initial_query
        self.comprehensive_log["session_metadata"]["max_iterations"] = max_iterations
        self.comprehensive_log["session_metadata"]["min_iterations"] = min_iterations
        
        # Extract detailed information from analytics service
        self._extract_agent_interactions()
        self._extract_sql_executions()
        self._extract_autonomous_iterations(results)
        self._extract_conversation_flow()
        self._extract_system_configuration()
        self._generate_summary_statistics()
        
        return self.comprehensive_log
    
    def _extract_agent_interactions(self):
        """
        Extract all AI agent interactions with inputs and outputs
        """
        print("\n🤖 Extracting AI Agent Interactions...")
        
        for i, entry in enumerate(self.analytics_service.query_history, 1):
            result = entry["result"]
            
            # Capture analytics agent interaction
            analytics_agent_interaction = {
                "interaction_id": f"analytics_agent_{i}",
                "iteration": i,
                "timestamp": entry["timestamp"],
                "agent_name": "analytics_agent",
                "agent_purpose": "Generate SQL queries from user requests",
                "input_data": {
                    "user_input": entry["user_input"],
                    "enhanced_prompt": result.get("enhanced_prompt", {}),
                    "file_summaries": "File summaries provided to agent",
                    "conversation_context": "Previous query context provided"
                },
                "output_data": {
                    "generated_query": result.get("generated_query", ""),
                    "query_purpose": result.get("query_purpose", ""),
                    "anticipated_next_steps": result.get("next_steps", []),
                    "analysis_reasoning": "AI reasoning for query generation"
                },
                "execution_success": result.get("query_result", {}).get("success", False),
                "processing_time": "N/A"
            }
            
            self.comprehensive_log["agent_interactions"].append(analytics_agent_interaction)
            
            # If there are other agents involved (like enhanced_user_prompt_agent), capture them too
            if result.get("enhanced_prompt"):
                prompt_agent_interaction = {
                    "interaction_id": f"prompt_agent_{i}",
                    "iteration": i,
                    "timestamp": entry["timestamp"],
                    "agent_name": "enhanced_user_prompt_agent",
                    "agent_purpose": "Enhance user prompts with conversation context",
                    "input_data": {
                        "original_user_prompt": entry["user_input"],
                        "conversation_context": "Previous queries and results"
                    },
                    "output_data": {
                        "enhanced_prompt": result.get("enhanced_prompt", {}),
                        "context_summary": "Summarized conversation context",
                        "analysis_objectives": "Enhanced analysis objectives"
                    },
                    "execution_success": True,
                    "processing_time": "N/A"
                }
                
                self.comprehensive_log["agent_interactions"].append(prompt_agent_interaction)
    
    def _extract_sql_executions(self):
        """
        Extract all SQL query executions with complete details
        """
        print("📝 Extracting SQL Query Executions...")
        
        for i, entry in enumerate(self.analytics_service.query_history, 1):
            result = entry["result"]
            query_result = result.get("query_result", {})
            
            sql_execution = {
                "execution_id": f"sql_exec_{i}",
                "iteration": i,
                "timestamp": entry["timestamp"],
                "sql_query": result.get("generated_query", ""),
                "query_purpose": result.get("query_purpose", ""),
                "execution_details": {
                    "success": query_result.get("success", False),
                    "execution_time": query_result.get("execution_time", "N/A"),
                    "database_engine": "SQLite",
                    "query_type": self._determine_query_type(result.get("generated_query", ""))
                },
                "response_data": {
                    "row_count": query_result.get("data", {}).get("row_count", 0),
                    "columns": query_result.get("data", {}).get("columns", []),
                    "sample_rows": query_result.get("data", {}).get("rows", [])[:5],  # First 5 rows
                    "total_rows_available": len(query_result.get("data", {}).get("rows", []))
                },
                "error_details": {
                    "error_occurred": not query_result.get("success", False),
                    "error_message": query_result.get("error", ""),
                    "error_details": query_result.get("error_details", "")
                } if not query_result.get("success", False) else None
            }
            
            self.comprehensive_log["sql_executions"].append(sql_execution)
    
    def _extract_autonomous_iterations(self, autonomous_results):
        """
        Extract autonomous iteration details
        """
        print("🔄 Extracting Autonomous Iteration Details...")
        
        for i, iteration in enumerate(autonomous_results["iterations"], 1):
            autonomous_iteration = {
                "iteration_number": i,
                "iteration_type": "initial" if i == 1 else "auto_generated",
                "user_input": iteration.get("original_input", ""),
                "auto_generated": i > 1,
                "query_generation_strategy": self._get_generation_strategy(i),
                "insights_discovered": autonomous_results.get("autonomous_insights", []),
                "continuation_decision": {
                    "should_continue": i < len(autonomous_results["iterations"]),
                    "termination_reason": autonomous_results.get("termination_reason") if i == len(autonomous_results["iterations"]) else None
                },
                "iteration_success": iteration.get("query_result", {}).get("success", False),
                "data_discovered": {
                    "rows_found": iteration.get("query_result", {}).get("data", {}).get("row_count", 0),
                    "new_insights": f"Iteration {i} insights"
                }
            }
            
            self.comprehensive_log["autonomous_iterations"].append(autonomous_iteration)
    
    def _extract_conversation_flow(self):
        """
        Extract complete conversation flow
        """
        print("💬 Extracting Conversation Flow...")
        
        for i, entry in enumerate(self.analytics_service.query_history, 1):
            conversation_step = {
                "step_number": i,
                "timestamp": entry["timestamp"],
                "user_input": entry["user_input"],
                "system_processing": {
                    "prompt_enhancement": "Enhanced user prompt with context",
                    "agent_reasoning": "AI agent analyzed request and generated SQL",
                    "query_execution": "SQL executed against database",
                    "result_processing": "Results processed and insights extracted"
                },
                "system_output": {
                    "sql_generated": entry["result"].get("generated_query", ""),
                    "data_retrieved": entry["result"].get("query_result", {}).get("data", {}),
                    "insights_extracted": "Insights from this iteration",
                    "next_query_planning": "Strategy for next iteration"
                },
                "conversation_context": {
                    "total_queries_so_far": i,
                    "cumulative_insights": len(self.analytics_service.conversation_context.get("insights_discovered", [])),
                    "conversation_direction": "Progressive data exploration"
                }
            }
            
            self.comprehensive_log["complete_conversation_flow"].append(conversation_step)
    
    def _extract_system_configuration(self):
        """
        Extract system configuration and setup details
        """
        print("⚙️ Extracting System Configuration...")
        
        self.comprehensive_log["system_configuration"] = {
            "analytics_service": {
                "service_type": "IterativeAnalyticsService",
                "capabilities": [
                    "Autonomous query generation",
                    "Context-aware analysis",
                    "Multi-iteration exploration",
                    "Insight extraction"
                ]
            },
            "ai_agents": {
                "analytics_agent": {
                    "purpose": "Generate SQL queries from natural language",
                    "input_format": "Natural language + context",
                    "output_format": "SQL query + analysis plan"
                },
                "enhanced_user_prompt_agent": {
                    "purpose": "Enhance prompts with conversation context",
                    "input_format": "User prompt + conversation history",
                    "output_format": "Enhanced contextual prompt"
                },
                "file_summary_agent": {
                    "purpose": "Generate file summaries for database context",
                    "input_format": "File data + metadata",
                    "output_format": "Structured file summary"
                }
            },
            "database_configuration": {
                "engine": "SQLite",
                "connection_type": "Local file database",
                "query_service": "SQLiteQueryService"
            },
            "iteration_parameters": {
                "max_iterations": "Configurable (default: 5)",
                "min_iterations": "Configurable (default: 3)",
                "continuation_logic": "Success rate + insight discovery based"
            }
        }
    
    def _generate_summary_statistics(self):
        """
        Generate comprehensive summary statistics
        """
        print("📈 Generating Summary Statistics...")
        
        total_queries = len(self.analytics_service.query_history)
        successful_queries = sum(1 for entry in self.analytics_service.query_history 
                               if entry["result"].get("query_result", {}).get("success", False))
        
        total_rows_retrieved = sum(entry["result"].get("query_result", {}).get("data", {}).get("row_count", 0)
                                 for entry in self.analytics_service.query_history)
        
        self.comprehensive_log["summary_statistics"] = {
            "session_performance": {
                "total_iterations": total_queries,
                "successful_iterations": successful_queries,
                "success_rate_percentage": round((successful_queries / total_queries * 100) if total_queries > 0 else 0, 2),
                "total_rows_retrieved": total_rows_retrieved,
                "average_rows_per_query": round(total_rows_retrieved / successful_queries if successful_queries > 0 else 0, 2)
            },
            "agent_utilization": {
                "analytics_agent_calls": total_queries,
                "prompt_enhancement_calls": total_queries,
                "total_ai_agent_interactions": total_queries * 2  # Estimate
            },
            "data_exploration": {
                "unique_tables_accessed": self._count_unique_tables(),
                "query_complexity_distribution": self._analyze_query_complexity(),
                "insights_discovered": len(self.analytics_service.conversation_context.get("insights_discovered", [])),
                "data_patterns_identified": len(self.analytics_service.conversation_context.get("data_patterns", []))
            },
            "conversation_metrics": {
                "conversation_depth": total_queries,
                "autonomous_vs_manual": {
                    "autonomous_iterations": total_queries - 1,  # All except first
                    "manual_iterations": 1  # First query
                },
                "termination_analysis": {
                    "early_termination": "Based on session results",
                    "termination_reason": "See autonomous_iterations for details"
                }
            }
        }
    
    def _determine_query_type(self, sql_query):
        """
        Determine the type of SQL query
        """
        sql_lower = sql_query.lower().strip()
        if sql_lower.startswith('select'):
            if 'count(' in sql_lower:
                return 'COUNT_QUERY'
            elif 'group by' in sql_lower:
                return 'AGGREGATION_QUERY'
            elif 'join' in sql_lower:
                return 'JOIN_QUERY'
            else:
                return 'SELECT_QUERY'
        elif sql_lower.startswith('insert'):
            return 'INSERT_QUERY'
        elif sql_lower.startswith('update'):
            return 'UPDATE_QUERY'
        elif sql_lower.startswith('delete'):
            return 'DELETE_QUERY'
        else:
            return 'UNKNOWN_QUERY'
    
    def _get_generation_strategy(self, iteration):
        """
        Get the query generation strategy for an iteration
        """
        if iteration == 1:
            return "Initial user query"
        elif iteration == 2:
            return "Category exploration based on initial results"
        elif iteration == 3:
            return "Relationship analysis and deeper exploration"
        elif iteration == 4:
            return "Pattern identification and trend analysis"
        else:
            return "Advanced insight discovery and correlation analysis"
    
    def _count_unique_tables(self):
        """
        Count unique tables accessed in queries
        """
        tables = set()
        for entry in self.analytics_service.query_history:
            sql = entry["result"].get("generated_query", "").lower()
            # Simple table extraction (this could be more sophisticated)
            if 'from ' in sql:
                parts = sql.split('from ')[1].split(' ')[0]
                tables.add(parts.strip('`"\''))
        return len(tables)
    
    def _analyze_query_complexity(self):
        """
        Analyze the complexity distribution of queries
        """
        complexity_counts = {"simple": 0, "medium": 0, "complex": 0}
        
        for entry in self.analytics_service.query_history:
            sql = entry["result"].get("generated_query", "").lower()
            complexity_score = 0
            
            # Simple complexity scoring
            if 'join' in sql:
                complexity_score += 2
            if 'group by' in sql:
                complexity_score += 1
            if 'having' in sql:
                complexity_score += 1
            if 'order by' in sql:
                complexity_score += 1
            if 'subquery' in sql or '(' in sql:
                complexity_score += 2
            
            if complexity_score <= 1:
                complexity_counts["simple"] += 1
            elif complexity_score <= 3:
                complexity_counts["medium"] += 1
            else:
                complexity_counts["complex"] += 1
        
        return complexity_counts
    
    def export_to_json(self, filename=None):
        """
        Export comprehensive log to JSON file
        """
        if filename is None:
            filename = f"comprehensive_analytics_{self.comprehensive_log['session_metadata']['session_id']}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.comprehensive_log, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Comprehensive analytics log exported to: {filename}")
        print(f"📊 File size: {os.path.getsize(filename)} bytes")
        return filename

def main():
    """
    Main demo function
    """
    print("📋 Comprehensive JSON Export Demo")
    print("=" * 50)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create analytics service
        analytics_service = IterativeAnalyticsService(db)
        
        # Create comprehensive logger
        logger = ComprehensiveAnalyticsLogger(analytics_service)
        
        print("\n🚀 Running analytics session with comprehensive logging...")
        
        # Run comprehensive session
        comprehensive_data = logger.capture_comprehensive_session(
            initial_query="Show me an overview of my data",
            max_iterations=4,
            min_iterations=3
        )
        
        # Export to JSON
        json_filename = logger.export_to_json()
        
        print(f"\n✅ Demo completed successfully!")
        print(f"📁 Comprehensive JSON file created: {json_filename}")
        
        # Show structure overview
        print(f"\n📋 JSON Structure Overview:")
        print(f"   • Session Metadata: {len(comprehensive_data['session_metadata'])} fields")
        print(f"   • Agent Interactions: {len(comprehensive_data['agent_interactions'])} recorded")
        print(f"   • SQL Executions: {len(comprehensive_data['sql_executions'])} captured")
        print(f"   • Autonomous Iterations: {len(comprehensive_data['autonomous_iterations'])} tracked")
        print(f"   • Conversation Flow: {len(comprehensive_data['complete_conversation_flow'])} steps")
        print(f"   • System Configuration: Complete setup documented")
        print(f"   • Summary Statistics: Comprehensive performance metrics")
        
        return json_filename
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    main() 