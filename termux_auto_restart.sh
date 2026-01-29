#!/bin/bash

# Discord Bot Auto-Restart Script for Termux
# 봇이 크래시하면 자동으로 재시작합니다

LOG_FILE="bot_run.log"
RESTART_DELAY=5

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ===== Bot Auto-Restart Service Started =====" >> $LOG_FILE

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Discord Bot..." >> $LOG_FILE
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Discord Bot..."
    
    python3 main.py >> $LOG_FILE 2>&1
    
    EXIT_CODE=$?
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bot crashed with exit code: $EXIT_CODE" >> $LOG_FILE
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Waiting ${RESTART_DELAY}s before restart..."
    
    sleep $RESTART_DELAY
done
