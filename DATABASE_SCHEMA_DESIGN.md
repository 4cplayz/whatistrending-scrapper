# Newsletter Database Schema Design

## Overview
CRM Dashboard approach with pre-calculated metrics for Next.js/TypeScript consumption. No calculations needed on frontend - all data ready to display.

## Main Tables

### 1. newsletters
**Primary newsletter data with all top performers and optimal specs**

```sql
CREATE TABLE newsletters (
  -- IDENTIFIERS
  id SERIAL PRIMARY KEY,
  week_start_date DATE NOT NULL,
  week_end_date DATE NOT NULL,
  newsletter_id TEXT UNIQUE, -- e.g., "car-trends-20250301"
  
  -- OVERVIEW METRICS
  total_videos_tracked INTEGER,
  total_views BIGINT,
  total_creators INTEGER,
  avg_engagement_rate DECIMAL(5,2),
  viral_videos_count INTEGER,
  viral_success_rate DECIMAL(5,2), -- % that went viral
  average_time_to_viral INTEGER, -- hours
  
  -- TOP PERFORMING CAR CONTENT
  top_car_brand TEXT,
  top_car_brand_views BIGINT,
  top_car_brand_engagement DECIMAL(5,2),
  top_car_brand_usage_count INTEGER,
  
  top_car_type TEXT, -- "supercar", "JDM", "classic"
  top_car_type_views BIGINT,
  top_car_type_engagement DECIMAL(5,2),
  
  -- TOP PERFORMING CONTENT ELEMENTS
  top_hook_type TEXT,
  top_hook_views BIGINT,
  top_hook_engagement DECIMAL(5,2),
  top_hook_usage_count INTEGER,
  
  top_transition_type TEXT,
  top_transition_views BIGINT,
  top_transition_engagement DECIMAL(5,2),
  top_transition_usage_count INTEGER,
  
  top_effect_used TEXT,
  top_effect_views BIGINT,
  top_effect_engagement DECIMAL(5,2),
  top_effect_usage_count INTEGER,
  
  -- TOP PERFORMING AUDIO
  top_music_track TEXT,
  top_music_track_views BIGINT,
  top_music_track_engagement DECIMAL(5,2),
  top_music_track_url TEXT, -- Link to track
  
  top_music_genre TEXT, -- "phonk", "trap", "house"
  top_music_genre_views BIGINT,
  top_music_genre_engagement DECIMAL(5,2),
  
  -- TOP PERFORMING TEXT ELEMENTS  
  top_hashtag TEXT,
  top_hashtag_usage_count INTEGER,
  top_hashtag_avg_views BIGINT,
  
  top_edit_style TEXT,
  top_edit_views BIGINT,
  top_edit_engagement DECIMAL(5,2),
  
  -- TOP PERFORMING CREATORS
  top_creator_tier TEXT, -- "mega", "large", "medium", "micro"
  top_creator_tier_performance BIGINT,
  top_creator_tier_engagement DECIMAL(5,2),
  
  -- OPTIMAL SPECIFICATIONS
  optimal_duration_seconds INTEGER,
  best_video_duration_range TEXT, -- "15-18 seconds"
  optimal_posting_hour INTEGER, -- 0-23
  optimal_posting_day TEXT, -- "Friday"
  best_upload_day_performance BIGINT,
  peak_engagement_timeframe TEXT, -- "7-9 PM EST"
  
  -- OPTIMAL TECHNICAL SPECS
  best_hashtag_count INTEGER,
  optimal_aspect_ratio TEXT, -- "9:16"
  optimal_resolution TEXT, -- "1080x1920"
  best_quality_score_range TEXT, -- "8.5-10"
  optimal_description_length INTEGER,
  
  -- PERFORMANCE BENCHMARKS
  viral_threshold BIGINT,
  high_performance_threshold BIGINT,
  avg_views_benchmark BIGINT,
  
  -- METADATA
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  analysis_completeness TEXT, -- "Complete", "Partial"
  data_quality_score TEXT -- "Excellent", "Good", "Fair"
);
```

### 2. newsletter_champions
**One champion video per category with video metadata and links**

