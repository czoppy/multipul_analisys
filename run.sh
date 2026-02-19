#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if ! python3 -c "import flask" 2>/dev/null; then
  echo "Installing dependencies..."
  pip install -r requirements.txt -q
fi

echo ""
echo "  Thesis Reading Tracker"
echo "  Open: http://localhost:5000"
echo ""
python3 app.py
