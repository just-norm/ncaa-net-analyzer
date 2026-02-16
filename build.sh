#!/bin/bash
set -e

echo "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Building site..."
python3 build.py

echo "Build complete!"
