#!/usr/bin/env python3
"""Script to manually create the essential database tables."""

import asyncio
from supabase import create_client
from dotenv import load_dotenv
import os

# Force reload environment variables
load_dotenv(override=True)

# Load environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

async def create_tables():
    """Create the essential database tables."""
    print("video2music Database Fix Tool")
    print("=============================")
    
    if not supabase_service_key:
        print("❌ SUPABASE_SERVICE_ROLE_KEY not found")
        return
    
    # Create service client
    service_client = create_client(supabase_url, supabase_service_key)
    
    print("Creating essential database tables...")
    
    # SQL commands to create tables
    sql_commands = [
        # Enable UUID extension
        """
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        """,
        
        # Create processing_status enum
        """
        DO $$ BEGIN
            CREATE TYPE processing_status AS ENUM (
                'pending', 'processing', 'completed', 'failed', 'cancelled'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """,
        
        # Create users table
        """
        CREATE TABLE IF NOT EXISTS public.users (
            id UUID REFERENCES auth.users(id) PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            is_active BOOLEAN DEFAULT TRUE
        );
        """,
        
        # Create processing_requests table
        """
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
        """,
        
        # Create processing_jobs table
        """
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
        """,
        
        # Enable RLS
        """
        ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.processing_requests ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.processing_jobs ENABLE ROW LEVEL SECURITY;
        """,
        
        # Create RLS policies
        """
        CREATE POLICY IF NOT EXISTS "Users can view their own profile" 
            ON public.users FOR SELECT 
            USING (auth.uid() = id);
        """,
        
        """
        CREATE POLICY IF NOT EXISTS "Users can update their own profile" 
            ON public.users FOR UPDATE 
            USING (auth.uid() = id);
        """,
        
        """
        CREATE POLICY IF NOT EXISTS "Users can view their own requests" 
            ON public.processing_requests FOR SELECT 
            USING (auth.uid() = user_id);
        """,
        
        """
        CREATE POLICY IF NOT EXISTS "Users can create their own requests" 
            ON public.processing_requests FOR INSERT 
            WITH CHECK (auth.uid() = user_id);
        """,
        
        """
        CREATE POLICY IF NOT EXISTS "Users can update their own requests" 
            ON public.processing_requests FOR UPDATE 
            USING (auth.uid() = user_id);
        """,
        
        """
        CREATE POLICY IF NOT EXISTS "Service role can manage jobs" 
            ON public.processing_jobs FOR ALL 
            USING (auth.role() = 'service_role');
        """,
        
        # Create function to handle user creation
        """
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
        """,
        
        # Create trigger for new user creation
        """
        DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
        CREATE TRIGGER on_auth_user_created
            AFTER INSERT ON auth.users
            FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
        """
    ]
    
    for i, sql in enumerate(sql_commands, 1):
        try:
            print(f"Executing SQL command {i}/{len(sql_commands)}...", end=" ")
            # Use the raw SQL execution through the service client
            response = service_client.rpc('exec_sql', {'sql': sql})
            if hasattr(response, 'execute'):
                response.execute()
            print("✅")
        except Exception as e:
            try:
                # Alternative approach: use postgrest directly
                print("Trying alternative approach...", end=" ")
                result = service_client.postgrest.rpc('exec_sql', {'sql': sql}).execute()
                print("✅")
            except Exception as e2:
                print(f"❌ ({e})")
    
    # Test if tables were created
    print("\n=== Testing table creation ===")
    try:
        response = service_client.table("processing_requests").select("id").limit(1).execute()
        print(f"✅ processing_requests table exists ({len(response.data)} rows)")
    except Exception as e:
        print(f"❌ processing_requests table check failed: {e}")
    
    try:
        response = service_client.table("users").select("id").limit(1).execute()
        print(f"✅ users table exists ({len(response.data)} rows)")
    except Exception as e:
        print(f"❌ users table check failed: {e}")

if __name__ == "__main__":
    asyncio.run(create_tables()) 