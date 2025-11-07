from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import StatusUpdate, TeamMember
from backend.schemas import (
    SemanticSearchRequest,
    StatusUpdateWithMember,
    WeeklySummaryRequest,
    WeeklySummaryResponse
)
from backend.services.vector_store import get_vector_store
from backend.services.llm_service import get_llm_service

router = APIRouter(prefix="/api/ai", tags=["AI Features"])


@router.post("/search")
async def semantic_search(
    search_request: SemanticSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform semantic search on status updates.

    Example: "What did John work on last month?"
    """
    vector_store = get_vector_store()
    llm_service = get_llm_service()

    # Perform semantic search
    results = vector_store.search_similar(
        query=search_request.query,
        n_results=search_request.limit
    )

    # Get full status update details from database
    status_updates = []
    for result in results:
        status_id = result['id']
        status = db.query(StatusUpdate).filter(StatusUpdate.id == status_id).first()
        if status:
            status_updates.append({
                'status_update': status,
                'relevance_score': 1.0 - result['distance'] if result['distance'] else 1.0
            })

    # Generate answer using LLM
    answer = llm_service.answer_query(
        query=search_request.query,
        relevant_updates=[
            {
                'status_text': item['status_update'].status_text,
                'team_member': {
                    'name': item['status_update'].team_member.name
                },
                'date': str(item['status_update'].date)
            }
            for item in status_updates
        ]
    )

    return {
        "query": search_request.query,
        "answer": answer,
        "relevant_updates": status_updates,
        "count": len(status_updates)
    }


@router.post("/weekly-summary", response_model=WeeklySummaryResponse)
async def generate_weekly_summary(
    summary_request: WeeklySummaryRequest,
    db: Session = Depends(get_db)
):
    """Generate a weekly summary of team progress."""
    llm_service = get_llm_service()

    # Calculate end date if not provided
    end_date = summary_request.end_date or (summary_request.start_date + timedelta(days=7))

    # Query status updates for the period
    query = db.query(StatusUpdate).filter(
        StatusUpdate.date >= summary_request.start_date,
        StatusUpdate.date <= end_date
    )

    # Filter by team member if specified
    team_member_name = None
    if summary_request.team_member_id:
        query = query.filter(StatusUpdate.team_member_id == summary_request.team_member_id)
        member = db.query(TeamMember).filter(TeamMember.id == summary_request.team_member_id).first()
        if member:
            team_member_name = member.name

    status_updates = query.all()

    if not status_updates:
        return WeeklySummaryResponse(
            start_date=summary_request.start_date,
            end_date=end_date,
            team_member=team_member_name,
            summary="No status updates found for the specified period.",
            status_count=0
        )

    # Format status updates for LLM
    formatted_updates = [
        {
            'status_text': update.status_text,
            'team_member': {
                'name': update.team_member.name
            },
            'date': str(update.date)
        }
        for update in status_updates
    ]

    # Generate summary
    summary = llm_service.generate_weekly_summary(
        status_updates=formatted_updates,
        team_member_name=team_member_name
    )

    return WeeklySummaryResponse(
        start_date=summary_request.start_date,
        end_date=end_date,
        team_member=team_member_name,
        summary=summary,
        status_count=len(status_updates)
    )


@router.post("/sync-vector-store")
async def sync_vector_store(db: Session = Depends(get_db)):
    """
    Sync all status updates to the vector store.
    Useful for initial setup or after database changes.
    """
    vector_store = get_vector_store()

    # Get all status updates
    status_updates = db.query(StatusUpdate).all()

    synced_count = 0
    for update in status_updates:
        try:
            vector_store.add_status_update(
                status_id=update.id,
                text=update.status_text,
                metadata={
                    'team_member_id': update.team_member_id,
                    'team_member_name': update.team_member.name,
                    'date': str(update.date)
                }
            )
            synced_count += 1
        except Exception as e:
            print(f"Error syncing status update {update.id}: {e}")

    return {
        "message": "Vector store sync completed",
        "total_updates": len(status_updates),
        "synced_count": synced_count
    }


@router.get("/health-check")
async def ai_health_check():
    """Check if AI services (Ollama, ChromaDB) are available."""
    llm_service = get_llm_service()
    vector_store = get_vector_store()

    ollama_status = llm_service.check_connection()
    vector_count = vector_store.get_collection_count()

    return {
        "ollama_available": ollama_status,
        "vector_store_count": vector_count,
        "status": "healthy" if ollama_status else "degraded"
    }
