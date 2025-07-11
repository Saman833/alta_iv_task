#!/usr/bin/env python3
"""
Quick Test of Autonomous Analytics

This script demonstrates the autonomous analytics system running multiple iterations
automatically based on previous results.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from services.iterative_analytics_service import IterativeAnalyticsService

def test_autonomous_analytics():
    """
    Test autonomous analytics with a simple scenario
    """
    print("🤖 Testing Autonomous Analytics")
    print("=" * 50)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create iterative analytics service
        analytics_service = IterativeAnalyticsService(db)
        
        # Test autonomous analytics with a simple query
        print("\n🚀 Running autonomous analytics for 'Show me an overview of my data'")
        
        # Run autonomous analytics for 3-4 iterations
        results = analytics_service.run_autonomous_analytics(
            initial_user_input="Show me an overview of my data",
            max_iterations=4,
            min_iterations=3
        )
        
        print("\n" + "=" * 60)
        print("📊 AUTONOMOUS ANALYTICS RESULTS")
        print("=" * 60)
        
        print(f"🎯 Initial Query: {results['initial_query']}")
        print(f"🔄 Total Iterations: {results['total_iterations']}")
        print(f"✅ Successful Queries: {results['successful_iterations']}")
        
        if results['early_termination']:
            print(f"🛑 Early Termination: {results['termination_reason']}")
        
        # Show insights
        if results['autonomous_insights']:
            print(f"\n💡 Insights Discovered:")
            for i, insight in enumerate(results['autonomous_insights'], 1):
                print(f"   {i}. {insight}")
        
        # Show query progression
        print(f"\n📋 Query Progression:")
        for i, iteration in enumerate(results['iterations'], 1):
            if iteration.get('query_result', {}).get('success', False):
                row_count = iteration['query_result']['data'].get('row_count', 0)
                print(f"   {i}. ✅ Query found {row_count} records")
                print(f"      '{iteration.get('original_input', 'N/A')}'")
            else:
                print(f"   {i}. ❌ Query failed")
                print(f"      '{iteration.get('original_input', 'N/A')}'")
        
        # Get session summary
        summary = analytics_service.get_autonomous_summary()
        print(f"\n📈 Session Summary:")
        print(f"   • Success Rate: {summary['session_metrics']['success_rate']}%")
        print(f"   • Insights Found: {summary['session_metrics']['insights_discovered']}")
        print(f"   • Data Patterns: {summary['session_metrics']['data_patterns_found']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during autonomous analytics: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_autonomous_analytics()
    if success:
        print("\n✅ Autonomous analytics test completed successfully!")
    else:
        print("\n❌ Autonomous analytics test failed!") 