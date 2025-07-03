#!/usr/bin/env python3
"""Fresh debug script that loads environment variables from .env file."""

import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Force reload environment variables from .env file
load_dotenv(override=True)

# Load environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

async def test_connection():
    """Test the database connection with fresh environment variables."""
    print("video2music Fresh Debug Tool")
    print("============================")
    print(f"Supabase URL: {supabase_url}")
    print(f"Anon key: {'*' * 20}...{supabase_anon_key[-10:] if supabase_anon_key else 'NOT SET'}")
    print(f"Service key: {'*' * 20}...{supabase_service_key[-10:] if supabase_service_key else 'NOT SET'}")
    
    if not supabase_anon_key:
        print("❌ SUPABASE_ANON_KEY not found")
        return
    
    if not supabase_service_key:
        print("❌ SUPABASE_SERVICE_ROLE_KEY not found")
        return
    
    # Create clients
    anon_client = create_client(supabase_url, supabase_anon_key)
    service_client = create_client(supabase_url, supabase_service_key)
    
    print("\n=== Testing Database Connection ===")
    
    # Test service client connection
    try:
        response = service_client.table("processing_requests").select("id").limit(1).execute()
        print(f"✅ Service client connection: OK ({len(response.data)} rows)")
    except Exception as e:
        print(f"❌ Service client connection failed: {e}")
        print("This means the database tables don't exist yet!")
        
        # Try to run the migration
        print("\n=== Attempting to create tables manually ===")
        try:
            # Create the processing_status enum
            service_client.rpc('exec_sql', {
                'sql': """
                DO $$ BEGIN
                    CREATE TYPE processing_status AS ENUM (
                        'pending', 'processing', 'completed', 'failed', 'cancelled'
                    );
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
                """
            }).execute()
            print("✅ Created processing_status enum")
            
            # Create users table
            service_client.rpc('exec_sql', {
                'sql': """
                CREATE TABLE IF NOT EXISTS public.users (
                    id UUID REFERENCES auth.users(id) PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE
                );
                """
            }).execute()
            print("✅ Created users table")
            
            # Create processing_requests table
            service_client.rpc('exec_sql', {
                'sql': """
                CREATE TABLE IF NOT EXISTS public.processing_requests (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
                    video_filename TEXT NOT NULL,
                    video_path TEXT,
                    video_url TEXT,
                    video_content_type TEXT,
                    status processing_status NOT NULL DEFAULT 'pending',
                    description TEXT,
                    result JSONB,
                    error_message TEXT,
                    edge_function_job_id TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    completed_at TIMESTAMPTZ
                );
                """
            }).execute()
            print("✅ Created processing_requests table")
            
        except Exception as create_error:
            print(f"❌ Failed to create tables: {create_error}")
            return
    
    # Test anon client connection (should fail without auth)
    try:
        response = anon_client.table("processing_requests").select("id").limit(1).execute()
        print(f"✅ Anon client connection: OK ({len(response.data)} rows)")
    except Exception as e:
        print(f"❌ Anon client connection failed (expected): {e}")
    
    # Get user credentials
    email = input("\nEnter test user email: ").strip()
    password = input("Enter test user password: ").strip()
    
    if not email or not password:
        print("No credentials provided, exiting")
        return
    
    print(f"\n=== Testing Authentication for {email} ===")
    
    # Test sign in
    try:
        auth_response = anon_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            print(f"✅ Sign in successful")
            print(f"User ID: {auth_response.user.id}")
            print(f"Email: {auth_response.user.email}")
            
            # Check if user exists in public.users table
            try:
                user_profile = service_client.table("users").select("*").eq("id", auth_response.user.id).execute()
                if user_profile.data:
                    print(f"✅ User profile exists in public.users table")
                    print(f"Profile: {user_profile.data[0]}")
                else:
                    print(f"❌ User profile missing from public.users table")
                    print("Creating user profile...")
                    
                    # Create the user profile
                    try:
                        new_profile = service_client.table("users").insert({
                            "id": auth_response.user.id,
                            "email": auth_response.user.email,
                            "full_name": auth_response.user.user_metadata.get('full_name', '') if auth_response.user.user_metadata else ''
                        }).execute()
                        print(f"✅ Created user profile: {new_profile.data}")
                    except Exception as e:
                        print(f"❌ Failed to create user profile: {e}")
                        
            except Exception as e:
                print(f"❌ Error checking user profile: {e}")
            
            # Now test getting user requests with proper session handling
            try:
                # Use the service client to test RLS policies work correctly
                response = service_client.table("processing_requests").select("*").eq("user_id", auth_response.user.id).execute()
                print(f"✅ User requests loaded via service client: {len(response.data)} requests")
                
                # Test with anon client and proper session
                if hasattr(auth_response, 'session') and auth_response.session:
                    # Set authorization header manually
                    anon_client.postgrest.auth(auth_response.session.access_token)
                    response = anon_client.table("processing_requests").select("*").eq("user_id", auth_response.user.id).execute()
                    print(f"✅ User requests loaded via anon client: {len(response.data)} requests")
                    print("🎉 The authentication issue should now be fixed!")
                    
            except Exception as e:
                print(f"❌ Failed to load user requests: {e}")
                
        else:
            print(f"❌ Sign in failed")
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection()) 