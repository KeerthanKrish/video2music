#!/usr/bin/env python3
"""Debug script to test authentication and API endpoints."""

import asyncio
import os
import sys
from typing import Dict, Any
import requests
import json

# Add app to path
sys.path.append('app')

from app.services.supabase_client import supabase_service
from app.config import settings

async def test_supabase_connection():
    """Test basic Supabase connection."""
    print("=== Testing Supabase Connection ===")
    try:
        # Test service role connection
        response = supabase_service.client.table("processing_requests").select("id").limit(1).execute()
        print(f"✅ Service role connection: OK")
        print(f"Processing requests count: {len(response.data)}")
    except Exception as e:
        print(f"❌ Service role connection failed: {e}")
    
    try:
        # Test anon connection
        response = supabase_service.anon_client.table("processing_requests").select("id").limit(1).execute()
        print(f"✅ Anonymous connection: OK")
    except Exception as e:
        print(f"❌ Anonymous connection failed: {e}")

async def test_user_authentication(email: str, password: str):
    """Test user authentication flow."""
    print(f"\n=== Testing Authentication for {email} ===")
    
    try:
        # Try to sign in with anon client
        auth_response = supabase_service.anon_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            print(f"✅ Sign in successful")
            print(f"User ID: {auth_response.user.id}")
            print(f"Email: {auth_response.user.email}")
            
            # Test token authentication
            token = auth_response.session.access_token
            print(f"Token: {token[:50]}...")
            
            user_data = await supabase_service.authenticate_user(token)
            if user_data:
                print(f"✅ Token authentication successful")
                print(f"User data: {user_data}")
                
                # Test getting user requests with the token
                try:
                    requests_data = await supabase_service.get_user_requests(user_data['id'])
                    print(f"✅ User requests loaded: {len(requests_data)} requests")
                    for req in requests_data:
                        print(f"  - {req['id']}: {req['status']} ({req.get('video_filename', 'No filename')})")
                except Exception as e:
                    print(f"❌ Failed to load user requests: {e}")
                    
                # Check if user exists in public.users table
                try:
                    user_profile = supabase_service.client.table("users").select("*").eq("id", user_data['id']).execute()
                    if user_profile.data:
                        print(f"✅ User profile exists in public.users table")
                        print(f"Profile: {user_profile.data[0]}")
                    else:
                        print(f"❌ User profile missing from public.users table")
                        
                        # Try to create the user profile
                        try:
                            new_profile = supabase_service.client.table("users").insert({
                                "id": user_data['id'],
                                "email": user_data['email'],
                                "full_name": user_data.get('user_metadata', {}).get('full_name', '')
                            }).execute()
                            print(f"✅ Created user profile: {new_profile.data}")
                        except Exception as e:
                            print(f"❌ Failed to create user profile: {e}")
                            
                except Exception as e:
                    print(f"❌ Error checking user profile: {e}")
                    
            else:
                print(f"❌ Token authentication failed")
        else:
            print(f"❌ Sign in failed: {auth_response}")
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")

async def test_api_endpoint(email: str, password: str):
    """Test the API endpoint directly."""
    print(f"\n=== Testing API Endpoint ===")
    
    try:
        # First sign in to get token
        auth_response = supabase_service.anon_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.user and auth_response.session:
            token = auth_response.session.access_token
            
            # Test API endpoint
            api_url = f"{settings.backend_url}/requests/"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(api_url, headers=headers)
            print(f"API Response Status: {response.status_code}")
            print(f"API Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API call successful: {len(data)} requests")
                for req in data:
                    print(f"  - {req['id']}: {req['status']}")
            else:
                print(f"❌ API call failed: {response.text}")
                
        else:
            print(f"❌ Could not get auth token for API test")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

async def main():
    """Main debug function."""
    print("video2music Authentication Debug Tool")
    print("====================================")
    
    # Check environment
    print(f"Supabase URL: {settings.supabase_url}")
    print(f"Frontend URL: {settings.frontend_url}")
    print(f"Backend URL: {settings.backend_url}")
    print(f"Service role key: {'*' * 20}...{settings.supabase_service_role_key[-10:]}")
    print(f"Anon key: {'*' * 20}...{settings.supabase_anon_key[-10:]}")
    
    # Test connection
    await test_supabase_connection()
    
    # Get user credentials
    email = input("\nEnter test user email: ").strip()
    password = input("Enter test user password: ").strip()
    
    if email and password:
        await test_user_authentication(email, password)
        await test_api_endpoint(email, password)
    else:
        print("Email or password not provided, skipping user tests")

if __name__ == "__main__":
    asyncio.run(main()) 