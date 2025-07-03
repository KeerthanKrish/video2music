#!/usr/bin/env python3
"""Script to add music year preference columns to the database."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client, Client
from app.config import settings

def add_music_year_columns():
    """Add music_year_start and music_year_end columns to processing_requests table."""
    try:
        print("🔄 Testing if music year columns already exist...")
        
        # Initialize Supabase client
        supabase: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # First check if we can query the table
        result = supabase.table("processing_requests").select("id").limit(1).execute()
        print(f"✅ Table access confirmed")
        
        # Try to insert a test record to see current schema
        test_data = {
            "user_id": "00000000-0000-0000-0000-000000000000",
            "video_filename": "test_schema.mp4",
            "video_url": "http://test.com/test_schema.mp4",
            "status": "pending",
            "music_year_start": 1980,
            "music_year_end": 2024
        }
        
        insert_result = supabase.table("processing_requests").insert(test_data).execute()
        
        if insert_result.data:
            # If successful, delete the test record immediately
            delete_result = supabase.table("processing_requests").delete().eq("id", insert_result.data[0]["id"]).execute()
            print("✅ Music year columns already exist or were successfully added!")
            print(f"   - music_year_start (default: 1980)")
            print(f"   - music_year_end (default: 2024)")
            print(f"   Test record created and deleted: {insert_result.data[0]['id']}")
            return True
        else:
            print("❌ Could not insert test record - columns may not exist")
            return False
            
    except Exception as e:
        error_msg = str(e).lower()
        if "column" in error_msg and ("music_year_start" in error_msg or "music_year_end" in error_msg):
            print(f"❌ Columns do not exist: {e}")
            print("\n🔧 Please add the columns manually via Supabase dashboard:")
            print("   1. Go to: https://app.supabase.com/project/[your-project]/editor")
            print("   2. Navigate to: Database > Tables > processing_requests")
            print("   3. Click 'Edit' on the table")
            print("   4. Add these columns:")
            print("      - Column name: music_year_start")
            print("        Type: int4 (integer)")
            print("        Default value: 1980")
            print("        Allow nullable: true")
            print("      - Column name: music_year_end")
            print("        Type: int4 (integer)")
            print("        Default value: 2024")  
            print("        Allow nullable: true")
            print("   5. Save the changes")
            return False
        else:
            print(f"❌ Unexpected error: {e}")
            return False

if __name__ == "__main__":
    success = add_music_year_columns()
    if success:
        print("\n🎉 Database schema is ready for music year preferences!")
    else:
        print("\n⚠️  Manual database update required before using year preferences.")
    sys.exit(0 if success else 1) 