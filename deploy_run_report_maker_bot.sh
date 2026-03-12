#!/bin/bash

# 1. Define variables (Update these to match your server)
PROJECT_DIR="/home/user/run_report_maker_bot"
VENV_PATH="$PROJECT_DIR/venv"
SERVICE_NAME="running_bot.service"

echo "🚀 Starting deployment..."

# 2. Navigate to project directory
cd $PROJECT_DIR || { echo "❌ Directory not found"; exit 1; }

# 3. Pull latest changes from GitHub
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# 4. Update dependencies (assuming you use a virtual environment)
if [ -d "$VENV_PATH" ]; then
    echo "📦 Updating python dependencies..."
    source $VENV_PATH/bin/activate
    pip install -r requirements.txt
else
    echo "⚠️ Virtual environment not found at $VENV_PATH. Skipping pip install."
fi

# 5. Restart the systemd service
echo "🔄 Restarting $SERVICE_NAME..."
sudo systemctl restart $SERVICE_NAME

# 6. Check status
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Deployment successful! $SERVICE_NAME is running."
else
    echo "❌ Deployment failed! Check logs with: sudo journalctl -u $SERVICE_NAME"
    exit 1
fi
