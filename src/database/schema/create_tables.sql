-- Newsletter Scraper Database Schema
-- Optimized for Supabase PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Videos table - stores filtered, high-quality TikTok videos
CREATE TABLE videos (
    -- Primary identifiers
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    video_id VARCHAR(50) UNIQUE NOT NULL, -- TikTok video ID
    video_url TEXT NOT NULL,
    
    -- Content data
    description TEXT,
    hashtags JSONB DEFAULT '[]'::jsonb, -- Array of hashtag objects
    
    -- Author information
    author_username VARCHAR(100) NOT NULL,
    author_nickname VARCHAR(100),
    author_verified BOOLEAN DEFAULT false,
    author_followers INTEGER,
    
    -- Music/Audio data
    music_title VARCHAR(200),
    music_author VARCHAR(100),
    music_id VARCHAR(50),
    
    -- Video metadata
    duration INTEGER, -- seconds
    width INTEGER,
    height INTEGER,
    cover_url TEXT,
    
    -- Performance metrics
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    engagement_score DECIMAL(10,6) DEFAULT 0.0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE, -- When video was created on TikTok
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- When we scraped it
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- When we processed it
    
    -- Processing metadata
    scrape_source VARCHAR(50) DEFAULT 'apify', -- hashtag, profile, search
    quality_score DECIMAL(8,6),
    
    -- Analysis data (for Twelve Labs integration)
    analysis_status VARCHAR(20) DEFAULT 'pending' CHECK (analysis_status IN ('pending', 'processing', 'completed', 'failed')),
    analysis_results JSONB,
    analysis_started_at TIMESTAMP WITH TIME ZONE,
    analysis_completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes for performance
    CONSTRAINT videos_video_id_key UNIQUE (video_id)
);

-- Create indexes for common queries
CREATE INDEX idx_videos_engagement_score ON videos(engagement_score DESC);
CREATE INDEX idx_videos_views ON videos(views DESC);
CREATE INDEX idx_videos_scraped_at ON videos(scraped_at DESC);
CREATE INDEX idx_videos_author_username ON videos(author_username);
CREATE INDEX idx_videos_analysis_status ON videos(analysis_status);
CREATE INDEX idx_videos_hashtags ON videos USING GIN (hashtags);

-- Scraping jobs table - track scraping runs for analytics
CREATE TABLE scraping_jobs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    run_id VARCHAR(50) UNIQUE NOT NULL, -- Apify run ID
    status VARCHAR(20) DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    
    -- Configuration used
    config JSONB NOT NULL,
    
    -- Results summary
    total_scraped INTEGER DEFAULT 0,
    total_filtered INTEGER DEFAULT 0,
    total_stored INTEGER DEFAULT 0,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Error tracking
    error_message TEXT
);

CREATE INDEX idx_scraping_jobs_started_at ON scraping_jobs(started_at DESC);
CREATE INDEX idx_scraping_jobs_status ON scraping_jobs(status);

-- Newsletter generations table - track newsletter creation
CREATE TABLE newsletters (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Generation settings
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    video_count INTEGER DEFAULT 0,
    
    -- Content
    content JSONB, -- Generated newsletter content
    html_content TEXT, -- Rendered HTML
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'generating', 'completed', 'failed')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    generated_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    generation_config JSONB,
    error_message TEXT
);

CREATE INDEX idx_newsletters_date_range ON newsletters(date_from, date_to);
CREATE INDEX idx_newsletters_created_at ON newsletters(created_at DESC);

-- Newsletter videos junction table - which videos were used in each newsletter
CREATE TABLE newsletter_videos (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    newsletter_id UUID REFERENCES newsletters(id) ON DELETE CASCADE,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    
    -- Position in newsletter
    position INTEGER,
    section VARCHAR(50), -- top_trending, rising, category_specific
    
    -- Unique constraint
    UNIQUE(newsletter_id, video_id)
);

CREATE INDEX idx_newsletter_videos_newsletter_id ON newsletter_videos(newsletter_id);
CREATE INDEX idx_newsletter_videos_video_id ON newsletter_videos(video_id);

-- Video analysis results table (if we need separate table for complex analysis)
CREATE TABLE video_analysis (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    
    -- Twelve Labs analysis results
    analysis_type VARCHAR(50) NOT NULL, -- transcript, topics, sentiment, etc.
    result_data JSONB NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    twelve_labs_task_id VARCHAR(100),
    
    UNIQUE(video_id, analysis_type)
);

CREATE INDEX idx_video_analysis_video_id ON video_analysis(video_id);
CREATE INDEX idx_video_analysis_type ON video_analysis(analysis_type);

-- Add Row Level Security (RLS) policies for Supabase
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletters ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_analysis ENABLE ROW LEVEL SECURITY;

-- Create policies (for now, allow all operations - adjust based on auth needs)
CREATE POLICY "Allow all operations on videos" ON videos FOR ALL USING (true);
CREATE POLICY "Allow all operations on scraping_jobs" ON scraping_jobs FOR ALL USING (true);
CREATE POLICY "Allow all operations on newsletters" ON newsletters FOR ALL USING (true);
CREATE POLICY "Allow all operations on newsletter_videos" ON newsletter_videos FOR ALL USING (true);
CREATE POLICY "Allow all operations on video_analysis" ON video_analysis FOR ALL USING (true);

-- Add helpful views
CREATE VIEW weekly_trending AS
SELECT 
    author_username,
    COUNT(*) as video_count,
    AVG(engagement_score) as avg_engagement,
    SUM(views) as total_views
FROM videos 
WHERE scraped_at >= NOW() - INTERVAL '7 days'
GROUP BY author_username
ORDER BY avg_engagement DESC;