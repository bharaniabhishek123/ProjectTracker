# 🚀 Quick Start - 5 Minute Setup

## For POC Testing (No Local Installation!)

You only need **Docker Desktop** installed. Nothing else!

### 1. Choose Your Setup Speed

**Option A: Full Setup with AI (5-10 min first time)**
```bash
./docker-test.sh
```

**Option B: Quick Start without waiting for AI (30 seconds)**
```bash
./docker-quick.sh
```

Both options start all containers, but the quick version doesn't wait for Ollama to be fully ready.

### What the Full Setup Does

The `docker-test.sh` script will:
- ✅ Start PostgreSQL in a container
- ✅ Start Ollama (AI) in a container
- ✅ Start the web app in a container
- ✅ Download the AI model
- ✅ Run automated tests
- ✅ Show you the URL

**Time:** 5-10 minutes first time (downloading images)
**Subsequent runs:** 30 seconds

### 2. Access Your Application

Open in browser: **http://localhost:8000**

### 3. What You Get

```
┌─────────────────────────────────────┐
│   Your Computer                     │
│   (Only Docker Installed)           │
│                                     │
│   ┌──────────┐  ┌──────────┐       │
│   │PostgreSQL│  │  Ollama  │       │
│   └────┬─────┘  └────┬─────┘       │
│        └──────┬───────┘             │
│               │                     │
│         ┌─────▼─────┐               │
│         │  Web App  │               │
│         └───────────┘               │
│               │                     │
└───────────────┼─────────────────────┘
                │
         Browser Access
      localhost:8000
```

### 4. Quick Demo

1. **Register Team Members** (Team Members tab)
   - Add Alice, Bob, Charlie

2. **Submit Status Updates** (Submit Status tab)
   - "Implemented feature X"
   - "Fixed bugs Y and Z"
   - "Completed code review"

3. **View Dashboard** (Dashboard tab)
   - See all updates chronologically
   - Filter by person or date

4. **Try AI Search** (AI Search tab)
   - "What did Alice work on?"
   - "Show me all bug fixes"
   - "What features were completed?"

5. **Generate Summary** (Weekly Summary tab)
   - Pick a date range
   - Get AI-generated summary

### 5. Stop Everything

```bash
docker-compose down
```

### 6. Clean Restart (Fresh Database)

```bash
docker-compose down -v
./docker-test.sh
```

## Windows Users

Use `docker-test.bat` instead of `docker-test.sh`

## Troubleshooting

**Ollama Taking Too Long or Timing Out?**

If you see "Ollama failed to start" or it's taking forever:

**Solution 1: Use the quick script (recommended)**
```bash
# Kill and restart with quick script
docker-compose down
./docker-quick.sh
```
The quick script starts everything but doesn't wait for Ollama to be fully ready. Your app works immediately, and AI features become available in 1-2 minutes background.

**Solution 2: Skip Ollama temporarily**
```bash
docker-compose up -d
curl http://localhost:8000/health  # Test if app is ready
# Use the app without AI features, or pull model later:
docker exec project_tracker_ollama ollama pull llama3.1
```

**Why?** Ollama can take 30-120 seconds to start. The core app doesn't need it!

---

**Containers won't start?**
```bash
docker-compose logs -f
```

**Port already in use?**
```bash
# Stop other services using these ports:
# 8000 (web), 5432 (postgres), 11434 (ollama)
```

**Clean slate?**
```bash
docker-compose down -v
docker system prune -a
./docker-test.sh
```

## What's Running?

Check container status:
```bash
docker-compose ps
```

View logs:
```bash
docker-compose logs -f app     # Application logs
docker-compose logs -f db      # Database logs
docker-compose logs -f ollama  # AI service logs
```

## Next Steps

- **Full Guide**: [DOCKER_SETUP.md](DOCKER_SETUP.md)
- **Architecture**: [README.md](README.md)
- **API Docs**: http://localhost:8000/docs (after starting)

---

**Perfect for POC - Zero setup hassle!** 🎉
