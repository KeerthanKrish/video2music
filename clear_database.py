import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Also try to load from backend.env
try:
    load_dotenv('app/backend.env')
    print("✅ Loaded app/backend.env")
except:
    pass

try:
    load_dotenv('backend.env')
    print("✅ Loaded backend.env")
except:
    pass

from supabase import create_client, Client

def clear_database():
    """Clear all cached processing results from the database."""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found!")
        print(f"SUPABASE_URL: {'✅' if supabase_url else '❌'}")
        print(f"SUPABASE_SERVICE_ROLE_KEY: {'✅' if supabase_key else '❌'}")
        return False
    
    print(f"🔗 Connecting to Supabase: {supabase_url}")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Clear all processing requests
        print("🗑️ Clearing processing_requests table...")
        result = supabase.table('processing_requests').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print(f"✅ Cleared {len(result.data)} processing requests")
        
        # Clear all processing jobs
        print("🗑️ Clearing processing_jobs table...")
        result = supabase.table('processing_jobs').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print(f"✅ Cleared {len(result.data)} processing jobs")
        
        print("🎉 Database cleared successfully!")
        print("\n💡 Now try uploading a video again - it should generate unique results!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

if __name__ == "__main__":
    clear_database() 