-- Essential tables creation script for video2music
-- Run this in Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum for processing status
DO $$ BEGIN
    CREATE TYPE processing_status AS ENUM (
        'pending', 'processing', 'completed', 'failed', 'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create processing_requests table
CREATE TABLE IF NOT EXISTS public.processing_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    video_filename TEXT NOT NULL,
    video_path TEXT,
    video_url TEXT,
    video_content_type TEXT,
    status processing_status NOT NULL DEFAULT 'pending',
    description TEXT,
    result JSONB,
    error_message TEXT,
    edge_function_job_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Create processing_jobs table for queue management
CREATE TABLE IF NOT EXISTS public.processing_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES public.processing_requests(id) NOT NULL,
    video_filename TEXT NOT NULL,
    status TEXT DEFAULT 'queued',
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_jobs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users table
DO $$ BEGIN
    CREATE POLICY "Users can view their own profile" 
        ON public.users FOR SELECT 
        USING (auth.uid() = id);
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE POLICY "Users can update their own profile" 
        ON public.users FOR UPDATE 
        USING (auth.uid() = id);
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create RLS policies for processing_requests table
DO $$ BEGIN
    CREATE POLICY "Users can view their own requests" 
        ON public.processing_requests FOR SELECT 
        USING (auth.uid() = user_id);
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE POLICY "Users can create their own requests" 
        ON public.processing_requests FOR INSERT 
        WITH CHECK (auth.uid() = user_id);
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE POLICY "Users can update their own requests" 
        ON public.processing_requests FOR UPDATE 
        USING (auth.uid() = user_id);
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create RLS policies for processing_jobs table (service role only)
DO $$ BEGIN
    CREATE POLICY "Service role can manage jobs" 
        ON public.processing_jobs FOR ALL 
        USING (auth.role() = 'service_role');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create function to handle user creation
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user creation
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Insert the existing test user into the users table
-- Replace the UUID with your actual test user ID
INSERT INTO public.users (id, email, full_name) 
VALUES ('88c3aa0f-f065-46e8-8290-2247769b4131', 'test@test.com', 'Test User')
ON CONFLICT (id) DO NOTHING; 