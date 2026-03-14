#!/usr/bin/env bash
# start.sh — Launch the paper trading market maker bot.
#
# Usage:
#   ./start.sh              # Live Polymarket data, $100 virtual capital
#   ./start.sh --demo       # Offline demo mode (no internet needed)
#   ./start.sh --capital 500 # Override starting capital
#
# Works on local machines, GitHub Codespaces, and any Linux/macOS terminal.

set -e

cd "$(dirname "$0")"

# Install dependency if missing
python -c "import requests" 2>/dev/null || pip install -r requirements.txt

exec python -m bot "$@"
