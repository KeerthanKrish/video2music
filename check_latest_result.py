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

def check_latest_result():
    """Check the very latest processing result to see if new Spotify search is working."""
    
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
        
        # Get the very latest processing request
        response = supabase.table('processing_requests').select('*').order('updated_at', desc=True).limit(1).execute()
        
        if response.data and len(response.data) > 0:
            row = response.data[0]
            print('📊 Latest processing result:')
            print('=' * 80)
            print(f'  ID: {row.get("id")}')
            print(f'  Status: {row.get("status")}')
            print(f'  Created: {row.get("created_at")}')
            print(f'  Updated: {row.get("updated_at")}')
            print(f'  Video URL: {row.get("video_url", "N/A")[:50]}...')
            
            if row.get('result'):
                result = row['result']
                print(f'\n🎯 Processing Results:')
                print(f'  Scene Mood: {result.get("scene_mood", "N/A")}')
                print(f'  Scene Description: {result.get("scene_description", "N/A")[:100]}...')
                print(f'  Visual Elements: {result.get("visual_elements", [])}')
                print(f'  Ambient Tags: {result.get("ambient_tags", [])}')
                print(f'  Transcription: {result.get("transcription", "N/A")[:80]}...')
                
                recommendations = result.get('recommendations', [])
                print(f'\n🎵 Music Recommendations ({len(recommendations)}):')
                for j, rec in enumerate(recommendations, 1):
                    title = rec.get("title", "Unknown")
                    artist = rec.get("artist", "Unknown")
                    genre = rec.get("genre", "Unknown")
                    confidence = rec.get("confidence_score", 0)
                    spotify_id = rec.get("spotify_id", "No Spotify ID")
                    print(f'  {j}. "{title}" by {artist}')
                    print(f'      Genre: {genre} | Confidence: {confidence:.2f}')
                    if spotify_id != "No Spotify ID":
                        print(f'      Spotify: https://open.spotify.com/track/{spotify_id}')
                    print()
                
                model_versions = result.get('model_versions', {})
                print(f'🤖 Model Versions: {model_versions}')
                processing_duration = result.get('processing_duration', 0)
                print(f'⏱️  Processing Duration: {processing_duration:.2f}s')
                
                # Check if these are the old problematic songs
                song_titles = [rec.get("title", "").lower() for rec in recommendations]
                old_songs = ["ordinary world", "always remember us this way", "always on time"]
                
                if any(old_song in " ".join(song_titles) for old_song in old_songs):
                    print(f'\n❌ STILL GETTING OLD SONGS!')
                    print(f'   Found: {song_titles}')
                    return False
                else:
                    print(f'\n🎉 SUCCESS: NEW SONGS DETECTED!')
                    print(f'   Songs: {song_titles}')
                    return True
            else:
                print(f'❌ No result data stored')
                return False
        else:
            print('❌ No processing requests found in database')
            return False
        
    except Exception as e:
        print(f'❌ Error checking database: {e}')
        return False

if __name__ == "__main__":
    print("🔍 Checking latest processing result...")
    check_latest_result() 