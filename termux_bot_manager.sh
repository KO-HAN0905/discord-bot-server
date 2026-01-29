#!/bin/bash

# Termux Bot Manager - 봇을 관리하는 편한 스크립트
# 사용: bash bot_manager.sh [start|stop|restart|status]

BOT_DIR="$HOME/discord-bot-server"
SCREEN_NAME="bot"

case "$1" in
    start)
        echo "[*] Starting bot..."
        cd $BOT_DIR
        screen -S $SCREEN_NAME -d -m python3 main.py
        sleep 1
        screen -ls | grep $SCREEN_NAME
        echo "[✓] Bot started"
        ;;
    
    stop)
        echo "[*] Stopping bot..."
        pkill -f "python3 main.py"
        screen -X -S $SCREEN_NAME quit 2>/dev/null
        echo "[✓] Bot stopped"
        ;;
    
    restart)
        echo "[*] Restarting bot..."
        pkill -f "python3 main.py"
        sleep 2
        cd $BOT_DIR
        screen -S $SCREEN_NAME -d -m python3 main.py
        echo "[✓] Bot restarted"
        ;;
    
    status)
        echo "[*] Checking bot status..."
        if pgrep -f "python3 main.py" > /dev/null; then
            echo "[✓] Bot is RUNNING"
            ps aux | grep "python3 main.py" | grep -v grep
        else
            echo "[✗] Bot is STOPPED"
        fi
        ;;
    
    *)
        echo "Bot Manager for Termux"
        echo "Usage: bash bot_manager.sh [start|stop|restart|status]"
        ;;
esac
