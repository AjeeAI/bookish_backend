#!/bin/bash

# 1. Initialize Database (Safe to run every time)
echo "🌱 Seeding Database..."
python seed.py

# 2. Start the Server
# Uses the PORT environment variable if available, otherwise defaults to 8000
echo "🚀 Starting Uvicorn Server..."
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}