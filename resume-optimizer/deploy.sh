#!/bin/bash
set -e

echo "🚀 Deploying Resume Optimizer..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env with your ANTHROPIC_API_KEY"
    exit 1
fi

# Source environment variables
source .env

# Check for required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not set in .env"
    exit 1
fi

echo "✅ Environment variables validated"

# Build and start containers
echo "📦 Building Docker images..."
docker-compose build

echo "🚀 Starting containers..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
echo "🔍 Checking service health..."
docker-compose ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop: docker-compose down"
echo "   Restart: docker-compose restart"
echo ""
