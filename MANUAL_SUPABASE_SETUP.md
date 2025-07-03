# Manual Supabase Environment Variables Setup

Since you have all your API keys configured, follow these steps to enable real AI processing in your Supabase Edge Functions:

## 🌐 Setup Environment Variables in Supabase Dashboard

### Step 1: Access Your Supabase Project
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `aolcnzeoxiofkwbfuinz`

### Step 2: Navigate to Environment Variables
1. Click on **Project Settings** (gear icon in sidebar)
2. Go to **API** section
3. Scroll down to **Environment Variables**

### Step 3: Add Your API Keys
Add these environment variables exactly as shown:

```
GEMINI_API_KEY = YOUR_ACTUAL_GEMINI_API_KEY_HERE
OPENAI_API_KEY = YOUR_ACTUAL_OPENAI_API_KEY_HERE
SPOTIFY_CLIENT_ID = YOUR_ACTUAL_SPOTIFY_CLIENT_ID_HERE
SPOTIFY_CLIENT_SECRET = YOUR_ACTUAL_SPOTIFY_CLIENT_SECRET_HERE
```

**⚠️ Important Notes:**
- Use the **exact variable names** above
- **No quotes** around the values
- **One space** before and after the equals sign
- Click **Save** after adding each variable
- Replace the placeholder values with your actual API keys

### Step 4: Deploy Updated Edge Function
After setting the environment variables, you need to deploy the updated video processor:

#### Option A: Using Supabase CLI
```bash
# If you complete the login process:
.\supabase.exe functions deploy video-processor
```

#### Option B: Manual Upload (if CLI doesn't work)
1. Go to **Edge Functions** in your Supabase dashboard
2. Find the `video-processor` function
3. Click **Edit**
4. Replace the entire content with the updated code from `supabase/functions/video-processor/index.ts`
5. Click **Deploy**

## 🧪 Testing the Setup

### Test 1: Check Environment Variables
1. Go to **Edge Functions** → **video-processor** → **Logs**
2. Upload a video
3. Look for log messages like:
   - `"Using Gemini API for video analysis"` ✅
   - `"Using OpenAI Whisper API"` ✅
   - NOT `"using simulation mode"` ❌

### Test 2: Upload Different Videos
Upload 3 different videos and verify:
- ✅ **Different scene descriptions** for each
- ✅ **Different moods** (not just "Joyful and Energetic")
- ✅ **Different visual elements**
- ✅ **Different music recommendations**
- ✅ **Unique transcriptions**

### Test 3: Check Processing Results
Look for these improvements:
- **Scene descriptions** should be detailed and specific
- **Moods** should vary: "Contemplative", "Energetic", "Mysterious", etc.
- **Visual elements** should reflect actual content
- **Reasoning** should reference specific video characteristics

## 🔍 Expected Log Messages

### ✅ Success (Real AI Mode):
```
[analyze_scene] Using Gemini API for video analysis
[transcribe_voice] Using OpenAI Whisper API
[query_music] Generating music recommendations using Spotify API
```

### ❌ Still in Simulation:
```
[analyze_scene] API key not configured, using content-aware analysis
[transcribe_voice] API key not configured, using content-aware simulation
[query_music] Spotify credentials not configured, using fallback
```

## 🚨 Troubleshooting

### Issue: Still getting simulation mode
**Solutions:**
1. **Double-check variable names** - they must be exact
2. **Restart Edge Functions** - redeploy after setting variables
3. **Check API key validity** - test with curl command
4. **Clear browser cache** - refresh the application

### Issue: API errors in logs
**Solutions:**
1. **Verify API keys** - ensure they're not truncated
2. **Check quotas** - ensure you haven't exceeded limits
3. **Test API directly** with curl commands

### Issue: Deployment fails
**Solutions:**
1. **Use manual upload** method in dashboard
2. **Check function syntax** for any errors
3. **Try deploying through CLI** if login completes

## ✅ Success Indicators

You'll know everything is working when:
1. **Backend logs show**: "🎯 Real AI processing enabled with Gemini API!"
2. **Edge Function logs show**: Gemini API calls
3. **Video results are**: Unique and detailed for each upload
4. **No more repetitive**: "joyful and energetic" descriptions

Once these variables are set and the function is deployed, your video processing will use real AI instead of mock data! 