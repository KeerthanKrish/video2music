# API Keys Setup Guide

This guide explains how to set up API keys to enable real video analysis instead of simulation mode.

## Current Issue
Your video processing system is using mock/simulation data because the API keys are not properly configured. Each video gets the same results because it's cycling through a small set of hardcoded responses.

## API Keys Required

### 1. Google Gemini API Key (FREE TIER AVAILABLE)
**Purpose**: Scene analysis, visual understanding, and mood detection
**Cost**: FREE up to 1,500 requests per day

#### How to get it:
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Select "Create API key in new project" 
5. Copy the generated API key

#### Features in free tier:
- Gemini 2.0 Flash: FREE (text, image, video analysis)
- 1M context window
- 1,500 requests per day
- Video understanding capabilities

### 2. OpenAI API Key (OPTIONAL - for better transcription)
**Purpose**: Audio transcription using Whisper
**Cost**: Pay-per-use (very affordable for testing)

#### How to get it:
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up/login
3. Create new API key
4. Add some credits (minimum $5)

### 3. Spotify API Keys (OPTIONAL - for real music data)
**Purpose**: Real music recommendations from Spotify catalog
**Cost**: FREE

#### How to get them:
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app
3. Get Client ID and Client Secret

## Setting Up the Keys

### For Development (Local Testing)

#### Option 1: Environment Variables (Recommended)
Create a `.env` file in your project root:

```env
# Copy your backend.env and update these values:
GEMINI_API_KEY=your_actual_gemini_api_key_here
OPENAI_API_KEY=your_actual_openai_api_key_here  # Optional
SPOTIFY_CLIENT_ID=your_spotify_client_id_here   # Optional
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here  # Optional
```

#### Option 2: Update backend.env directly
Edit `backend.env` and replace the placeholder values with your actual API keys.

**Note**: Gemini keys start with "AIzaSy" and OpenAI keys start with "sk-proj-"

### For Supabase Edge Functions

1. Go to your Supabase project dashboard
2. Navigate to Project Settings → API → Environment Variables
3. Add these environment variables:

```
GEMINI_API_KEY = your_actual_gemini_api_key_here
OPENAI_API_KEY = your_actual_openai_api_key_here
SPOTIFY_CLIENT_ID = your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET = your_spotify_client_secret_here
```

## Testing the Setup

### 1. Verify API Keys Work
Test your Gemini key:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=YOUR_API_KEY" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"contents": [{"parts": [{"text": "Hello, can you analyze video content?"}]}]}'
```

### 2. Restart Your Application
After setting up the keys:
1. Restart your backend server
2. Redeploy your Supabase edge functions (if using them)
3. Test with a new video upload

### 3. Check Logs
Monitor the logs to see:
- `"Using Gemini API for video analysis"` instead of `"using simulation mode"`
- `"Using OpenAI Whisper API"` instead of mock transcription
- `"Using Spotify API"` instead of fallback recommendations

## Expected Changes After Setup

### Before (Mock Data):
- Same 2-3 descriptions rotating
- Same mood categories
- Identical transcriptions
- Same song recommendations

### After (Real AI):
- Unique analysis for each video
- Actual visual content analysis
- Real audio transcription (if audio present)
- Contextual music recommendations
- Higher quality scene descriptions

## Cost Estimation

### Minimal Setup (Gemini only):
- **Cost**: FREE
- **Requests**: 1,500 per day
- **Capability**: Full video analysis, unique results

### Full Setup (All APIs):
- **Gemini**: FREE (1,500 requests/day)
- **OpenAI**: ~$0.006 per minute of audio
- **Spotify**: FREE
- **Total**: ~$1-5/month for moderate usage

## Troubleshooting

### Issue: Still getting same results
**Solution**: 
1. Check API keys are actually set (not placeholder values)
2. Restart your application completely
3. Clear any cached results
4. Check application logs for API errors

### Issue: API errors
**Solution**:
1. Verify API keys are correct
2. Check quota limits
3. Ensure billing is set up (for OpenAI)
4. Check network connectivity

### Issue: Quota exceeded
**Solutions**:
- Gemini: Wait for daily reset (midnight UTC)
- OpenAI: Add more credits
- Implement caching to reduce API calls

## Next Steps

1. **Start with Gemini only** (it's free and provides the biggest improvement)
2. **Test with a few videos** to see unique results
3. **Add other APIs gradually** based on your needs
4. **Monitor usage** to stay within free tiers

The most important API key is **Gemini** as it provides:
- Scene analysis 
- Visual understanding
- Mood detection
- Context-aware processing

This single key will eliminate the repetitive results you're experiencing. 