#!/usr/bin/env python3
"""
Deployment script for Supabase Edge Functions
Updates the video processor with the latest code changes
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and print its output."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Warning: {result.stderr}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def check_supabase_cli():
    """Check if Supabase CLI is installed."""
    if not run_command("supabase --version", check=False):
        print("❌ Supabase CLI not found!")
        print("Install it with: npm install -g supabase")
        print("Or visit: https://supabase.com/docs/guides/cli")
        return False
    return True

def check_project_link():
    """Check if project is linked to Supabase."""
    if not run_command("supabase status", check=False):
        print("❌ Project not linked to Supabase!")
        print("Run: supabase login")
        print("Then: supabase link --project-ref YOUR_PROJECT_REF")
        return False
    return True

def deploy_edge_function():
    """Deploy the video processor edge function."""
    print("🚀 Deploying video processor edge function...")
    
    # Check if the function directory exists
    func_path = Path("supabase/functions/video-processor")
    if not func_path.exists():
        print(f"❌ Function directory not found: {func_path}")
        return False
    
    # Deploy the function
    cmd = "supabase functions deploy video-processor"
    if run_command(cmd):
        print("✅ Edge function deployed successfully!")
        return True
    else:
        print("❌ Failed to deploy edge function")
        return False

def set_environment_variables():
    """Guide user to set environment variables."""
    print("\n📝 IMPORTANT: Set your API keys in Supabase Dashboard")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to Project Settings → API → Environment Variables")
    print("3. Add these variables:")
    print("   - GEMINI_API_KEY = your_actual_gemini_api_key")
    print("   - OPENAI_API_KEY = your_openai_api_key (optional)")
    print("   - SPOTIFY_CLIENT_ID = your_spotify_client_id (optional)")
    print("   - SPOTIFY_CLIENT_SECRET = your_spotify_client_secret (optional)")
    print("\n📖 See SETUP_API_KEYS.md for detailed instructions")

def main():
    """Main deployment function."""
    print("🔧 Deploying Video2Music Edge Functions")
    print("=" * 50)
    
    # Check prerequisites
    if not check_supabase_cli():
        sys.exit(1)
    
    if not check_project_link():
        sys.exit(1)
    
    # Deploy edge function
    if deploy_edge_function():
        print("\n✅ Deployment completed successfully!")
        set_environment_variables()
        
        print("\n🎉 Your video processing system has been updated!")
        print("📋 Next steps:")
        print("1. Set up your API keys (see SETUP_API_KEYS.md)")
        print("2. Test with a new video upload")
        print("3. Check logs to verify real AI processing is working")
        
    else:
        print("\n❌ Deployment failed!")
        print("Check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 