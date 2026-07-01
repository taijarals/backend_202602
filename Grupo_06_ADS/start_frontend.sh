#!/bin/bash
# EduGame Platform - Start Frontend
echo "Starting EduGame Platform Frontend..."
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
streamlit run Home.py
