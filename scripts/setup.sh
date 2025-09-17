#!/bin/bash
set -euo pipefail

# Setup script for Mini Cluster
# This script reads config.yml and sets up the environment

echo "Mini Cluster Setup"
echo "=================="

# Check if config.yml exists
if [ ! -f "config.yml" ]; then
    echo "Error: config.yml not found!"
    echo "Please ensure config.yml exists in the current directory."
    exit 1
fi

# Install Python dependencies if needed
echo "Checking Python dependencies..."
python3 -c "import yaml" 2>/dev/null || {
    echo "Installing PyYAML..."
    pip3 install PyYAML
}

# Generate .env file from config.yml
echo "Generating .env file from config.yml..."
python3 config_loader.py generate-env

echo "✅ .env file generated successfully!"
echo ""

# Show current configuration
echo "Current configuration:"
echo "====================="
cat .env
echo ""

# Offer to start the cluster
read -p "Do you want to start the cluster now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting the cluster..."
    make up
else
    echo "Setup complete! Run 'make up' when you're ready to start the cluster."
fi
