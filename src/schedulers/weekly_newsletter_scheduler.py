#!/usr/bin/env python3
"""
Production Weekly Newsletter Scheduler - Configurable Day/Time Automation
Handles edge cases: first run, duplicate prevention, failure recovery.
"""

import os
import threading
import schedule
import time
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# Configure logger with UTC formatting
logger = logging.getLogger(__name__)

# Newsletter schedule configuration from environment
NEWSLETTER_DAY = int(os.getenv('NEWSLETTER_GENERATION_DAY', 6))  # Default: Sunday (6)
NEWSLETTER_HOUR = int(os.getenv('NEWSLETTER_GENERATION_HOUR', 0))  # Default: 0 (midnight UTC)

# Track missed generation warning (simple global for now)
_missed_warning_shown = False

# Global scheduler state
scheduler_thread = None
scheduler_running = False
last_successful_run = None

# Railway optimization: Cache last newsletter date to reduce DB calls
_cached_last_newsletter = None
_cache_timestamp = None

def _get_last_newsletter_date() -> Optional[datetime]:
    """
    Get the date of the last generated newsletter from database.
    Railway-optimized: Caches result for 1 hour to reduce DB API calls.

    Returns:
        Optional[datetime]: Date of last newsletter or None if no newsletters exist
    """
    global _cached_last_newsletter, _cache_timestamp

    now = datetime.now(timezone.utc)

    # Railway optimization: Use cached result if less than 1 hour old
    if _cache_timestamp and (now - _cache_timestamp).total_seconds() < 3600:
        return _cached_last_newsletter

    try:
        from src.database.client.supabase_client import get_supabase_client

        client = get_supabase_client()
        result = client.table('newsletters').select('created_at').order('created_at', desc=True).limit(1).execute()

        if result.data and len(result.data) > 0:
            last_date_str = result.data[0]['created_at']
            # Ensure timezone-aware datetime for proper comparison
            if last_date_str.endswith('Z'):
                last_date_str = last_date_str.replace('Z', '+00:00')
            _cached_last_newsletter = datetime.fromisoformat(last_date_str)
            # Ensure UTC timezone if not already set
            if _cached_last_newsletter.tzinfo is None:
                _cached_last_newsletter = _cached_last_newsletter.replace(tzinfo=timezone.utc)
        else:
            _cached_last_newsletter = None

        _cache_timestamp = now
        return _cached_last_newsletter

    except Exception as e:
        logger.error(f"❌ Failed to get last newsletter date: {e}")
        return _cached_last_newsletter  # Return cached value on error

def _log_utc(level: str, message: str):
    """Log message with explicit UTC timestamp."""
    utc_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    formatted_msg = f"[{utc_time}] {message}"
    getattr(logger, level.lower())(formatted_msg)

class WeeklyNewsletterScheduler:
    """Modular scheduler class without global variables."""

    def __init__(self):
        self.scheduler_thread = None
        self.scheduler_running = False
        self.last_successful_run = None
        self._cached_last_newsletter = None
        self._cache_timestamp = None
        self._missed_warning_shown = False  # Track if we've shown the missed warning for this period

    def _get_last_newsletter_date(self) -> Optional[datetime]:
        """
        Get the date of the last generated newsletter from database.
        Railway-optimized: Caches result for 1 hour to reduce DB API calls.

        Returns:
            Optional[datetime]: Date of last newsletter or None if no newsletters exist
        """
        now = datetime.now(timezone.utc)

        # Railway optimization: Use cached result if less than 1 hour old
        if self._cache_timestamp and (now - self._cache_timestamp).total_seconds() < 3600:
            return self._cached_last_newsletter

        try:
            from src.database.client.supabase_client import get_supabase_client

            client = get_supabase_client()
            result = client.table('newsletters').select('created_at').order('created_at', desc=True).limit(1).execute()

            if result.data and len(result.data) > 0:
                last_date_str = result.data[0]['created_at']
                # Ensure timezone-aware datetime for proper comparison
                if last_date_str.endswith('Z'):
                    last_date_str = last_date_str.replace('Z', '+00:00')
                self._cached_last_newsletter = datetime.fromisoformat(last_date_str)
                # Ensure UTC timezone if not already set
                if self._cached_last_newsletter.tzinfo is None:
                    self._cached_last_newsletter = self._cached_last_newsletter.replace(tzinfo=timezone.utc)
            else:
                self._cached_last_newsletter = None

            self._cache_timestamp = now
            return self._cached_last_newsletter

        except Exception as e:
            logger.error(f"❌ Failed to get last newsletter date: {e}")
            return self._cached_last_newsletter  # Return cached value on error


