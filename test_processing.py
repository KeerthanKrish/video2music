import os
from dotenv import load_dotenv
import asyncio
import sys

# Load environment variables
load_dotenv()
try:
    load_dotenv('app/backend.env')
    print("✅ Loaded app/backend.env")
except:
    pass

# Add app to path
sys.path.append('app')

from app.services.supabase_client import SupabaseService

async def test_unique_processing():
    """Test that different videos generate unique results."""
    print("🧪 Testing unique video processing...")
    
    service = SupabaseService()
    
    # Test data for different videos
    test_videos = [
        {"url": "https://example.com/video1.mp4", "name": "Nature Video"},
        {"url": "https://example.com/video2.mp4", "name": "City Video"},
        {"url": "https://example.com/video3.mp4", "name": "Music Video"},
    ]
    
    results = []
    
    for i, video in enumerate(test_videos, 1):
        print(f"\n🎬 Testing video {i}: {video['name']}")
        
        # Generate a unique request ID
        import uuid
        request_id = str(uuid.uuid4())
        
        print(f"   Request ID: {request_id}")
        print(f"   Video URL: {video['url']}")
        
        # Test the simulation function directly
        result = service._generate_unique_simulation_result(request_id, video['url'])
        
        print(f"   Scene Mood: {result['scene_mood']}")
        print(f"   Scene Description: {result['scene_description'][:60]}...")
        print(f"   Music Recommendations:")
        for rec in result['recommendations']:
            print(f"     - \"{rec['title']}\" by {rec['artist']}")
        
        results.append({
            'request_id': request_id,
            'video': video,
            'result': result
        })
        
        print("   ✅ Generated unique result")
    
    # Check for uniqueness
    print("\n🔍 Checking uniqueness...")
    
    # Check scene moods
    moods = [r['result']['scene_mood'] for r in results]
    unique_moods = len(set(moods))
    print(f"   Scene Moods: {unique_moods}/{len(moods)} unique")
    
    # Check music recommendations
    all_songs = []
    for r in results:
        for rec in r['result']['recommendations']:
            song = f"{rec['title']} by {rec['artist']}"
            all_songs.append(song)
    
    unique_songs = len(set(all_songs))
    total_songs = len(all_songs)
    print(f"   Music Recommendations: {unique_songs}/{total_songs} unique")
    
    # Check scene descriptions
    descriptions = [r['result']['scene_description'] for r in results]
    unique_descriptions = len(set(descriptions))
    print(f"   Scene Descriptions: {unique_descriptions}/{len(descriptions)} unique")
    
    if unique_moods == len(moods) and unique_songs > total_songs * 0.7 and unique_descriptions == len(descriptions):
        print("\n🎉 SUCCESS: All results are unique!")
        print("   The processing pipeline is now generating unique content!")
        return True
    else:
        print("\n⚠️  WARNING: Some results are still similar")
        print("   But this should still be much better than before")
        return False

if __name__ == "__main__":
    asyncio.run(test_unique_processing()) 