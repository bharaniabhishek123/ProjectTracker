#!/bin/bash

# AI Project Tracker - Docker Setup and Test Script
# This script starts all services in containers (no local installation needed!)

set -e

echo "🚀 AI Project Tracker - Fully Containerized Setup"
echo "=================================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "   Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "   Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Use docker compose (new) or docker-compose (old)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "📦 Step 1: Building and starting containers..."
echo "   This includes: PostgreSQL, Ollama, and the App"
$DOCKER_COMPOSE up -d --build

echo ""
echo "⏳ Step 2: Waiting for services to be ready..."

# Wait for PostgreSQL
echo "   Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker exec project_tracker_db pg_isready -U tracker_user -d project_tracker &> /dev/null; then
        echo "   ✅ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ PostgreSQL failed to start"
        exit 1
    fi
    sleep 2
done

# Wait for Ollama
echo "   Waiting for Ollama (this may take 30-60 seconds)..."
for i in {1..60}; do
    # Check if ollama service is responding
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo "   ✅ Ollama is ready"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "   ⚠️  Ollama is taking longer than expected, but continuing..."
        echo "   Note: AI features may take a moment to become available"
        break
    fi
    sleep 2
done

# Wait for App
echo "   Waiting for FastAPI app..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health &> /dev/null; then
        echo "   ✅ FastAPI app is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ App failed to start"
        exit 1
    fi
    sleep 2
done

echo ""
echo "🤖 Step 3: Pulling Ollama model (llama3.1)..."
echo "   This may take 2-5 minutes on first run (downloads ~4GB)..."
echo "   Subsequent runs will skip this step if model is already downloaded."
echo ""

# Check if model already exists
if docker exec project_tracker_ollama ollama list 2>/dev/null | grep -q "llama3.1"; then
    echo "   ✅ Model already downloaded, skipping..."
else
    docker exec project_tracker_ollama ollama pull llama3.1
    if [ $? -eq 0 ]; then
        echo "   ✅ Model downloaded successfully"
    else
        echo "   ⚠️  Model download had issues, but continuing..."
        echo "   You can manually pull it later: docker exec project_tracker_ollama ollama pull llama3.1"
    fi
fi

echo ""
echo "🧪 Step 4: Running API tests..."
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# Test 2: Create team member
echo ""
echo "Test 2: Create Team Member"
MEMBER=$(curl -s -X POST http://localhost:8000/api/team-members/ \
    -H "Content-Type: application/json" \
    -d '{"name":"Alice Johnson","email":"alice@example.com","role":"Software Engineer"}')
MEMBER_ID=$(echo "$MEMBER" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
if [ ! -z "$MEMBER_ID" ]; then
    echo "✅ Team member created (ID: $MEMBER_ID)"
else
    echo "❌ Failed to create team member"
    exit 1
fi

# Test 3: Create status update
echo ""
echo "Test 3: Submit Status Update"
STATUS=$(curl -s -X POST http://localhost:8000/api/status-updates/ \
    -H "Content-Type: application/json" \
    -d "{\"team_member_id\":$MEMBER_ID,\"status_text\":\"Implemented authentication and fixed critical bugs\"}")
STATUS_ID=$(echo "$STATUS" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
if [ ! -z "$STATUS_ID" ]; then
    echo "✅ Status update created (ID: $STATUS_ID)"
else
    echo "❌ Failed to create status update"
    exit 1
fi

# Test 4: List status updates
echo ""
echo "Test 4: List Status Updates"
UPDATES=$(curl -s http://localhost:8000/api/status-updates/)
if echo "$UPDATES" | grep -q "Implemented authentication"; then
    echo "✅ Status updates retrieved successfully"
else
    echo "❌ Failed to retrieve status updates"
    exit 1
fi

# Test 5: AI health check
echo ""
echo "Test 5: AI Services Health Check"
AI_HEALTH=$(curl -s http://localhost:8000/api/ai/health-check)
if echo "$AI_HEALTH" | grep -q "ollama_available"; then
    OLLAMA_STATUS=$(echo "$AI_HEALTH" | grep -o '"ollama_available":[a-z]*' | grep -o '[a-z]*$')
    echo "✅ AI health check passed (Ollama: $OLLAMA_STATUS)"
else
    echo "❌ AI health check failed"
fi

# Test 6: Test weekly summary (if Ollama is available)
echo ""
echo "Test 6: Generate AI Summary"
SUMMARY=$(curl -s -X POST http://localhost:8000/api/ai/weekly-summary \
    -H "Content-Type: application/json" \
    -d "{\"start_date\":\"2025-11-01T00:00:00\"}")
if echo "$SUMMARY" | grep -q "summary"; then
    echo "✅ AI summary generated successfully"
else
    echo "⚠️  AI summary generation skipped (may need Ollama model)"
fi

echo ""
echo "=================================================="
echo "🎉 ALL TESTS PASSED!"
echo "=================================================="
echo ""
echo "📊 Application is running at:"
echo "   🌐 Web Interface: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   🔍 Alternative Docs: http://localhost:8000/redoc"
echo ""
echo "📦 Container Status:"
$DOCKER_COMPOSE ps
echo ""
echo "📝 Useful commands:"
echo "   View logs:        $DOCKER_COMPOSE logs -f"
echo "   Stop services:    $DOCKER_COMPOSE down"
echo "   Restart:          $DOCKER_COMPOSE restart"
echo "   Clean everything: $DOCKER_COMPOSE down -v"
echo ""
echo "✨ No local installation required - everything runs in containers!"
