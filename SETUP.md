# 🎵 video2music Setup Guide

Complete setup instructions for the production video2music application with real AI services and Supabase infrastructure.

## 📋 Prerequisites

- **Python 3.11+** with `pip` and `venv`
- **Node.js 18+** with `npm`
- **FFmpeg** installed on your system
- **Supabase account** (free tier is sufficient)
- **API Keys** for:
  - Google Gemini 2.5 Pro API
  - OpenAI API (for Whisper)

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
git clone https://github.com/KeerthanKrish/video2music.git
cd video2music

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install production dependencies
pip install -r requirements-production.txt
```

### 2. Supabase Setup

#### Create Supabase Project
1. Go to [https://supabase.com](https://supabase.com)
2. Create a new project
3. Wait for project initialization (2-3 minutes)
4. Go to Settings → API to get your keys

#### Run Database Migration
```bash
# 1. Login to Supabase (this will open your browser)
.\supabase.exe login

# 2. Initialize Supabase in your project
.\supabase.exe init

# 3. Link to your Supabase project (replace YOUR_PROJECT_ID)
.\supabase.exe link --project-ref YOUR_PROJECT_ID

# 4. Push the database schema
.\supabase.exe db push

# 5. Deploy the Edge Function
.\supabase.exe functions deploy video-processor

# 6. Set environment variables for the Edge Function
.\supabase.exe secrets set GEMINI_API_KEY=your-gemini-key
.\supabase.exe secrets set OPENAI_API_KEY=your-openai-key
```

#### Create Storage Bucket
1. Go to Storage in Supabase dashboard
2. Create new bucket named `videos`
3. Set bucket to **Private** (we use RLS for security)

### 3. Get API Keys

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Copy the key

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new secret key
3. Copy the key

### 4. Environment Configuration

#### Backend Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env with your values:
nano .env
```

Fill in your `.env` file:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-actual-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-actual-service-role-key-here

# JWT Configuration
JWT_SECRET=your-random-jwt-secret-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Service API Keys
GEMINI_API_KEY=your-actual-gemini-api-key-here
OPENAI_API_KEY=your-actual-openai-api-key-here
SPOTIFY_CLIENT_ID=your-actual-spotify-client-id-here
SPOTIFY_CLIENT_SECRET=your-actual-spotify-client-secret-here

# URLs (use defaults for development)
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

#### Frontend Environment
```bash
# Copy frontend environment template
cp frontend/env.example frontend/.env

# Edit frontend/.env with your values:
nano frontend/.env
```

Fill in your `frontend/.env` file:
```env
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-actual-anon-key-here

# Backend API URL
VITE_API_BASE_URL=http://localhost:8000
```

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 6. Deploy Edge Function

```bash
# Deploy the video processing Edge Function
supabase functions deploy video-processor --project-ref YOUR_PROJECT_ID

# Set environment variables for Edge Function
supabase secrets set GEMINI_API_KEY=your-gemini-key --project-ref YOUR_PROJECT_ID
supabase secrets set OPENAI_API_KEY=your-openai-key --project-ref YOUR_PROJECT_ID
```

## 🏃‍♂️ Running the Application

### Development Mode

#### Terminal 1: Backend
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Start FastAPI server
python test_server.py
```

Backend will be available at: `http://localhost:8000`
API docs available at: `http://localhost:8000/docs`

#### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhos t:5173`

## 👤 User Account Creation

Since this uses real Supabase authentication:

1. Go to `http://localhost:5173`
2. Click "Sign Up" (you'll need to implement this UI)
3. Or use Supabase dashboard to manually create test users
4. Or enable email signup in Supabase Auth settings

## 🧪 Testing the Application

### Test Video Upload
1. Sign in to the application
2. Upload a video file (max 100MB)
3. Add an optional description
4. Click "Analyze Video"
5. Watch the processing status update in real-time
6. View results with AI-generated music recommendations

### Backend API Testing
```bash
# Health check
curl http://localhost:8000/

# Test with authentication
# (Get JWT token from browser dev tools after login)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/requests/
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Python Dependencies
```bash
# If you get build errors, try:
pip install --upgrade pip setuptools wheel
pip install -r requirements-production.txt
```

#### 2. FFmpeg Not Found
- **Windows**: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`

#### 3. Supabase Connection Issues
- Verify your project URL and keys in Supabase dashboard
- Check if your project is paused (free tier)
- Ensure RLS policies are set up correctly

#### 4. Edge Function Errors
```bash
# Check Edge Function logs
supabase functions logs video-processor --project-ref YOUR_PROJECT_ID

# Redeploy if needed
supabase functions deploy video-processor --project-ref YOUR_PROJECT_ID
```

#### 5. Frontend Build Issues
```bash
# Clear npm cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Debug Mode

#### Enable Verbose Logging
Add to your `.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

#### Check Database
```bash
# Connect to your Supabase database
supabase db connect

# Check tables
\dt

# Check processing requests
SELECT * FROM processing_requests ORDER BY created_at DESC LIMIT 5;
```

## 📊 Production Deployment

### Environment Variables for Production
- Set `DEBUG=false`
- Use secure JWT secrets (256-bit random strings)
- Configure CORS origins for your domain
- Set up proper SSL certificates
- Use environment-specific Supabase projects

### Scaling Considerations
- **File Storage**: Supabase Storage handles CDN and global distribution
- **Database**: Supabase Postgres scales automatically
- **Processing**: Edge Functions auto-scale with usage
- **Rate Limiting**: Implement in FastAPI for API protection

## 🎯 Next Steps

Once you have the basic setup working:

1. **Real AI Integration**: Replace mock responses with actual Gemini/Whisper/YAMNet calls
2. **Music Database**: Integrate with Spotify Web API for real music recommendations
3. **User Profiles**: Add user preferences and listening history
4. **Analytics**: Track processing metrics and user engagement
5. **Mobile App**: Build React Native version using same backend

## 📝 Support

If you encounter issues:

1. Check this setup guide first
2. Review the application logs
3. Check Supabase dashboard for errors
4. Verify all environment variables are set correctly
5. Test each component individually (auth, upload, processing)

## 🔐 Security Notes

- Never commit `.env` files to version control
- Use different Supabase projects for development/production
- Regularly rotate API keys
- Enable Supabase Auth email verification in production
- Set up proper CORS policies
- Use HTTPS in production
- Enable Supabase Row Level Security (RLS) policies

---

🎵 **Ready to build the future of video-to-music AI!** 🚀 