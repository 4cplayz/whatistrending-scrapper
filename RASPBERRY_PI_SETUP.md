# TikTok Newsletter - Raspberry Pi Setup Guide

This guide walks you through deploying the TikTok Car Edit Newsletter service on a Raspberry Pi for 24/7 operation.

## Prerequisites

- Raspberry Pi with Raspberry Pi OS installed
- Internet connection
- SSH access to your Pi
- GitHub repository access

## Required API Keys

Before starting, obtain these API keys:
- **Supabase**: Database (supabase.com)
- **Apify Token**: TikTok scraping (console.apify.com/account/integrations)
- **Twelve Labs API**: Video analysis
- **OpenAI API**: Content generation

## Step 1: Clone Repository

```bash
# Make your repository public temporarily for easy cloning
# On GitHub: Settings → Make Public

# Clone to Pi
git clone https://github.com/yourusername/whatistrending-scrapper.git
cd whatistrending-scrapper
```

## Step 2: Install System Dependencies

```bash
# Update system packages
sudo apt update

# Install required system packages
sudo apt install python3-pip python3-venv python3-dev build-essential
```

## Step 3: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt now

# Install Python dependencies (takes 15-30 minutes on Pi)
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

Add your API keys to the .env file:
```env
# Required API Keys
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
APIFY_TOKEN=your_apify_token
TWELVE_LABS_API_KEY=your_twelve_labs_api_key
OPENAI_API_KEY=your_openai_api_key

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
FLASK_PORT=8080
FLASK_HOST=0.0.0.0
```

Save and exit: `Ctrl+X`, `Y`, `Enter`

## Step 5: Test Manual Run

```bash
# Test the application works
python3 main.py

# You should see:
# 🚀 Starting TikTok Car Edit Newsletter Service
# ✅ All environment variables present
# 🌐 Flask server starting on port 8080
# * Running on http://192.168.x.x:8080

# Test from another terminal or browser:
curl http://localhost:8080/health

# Stop with Ctrl+C when confirmed working
```

## Step 6: Create System Service

Create the systemd service file:

```bash
sudo nano /etc/systemd/system/tiktok-newsletter.service
```

Paste this content (replace `tom` with your username):

```ini
[Unit]
Description=TikTok Newsletter Service
After=network.target

[Service]
Type=simple
User=tom
WorkingDirectory=/home/tom/whatistrending-scrapper
Environment=PATH=/home/tom/whatistrending-scrapper/venv/bin
ExecStart=/home/tom/whatistrending-scrapper/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save and exit: `Ctrl+X`, `Y`, `Enter`

## Step 7: Enable and Start Service

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable tiktok-newsletter.service

# Start the service
sudo systemctl start tiktok-newsletter.service

# Check service status
sudo systemctl status tiktok-newsletter.service
```

You should see:
```
● tiktok-newsletter.service - TikTok Newsletter Service
   Active: active (running)
```

## Step 8: Verify Installation

```bash
# Test health endpoint
curl http://localhost:8080/health

# Check service endpoints
curl http://localhost:8080/status

# View live logs
sudo journalctl -u tiktok-newsletter.service -f
```

## Service Management Commands

```bash
# View service status
sudo systemctl status tiktok-newsletter.service

# Stop service
sudo systemctl stop tiktok-newsletter.service

# Start service
sudo systemctl start tiktok-newsletter.service

# Restart service
sudo systemctl restart tiktok-newsletter.service

# Disable service (won't start on boot)
sudo systemctl disable tiktok-newsletter.service

# View all logs
sudo journalctl -u tiktok-newsletter.service --no-pager

# View live logs (real-time updates)
sudo journalctl -u tiktok-newsletter.service -f

# View last 50 log lines
sudo journalctl -u tiktok-newsletter.service -n 50 --no-pager

# Save logs to file
sudo journalctl -u tiktok-newsletter.service --no-pager > newsletter-logs.txt
```

## Network Access

The service runs on port 8080. Access it via:
- Local: `http://localhost:8080`
- Network: `http://[PI_IP_ADDRESS]:8080`
- Find Pi IP: `hostname -I`

## Available Endpoints

- `/` - Home page with service info
- `/health` - Detailed health check with database status
- `/status` - Service status and available endpoints  
- `/newsletter/latest` - Get most recent newsletter
- `/scheduler/status` - Scheduler status
- `/scheduler/force-run` - Manually trigger newsletter generation (POST)

## Scheduled Operation

The service automatically:
- Runs 24/7 with minimal resource usage
- Generates newsletters every Sunday at midnight UTC
- Scrapes TikTok data for the past 7 days
- Analyzes videos with AI for trends
- Stores results in Supabase database

## Troubleshooting

### Service Won't Start
```bash
# Check detailed error logs
sudo journalctl -u tiktok-newsletter.service -n 20

# Verify environment file exists
ls -la /home/tom/whatistrending-scrapper/.env

# Test manual run
cd /home/tom/whatistrending-scrapper
source venv/bin/activate
python3 main.py
```

### Dependencies Issues
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R tom:tom /home/tom/whatistrending-scrapper
chmod +x /home/tom/whatistrending-scrapper/main.py
```

### Network Issues
```bash
# Check if port 8080 is in use
sudo netstat -tlnp | grep :8080

# Check firewall (if enabled)
sudo ufw status
```

## Performance Optimization for Pi

The service is optimized for Raspberry Pi with:
- Low resource usage when inactive (sleeps 5 minutes between checks)
- Only active during Sunday midnight window for newsletter generation
- Efficient caching to reduce database calls
- Graceful shutdown handling

## Security Notes

- Keep `.env` file secure with your API keys
- Consider changing the default port 8080 if needed
- Monitor logs for any unauthorized access attempts
- Keep your Pi system updated with `sudo apt update && sudo apt upgrade`

## Success Indicators

✅ Service shows "active (running)" status  
✅ Health endpoint returns database connection info  
✅ Logs show scheduler started successfully  
✅ No error messages in recent logs  
✅ Service survives Pi reboot  

Your TikTok Newsletter service is now running 24/7 on your Raspberry Pi!