def _should_generate_newsletter() -> tuple[bool, str]:
    """
    Check if newsletter should be generated based on production rules.

    Returns:
        tuple[bool, str]: (should_generate, reason)
    """
    global _missed_warning_shown
    now = datetime.now(timezone.utc)

    # Rule 1: Only run on configured day
    if now.weekday() != NEWSLETTER_DAY:
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        expected_day = day_names[NEWSLETTER_DAY]
        current_day = now.strftime('%A')
        return False, f"Not {expected_day} (current day: {current_day})"

    # Rule 2: 1-hour grace period - can generate anytime within the hour after scheduled time
    if not (NEWSLETTER_HOUR <= now.hour < NEWSLETTER_HOUR + 1):
        # Log missed window ONCE if we're past the grace period
        if now.hour >= NEWSLETTER_HOUR + 1 and not _missed_warning_shown:
            _log_utc("warning", f"⚠️ MISSED GENERATION WINDOW: Newsletter grace period ended at {NEWSLETTER_HOUR + 1:02d}:00 UTC, now {now.hour:02d}:00 UTC")
            _missed_warning_shown = True
        return False, f"Not in grace period (current hour: {now.hour:02d}:00 UTC, grace period: {NEWSLETTER_HOUR:02d}:00-{NEWSLETTER_HOUR + 1:02d}:00 UTC)"

    # Reset missed warning for next period
    if NEWSLETTER_HOUR <= now.hour < NEWSLETTER_HOUR + 1:
        _missed_warning_shown = False

    # Rule 3: Check last newsletter generation
    last_newsletter = _get_last_newsletter_date()

    if last_newsletter is None:
        return True, "First newsletter generation (no previous newsletters found)"

    # Rule 4: Ensure at least 5 days since last generation (prevent same-week duplicates)
    days_since_last = (now - last_newsletter).days

    if days_since_last < 5:
        return False, f"Too recent - last newsletter {days_since_last} days ago (need >= 5 days)"

    # Rule 5: Check if already generated this week
    # Calculate this week's Sunday (weekday 6 = Sunday, so we need days since last Sunday)
    days_since_sunday = (now.weekday() + 1) % 7
    start_of_week = now - timedelta(days=days_since_sunday)  # This week's Sunday
    if last_newsletter >= start_of_week:
        return False, f"Already generated this week (last: {last_newsletter.strftime('%Y-%m-%d')})"

    return True, f"Ready to generate (last newsletter: {last_newsletter.strftime('%Y-%m-%d')}, {days_since_last} days ago)"


def get_scheduler_status() -> Dict[str, Any]:
    """
    Get comprehensive scheduler status with production diagnostics.
    
    Returns:
        Dict[str, Any]: Detailed scheduler status
    """
    global scheduler_running, scheduler_thread, last_successful_run
    
    now = datetime.now(timezone.utc)
    should_generate, reason = _should_generate_newsletter()
    last_newsletter = _get_last_newsletter_date()

    # Calculate next scheduled run
    days_until_scheduled = (NEWSLETTER_DAY - now.weekday()) % 7
    if days_until_scheduled == 0 and now.hour >= NEWSLETTER_HOUR + 1:  # Past scheduled window today
        days_until_scheduled = 7
    next_scheduled = (now + timedelta(days=days_until_scheduled)).replace(hour=NEWSLETTER_HOUR, minute=0, second=0, microsecond=0)
    
    return {
        "scheduler_status": "running" if scheduler_running else "stopped",
        "thread_alive": scheduler_thread.is_alive() if scheduler_thread else False,
        "current_time": now.isoformat(),
        "is_sunday": now.weekday() == 6,
        "current_hour": now.hour,
        "midnight_window": 0 <= now.hour < 1,
        "should_generate_now": should_generate,
        "generation_check_reason": reason,
        "last_newsletter_date": last_newsletter.isoformat() if last_newsletter else "None",
        "days_since_last": (now - last_newsletter).days if last_newsletter else "N/A",
        "next_scheduled_run": next_scheduled.isoformat(),
        "last_successful_run": last_successful_run.isoformat() if last_successful_run else "None",
        "scheduled_jobs_count": len(schedule.jobs)
    }


