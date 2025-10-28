# Quick test script to run generate command in Docker (Windows PowerShell)

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create .env from .env.example and add your GOOGLE_API_KEY"
    exit 1
}

# Build the Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Cyan
docker-compose build

# Run the generate command
Write-Host "🚀 Running test generation..." -ForegroundColor Green
docker-compose run --rm ai-tester generate $args
