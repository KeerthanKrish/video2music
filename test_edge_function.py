import os
from dotenv import load_dotenv
import requests
import json
import time

# Load environment variables
load_dotenv()
try:
    load_dotenv('app/backend.env')
    print("✅ Loaded app/backend.env")
except:
    pass

def test_edge_function():
    """Test the video processor edge function directly."""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_anon_key:
        print("❌ Supabase credentials not found!")
        return False
    
    print(f"🔗 Testing edge function at: {supabase_url}")
    
    # Test data
    test_request = {
        "request_id": f"test_{int(time.time())}",
        "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
    }
    
    print(f"📤 Sending test request: {test_request}")
    
    try:
        # Call the edge function
        response = requests.post(
            f"{supabase_url}/functions/v1/video-processor",
            headers={
                "Authorization": f"Bearer {supabase_anon_key}",
                "Content-Type": "application/json"
            },
            json=test_request,
            timeout=60  # 1 minute timeout
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Edge function response:")
                print(json.dumps(result, indent=2))
                
                # Check if it used real AI
                if result.get("success") and result.get("data"):
                    data = result["data"]
                    print("\n🎯 Analysis Results:")
                    print(f"   Scene Mood: {data.get('scene_mood', 'N/A')}")
                    print(f"   Scene Description: {data.get('scene_description', 'N/A')[:80]}...")
                    print(f"   Visual Elements: {len(data.get('visual_elements', []))} elements")
                    print(f"   Ambient Tags: {data.get('ambient_tags', [])}")
                    print(f"   Transcription: {data.get('transcription', 'N/A')[:50]}...")
                    
                    recommendations = data.get('recommendations', [])
                    print(f"\n🎵 Music Recommendations ({len(recommendations)}):")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"   {i}. \"{rec.get('title', 'Unknown')}\" by {rec.get('artist', 'Unknown')}")
                        if rec.get('spotify_id'):
                            print(f"      Spotify ID: {rec['spotify_id']}")
                    
                    model_versions = data.get('model_versions', {})
                    print(f"\n🤖 Model Versions: {model_versions}")
                    
                    # Check if real AI was used
                    if any("gemini" in str(v).lower() or "gpt" in str(v).lower() for v in model_versions.values()):
                        print("\n🎉 SUCCESS: Real AI processing detected!")
                        return True
                    else:
                        print("\n⚠️  Using simulation mode")
                        return False
                else:
                    print("❌ Invalid response structure")
                    return False
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text[:200]}...")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error calling edge function: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing video processor edge function...")
    test_edge_function() 