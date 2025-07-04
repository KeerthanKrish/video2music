# Database Setup Guide

## Setup Instructions

1. Go to your Supabase Dashboard: https://app.supabase.com/project/YOUR_PROJECT_ID/sql/new
2. Copy the contents of `create_tables.sql`
3. Paste it into the SQL editor
4. Click "Run" to create the tables

## Tables Created

- `users` - User profiles and authentication data
- `requests` - Video processing requests
- `request_results` - Analysis results for each request

## Verification

After running the SQL, verify the tables were created:

```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

## Test Data

You can optionally insert some test data:

```sql
-- Insert test user (optional)
INSERT INTO users (id, email, created_at, updated_at) 
VALUES (gen_random_uuid(), 'test@example.com', NOW(), NOW());
```

## Next Steps

1. Update your `backend.env` file with your Supabase credentials
2. Test the connection by running the backend server
3. Try uploading a video to test the complete flow

## Troubleshooting

- **Permission Errors**: Make sure you're using the service role key
- **Connection Issues**: Verify your Supabase URL and keys in backend.env
- **Table Creation Failed**: Check the SQL syntax and run each statement individually 