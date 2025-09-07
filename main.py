#!/usr/bin/env python3
"""
Production Railway Entry Point - TikTok Car Edit Newsletter Service
Combines lightweight Flask server with weekly newsletter scheduler.
Optimized for low resource usage when inactive.
"""

import os
import sys
import signal
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify
from dotenv import load_dotenv
from src.config.settings import get_config

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Global scheduler
scheduler = None

@app.route('/')
def home():
    """Health check endpoint for Railway."""
    return jsonify({
        "status": "running",
        "service": "TikTok Car Edit Newsletter API",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route('/health')
def health_check():
    """Detailed health check with service status."""
    try:
        # Check database connection
        from src.database.client.supabase_client import get_supabase_client
        client = get_supabase_client()
        
        # Test query
        result = client.table('videos').select('count', count='exact').execute()
        video_count = result.count if result.count is not None else 0
        
        # Get scheduler status
        from src.schedulers.weekly_newsletter_scheduler import get_scheduler_status
        scheduler_status = get_scheduler_status()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "total_videos": video_count,
            "scheduler": scheduler_status,
            "uptime_hours": (datetime.utcnow() - start_time).total_seconds() / 3600
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/status')
def status():
    """Service status and available endpoints."""
    return jsonify({
        "service": "TikTok Car Edit Newsletter",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Home page"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/status", "method": "GET", "description": "Service status"},
            {"path": "/newsletter/latest", "method": "GET", "description": "Get latest newsletter"},
            {"path": "/scheduler/status", "method": "GET", "description": "Scheduler status"},
            {"path": "/scheduler/force-run", "method": "POST", "description": "Force run newsletter (testing)"}
        ],
        "scheduler": "Weekly Sunday midnight UTC automation",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/newsletter/latest')
def latest_newsletter():
    """Get the most recent newsletter data."""
    try:
        from src.database.client.supabase_client import get_supabase_client
        client = get_supabase_client()
        
        # Get latest newsletter
        result = client.table('newsletters').select('*').order('created_at', desc=True).limit(get_config().NEWSLETTER_RETRIEVAL_LIMIT).execute()
        
        if result.data:
            newsletter = result.data[0]
            return jsonify({
                "newsletter": newsletter,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                "message": "No newsletters found",
                "status": "empty",
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Failed to fetch newsletter: {e}")
        return jsonify({
            "error": str(e),
            "status": "error",
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/scheduler/status')
def scheduler_status():
    """Get detailed scheduler status."""
    try:
        from src.schedulers.weekly_newsletter_scheduler import get_scheduler_status
        status = get_scheduler_status()
        
        return jsonify({
            "scheduler_status": status,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}")
        return jsonify({
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/scheduler/force-run', methods=['POST'])
def force_run_newsletter():
    """Force run newsletter immediately (for testing)."""
    try:
        logger.info("🧪 Manual newsletter generation triggered via API")
        
        from src.schedulers.weekly_newsletter_scheduler import force_run_newsletter
        success = force_run_newsletter()
        
        if success:
            return jsonify({
                "message": "Newsletter generation completed successfully",
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                "message": "Newsletter generation failed",
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Failed to force run newsletter: {e}")
        return jsonify({
            "error": str(e),
            "status": "error",
            "timestamp": datetime.utcnow().isoformat()
        }), 500

def start_weekly_scheduler():
    """Start the weekly newsletter scheduler in background."""
    try:
        from src.schedulers.weekly_newsletter_scheduler import start_weekly_scheduler as start_scheduler
        start_scheduler()
        logger.info("✅ Weekly newsletter scheduler started")
    except Exception as e:
        logger.error(f"❌ Failed to start weekly scheduler: {e}")
        raise

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"📡 Received signal {signum}, initiating graceful shutdown...")
    
    try:
        from src.schedulers.weekly_newsletter_scheduler import stop_weekly_scheduler as stop_scheduler
        stop_scheduler()
        logger.info("✅ Weekly scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
    
    logger.info("👋 Graceful shutdown complete")
    sys.exit(0)

if __name__ == '__main__':
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🚀 Starting TikTok Car Edit Newsletter Service")
    logger.info("=" * 60)
    
    # Store start time for uptime tracking
    start_time = datetime.utcnow()
    
    # Validate environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "APIFY_TOKEN", "TWELVE_LABS_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        sys.exit(1)
    
    logger.info("✅ All environment variables present")
    
    # Start weekly newsletter scheduler
    try:
        start_weekly_scheduler()
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")
        sys.exit(1)
    
    # Get port from Railway environment
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"🌐 Flask server starting on port {port}")
    logger.info("📅 Weekly newsletter scheduler running (Sunday midnight UTC)")
    logger.info("💤 Low resource usage when inactive")
    logger.info("=" * 60)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)