```sql
CREATE TABLE newsletter_champions (
  id SERIAL PRIMARY KEY,
  newsletter_id INTEGER REFERENCES newsletters(id),
  
  -- CATEGORY IDENTIFICATION
  category TEXT NOT NULL, -- 'car_brand', 'hook_type', 'transition', 'effect', 'music_track', 'hashtag', 'creator_tier'
  element_name TEXT NOT NULL, -- 'Lamborghini', 'VS Graphics', 'Quick Cut', etc.
  
  -- VIDEO METADATA
  video_id TEXT NOT NULL,
  author_username TEXT NOT NULL,
  video_url TEXT NOT NULL, -- Direct TikTok link
  video_description TEXT,
  
  -- PERFORMANCE METRICS
  views BIGINT,
  likes INTEGER,
  comments INTEGER,
  shares INTEGER,
  engagement_rate DECIMAL(5,2),
  viral_score DECIMAL(5,2),
  
  -- CHAMPION DETAILS
  champion_reason TEXT, -- "Top performing Lamborghini video"
  performance_advantage TEXT, -- "34% above average"
  statistical_backing TEXT, -- "p < 0.01"
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. newsletter_top_rankings
**Top 5 rankings for each category with numbers**

```sql
CREATE TABLE newsletter_top_rankings (
  id SERIAL PRIMARY KEY,
  newsletter_id INTEGER REFERENCES newsletters(id),
  
  -- RANKING DETAILS
  category TEXT NOT NULL, -- 'hashtags', 'effects', 'car_types', 'music_genres', 'music_tracks', 'creator_tiers'
  rank_position INTEGER NOT NULL, -- 1, 2, 3, 4, 5
  element_name TEXT NOT NULL,
  
  -- PERFORMANCE NUMBERS
  usage_count INTEGER, -- How many videos used this element
  avg_views BIGINT,
  avg_engagement DECIMAL(5,2),
  total_views BIGINT, -- Combined views across all videos
  
  -- ADDITIONAL DATA
  element_url TEXT, -- Link to music track, hashtag page, etc.
  trend_direction TEXT, -- "Rising", "Stable", "Declining"
  week_over_week_change DECIMAL(5,2), -- % change from last week
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. newsletter_recommendations
**AI-generated recommendations by category and creator tier**

```sql
CREATE TABLE newsletter_recommendations (
  id SERIAL PRIMARY KEY,
  newsletter_id INTEGER REFERENCES newsletters(id),
  
  -- RECOMMENDATION DETAILS
  recommendation_type TEXT NOT NULL, -- 'hook_idea', 'content_gap', 'trend_prediction', 'timing_strategy'
  target_audience TEXT NOT NULL, -- 'new_creators', 'growing_creators', 'established_creators', 'all_creators'
  
  -- RECOMMENDATION CONTENT
  recommendation_title TEXT NOT NULL,
  recommendation_text TEXT NOT NULL,
  implementation_steps TEXT[], -- Array of steps
  
  -- VALIDATION DATA
  statistical_backing TEXT, -- "p < 0.01, 34% view increase"
  confidence_level TEXT, -- "High", "Medium", "Low"
  implementation_difficulty TEXT, -- "Easy", "Medium", "Hard"
  expected_impact TEXT, -- "2.3x engagement boost"
  
  -- SUPPORTING DATA
  example_video_url TEXT, -- Link to example demonstrating this
  success_probability TEXT, -- "85% success rate"
  timeline TEXT, -- "Implement within 1 week"
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. newsletter_statistical_findings
**Significant statistical findings for the data nerds**

```sql
CREATE TABLE newsletter_statistical_findings (
  id SERIAL PRIMARY KEY,
  newsletter_id INTEGER REFERENCES newsletters(id),
  
  -- STATISTICAL TEST DETAILS
  finding_type TEXT NOT NULL, -- 'correlation', 'significance_test', 'effect_size'
  test_name TEXT, -- "Pearson correlation", "Chi-square test", "T-test"
  variable_tested TEXT, -- "hook_type vs views", "car_brand performance"
  
  -- STATISTICAL RESULTS
  p_value DECIMAL(10,8),
  test_statistic DECIMAL(10,4),
  effect_size DECIMAL(5,3),
  effect_magnitude TEXT, -- "Large", "Medium", "Small"
  
  -- PRACTICAL INTERPRETATION
  finding_description TEXT, -- "Multi-hook videos perform 47% better"
  practical_significance BOOLEAN,
  confidence_interval_lower DECIMAL(10,2),
  confidence_interval_upper DECIMAL(10,2),
  
  -- VALIDATION
  sample_size INTEGER,
  statistical_power DECIMAL(3,2), -- 0.80 = 80% power
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## TypeScript Interfaces

### Main Newsletter Interface
```typescript
interface NewsletterOverview {
  id: number;
  weekStartDate: string;
  weekEndDate: string;
  
  // Overview metrics
  totalVideosTracked: number;
  totalViews: number;
  totalCreators: number;
  avgEngagementRate: number;
  viralVideosCount: number;
  viralSuccessRate: number;
  
  // Top performers
  topPerformers: {
    carBrand: { name: string; views: number; engagement: number; };
    carType: { name: string; views: number; engagement: number; };
    hookType: { name: string; views: number; engagement: number; };
    transition: { name: string; views: number; engagement: number; };
    effect: { name: string; views: number; engagement: number; };
    musicTrack: { name: string; views: number; url: string; };
    musicGenre: { name: string; views: number; engagement: number; };
    hashtag: { name: string; usageCount: number; avgViews: number; };
    creatorTier: { name: string; performance: number; engagement: number; };
  };
  
  // Optimal specs
  optimalSpecs: {
    durationSeconds: number;
    durationRange: string;
    postingHour: number;
    postingDay: string;
    hashtagCount: number;
    aspectRatio: string;
    resolution: string;
  };
}

interface ChampionVideo {
  id: number;
  category: string;
  elementName: string;
  videoId: string;
  authorUsername: string;
  videoUrl: string;
  views: number;
  engagementRate: number;
  championReason: string;
}

interface TopRanking {
  category: string;
  rankPosition: number;
  elementName: string;
  usageCount: number;
  avgViews: number;
  avgEngagement: number;
  elementUrl?: string;
  trendDirection: 'Rising' | 'Stable' | 'Declining';
}

interface AIRecommendation {
  recommendationType: string;
  targetAudience: string;
  title: string;
  text: string;
  implementationSteps: string[];
  statisticalBacking: string;
  confidenceLevel: 'High' | 'Medium' | 'Low';
  expectedImpact: string;
}
```

## Dashboard Sections

### 1. Overview Dashboard
- Total videos, views, creators, engagement rates
- Viral success rate and benchmarks
- Week-over-week growth metrics

### 2. Performance Leaders  
- Top car brands, types, hooks, transitions, effects
- With champion video links for each category
- Usage counts and performance metrics

### 3. Audio Intelligence
- Top music tracks with Spotify/TikTok links
- Top music genres with performance data  
- Rankings with trend directions

### 4. Creator Intelligence
- Performance by creator tier
- AI recommendations by creator level
- Statistical backing for each recommendation

### 5. Optimal Specs
- Best posting times and days
- Optimal video specifications
- Technical recommendations with confidence levels

### 6. Statistical Insights
- Significant findings with p-values
- Effect sizes and confidence intervals
- Correlation discoveries

### 7. Top 5 Rankings
- Hashtags, effects, car types, music genres
- All with numbers and trend directions
- Links where applicable

## Usage Examples

### Generating Database-Ready Newsletter
```python
from src.newsletter.generation.content_generator import generate_database_newsletter_structure

# Generate complete database structure
newsletter_data = generate_database_newsletter_structure(df, all_analysis_results, champion_portfolio)

# Insert into database
# newsletter_main -> INSERT INTO newsletters
# newsletter_champions -> INSERT INTO newsletter_champions  
# newsletter_top_rankings -> INSERT INTO newsletter_top_rankings
# newsletter_recommendations -> INSERT INTO newsletter_recommendations
# newsletter_statistical_findings -> INSERT INTO newsletter_statistical_findings
```

### Next.js Dashboard Queries
```sql
-- Get complete newsletter overview
SELECT * FROM newsletters WHERE week_start_date = '2025-01-20';

-- Get all champions for a newsletter
SELECT * FROM newsletter_champions WHERE newsletter_id = 1 ORDER BY category;

-- Get top 5 hashtags for this week
SELECT * FROM newsletter_top_rankings 
WHERE newsletter_id = 1 AND category = 'hashtags' 
ORDER BY rank_position;

-- Get AI recommendations for new creators
SELECT * FROM newsletter_recommendations 
WHERE newsletter_id = 1 AND target_audience = 'new_creators';

-- Get statistical findings with high confidence
SELECT * FROM newsletter_statistical_findings 
WHERE newsletter_id = 1 AND p_value < 0.01 
ORDER BY effect_size DESC;
```

### TypeScript API Response Types
```typescript
// API endpoint: /api/newsletter/[id]
interface NewsletterApiResponse {
  newsletter: NewsletterMain;
  champions: NewsletterChampion[];
  topRankings: NewsletterTopRanking[];
  recommendations: NewsletterRecommendation[];
  statisticalFindings: NewsletterStatisticalFinding[];
}

// Dashboard component props
interface DashboardProps {
  newsletterData: NewsletterApiResponse;
}
```

This structure gives you a complete CRM dashboard with all data pre-calculated and ready for TypeScript consumption!