import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()
try:
    load_dotenv('app/backend.env')
    print("✅ Loaded app/backend.env")
except:
    pass

def check_database_results():
    """Check what's stored in the database from the edge function."""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found!")
        return False
    
    print(f"🔗 Connecting to Supabase: {supabase_url}")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Get the most recent processing requests
        response = supabase.table('processing_requests').select('*').order('created_at', desc=True).limit(3).execute()
        
        if response.data:
            print('📊 Recent processing results:')
            print('=' * 80)
            for i, row in enumerate(response.data):
                print(f'\nResult {i+1}:')
                print(f'  ID: {row.get("id")}')
                print(f'  Status: {row.get("status")}')
                print(f'  Created: {row.get("created_at")}')
                print(f'  Updated: {row.get("updated_at")}')
                print(f'  Video URL: {row.get("video_url", "N/A")[:50]}...')
                
                if row.get('result'):
                    result = row['result']
                    print(f'\n  🎯 Processing Results:')
                    print(f'    Scene Mood: {result.get("scene_mood", "N/A")}')
                    print(f'    Scene Description: {result.get("scene_description", "N/A")[:100]}...')
                    print(f'    Visual Elements: {result.get("visual_elements", [])}')
                    print(f'    Ambient Tags: {result.get("ambient_tags", [])}')
                    print(f'    Transcription: {result.get("transcription", "N/A")[:80]}...')
                    
                    recommendations = result.get('recommendations', [])
                    print(f'\n  🎵 Music Recommendations ({len(recommendations)}):')
                    for j, rec in enumerate(recommendations[:3], 1):
                        title = rec.get("title", "Unknown")
                        artist = rec.get("artist", "Unknown")
                        confidence = rec.get("confidence_score", 0)
                        spotify_id = rec.get("spotify_id", "No Spotify ID")
                        print(f'    {j}. "{title}" by {artist} (confidence: {confidence:.2f})')
                        if spotify_id != "No Spotify ID":
                            print(f'       Spotify: https://open.spotify.com/track/{spotify_id}')
                    
                    model_versions = result.get('model_versions', {})
                    print(f'\n  🤖 Model Versions: {model_versions}')
                    processing_duration = result.get('processing_duration', 0)
                    print(f'  ⏱️  Processing Duration: {processing_duration:.2f}s')
                    
                    # Check if real AI was used
                    is_real_ai = False
                    if any("2.0" in str(v) or "gpt" in str(v).lower() or "web-api" in str(v).lower() for v in model_versions.values()):
                        print(f'\n  🎉 REAL AI DETECTED: Using actual Gemini/OpenAI/Spotify APIs!')
                        is_real_ai = True
                    elif any("simulation" in str(v) or "content-aware" in str(v) for v in model_versions.values()):
                        print(f'\n  🧪 Simulation mode detected')
                    else:
                        print(f'\n  ❓ Unknown processing mode')
                    
                    return is_real_ai
                else:
                    print(f'  ❌ No result data stored')
                
                print('-' * 60)
        else:
            print('❌ No processing requests found in database')
            
        return False
        
    except Exception as e:
        print(f'❌ Error checking database: {e}')
        return False

if __name__ == "__main__":
    print("🔍 Checking database for processing results...")
    check_database_results() 