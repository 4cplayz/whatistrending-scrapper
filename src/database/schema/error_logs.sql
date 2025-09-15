-- Failed Actions Log Table
-- Only logs critical failures: DB errors, Newsletter generation failures, API call failures

CREATE TABLE IF NOT EXISTS failed_actions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Action classification
    action_type VARCHAR(50) NOT NULL,  -- 'database', 'newsletter_generation', 'api_call'
    action_name VARCHAR(100) NOT NULL, -- 'supabase_insert', 'weekly_newsletter', 'apify_scrape', etc.

    -- Failure details
    error_message TEXT NOT NULL,

    -- Optional context
    additional_context JSONB,          -- Any relevant data (video_count, api_endpoint, etc.)

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for monitoring dashboard
CREATE INDEX IF NOT EXISTS idx_failed_actions_timestamp ON failed_actions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_failed_actions_type ON failed_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_failed_actions_created_at ON failed_actions(created_at DESC);