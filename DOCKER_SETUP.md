# Docker Setup Guide - No Local Installation Required!

This guide helps you run the AI Project Tracker entirely in Docker containers - **no need to install PostgreSQL, Ollama, or Python locally!**

## Prerequisites

**Only Docker is required:**
- [Docker Desktop](https://docs.docker.com/get-docker/) (includes Docker Compose)
- That's it! No other installation needed.

## Quick Start (Automated)

### Option 1: One-Command Setup and Test

```bash
# This will build, start, and test everything automatically
./docker-test.sh
```

The script will:
1. ✅ Build and start all containers (PostgreSQL, Ollama, FastAPI app)
2. ✅ Wait for services to be ready
3. ✅ Download the Llama 3.1 model for AI features
4. ✅ Run automated tests
5. ✅ Display access URLs

**Expected output:** All tests should pass in ~2-5 minutes (depending on model download speed)

### Option 2: Manual Setup

If you prefer to do it step-by-step:

```bash
# 1. Start all services
docker-compose up -d --build

# 2. Wait ~30 seconds for services to start, then check status
docker-compose ps

# 3. Pull the Ollama model (first time only, takes 2-3 minutes)
docker exec project_tracker_ollama ollama pull llama3.1

# 4. Verify everything is running
curl http://localhost:8000/health
```

## Accessing the Application

Once running, access:

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Container Architecture

```
┌─────────────────────────────────────────────────┐
│  Your Computer (only Docker installed)         │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  PostgreSQL  │  │    Ollama    │           │
│  │  Container   │  │   Container  │           │
│  │  Port: 5432  │  │  Port: 11434 │           │
│  └──────┬───────┘  └──────┬───────┘           │
│         │                  │                    │
│         └────────┬─────────┘                   │
│                  │                              │
│         ┌────────▼─────────┐                   │
│         │   FastAPI App    │                   │
│         │    Container     │                   │
│         │   Port: 8000     │                   │
│         └──────────────────┘                   │
│                  │                              │
└──────────────────┼──────────────────────────────┘
                   │
            Access via browser
         http://localhost:8000
```

## Testing the Setup

### Quick API Tests

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Create a team member
curl -X POST http://localhost:8000/api/team-members/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "role": "Developer"
  }'

# 3. Submit a status update (replace MEMBER_ID with actual ID from step 2)
curl -X POST http://localhost:8000/api/status-updates/ \
  -H "Content-Type: application/json" \
  -d '{
    "team_member_id": 1,
    "status_text": "Completed feature X and fixed bugs Y and Z"
  }'

# 4. List all status updates
curl http://localhost:8000/api/status-updates/

# 5. Check AI services
curl http://localhost:8000/api/ai/health-check
```

### Using the Web Interface

1. Open http://localhost:8000
2. Go to **Team Members** tab → Register team members
3. Go to **Submit Status** tab → Submit daily updates
4. Go to **Dashboard** tab → View all updates
5. Go to **AI Search** tab → Ask questions like "What did John work on?"
6. Go to **Weekly Summary** tab → Generate AI summaries

## Managing Containers

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f ollama
```

### Check Status

```bash
docker-compose ps
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart app
```

### Stop Services

```bash
# Stop but keep data
docker-compose down

# Stop and remove all data (clean slate)
docker-compose down -v
```

### Update and Rebuild

```bash
# Rebuild after code changes
docker-compose up -d --build
```

## Troubleshooting

### Ollama Model Not Downloaded

If AI features don't work:

```bash
# Check if model is downloaded
docker exec project_tracker_ollama ollama list

# Download if missing
docker exec project_tracker_ollama ollama pull llama3.1
```

### Container Won't Start

```bash
# Check logs
docker-compose logs app
docker-compose logs db

# Clean restart
docker-compose down -v
docker-compose up -d --build
```

### Port Already in Use

If you get "port already allocated" errors:

```bash
# Check what's using the port
lsof -i :8000  # or :5432, :11434

# Either stop that service or change ports in docker-compose.yml
```

### Database Connection Issues

```bash
# Connect to database to check
docker exec -it project_tracker_db psql -U tracker_user -d project_tracker

# Inside psql:
\dt  # List tables
SELECT * FROM team_members;  # Query data
\q   # Exit
```

### Reset Everything

```bash
# Nuclear option - complete fresh start
docker-compose down -v
docker system prune -a
./docker-test.sh
```

## Performance Notes

### First Run
- **Time**: 5-10 minutes
- **Why**: Downloading images + Ollama model (4GB+)
- **Space**: ~8GB total

### Subsequent Runs
- **Time**: 10-30 seconds
- **Space**: Data grows with usage

### Resource Usage
- **CPU**: Moderate (higher during AI operations)
- **RAM**: 2-4GB recommended
- **Disk**: 8GB + data

## Production Considerations

This Docker setup is perfect for:
- ✅ POC and testing
- ✅ Development
- ✅ Small team deployments
- ✅ Demo environments

For production at scale, consider:
- Using external PostgreSQL (like AWS RDS)
- Deploying Ollama separately with GPU support
- Using Kubernetes for orchestration
- Adding proper secrets management
- Implementing backup strategies

## FAQ

**Q: Do I need to install Python, PostgreSQL, or Ollama locally?**
A: No! Everything runs in containers.

**Q: Can I use a different LLM model?**
A: Yes! Change `OLLAMA_MODEL` in docker-compose.yml to any Ollama model (mistral, codellama, etc.)

**Q: How do I backup my data?**
A: Data is in Docker volumes. Export with:
```bash
docker exec project_tracker_db pg_dump -U tracker_user project_tracker > backup.sql
```

**Q: Can I run this on a server?**
A: Yes! Just ensure Docker is installed and ports are accessible.

**Q: What if I want to use GPU for faster AI?**
A: Update the ollama service in docker-compose.yml:
```yaml
ollama:
  image: ollama/ollama:latest
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

## Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify all containers are running: `docker-compose ps`
3. Try clean restart: `docker-compose down -v && docker-compose up -d`
4. Check disk space: `docker system df`

---

**That's it! No local installations, just Docker.** 🐳
