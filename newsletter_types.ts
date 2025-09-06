
// Newsletter Database TypeScript Interfaces

interface NewsletterMain {
  id?: number;
  week_start_date: string;
  week_end_date: string;
  newsletter_id: string;
  
  // Overview metrics
  total_videos_tracked: number;
  total_views: number;
  total_creators: number;
  avg_engagement_rate: number;
  viral_videos_count: number;
  viral_success_rate: number;
  average_time_to_viral: number;
  
  // Top performers
  top_car_brand: string;
  top_car_brand_views: number;
  top_car_brand_engagement: number;
  top_car_brand_usage_count: number;
  
  top_car_type: string;
  top_car_type_views: number;
  top_car_type_engagement: number;
  
  top_hook_type: string;
  top_hook_views: number;
  top_hook_engagement: number;
  top_hook_usage_count: number;
  
  top_transition_type: string;
  top_transition_views: number;
  top_transition_engagement: number;
  top_transition_usage_count: number;
  
  top_effect_used: string;
  top_effect_views: number;
  top_effect_engagement: number;
  top_effect_usage_count: number;
  
  top_music_track: string;
  top_music_track_views: number;
  top_music_track_engagement: number;
  top_music_track_url: string;
  
  top_music_genre: string;
  top_music_genre_views: number;
  top_music_genre_engagement: number;
  
  top_hashtag: string;
  top_hashtag_usage_count: number;
  top_hashtag_avg_views: number;
  
  top_edit_style: string;
  top_edit_views: number;
  top_edit_engagement: number;
  
  top_creator_tier: string;
  top_creator_tier_performance: number;
  top_creator_tier_engagement: number;
  
  // Optimal specs
  optimal_duration_seconds: number;
  best_video_duration_range: string;
  optimal_posting_hour: number;
  optimal_posting_day: string;
  best_upload_day_performance: number;
  peak_engagement_timeframe: string;
  
  best_hashtag_count: number;
  optimal_aspect_ratio: string;
  optimal_resolution: string;
  best_quality_score_range: string;
  optimal_description_length: number;
  
  // Benchmarks
  viral_threshold: number;
  high_performance_threshold: number;
  avg_views_benchmark: number;
  
  analysis_completeness: string;
  data_quality_score: string;
  created_at?: string;
}

interface NewsletterChampion {
  id?: number;
  newsletter_id?: number;
  category: string;
  element_name: string;
  video_id: string;
  author_username: string;
  video_url: string;
  video_description: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  engagement_rate: number;
  viral_score: number;
  champion_reason: string;
  performance_advantage: string;
  statistical_backing: string;
  created_at?: string;
}

interface NewsletterTopRanking {
  id?: number;
  newsletter_id?: number;
  category: string;
  rank_position: number;
  element_name: string;
  usage_count: number;
  avg_views: number;
  avg_engagement: number;
  total_views: number;
  element_url?: string;
  trend_direction: "Rising" | "Stable" | "Declining";
  week_over_week_change: number;
  created_at?: string;
}

interface NewsletterRecommendation {
  id?: number;
  newsletter_id?: number;
  recommendation_type: string;
  target_audience: string;
  recommendation_title: string;
  recommendation_text: string;
  implementation_steps: string[];
  statistical_backing: string;
  confidence_level: "High" | "Medium" | "Low";
  implementation_difficulty: "Easy" | "Medium" | "Hard";
  expected_impact: string;
  example_video_url?: string;
  success_probability: string;
  timeline: string;
  created_at?: string;
}

interface NewsletterStatisticalFinding {
  id?: number;
  newsletter_id?: number;
  finding_type: string;
  test_name: string;
  variable_tested: string;
  p_value: number;
  test_statistic: number;
  effect_size: number;
  effect_magnitude: string;
  finding_description: string;
  practical_significance: boolean;
  confidence_interval_lower: number;
  confidence_interval_upper: number;
  sample_size: number;
  statistical_power: number;
  created_at?: string;
}

// Complete newsletter structure for API responses
interface NewsletterDatabaseStructure {
  newsletter_main: NewsletterMain;
  newsletter_champions: NewsletterChampion[];
  newsletter_top_rankings: NewsletterTopRanking[];
  newsletter_recommendations: NewsletterRecommendation[];
  newsletter_statistical_findings: NewsletterStatisticalFinding[];
}

// Dashboard display interfaces
interface DashboardOverview {
  totalVideos: number;
  totalViews: number;
  totalCreators: number;
  avgEngagement: number;
  viralSuccessRate: number;
  topPerformers: {
    carBrand: { name: string; views: number; };
    hookType: { name: string; views: number; };
    musicTrack: { name: string; url: string; };
  };
}

export type {
  NewsletterMain,
  NewsletterChampion,
  NewsletterTopRanking,
  NewsletterRecommendation,
  NewsletterStatisticalFinding,
  NewsletterDatabaseStructure,
  DashboardOverview
};
