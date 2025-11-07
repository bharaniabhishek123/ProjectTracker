#!/bin/bash

# Quick Docker Test - Starts containers without waiting for Ollama model
# Use this for faster testing when you don't need AI features immediately

set -e

echo "🚀 Quick Docker Setup (No Ollama Wait)"
echo "========================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed. Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Determine docker compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "📦 Starting containers..."
$DOCKER_COMPOSE up -d --build

echo ""
echo "⏳ Waiting for core services..."

# Wait for PostgreSQL
echo "   Checking PostgreSQL..."
sleep 5
for i in {1..20}; do
    if docker exec project_tracker_db pg_isready -U tracker_user -d project_tracker &> /dev/null; then
        echo "   ✅ PostgreSQL ready"
        break
    fi
    sleep 2
done

# Wait for App
echo "   Checking FastAPI app..."
for i in {1..20}; do
    if curl -s http://localhost:8000/health &> /dev/null; then
        echo "   ✅ App ready"
        break
    fi
    sleep 2
done

echo ""
echo "🧪 Running basic tests..."

# Quick health check
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ API is responding"
else
    echo "❌ API health check failed"
    exit 1
fi

# Test team member creation
MEMBER=$(curl -s -X POST http://localhost:8000/api/team-members/ \
    -H "Content-Type: application/json" \
    -d '{"name":"Test User","email":"test@example.com","role":"Tester"}')
if echo "$MEMBER" | grep -q "id"; then
    echo "✅ Database operations working"
else
    echo "❌ Database test failed"
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ CORE FUNCTIONALITY WORKING!"
echo "=================================================="
echo ""
echo "🌐 Access your app at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo ""
echo "⏰ Note: Ollama (AI features) is starting in background"
echo "   AI features will be available in 1-2 minutes"
echo ""
echo "To pull the AI model manually:"
echo "   docker exec project_tracker_ollama ollama pull llama3.1"
echo ""
echo "View logs with:"
echo "   $DOCKER_COMPOSE logs -f"
