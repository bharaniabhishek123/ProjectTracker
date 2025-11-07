# AI Project Tracker

An AI-powered system that tracks team deliverables and provides chronological views of team progress with semantic search and automated summaries.

## Features

- **Daily Status Tracking**: Team members can submit daily status updates
- **Chronological Dashboard**: View team progress over time with filtering options
- **Semantic Search**: Ask natural language questions about team activities
- **AI-Powered Summaries**: Generate weekly summaries using Ollama LLM
- **Team Management**: Register and manage team members
- **Vector Search**: ChromaDB-powered semantic search for finding relevant updates

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (structured data) + ChromaDB (vector store)
- **LLM**: Ollama with Llama 3.1 or Mistral
- **Frontend**: HTML/JavaScript with htmx
- **Deployment**: Docker & Docker Compose

## Prerequisites

1. **Docker & Docker Compose** (recommended) OR:
2. **Python 3.11+**
3. **PostgreSQL 15+**
4. **Ollama** - [Installation Guide](https://ollama.ai/)

## Quick Start with Docker (Recommended)

### 1. Install Ollama

First, install Ollama on your host machine:

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.ai/download
```

Pull the Llama 3.1 model:

```bash
ollama pull llama3.1
```

### 2. Start the Application

```bash
# Clone the repository
git clone <repository-url>
cd ProjectTracker

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app
```

The application will be available at: **http://localhost:8000**

### 3. Stop the Application

```bash
docker-compose down

# To remove volumes (database data)
docker-compose down -v
```

## Manual Setup (Without Docker)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Setup PostgreSQL

```bash
# Create database
createdb project_tracker

# Or using psql
psql -U postgres
CREATE DATABASE project_tracker;
```

### 3. Configure Environment

Create a `.env` file:

```env
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/project_tracker
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
CHROMA_PERSIST_DIR=./data/chroma_data
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

### 4. Install and Start Ollama

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama3.1

# Start Ollama service (runs in background)
ollama serve
```

### 5. Run the Application

```bash
# Run directly
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Or using the main module
python backend/main.py
```

Visit: **http://localhost:8000**

## Usage Guide

### 1. Register Team Members

1. Navigate to the **Team Members** tab
2. Fill in name, email, and optional role
3. Click "Register Member"

### 2. Submit Status Updates

1. Go to the **Submit Status** tab
2. Select your name from the dropdown
3. Write your daily status update
4. Click "Submit Status"

### 3. View Dashboard

1. Navigate to the **Dashboard** tab
2. Filter by team member or time period
3. View chronological status updates

### 4. Semantic Search

1. Go to the **AI Search** tab
2. Ask natural language questions:
   - "What did John work on last week?"
   - "Show me all bug fixes"
   - "What features were completed in November?"
3. Get AI-powered answers with relevant status updates

### 5. Generate Weekly Summaries

1. Navigate to the **Weekly Summary** tab
2. Select start date
3. Optionally filter by team member
4. Click "Generate Summary"
5. Get an AI-generated summary of the week's activities

## API Documentation

Once the application is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### Key Endpoints

#### Team Members
- `POST /api/team-members/` - Register a new team member
- `GET /api/team-members/` - List all team members
- `GET /api/team-members/{id}` - Get specific team member
- `DELETE /api/team-members/{id}` - Delete team member

#### Status Updates
- `POST /api/status-updates/` - Submit status update
- `GET /api/status-updates/` - List status updates (with filters)
- `GET /api/status-updates/{id}` - Get specific status update
- `DELETE /api/status-updates/{id}` - Delete status update

#### AI Features
- `POST /api/ai/search` - Semantic search
- `POST /api/ai/weekly-summary` - Generate weekly summary
- `POST /api/ai/sync-vector-store` - Sync database to vector store
- `GET /api/ai/health-check` - Check AI services status

## Project Structure

```
ProjectTracker/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── routes/              # API routes
│   │   ├── team_members.py
│   │   ├── status_updates.py
│   │   └── ai_features.py
│   └── services/            # Business logic
│       ├── vector_store.py  # ChromaDB integration
│       └── llm_service.py   # Ollama LLM integration
├── frontend/
│   ├── static/
│   │   └── style.css        # CSS styles
│   └── templates/
│       └── index.html       # Main web interface
├── data/                    # Data directory (gitignored)
│   └── chroma_data/        # ChromaDB persistence
├── docker-compose.yml       # Docker services definition
├── Dockerfile              # Application container
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── CLAUDE.md              # Project requirements
└── README.md              # This file
```

## Troubleshooting

### Ollama Connection Issues

If you see "Error generating summary" or AI features not working:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Check if model is downloaded
ollama list

# Pull model if needed
ollama pull llama3.1
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U tracker_user -d project_tracker
```

### Vector Store Issues

If semantic search isn't working:

1. Navigate to AI Search tab
2. The application automatically syncs new status updates
3. For existing data, use the sync endpoint:

```bash
curl -X POST http://localhost:8000/api/ai/sync-vector-store
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest
```

### Database Migrations

```bash
# Create migration (when using Alembic)
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Hot Reload

The application runs with `--reload` flag by default in development mode, so changes to Python files will automatically reload the server.

## Configuration

All configuration is done via environment variables. See `.env.example` for available options:

- `DATABASE_URL` - PostgreSQL connection string
- `OLLAMA_BASE_URL` - Ollama API endpoint
- `OLLAMA_MODEL` - LLM model to use (llama3.1, mistral, etc.)
- `CHROMA_PERSIST_DIR` - ChromaDB data directory
- `APP_HOST` - Application host (default: 0.0.0.0)
- `APP_PORT` - Application port (default: 8000)
- `DEBUG` - Debug mode (True/False)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review API documentation at `/docs`

## Future Enhancements

- [ ] User authentication and authorization
- [ ] Email notifications for status reminders
- [ ] Advanced analytics and charts
- [ ] Export reports to PDF
- [ ] Mobile app
- [ ] Slack/Teams integration
- [ ] Custom AI prompts
- [ ] Multi-project support
