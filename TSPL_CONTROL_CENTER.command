#!/bin/bash
# TSPL Control Center Launcher
# Created by Antigravity AI

# 1. Navigate to project directory
cd "/Users/phu/Desktop/งานพี่กบ/Web"

# 2. Kill existing process on port 5556 (Safety first)
lsof -ti:5556 | xargs kill -9 2>/dev/null || true

# 3. Start the dashboard in the background
echo "🟢 Starting TSPL Control Center (Matrix Mode)..."
python3 tools_web/dashboard.py > /dev/null 2>&1 &

# 4. Wait for server to warm up
sleep 2

# 5. Open the dashboard in default browser
open "http://localhost:5556"

echo "✅ Dashboard is now running at http://localhost:5556"
echo "You can minimize this window. Closing it will NOT stop the dashboard."
