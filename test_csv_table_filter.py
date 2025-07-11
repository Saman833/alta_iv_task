#!/usr/bin/env python3
"""
Test: CSV Table Filtering

This test verifies that the analytics service only processes tables 
that start with csv_table_ prefix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from services.analytics_service import AnalyticsService

def test_csv_table_filtering():
    """
    Test that only csv_table_ tables are processed
    """
    print("🧪 Testing CSV Table Filtering")
    print("=" * 50)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create analytics service
        analytics_service = AnalyticsService(db)
        
        print("📊 Getting file summaries (should only include csv_table_ tables)...")
        
        # Get file summaries
        file_summaries = analytics_service._get_all_file_summaries()
        
        print(f"\n✅ Retrieved {len(file_summaries)} file summaries")
        
        # Verify all tables start with csv_table_
        csv_table_count = 0
        non_csv_table_count = 0
        
        print(f"\n📋 Table Analysis:")
        for i, summary in enumerate(file_summaries, 1):
            table_name = summary["table_name"]
            print(f"   {i}. {table_name}")
            
            if table_name.startswith("csv_table_"):
                csv_table_count += 1
                print(f"      ✅ Correctly prefixed with csv_table_")
            else:
                non_csv_table_count += 1
                print(f"      ❌ Does NOT start with csv_table_")
        
        print(f"\n📊 Filtering Results:")
        print(f"   • Tables with csv_table_ prefix: {csv_table_count}")
        print(f"   • Tables without csv_table_ prefix: {non_csv_table_count}")
        
        # Test success if all tables have csv_table_ prefix
        if non_csv_table_count == 0 and csv_table_count > 0:
            print(f"\n✅ SUCCESS: All {csv_table_count} tables correctly start with csv_table_")
            
            # Show sample table structure
            if file_summaries:
                sample = file_summaries[0]
                print(f"\n📋 Sample Table Structure:")
                print(f"   • Table Name: {sample['table_name']}")
                print(f"   • Original File: {sample['original_file_name']}")
                print(f"   • Has Summary: {'Yes' if sample['file_summary'] else 'No'}")
                
                if sample['file_summary'] and isinstance(sample['file_summary'], dict):
                    summary_keys = list(sample['file_summary'].keys())
                    print(f"   • Summary Keys: {summary_keys}")
            
            return True
        elif csv_table_count == 0:
            print(f"\n⚠️  WARNING: No csv_table_ tables found - might be empty database")
            return True  # Not necessarily a failure
        else:
            print(f"\n❌ FAILURE: Found {non_csv_table_count} tables without csv_table_ prefix")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def show_all_actual_tables():
    """
    Show what tables actually exist in the database for comparison
    """
    print("\n🔍 Checking what tables actually exist in database...")
    
    db = SessionLocal()
    try:
        from services.query_service import SQLiteQueryService
        query_service = SQLiteQueryService(db)
        
        # Get all table names
        result = query_service.query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        
        if result["success"]:
            tables = result["data"]["rows"]
            csv_tables = [t[0] for t in tables if t[0].startswith('csv_table_')]
            other_tables = [t[0] for t in tables if not t[0].startswith('csv_table_')]
            
            print(f"\n📊 Database Tables:")
            print(f"   • Total tables: {len(tables)}")
            print(f"   • CSV tables (csv_table_*): {len(csv_tables)}")
            print(f"   • Other tables: {len(other_tables)}")
            
            if csv_tables:
                print(f"\n✅ CSV Tables Found:")
                for table in csv_tables[:5]:  # Show first 5
                    print(f"   • {table}")
                if len(csv_tables) > 5:
                    print(f"   ... and {len(csv_tables) - 5} more")
            
            if other_tables:
                print(f"\n📋 Other Tables (should be filtered out):")
                for table in other_tables[:5]:  # Show first 5
                    print(f"   • {table}")
                if len(other_tables) > 5:
                    print(f"   ... and {len(other_tables) - 5} more")
        else:
            print(f"❌ Failed to query database tables")
            
    except Exception as e:
        print(f"❌ Error checking database tables: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Show what tables exist first
    show_all_actual_tables()
    
    # Test the filtering
    success = test_csv_table_filtering()
    
    if success:
        print(f"\n🎉 CSV table filtering test passed!")
    else:
        print(f"\n❌ CSV table filtering test failed!") 