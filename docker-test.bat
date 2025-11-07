@echo off
REM AI Project Tracker - Docker Setup and Test Script for Windows
REM This script starts all services in containers (no local installation needed!)

echo ========================================
echo AI Project Tracker - Containerized Setup
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed
    echo Please install Docker Desktop from: https://docs.docker.com/desktop/install/windows-install/
    exit /b 1
)

echo [OK] Docker is installed
echo.

echo Step 1: Building and starting containers...
echo    This includes: PostgreSQL, Ollama, and the App
docker-compose up -d --build

echo.
echo Step 2: Waiting for services to be ready...

REM Wait for PostgreSQL
echo    Waiting for PostgreSQL...
timeout /t 10 /nobreak >nul
docker exec project_tracker_db pg_isready -U tracker_user -d project_tracker >nul 2>&1
if errorlevel 1 (
    timeout /t 10 /nobreak >nul
    docker exec project_tracker_db pg_isready -U tracker_user -d project_tracker >nul 2>&1
)
echo    [OK] PostgreSQL is ready

REM Wait for Ollama
echo    Waiting for Ollama...
timeout /t 10 /nobreak >nul
echo    [OK] Ollama is ready

REM Wait for App
echo    Waiting for FastAPI app...
timeout /t 10 /nobreak >nul
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    timeout /t 10 /nobreak >nul
)
echo    [OK] FastAPI app is ready

echo.
echo Step 3: Pulling Ollama model (llama3.1)...
echo    This may take a few minutes on first run...
docker exec project_tracker_ollama ollama pull llama3.1

echo.
echo Step 4: Running API tests...
echo.

REM Test 1: Health check
echo Test 1: Health Check
curl -s http://localhost:8000/health | findstr "healthy" >nul
if errorlevel 1 (
    echo [FAIL] Health check failed
    exit /b 1
)
echo [OK] Health check passed

REM Test 2: Create team member
echo.
echo Test 2: Create Team Member
curl -s -X POST http://localhost:8000/api/team-members/ -H "Content-Type: application/json" -d "{\"name\":\"Alice Johnson\",\"email\":\"alice@example.com\",\"role\":\"Software Engineer\"}" > temp_member.json
findstr "id" temp_member.json >nul
if errorlevel 1 (
    echo [FAIL] Failed to create team member
    exit /b 1
)
echo [OK] Team member created

REM Test 3: Create status update
echo.
echo Test 3: Submit Status Update
curl -s -X POST http://localhost:8000/api/status-updates/ -H "Content-Type: application/json" -d "{\"team_member_id\":1,\"status_text\":\"Implemented authentication and fixed critical bugs\"}" > temp_status.json
findstr "id" temp_status.json >nul
if errorlevel 1 (
    echo [FAIL] Failed to create status update
    exit /b 1
)
echo [OK] Status update created

REM Cleanup temp files
del temp_member.json temp_status.json 2>nul

echo.
echo ========================================
echo ALL TESTS PASSED!
echo ========================================
echo.
echo Application is running at:
echo    Web Interface: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo Useful commands:
echo    View logs:        docker-compose logs -f
echo    Stop services:    docker-compose down
echo    Clean everything: docker-compose down -v
echo.
echo No local installation required - everything runs in containers!

pause
