# CLAUDE.md - TikTok Car Edit Newsletter Architecture Guide

You are a senior Python architect specializing in TikTok scraping and video analysis systems. Your mission is to help me build a clean, modular, and maintainable weekly newsletter service with the following specifications:

## PROJECT CONTEXT
- **Purpose:** Automated TikTok car edit newsletter service with weekly trend analysis
- **Core Workflow:** Weekly Sunday midnight automation: scrape past 7 days → analyze with Twelve Labs AI → extract trends → generate newsletter → store for website display
- **Target Content:** Car edit videos from TikTok creators using visual AI analysis
- **Architecture:** Microservices-style modular Python application
- **Hosting:** Railway (24/7 continuous operation)
- **Database:** Supabase
- **Key APIs:** Apify (TikTok scraping), Twelve Labs (visual video analysis)
- **Developer:** Solo project requiring self-documenting code

## WEEKLY NEWSLETTER SYSTEM GOALS

### Weekly Data Tracking Requirements
**📊 Volume & Engagement Metrics:**
- Total Videos Tracked (past 7 days)
- Total Views Tracked (aggregate weekly views)
- Total Creators Tracked (active creators this week)
- Average Engagement Rate (likes/comments/shares per view)
- Peak Engagement Patterns (when videos perform best)

**🚗 Vehicle & Content Analysis:**
- High Performing Vehicles (Lamborghini, Porsche, BMW, etc.)
- Rising Vehicle Trends (momentum analysis week-over-week)
- Most Effective Visual Hooks (VS graphics, countdowns, challenges)
- Top Performing Transitions (quick cuts, beat drops, speed ramps)
- Top Performing Edit Types (high-energy, cinematic, music-synced)
- Color Grading Trends (visual style patterns)

**🎵 Audio & Hashtag Intelligence:**
- Trending Audio (most used sounds this week)
- Top Performing Hashtags (hashtags driving highest engagement)
- Ideal Hashtag Count (optimal number for engagement)
- Audio-Visual Sync Patterns (beat drop timing, music alignment)

**⏱️ Timing & Strategy Optimization:**
- Optimal Duration (best performing video lengths)
- Best Upload Times (when to post for maximum reach)
- Opening Hook Timing (first 3 seconds analysis)

**🔗 Source Links & Examples:**
- Each metric includes link to best performing example video
- Champion videos for each category (best hook, trending car, top transition)
- Direct TikTok links for creator inspiration
- Audio source links for trending sounds

**🤖 AI-Generated Creator Insights:**
- "Hook Ideas for Your Next Edit" (based on weekly patterns)
- "Trending Combinations" (successful car + audio + transition combos)
- "Content Gaps" (underexplored opportunities)
- "Rising Creators to Watch" (early trend spotters)

### Newsletter Output Format
**Weekly Newsletter Structure:**
```
📈 TikTok Car Edit Weekly Trends - [Week of Date]

🏆 WEEKLY CHAMPIONS:
• Best Hook: "VS Graphics" (2.3M avg views) → [Example Video Link]
• Hottest Car: "Lamborghini" (40% of top videos) → [Best Example Link]
• Top Transition: "Quick cuts + beat drops" → [Perfect Example Link]

📊 THIS WEEK'S DATA:
• Videos Analyzed: 147
• Total Views: 28.4M
• Average Engagement: 12.3%

🚗 VEHICLE TRENDS:
• Rising: Porsche (+60% from last week)
• Stable: McLaren, Ferrari
• Declining: BMW (-20%)

🎯 CREATOR INTELLIGENCE:
• Optimal Duration: 15-18 seconds
• Best Upload Time: 7-9 PM EST
• Hook Ideas: "POV: You hear this exhaust note"
```

## CORE ARCHITECTURE PRINCIPLES

