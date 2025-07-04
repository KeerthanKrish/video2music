#!/usr/bin/env python3
"""Simple debug script to test authentication issues."""

import asyncio
import os
from supabase import create_client, Client
from supabase.client import ClientOptions
from app.config import settings

# Use environment variables for Supabase credentials
supabase_url = os.getenv("SUPABASE_URL", "https://your-project-id.supabase.co")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

async def test_authentication():
    """Test authentication flow."""
    print("video2music Simple Debug Tool")
    print("=============================")
    print(f"Supabase URL: {supabase_url}")
    print(f"Anon key: {'*' * 20}...{supabase_anon_key[-10:] if supabase_anon_key else 'NOT SET'}")
    print(f"Service key: {'*' * 20}...{supabase_service_key[-10:] if supabase_service_key else 'NOT SET'}")
    
    if not supabase_anon_key:
        print("❌ SUPABASE_ANON_KEY not found in environment")
        return
    
    if not supabase_service_key:
        print("❌ SUPABASE_SERVICE_ROLE_KEY not found in environment")
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
    
    # Test anon client connection (should fail without auth)
    try:
        response = anon_client.table("processing_requests").select("id").limit(1).execute()
        print(f"✅ Anon client connection: OK ({len(response.data)} rows)")
    except Exception as e:
        print(f"❌ Anon client connection failed: {e}")
    
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
                    print("This is likely the cause of the 'Failed to load processing requests' error!")
                    
                    # Try to create the user profile
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
            
            # Test getting user requests with authenticated anon client
            try:
                # Set the session for the anon client
                anon_client.auth.set_session(auth_response.session)
                
                response = anon_client.table("processing_requests").select("*").eq("user_id", auth_response.user.id).execute()
                print(f"✅ User requests loaded: {len(response.data)} requests")
                for req in response.data:
                    print(f"  - {req['id']}: {req['status']} ({req.get('video_filename', 'No filename')})")
            except Exception as e:
                print(f"❌ Failed to load user requests: {e}")
                print("This is the error you're seeing in the frontend!")
                
        else:
            print(f"❌ Sign in failed")
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")

if __name__ == "__main__":
    asyncio.run(test_authentication()) 