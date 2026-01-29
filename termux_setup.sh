#!/bin/bash

# Termux Setup Script for Discord Bot
# 스마트폰에서 첫 실행할 때 이 스크립트를 사용하세요

echo "=========================================="
echo "Discord Bot Termux Setup Script"
echo "=========================================="
echo ""

echo "[1/6] Updating packages..."
apt update && apt upgrade -y

echo "[2/6] Installing required tools..."
apt install -y python3 python3-pip git curl wget openssh nano

echo "[3/6] Python version check..."
python3 --version

echo "[4/6] Setting up repository..."
if [ ! -d "discord-bot-server" ]; then
    git clone https://github.com/KO-HAN0905/discord-bot-server.git
else
    cd discord-bot-server
    git pull origin main
    cd ..
fi

cd discord-bot-server

echo "[5/6] Installing Python dependencies..."
pip install discord.py requests python-dotenv APScheduler gspread google-auth gtts

echo "[6/6] Setting up permissions..."
chmod +x *.sh 2>/dev/null

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next: nano .env (add DISCORD_BOT_TOKEN)"
