-- Database Cleanup Script
-- Removes over-engineered tables and keeps only the videos table
-- Run this in Supabase SQL Editor

-- Drop views first (they depend on tables)
DROP VIEW IF EXISTS weekly_trending;

-- Drop RLS policies before dropping tables
DROP POLICY IF EXISTS "Allow all operations on video_analysis" ON video_analysis;
DROP POLICY IF EXISTS "Allow all operations on newsletter_videos" ON newsletter_videos;
DROP POLICY IF EXISTS "Allow all operations on newsletters" ON newsletters;
DROP POLICY IF EXISTS "Allow all operations on scraping_jobs" ON scraping_jobs;

-- Drop unnecessary tables (in correct order due to foreign key constraints)
DROP TABLE IF EXISTS newsletter_videos CASCADE;
DROP TABLE IF EXISTS video_analysis CASCADE;
DROP TABLE IF EXISTS newsletters CASCADE;
DROP TABLE IF EXISTS scraping_jobs CASCADE;

-- Clean up the videos table - remove RLS and unnecessary fields
ALTER TABLE videos DISABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all operations on videos" ON videos;

-- Remove analysis timestamp fields (we only need analysis_results JSONB)
ALTER TABLE videos DROP COLUMN IF EXISTS analysis_started_at;
ALTER TABLE videos DROP COLUMN IF EXISTS analysis_completed_at;

-- Remove unnecessary indexes that won't be used
DROP INDEX IF EXISTS idx_videos_analysis_status;

-- Keep only essential indexes for the videos table
-- These are already created, just confirming they exist:
-- CREATE INDEX IF NOT EXISTS idx_videos_engagement_score ON videos(engagement_score DESC);
-- CREATE INDEX IF NOT EXISTS idx_videos_views ON videos(views DESC);
-- CREATE INDEX IF NOT EXISTS idx_videos_scraped_at ON videos(scraped_at DESC);
-- CREATE INDEX IF NOT EXISTS idx_videos_author_username ON videos(author_username);
-- CREATE INDEX IF NOT EXISTS idx_videos_hashtags ON videos USING GIN (hashtags);

-- Success message
SELECT 'Database cleanup completed - only videos table remains' as status;