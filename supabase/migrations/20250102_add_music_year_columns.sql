-- Add music year range columns to processing_requests table
ALTER TABLE processing_requests 
ADD COLUMN music_year_start int4 DEFAULT 1980,
ADD COLUMN music_year_end int4 DEFAULT 2024;

-- Add constraints to ensure valid year ranges
ALTER TABLE processing_requests 
ADD CONSTRAINT music_year_start_valid CHECK (music_year_start >= 1950 AND music_year_start <= 2024),
ADD CONSTRAINT music_year_end_valid CHECK (music_year_end >= 1950 AND music_year_end <= 2024),
ADD CONSTRAINT music_year_range_valid CHECK (music_year_start <= music_year_end); 