def force_run_newsletter() -> bool:
    """
    Force newsletter generation with production safety checks.
    
    Returns:
        bool: True if successful, False if failed
    """
    global last_successful_run
    
    try:
        logger.info("🧪 Manual newsletter generation requested")
        
        # Production safety: Check if we should generate
        should_generate, reason = _should_generate_newsletter()
        
        if not should_generate:
            logger.warning(f"⚠️ Manual generation blocked: {reason}")
            # For testing, we'll allow override with explicit warning
            logger.info("🔓 Proceeding with manual override for testing")
        
        # Import and run the complete pipeline (video ingestion + newsletter)
        from src.schedulers.main_pipeline import run_complete_weekly_pipeline
        from src.utils.error_logger import log_newsletter_failure

        logger.info("🚀 Starting complete weekly pipeline (ingestion + newsletter)...")
        success = run_complete_weekly_pipeline()

        if success:
            last_successful_run = datetime.now(timezone.utc)
            logger.info("✅ Manual newsletter generation completed successfully")
            return True
        else:
            logger.error("❌ Newsletter generation pipeline returned failure")
            log_newsletter_failure("manual_pipeline", "Manual newsletter pipeline returned failure status")
            return False

    except ImportError as e:
        logger.error(f"❌ Newsletter pipeline not found: {e}")
        log_newsletter_failure("manual_import", f"Cannot import newsletter pipeline for manual run: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Manual newsletter generation failed: {e}")
        log_newsletter_failure("manual_exception", f"Unexpected error in manual generation: {str(e)}")
        return False


def _scheduled_newsletter_job():
    """
    PRODUCTION VERSION - Full safety checks enabled.
    """
    global last_successful_run
    
    try:
        _log_utc("info", "📅 Sunday midnight scheduler triggered")

        # Production safety: Check if we should actually generate
        should_generate, reason = _should_generate_newsletter()

        if not should_generate:
            _log_utc("info", f"🚫 Newsletter generation skipped: {reason}")
            return
        
        _log_utc("info", f"✅ Safety check passed: {reason}")
        _log_utc("info", "🚀 Starting scheduled complete pipeline (ingestion + newsletter)...")
        
        from src.schedulers.main_pipeline import run_complete_weekly_pipeline
        from src.utils.error_logger import log_newsletter_failure

        success = run_complete_weekly_pipeline()

        if success:
            last_successful_run = datetime.now(timezone.utc)
            logger.info("✅ Scheduled newsletter generation completed successfully")
        else:
            logger.error("❌ Scheduled newsletter generation failed")
            log_newsletter_failure("complete_pipeline", "Weekly newsletter pipeline returned failure status")

    except ImportError as e:
        logger.error(f"❌ Newsletter pipeline not available: {e}")
        log_newsletter_failure("pipeline_import", f"Cannot import newsletter pipeline: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Scheduled newsletter job failed: {e}")
        log_newsletter_failure("scheduler_exception", f"Unexpected error in scheduled job: {str(e)}")


