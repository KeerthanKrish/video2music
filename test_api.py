#!/usr/bin/env python3
"""
Test script to verify API keys are working
"""

import requests
import os
from app.config import settings

def test_gemini_api():
    """Test Gemini API key."""
    print("🧪 Testing Gemini API...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.gemini_api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "Hello, this is a test. Respond with 'API is working!'"}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and data['candidates']:
                content = data['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ Gemini API is working! Response: {content[:50]}...")
                return True
            else:
                print(f"❌ Unexpected response format: {data}")
                return False
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_openai_api():
    """Test OpenAI API key."""
    print("\n🧪 Testing OpenAI API...")
    
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello, respond with 'OpenAI is working!'"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", 
                               json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and data['choices']:
                content = data['choices'][0]['message']['content']
                print(f"✅ OpenAI API is working! Response: {content}")
                return True
            else:
                print(f"❌ Unexpected response format: {data}")
                return False
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_spotify_api():
    """Test Spotify API credentials."""
    print("\n🧪 Testing Spotify API...")
    
    # Get access token
    auth_url = "https://accounts.spotify.com/api/token"
    auth_data = {
        "grant_type": "client_credentials"
    }
    
    import base64
    credentials = base64.b64encode(f"{settings.spotify_client_id}:{settings.spotify_client_secret}".encode()).decode()
    auth_headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(auth_url, data=auth_data, headers=auth_headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print("✅ Spotify API credentials are working!")
                return True
            else:
                print(f"❌ No access token in response: {data}")
                return False
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def main():
    """Run all API tests."""
    print("🔧 Testing API Keys Configuration")
    print("=" * 50)
    
    print(f"📋 Configuration Summary:")
    print(f"  • Gemini API Key: {settings.gemini_api_key[:10]}...{settings.gemini_api_key[-6:]}")
    print(f"  • OpenAI API Key: {settings.openai_api_key[:10]}...{settings.openai_api_key[-6:]}")
    print(f"  • Spotify Client ID: {settings.spotify_client_id}")
    print(f"  • Use Real AI: {settings.use_real_ai}")
    print()
    
    results = []
    
    # Test APIs
    results.append(("Gemini", test_gemini_api()))
    results.append(("OpenAI", test_openai_api()))
    results.append(("Spotify", test_spotify_api()))
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("-" * 30)
    for service, success in results:
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"  {service:12}: {status}")
    
    working_apis = sum(1 for _, success in results if success)
    print(f"\n🎯 {working_apis}/3 APIs are working!")
    
    if working_apis >= 1:
        print("\n✅ Your video processing will work with real AI!")
        print("💡 Even with just Gemini, you'll get unique video analysis.")
    else:
        print("\n⚠️ No APIs are working. Check your keys and network connection.")
    
    print("\n📋 Next Steps:")
    if working_apis > 0:
        print("1. 🚀 Start your backend server")
        print("2. 🌐 Set up Supabase environment variables (see MANUAL_SUPABASE_SETUP.md)")
        print("3. 🎬 Test with video uploads")
    else:
        print("1. 🔑 Double-check your API keys")
        print("2. 🌐 Check internet connection")
        print("3. 📖 Review SETUP_API_KEYS.md")

if __name__ == "__main__":
    main() 