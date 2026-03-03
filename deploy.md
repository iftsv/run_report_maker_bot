# Deployment Guide

This guide explains how to deploy the Run Report Maker Bot on an Ubuntu server.

## 1. Clone the repository
```bash
git clone <your-repo-url> /home/user/running_bot
cd /home/user/running_bot
```

## 2. Set up environment
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## 3. Configuration
Create a `.env` file from the example:
```bash
cp .env.example .env
nano .env
```
Fill in your `BOT_TOKEN`.

## 4. Set up as a Systemd Service
Copy the service file and enable it:
```bash
sudo cp running_bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable running_bot.service
sudo systemctl start running_bot.service
```

## 5. Monitoring
To check if the bot is running:
```bash
sudo systemctl status running_bot.service
```
To view logs:
```bash
journalctl -u running_bot.service -f
```