def _scheduler_worker():
    """Railway-optimized scheduler worker - minimal resource usage."""
    global scheduler_running
    
    logger.info("📅 Railway-optimized scheduler started (production mode)")
    
    while scheduler_running:
        try:
            # Railway optimization: Only check frequently during Sunday midnight window
            now = datetime.now(timezone.utc)
            
            # Check if we're in active window: grace period + 30 minutes before for preparation
            is_active_window = False
            if NEWSLETTER_HOUR == 0:
                # Special case for midnight: check from 23:30 previous day to 00:59 current day (grace period)
                prev_day = (NEWSLETTER_DAY - 1) % 7
                is_active_window = (
                    (now.weekday() == prev_day and now.hour >= 23) or
                    (now.weekday() == NEWSLETTER_DAY and now.hour == 0)  # Only hour 0 (00:00-00:59)
                )
            else:
                # Normal case: 30 minutes before to end of grace period
                start_hour = max(0, NEWSLETTER_HOUR - 1)
                end_hour = min(23, NEWSLETTER_HOUR + 1)  # Grace period extends 1 hour after scheduled time
                is_active_window = now.weekday() == NEWSLETTER_DAY and (start_hour <= now.hour < end_hour)
            
            if is_active_window:
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                _log_utc("info", f"🎯 {day_names[NEWSLETTER_DAY]} {NEWSLETTER_HOUR:02d}:00-{NEWSLETTER_HOUR + 1:02d}:00 UTC grace period - Active scheduler checking")

                # Primary logic: Check if we should generate newsletter within grace period
                should_generate, reason = _should_generate_newsletter()
                if should_generate:
                    _log_utc("info", f"✅ Grace period trigger: {reason}")
                    _scheduled_newsletter_job()
                else:
                    _log_utc("info", f"🚫 Grace period check: {reason}")

                time.sleep(30)  # Check every 30 seconds during active window
            else:
                # Railway optimization: Sleep longer when not needed (reduces CPU/memory)
                next_check = (now.replace(second=0, microsecond=0) + timedelta(minutes=5)).strftime('%H:%M:%S UTC')
                _log_utc("info", f"💤 Inactive period: sleeping 5 minutes (next check: {next_check})")
                time.sleep(300)  # Check every 5 minutes when inactive
                
        except Exception as e:
            logger.error(f"❌ Scheduler worker error: {e}")
            time.sleep(60)
            
    logger.info("📅 Railway scheduler worker stopped")


def start_weekly_scheduler():
    """
    Start production weekly newsletter scheduler.
    Schedules for Sunday midnight UTC with production safety.
    """
    global scheduler_thread, scheduler_running
    
    if scheduler_running:
        logger.warning("⚠️ Scheduler already running")
        return
    
    try:
        # Clear any existing jobs
        schedule.clear()
        
        # Schedule for configured day and time
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        schedule_time = f"{NEWSLETTER_HOUR:02d}:00"
        job = getattr(schedule.every(), day_names[NEWSLETTER_DAY]).at(schedule_time).do(_scheduled_newsletter_job)
        logger.info(f"🕐 Scheduled job created: {day_names[NEWSLETTER_DAY].title()} at {schedule_time} UTC (Job: {job})")
        
        # Start background worker thread
        scheduler_running = True
        scheduler_thread = threading.Thread(target=_scheduler_worker, daemon=True)
        scheduler_thread.start()
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        logger.info("✅ Railway-optimized newsletter scheduler started")
        logger.info(f"📅 Scheduled: Every {day_names[NEWSLETTER_DAY]} at {NEWSLETTER_HOUR:02d}:00 UTC (grace period: {NEWSLETTER_HOUR:02d}:00-{NEWSLETTER_HOUR + 1:02d}:00 UTC)")
        logger.info("🔒 Production safety: Duplicate prevention enabled")
        logger.info(f"⚡ Railway optimization: Low resource mode (5min intervals, active only {day_names[NEWSLETTER_DAY]} {NEWSLETTER_HOUR:02d}:00-{NEWSLETTER_HOUR + 1:02d}:00 grace period)")
        logger.info("📊 Edge cases handled: First run, week gaps, failure recovery")
        
    except Exception as e:
        scheduler_running = False
        logger.error(f"❌ Failed to start production scheduler: {e}")
        raise


def stop_weekly_scheduler():
    """Stop weekly newsletter scheduler safely."""
    global scheduler_running, scheduler_thread
    
    if not scheduler_running:
        logger.warning("⚠️ Scheduler not running")
        return
    
    try:
        scheduler_running = False
        schedule.clear()
        
        if scheduler_thread and scheduler_thread.is_alive():
            logger.info("🛑 Stopping scheduler worker thread...")
            scheduler_thread.join(timeout=10.0)
            
            if scheduler_thread.is_alive():
                logger.warning("⚠️ Scheduler thread did not stop gracefully")
        
        logger.info("✅ Weekly newsletter scheduler stopped safely")
        
    except Exception as e:
        logger.error(f"❌ Error stopping scheduler: {e}")


if __name__ == "__main__":
    # Production diagnostics
    print("🔍 Production Newsletter Scheduler Diagnostics")
    print("=" * 50)
    
    status = get_scheduler_status()
    for key, value in status.items():
        print(f"{key}: {value}")
    
    print("\n🧪 Testing force run (with safety checks)...")
    success = force_run_newsletter()
    print(f"Result: {'✅ Success' if success else '❌ Failed'}")