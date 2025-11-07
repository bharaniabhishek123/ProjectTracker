# Project: AI Project Tracker Agent

## Overview
An AI-powered system that tracks team deliverables and provides chronological views of team progress.

## Requirements

### Core Features
1. **Daily Status Input**
   - Team members submit daily status updates
   - Simple input interface (web form or chat bot)

2. **Memory & Retrieval**
   - Remember what each team member did daily
   - Semantic search: "What did John work on last month?"
   - Retrieve historical context

3. **Chronological Dashboard**
   - Web interface for management
   - Filter by date, week, team member
   - Timeline visualization of achievements

### Technical Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (structured data) + ChromaDB/Qdrant (vector store)
- **LLM**: Ollama with Llama 3.1 or Mistral (local/open-source)
- **Frontend**: Simple HTML/JS with htmx or React
- **Visualization**: Timeline library (vis-timeline or similar)

### Architecture
- RESTful API for status submissions
- Vector database for semantic memory
- LLM for summarization and query answering
- Authentication for management dashboard

## MVP Scope
Start with:
1. Team member registration
2. Daily status text submission
3. Store in PostgreSQL with timestamps
4. Simple chronological list view
5. Basic weekly summary generation
```

