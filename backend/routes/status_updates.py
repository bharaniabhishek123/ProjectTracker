from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import TeamMember, StatusUpdate
from backend.schemas import (
    StatusUpdateCreate,
    StatusUpdateResponse,
    StatusUpdateWithMember
)
from backend.services.vector_store import get_vector_store

router = APIRouter(prefix="/api/status-updates", tags=["Status Updates"])


@router.post("/", response_model=StatusUpdateResponse, status_code=status.HTTP_201_CREATED)
async def create_status_update(
    status_update: StatusUpdateCreate,
    db: Session = Depends(get_db)
):
    """Submit a daily status update."""
    # Verify team member exists
    member = db.query(TeamMember).filter(TeamMember.id == status_update.team_member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team member with ID {status_update.team_member_id} not found"
        )

    # Create status update
    update_data = status_update.model_dump()
    if update_data['date'] is None:
        update_data['date'] = datetime.utcnow()

    db_status = StatusUpdate(**update_data)
    db.add(db_status)
    db.commit()
    db.refresh(db_status)

    # Sync to vector store for semantic search
    try:
        vector_store = get_vector_store()
        vector_store.add_status_update(
            status_id=db_status.id,
            text=db_status.status_text,
            metadata={
                'team_member_id': db_status.team_member_id,
                'team_member_name': member.name,
                'date': str(db_status.date)
            }
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Failed to sync to vector store: {e}")

    return db_status


@router.get("/", response_model=List[StatusUpdateWithMember])
async def list_status_updates(
    team_member_id: Optional[int] = Query(None, description="Filter by team member ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of status updates with filters."""
    query = db.query(StatusUpdate)

    # Apply filters
    if team_member_id:
        query = query.filter(StatusUpdate.team_member_id == team_member_id)

    if start_date:
        query = query.filter(StatusUpdate.date >= start_date)

    if end_date:
        query = query.filter(StatusUpdate.date <= end_date)

    # Order by date descending (most recent first)
    query = query.order_by(StatusUpdate.date.desc())

    # Apply pagination
    status_updates = query.offset(skip).limit(limit).all()

    return status_updates


@router.get("/{update_id}", response_model=StatusUpdateWithMember)
async def get_status_update(
    update_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific status update by ID."""
    status_update = db.query(StatusUpdate).filter(StatusUpdate.id == update_id).first()
    if not status_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Status update with ID {update_id} not found"
        )
    return status_update


@router.delete("/{update_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_status_update(
    update_id: int,
    db: Session = Depends(get_db)
):
    """Delete a status update."""
    status_update = db.query(StatusUpdate).filter(StatusUpdate.id == update_id).first()
    if not status_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Status update with ID {update_id} not found"
        )

    # Delete from vector store
    try:
        vector_store = get_vector_store()
        vector_store.delete_status_update(update_id)
    except Exception as e:
        print(f"Warning: Failed to delete from vector store: {e}")

    db.delete(status_update)
    db.commit()
    return None