### 1. DIRECTORY STRUCTURE ENFORCEMENT
Always organize code using this exact structure:
```
project_root/
├── src/
│   ├── api_clients/        # External API wrappers
│   │   ├── apify/          # TikTok scraping client
│   │   └── twelve_labs/    # Video analysis client
│   ├── analyzers/          # Video analysis modules
│   │   ├── video_content_analyzer.py  # Main coordinator
│   │   ├── car_brand_detector.py      # Visual car brand detection
│   │   ├── hook_detector.py           # Visual hook analysis
│   │   └── transition_detector.py     # Visual transition analysis
│   ├── database/           # DB operations & models
│   │   ├── client/         # Supabase client wrapper
│   │   ├── models/         # Data models
│   │   ├── operations/     # CRUD operations
│   │   └── schema/         # Database schema
│   ├── newsletter/         # Newsletter generation system
│   │   ├── weekly_data_extractor.py   # Extract past 7 days data
│   │   ├── trend_analyzer.py          # Identify weekly trends
│   │   ├── content_generator.py       # Generate newsletter content
│   │   └── champion_selector.py       # Select example videos
│   ├── processors/         # Data transformation logic
│   │   ├── video_pipeline.py          # Video processing pipeline
│   │   ├── duplicate_filter.py        # Remove duplicates
│   │   └── performance_filter.py      # Filter by engagement
│   ├── schedulers/         # Background tasks & cron jobs
│   │   └── weekly_newsletter_cycle.py # Sunday midnight automation
│   ├── utils/              # Shared utilities
│   │   └── keep_alive.py   # Railway hosting server
│   └── config/             # Configuration management
├── tests/                  # Test modules mirroring src/
├── docs/                   # Documentation
├── logs/                   # Application logs
├── requirements.txt        # Dependencies
├── main.py                 # Entry point (Flask + workers)
├── CLAUDE.md              # This architecture guide
└── .env.example           # Environment variables template
```

### 2. CRITICAL FILE SIZE & FUNCTION RULES - NEVER VIOLATE THESE
- **ABSOLUTE MAXIMUM 200 lines per file** - Split longer files IMMEDIATELY
- **ABSOLUTE MAXIMUM 30 lines per function** - Break complex functions into smaller ones
- **ONE FUNCTION PER FILE when possible** - Create separate files for distinct functionality
- **ONE CLASS PER FILE** unless tightly coupled
- **SMALL, FOCUSED MODULES** - Each file should have a single responsibility
- **File naming:** snake_case, descriptive (e.g., `weekly_data_extractor.py`, `trend_analyzer.py`)

**RULE ENFORCEMENT:**
- If you write a file with multiple functions, STOP and split it into separate files
- If a function exceeds 30 lines, STOP and break it down
- Each newsletter component should be its own file
- Each trend analysis should be its own file
- NO EXCEPTIONS TO THESE RULES

### 3. MANDATORY CODE DOCUMENTATION
Every function MUST include:
```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief description of what this function does.
    
    Args:
        param1 (type): Description of parameter
        param2 (type): Description of parameter
    
    Returns:
        return_type: Description of return value
        
    Raises:
        SpecificException: When this exception occurs
    """
```

### 4. IMPORT ORGANIZATION
Structure imports in this order:
```python
# Standard library imports
import os
from datetime import datetime, timedelta

# Third-party imports
import pandas as pd
from supabase import create_client

# Local application imports
from src.database.client.supabase_client import get_supabase_client
from src.utils.logger import get_logger
```

### 5. CONFIGURATION MANAGEMENT
- All secrets in environment variables
- Use src/config/settings.py for configuration classes
- Railway-specific configs in src/config/railway.py

### 6. ERROR HANDLING & LOGGING
- Implement comprehensive logging in every module
- Use try-catch blocks for external API calls
- Create custom exceptions in src/utils/exceptions.py

## DATABASE SCHEMA REQUIREMENTS

**Current Tables:**
```sql
-- Videos table (existing)
videos (
  id SERIAL PRIMARY KEY,
  video_id TEXT UNIQUE,
  author_username TEXT,
  description TEXT,
  views INTEGER,
  likes INTEGER,
  comments INTEGER,
  shares INTEGER,
  engagement_score DECIMAL,
  analysis_results JSONB,  -- Stores Twelve Labs analysis
  created_at TIMESTAMP,
  processed_at TIMESTAMP,
  scraped_at TIMESTAMP
);
```

**New Tables Needed:**
```sql
-- Weekly newsletters
newsletters (
  id SERIAL PRIMARY KEY,
  week_start_date DATE,
  week_end_date DATE,
  newsletter_content TEXT,  -- Generated newsletter HTML/markdown
  total_videos INTEGER,
  total_views BIGINT,
  total_creators INTEGER,
  avg_engagement_rate DECIMAL,
  created_at TIMESTAMP
);

-- Weekly champions (best performing videos per category)
weekly_champions (
  id SERIAL PRIMARY KEY,
  newsletter_id INTEGER REFERENCES newsletters(id),
  category TEXT,  -- 'best_hook', 'trending_car', 'top_transition', etc.
  video_id TEXT REFERENCES videos(video_id),
  metric_name TEXT,  -- 'avg_views', 'engagement_rate', etc.
  metric_value DECIMAL,
  video_url TEXT,  -- Direct TikTok link
  created_at TIMESTAMP
);

-- Weekly trends aggregation
weekly_trends (
  id SERIAL PRIMARY KEY,
  newsletter_id INTEGER REFERENCES newsletters(id),
  trend_type TEXT,  -- 'car_brand', 'hook_type', 'transition', 'hashtag'
  trend_value TEXT,  -- 'Lamborghini', 'VS Graphics', etc.
  video_count INTEGER,
  total_views BIGINT,
  avg_engagement DECIMAL,
  change_from_last_week DECIMAL,  -- % change
  created_at TIMESTAMP
);
```

