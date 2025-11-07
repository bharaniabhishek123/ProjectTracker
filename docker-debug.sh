#!/bin/bash

# Docker Debug Script - Diagnose common container issues

echo "🔍 Docker Container Diagnostics"
echo "================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed"
    exit 1
fi

# Determine docker compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "1. Container Status"
echo "-------------------"
$DOCKER_COMPOSE ps
echo ""

echo "2. Port Usage Check"
echo "-------------------"
echo "Checking if required ports are available..."
for port in 8000 5432 11434; do
    if lsof -i :$port &> /dev/null; then
        echo "❌ Port $port is IN USE"
        lsof -i :$port | head -2
    else
        echo "✅ Port $port is available"
    fi
done
echo ""

echo "3. App Container Logs (last 30 lines)"
echo "--------------------------------------"
docker logs project_tracker_app --tail 30 2>&1
echo ""

echo "4. Database Container Logs (last 20 lines)"
echo "-------------------------------------------"
docker logs project_tracker_db --tail 20 2>&1
echo ""

echo "5. Ollama Container Logs (last 20 lines)"
echo "-----------------------------------------"
docker logs project_tracker_ollama --tail 20 2>&1
echo ""

echo "6. Docker Network Status"
echo "------------------------"
docker network inspect projecttracker_tracker_network 2>&1 | head -20
echo ""

echo "7. Volume Status"
echo "----------------"
docker volume ls | grep project
echo ""

echo "8. Quick Tests"
echo "--------------"
echo "Testing database connection..."
if docker exec project_tracker_db pg_isready -U tracker_user -d project_tracker &> /dev/null; then
    echo "✅ Database is responding"
else
    echo "❌ Database is not responding"
fi

echo "Testing app health..."
if curl -s http://localhost:8000/health &> /dev/null; then
    echo "✅ App is responding"
    curl -s http://localhost:8000/health | head -3
else
    echo "❌ App is not responding"
fi

echo "Testing Ollama..."
if curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "✅ Ollama is responding"
else
    echo "❌ Ollama is not responding"
fi
echo ""

echo "9. Common Solutions"
echo "-------------------"
echo "If app container keeps restarting:"
echo "  → docker logs project_tracker_app -f"
echo ""
echo "If port is in use:"
echo "  → Stop the conflicting service or change port in docker-compose.yml"
echo ""
echo "If database connection fails:"
echo "  → docker-compose restart db"
echo "  → Check DATABASE_URL in docker-compose.yml"
echo ""
echo "Nuclear option (fresh start):"
echo "  → docker-compose down -v"
echo "  → docker-compose up --build -d"
echo ""
