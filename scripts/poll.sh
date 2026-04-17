#!/bin/bash
# DataGate RSS Poller — 由 macOS LaunchAgent 定時呼叫
# 也可手動執行：bash scripts/poll.sh

set -e

# 取得專案根目錄（此腳本的上一層）
DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 載入 .env（若存在）
if [ -f "$DIR/.env" ]; then
  export $(grep -v '^#' "$DIR/.env" | xargs)
fi

# 使用 pyenv 或系統 python
PYTHON="${PYTHON_BIN:-python3}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] DataGate RSS Poller 啟動"
cd "$DIR"
$PYTHON pipeline/rss_poller.py
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成"