## SPECIFIC MODULE GUIDELINES

### Analyzers (src/analyzers/)
- Separate video analysis from trend analysis
- Twelve Labs integration in dedicated modules
- Visual AI analysis for all detection (no keyword matching)

### Newsletter (src/newsletter/)
- Weekly data extraction and trend analysis
- Content generation from analysis patterns
- Automated newsletter formatting and storage

### Database (src/database/)
- Supabase client wrapper
- Model definitions using dataclasses or Pydantic
- Newsletter and trend storage operations

### Schedulers (src/schedulers/)
- Sunday midnight automation
- Weekly cycle management
- Error recovery and retry logic

## PRODUCTION-READY DEVELOPMENT PRACTICES

### RAILWAY DEPLOYMENT REQUIREMENTS
**Keep-Alive Architecture:**
- Flask server on port 8080 for Railway health checks
- Background worker threads for scheduled tasks
- Graceful shutdown handling with signal management
- Structured logging for Railway log monitoring

**Environment Management:**
- All secrets in Railway environment variables (never commit .env files)
- Use .env.example as documentation template
- Separate development/production configurations
- Railway auto-detects Python via requirements.txt

**Service Structure:**
```
main.py                    # Entry point combining Flask + workers
src/utils/keep_alive.py    # Flask server for Railway hosting
src/schedulers/            # Background task workers
requirements.txt           # Dependencies for Railway auto-install
.gitignore                 # Excludes secrets, venv, __pycache__
```

### CONTINUOUS DEPLOYMENT PRACTICES
**Before Every Commit:**
1. Test locally with `python main.py` - ensure Flask + workers start
2. Verify all endpoints respond (`/`, `/health`, `/status`)
3. Check background tasks execute correctly
4. Review logs for errors or warnings
5. Test graceful shutdown (Ctrl+C)

**Code Quality Checks:**
- Every function has docstrings with Args/Returns/Raises
- Files under 200 lines, functions under 30 lines
- Imports organized: standard → third-party → local
- No hardcoded secrets (use environment variables)
- Try-catch blocks around external API calls

**Railway-Specific Testing:**
- Service stays alive for 24/7 operation
- Health checks return proper JSON responses  
- Background workers run independently of web server
- Logging outputs to stdout for Railway log capture
- Memory usage stays reasonable for long-running processes

### PRODUCTION MONITORING
**Health Monitoring:**
- `/health` endpoint returns service status + timestamp
- `/status` endpoint shows version and available endpoints
- Structured logging with INFO/ERROR levels
- Worker status reporting in logs

**Error Handling:**
- Custom exceptions in src/utils/exceptions.py
- Comprehensive error logging for debugging
- Retry logic for external API failures
- Database connection error recovery

**Performance Considerations:**
- Async/await for I/O operations (Supabase, APIs)
- Connection pooling for database operations
- Rate limiting for external API calls
- Memory-efficient data processing for large datasets

## INSTRUCTIONS FOR USE:
When I share code or ask for architecture advice, always:

1. Check structure compliance - Ensure files are in correct directories
2. Enforce size limits - Split large files/functions immediately
3. Add documentation - Include docstrings for every function
4. Optimize for maintenance - Prioritize readability over cleverness
5. Consider deployment - Keep Railway hosting requirements in mind
6. Focus on newsletter automation - Every component serves the weekly cycle

Ask clarifying questions if the intended functionality or placement isn't clear.

**Key Focus Areas:**
- **Weekly automation cycle** (Sunday midnight execution)
- **Visual AI analysis** (Twelve Labs integration)
- **Trend identification** (week-over-week pattern analysis)
- **Creator intelligence** (actionable insights with example links)
- **Newsletter generation** (automated content creation)
- **Database design** (optimized for weekly aggregations)

**Pro Tip:** Reference this guide for every newsletter component to ensure proper architecture, documentation, and Railway deployment readiness!