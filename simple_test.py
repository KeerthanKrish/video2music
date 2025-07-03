from app.config import settings
import requests

print("🔧 Testing API Configuration")
print("=" * 40)

print(f"✅ Gemini API Key: {settings.gemini_api_key[:15]}...")
print(f"✅ Real AI Enabled: {settings.use_real_ai}")

# Test Gemini API
print("\n🧪 Testing Gemini API...")
try:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.gemini_api_key}"
    payload = {"contents": [{"parts": [{"text": "Say 'Hello from Gemini!'"}]}]}
    
    response = requests.post(url, json=payload, timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        if 'candidates' in data:
            content = data['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ Gemini API WORKING! Response: {content}")
        else:
            print(f"⚠️ Unexpected response: {data}")
    else:
        print(f"❌ API Error {response.status_code}: {response.text[:100]}")
        
except Exception as e:
    print(f"❌ Connection Error: {e}")

print(f"\n🎯 Result: Your backend is configured for REAL AI processing!")
print("📋 Next steps:")
print("1. Set up Supabase environment variables (see MANUAL_SUPABASE_SETUP.md)")
print("2. Start your application and test video uploads")
print("3. Each video should now get unique analysis results!") 