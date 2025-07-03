import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv('backend.env')
from services.supabase_client import SupabaseService
import asyncio
import json

async def check_database():
    service = SupabaseService()
    
    try:
        # Check if there are any stored results in the database
        response = service.client.table('processing_requests').select('result, status, created_at').order('created_at', desc=True).limit(10).execute()
        
        if response.data:
            print('📊 Database contains stored results:')
            print('=' * 80)
            for i, row in enumerate(response.data):
                print(f'Row {i+1}:')
                print(f'  Status: {row.get("status")}')
                print(f'  Created: {row.get("created_at")}')
                if row.get('result'):
                    result = row['result']
                    if isinstance(result, dict) and 'recommendations' in result:
                        print(f'  Recommendations:')
                        for rec in result['recommendations']:
                            title = rec.get("title", "Unknown")
                            artist = rec.get("artist", "Unknown")
                            print(f'    - "{title}" by {artist}')
                    if isinstance(result, dict) and 'scene_mood' in result:
                        print(f'  Scene Mood: {result.get("scene_mood")}')
                    if isinstance(result, dict) and 'scene_description' in result:
                        desc = result.get("scene_description", "")[:100] + "..." if len(result.get("scene_description", "")) > 100 else result.get("scene_description", "")
                        print(f'  Scene Description: {desc}')
                print('-' * 40)
        else:
            print('❌ No stored results found in database')
            
        # Also check processing jobs table
        print('\n📋 Checking processing jobs:')
        jobs_response = service.client.table('processing_jobs').select('*').order('created_at', desc=True).limit(5).execute()
        
        if jobs_response.data:
            for job in jobs_response.data:
                print(f'Job ID: {job.get("id")}')
                print(f'  Status: {job.get("status")}')
                print(f'  Request ID: {job.get("request_id")}')
                print(f'  Created: {job.get("created_at")}')
                print('-' * 40)
        else:
            print('No processing jobs found')
            
    except Exception as e:
        print(f'❌ Error checking database: {e}')

if __name__ == "__main__":
    asyncio.run(check_database()) 