-- TikTok Car Edit Newsletter Database Setup
-- Simple structure with RLS disabled for easy development

-- 1. Main newsletter table
CREATE TABLE IF NOT EXISTS newsletters (
  id SERIAL PRIMARY KEY,
  week_start_date DATE NOT NULL,
  week_end_date DATE NOT NULL,
  newsletter_id TEXT UNIQUE NOT NULL,
  
  -- Overview metrics
  total_videos_tracked INTEGER DEFAULT 0,
  total_views BIGINT DEFAULT 0,
  total_creators INTEGER DEFAULT 0,
  avg_engagement_rate DECIMAL(5,2) DEFAULT 0.00,
  viral_videos_count INTEGER DEFAULT 0,
  viral_success_rate DECIMAL(5,2) DEFAULT 0.00,
  
  -- Top performers
  top_car_brand TEXT DEFAULT 'Unknown',
  top_car_brand_views BIGINT DEFAULT 0,
  top_car_brand_engagement DECIMAL(5,2) DEFAULT 0.00,
  
  top_hook_type TEXT DEFAULT 'Unknown',
  top_hook_views BIGINT DEFAULT 0,
  top_hook_engagement DECIMAL(5,2) DEFAULT 0.00,
  
  top_transition_type TEXT DEFAULT 'Unknown',
  top_transition_views BIGINT DEFAULT 0,
  top_transition_engagement DECIMAL(5,2) DEFAULT 0.00,
  
  top_music_track TEXT DEFAULT 'Unknown',
  top_music_track_views BIGINT DEFAULT 0,
  top_music_track_url TEXT DEFAULT '',
  
  top_hashtag TEXT DEFAULT 'Unknown',
  top_hashtag_usage_count INTEGER DEFAULT 0,
  top_hashtag_avg_views BIGINT DEFAULT 0,
  
  -- Optimal specs
  optimal_duration_seconds INTEGER DEFAULT 15,
  optimal_posting_hour INTEGER DEFAULT 19,
  optimal_posting_day TEXT DEFAULT 'Friday',
  best_hashtag_count INTEGER DEFAULT 5,
  
  -- Benchmarks
  viral_threshold BIGINT DEFAULT 1000000,
  avg_views_benchmark BIGINT DEFAULT 100000,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Champion videos table
CREATE TABLE IF NOT EXISTS newsletter_champions (
  id SERIAL PRIMARY KEY,
  newsletter_id INTEGER REFERENCES newsletters(id) ON DELETE CASCADE,
  
  category TEXT NOT NULL,
  element_name TEXT NOT NULL,
  video_id TEXT NOT NULL,
  author_username TEXT NOT NULL,
  video_url TEXT NOT NULL,
  
  views BIGINT DEFAULT 0,
  engagement_rate DECIMAL(5,2) DEFAULT 0.00,
  viral_score DECIMAL(5,2) DEFAULT 0.00,
  champion_reason TEXT DEFAULT 'Top performer',
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Top rankings table
CREATE TABLE IF NOT EXISTS newsletter_top_rankings (
  id SERIAL PRIMARY KEY,
  newsletter_id INTEGER REFERENCES newsletters(id) ON DELETE CASCADE,
  
  category TEXT NOT NULL,
  rank_position INTEGER NOT NULL,
  element_name TEXT NOT NULL,
  usage_count INTEGER DEFAULT 0,
  avg_views BIGINT DEFAULT 0,
  avg_engagement DECIMAL(5,2) DEFAULT 0.00,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. AI recommendations table
CREATE TABLE IF NOT EXISTS newsletter_recommendations (
  id SERIAL PRIMARY KEY,
  newsletter_id INTEGER REFERENCES newsletters(id) ON DELETE CASCADE,
  
  recommendation_type TEXT NOT NULL,
  target_audience TEXT NOT NULL,
  recommendation_title TEXT NOT NULL,
  recommendation_text TEXT NOT NULL,
  
  confidence_level TEXT DEFAULT 'Medium',
  expected_impact TEXT DEFAULT '',
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Statistical findings table
CREATE TABLE IF NOT EXISTS newsletter_statistical_findings (
  id SERIAL PRIMARY KEY,
  newsletter_id INTEGER REFERENCES newsletters(id) ON DELETE CASCADE,
  
  finding_type TEXT NOT NULL,
  variable_tested TEXT NOT NULL,
  p_value DECIMAL(10,8) DEFAULT 1.0,
  effect_size DECIMAL(5,3) DEFAULT 0.0,
  effect_magnitude TEXT DEFAULT 'Small',
  finding_description TEXT NOT NULL,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Disable RLS on all tables for easy development
ALTER TABLE newsletters DISABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_champions DISABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_top_rankings DISABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_recommendations DISABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_statistical_findings DISABLE ROW LEVEL SECURITY;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_newsletters_week ON newsletters(week_start_date);
CREATE INDEX IF NOT EXISTS idx_champions_newsletter ON newsletter_champions(newsletter_id);
CREATE INDEX IF NOT EXISTS idx_rankings_newsletter ON newsletter_top_rankings(newsletter_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_newsletter ON newsletter_recommendations(newsletter_id);
CREATE INDEX IF NOT EXISTS idx_findings_newsletter ON newsletter_statistical_findings(newsletter_id);

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL ON newsletters TO your_app_user;
-- GRANT ALL ON newsletter_champions TO your_app_user;
-- GRANT ALL ON newsletter_top_rankings TO your_app_user;
-- GRANT ALL ON newsletter_recommendations TO your_app_user;
-- GRANT ALL ON newsletter_statistical_findings TO your_app_user;

-- Grant sequence permissions
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;