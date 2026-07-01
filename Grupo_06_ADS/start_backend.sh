#!/bin/bash
# EduGame Platform - Start Backend
echo "Starting EduGame Platform Backend..."
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
