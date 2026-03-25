#!/bin/bash

echo "========================================"
echo "PlayStation Cafe Manager - Quick Build"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

echo "Cleaning previous builds..."
rm -rf dist
rm -rf build/build
rm -f build/*.spec

echo ""
echo "Building executable..."
python3 build/build.py

echo ""
echo "Done! Check the 'dist' folder."