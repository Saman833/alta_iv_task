from db import SessionLocal
from services.autonomous_analytics_service import AutonomousAnalyticsService

def main():
    """
    Complete Analytics Flow Demo
    This demonstrates the entire analytics pipeline working with real data
    """
    print('🚀 COMPLETE ANALYTICS FLOW - REAL DATA PIPELINE')
    print('=' * 70)
    
    db = None
    try:
        # Initialize database and service
        print('🔧 Initializing autonomous analytics service...')
        db = SessionLocal()
        analytics_service = AutonomousAnalyticsService(db)
        print('✅ Autonomous analytics service ready!')
        print()
        
        # Example user query
        user_query = "Show me insights about my data and suggest analysis approaches"
        print(f'👤 USER QUERY: "{user_query}"')
        print('-' * 50)
        
        # Run the complete autonomous analytics flow
        print('🔄 Running complete autonomous analytics pipeline...')
        result = analytics_service.analyze_user_request_autonomously(user_query)
        
        print('\n📊 AUTONOMOUS ANALYTICS RESULTS:')
        print('=' * 50)

        print(f'📝 User Question: {result.get("user_question", "N/A")}')
        print()

        # Print research analysis summary
        research_analysis = result.get("research_analysis")
        if research_analysis:
            print('📋 Research Analysis:')
            print(f'   Understanding: {research_analysis.get("user_question_understanding", "")[:200]}')
            print(f'   Current Knowledge: {research_analysis.get("current_knowledge", "")[:200]}')
            print(f'   Knowledge Gaps: {research_analysis.get("knowledge_gaps", [])}')
            print(f'   Strategy: {research_analysis.get("research_strategy", "")[:200]}')
            print()

        # Print the 5-step research plan
        five_step_plan = result.get("five_step_research_plan", [])
        print('🔍 5-Step Research Plan:')
        for step in five_step_plan:
            print(f'   Step {step.get("step_number")}: {step.get("step_name")}')
            print(f'      Purpose: {step.get("step_purpose")[:120]}')
            print(f'      Rationale: {step.get("step_rationale")[:120]}')
            print(f'      Deepening: {step.get("deepening_strategy")[:120]}')
            print(f'      Query: {step.get("query")[:120]}')
            print(f'      Expected Findings: {step.get("expected_findings", [])}')
            print(f'      Insights: {step.get("expected_insights", "")[:120]}')
            print(f'      Phase: {step.get("research_phase", "")}, Adaptive: {step.get("adaptive_reasoning", "")[:80]}')
            print()

        # Print comprehensive research synthesis
        comprehensive = result.get("comprehensive_research")
        if comprehensive:
            print('📝 Comprehensive Synthesis:')
            print(f'   Summary: {comprehensive.get("research_summary", "")[:300]}')
            print(f'   Key Questions: {comprehensive.get("research_questions", [])}')
            print(f'   Requirements: {comprehensive.get("research_requirements", [])}')
            print(f'   Expected Answer: {comprehensive.get("expected_comprehensive_answer", "")[:300]}')
            print(f'   Step Progression: {comprehensive.get("step_progression_logic", "")[:200]}')
            print()

        print('\n' + '=' * 70)
        print('✨ AUTONOMOUS ANALYTICS FLOW SUCCESSFUL!')
        print('🎉 Comprehensive analysis completed with dynamic 5-step research and structured response!')
        print('=' * 70)

        return result
        
    except Exception as e:
        print(f'❌ Error in analytics flow: {e}')
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 