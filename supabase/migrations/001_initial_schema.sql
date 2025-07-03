-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum for processing status
CREATE TYPE processing_status AS ENUM (
    'pending',
    'processing', 
    'completed',
    'failed',
    'cancelled'
);

-- Create users table (extends Supabase auth.users)
CREATE TABLE public.users (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create processing_requests table
CREATE TABLE public.processing_requests (
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
CREATE TABLE public.processing_jobs (
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

-- Create indexes for better performance
CREATE INDEX idx_processing_requests_user_id ON public.processing_requests(user_id);
CREATE INDEX idx_processing_requests_status ON public.processing_requests(status);
CREATE INDEX idx_processing_requests_created_at ON public.processing_requests(created_at DESC);
CREATE INDEX idx_processing_jobs_status ON public.processing_jobs(status);
CREATE INDEX idx_processing_jobs_scheduled_at ON public.processing_jobs(scheduled_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_processing_requests_updated_at 
    BEFORE UPDATE ON public.processing_requests 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_jobs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users table
CREATE POLICY "Users can view their own profile" 
    ON public.users FOR SELECT 
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" 
    ON public.users FOR UPDATE 
    USING (auth.uid() = id);

-- Create RLS policies for processing_requests table
CREATE POLICY "Users can view their own requests" 
    ON public.processing_requests FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own requests" 
    ON public.processing_requests FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own requests" 
    ON public.processing_requests FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own requests" 
    ON public.processing_requests FOR DELETE 
    USING (
        auth.uid() = user_id 
        AND status IN ('pending', 'failed', 'cancelled')
    );

-- Create RLS policies for processing_jobs table (service role only)
CREATE POLICY "Service role can manage jobs" 
    ON public.processing_jobs FOR ALL 
    USING (auth.role() = 'service_role');

-- Create storage bucket for videos
INSERT INTO storage.buckets (id, name, public) 
VALUES ('videos', 'videos', false);

-- Create storage bucket for processed frames
INSERT INTO storage.buckets (id, name, public) 
VALUES ('frames', 'frames', false);

-- Create storage policies for videos bucket
CREATE POLICY "Users can upload videos" 
    ON storage.objects FOR INSERT 
    WITH CHECK (bucket_id = 'videos' AND auth.role() = 'authenticated');

CREATE POLICY "Users can view their own videos" 
    ON storage.objects FOR SELECT 
    USING (bucket_id = 'videos' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Create storage policies for frames bucket
CREATE POLICY "Service can manage frames" 
    ON storage.objects FOR ALL 
    USING (bucket_id = 'frames' AND auth.role() = 'service_role');

CREATE POLICY "Users can view their frames" 
    ON storage.objects FOR SELECT 
    USING (bucket_id = 'frames' AND auth.role() = 'authenticated');

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
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Insert sample data for development (optional)
-- Uncomment for development environment
/*
INSERT INTO public.users (id, email, full_name) VALUES 
    ('00000000-0000-0000-0000-000000000001', 'demo@video2music.com', 'Demo User');

INSERT INTO public.processing_requests (
    id, user_id, video_filename, status, description, result
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'sample-video.mp4',
    'completed',
    'Sample video for testing',
    '{
        "extracted_frames": ["frame1.jpg", "frame2.jpg"],
        "scene_description": "A peaceful outdoor scene",
        "scene_mood": "calm",
        "transcription": "Birds chirping in the background",
        "ambient_tags": ["nature", "birds", "peaceful"],
        "recommendations": [
            {
                "title": "Forest Meditation",
                "artist": "Nature Sounds",
                "genre": "Ambient",
                "mood": "peaceful",
                "energy_level": 0.3,
                "valence": 0.7,
                "confidence_score": 0.9
            }
        ],
        "reasoning": "Based on the peaceful nature scene, ambient music is recommended"
    }'
);
*/

-- Create a function to get processing request statistics
CREATE OR REPLACE FUNCTION get_user_processing_stats(user_uuid UUID)
RETURNS TABLE (
    total_requests BIGINT,
    pending_requests BIGINT,
    processing_requests BIGINT,
    completed_requests BIGINT,
    failed_requests BIGINT
) 
LANGUAGE SQL 
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT 
        COUNT(*) as total_requests,
        COUNT(*) FILTER (WHERE status = 'pending') as pending_requests,
        COUNT(*) FILTER (WHERE status = 'processing') as processing_requests,
        COUNT(*) FILTER (WHERE status = 'completed') as completed_requests,
        COUNT(*) FILTER (WHERE status = 'failed') as failed_requests
    FROM public.processing_requests 
    WHERE user_id = user_uuid;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION get_user_processing_stats(UUID) TO authenticated;

-- Create a function to cleanup old failed requests (older than 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_requests()
RETURNS INTEGER
LANGUAGE SQL
SECURITY DEFINER
SET search_path = public
AS $$
    WITH deleted AS (
        DELETE FROM public.processing_requests 
        WHERE status = 'failed' 
        AND created_at < NOW() - INTERVAL '30 days'
        RETURNING id
    )
    SELECT COUNT(*) FROM deleted;
$$;

-- Grant execute permission to service role
GRANT EXECUTE ON FUNCTION cleanup_old_requests() TO service_role;

-- Insert some sample data for testing (optional)
-- Note: This will only work if you have test users set up
/*
INSERT INTO public.processing_requests (user_id, video_filename, video_url, status, description) 
VALUES 
    ('00000000-0000-0000-0000-000000000000'::UUID, 'sample_video.mp4', 'https://example.com/video.mp4', 'completed', 'Sample video for testing'),
    ('00000000-0000-0000-0000-000000000000'::UUID, 'test_video.mov', 'https://example.com/test.mov', 'pending', 'Test video upload');
*/ 