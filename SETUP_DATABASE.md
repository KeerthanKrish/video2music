# Database Setup Instructions

## Step 1: Create Database Tables

1. Go to your Supabase Dashboard: https://app.supabase.com/project/aolcnzeoxiofkwbfuinz/sql/new

2. Copy the entire contents of `create_tables.sql` file

3. Paste it into the SQL editor and click **"Run"**

## Step 2: Test the Application

1. Start the frontend: `cd frontend && npm run dev`

2. Start the backend: `cd app && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`

3. Open http://localhost:5173

4. Click "Create Account" to sign up with a new user

5. Check your email for verification (if required)

6. Sign in and test uploading a video

## What This Fixes

- ✅ Creates `users` and `processing_requests` tables
- ✅ Sets up proper Row Level Security (RLS) policies  
- ✅ Creates trigger to auto-create user profiles
- ✅ Fixes "Failed to load processing requests" error
- ✅ Enables proper user signup/signin flow

## Troubleshooting

If you still get "table does not exist" errors:
1. Check the SQL script ran without errors
2. Verify tables exist in your Supabase Dashboard under "Database" > "Tables"
3. Restart the backend server after creating tables 