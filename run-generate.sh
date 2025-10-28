#!/bin/bash
# Quick test script to run generate command in Docker

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Please create .env from .env.example and add your GOOGLE_API_KEY"
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker-compose build

# Run the generate command
echo "🚀 Running test generation..."
docker-compose run --rm ai-tester generate "$@"
