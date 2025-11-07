from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from backend.database import get_db
from backend.models import TeamMember
from backend.schemas import TeamMemberCreate, TeamMemberResponse

router = APIRouter(prefix="/api/team-members", tags=["Team Members"])


@router.post("/", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    member: TeamMemberCreate,
    db: Session = Depends(get_db)
):
    """Register a new team member."""
    try:
        # Check if email already exists
        existing_member = db.query(TeamMember).filter(TeamMember.email == member.email).first()
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team member with email {member.email} already exists"
            )

        # Create new team member
        db_member = TeamMember(**member.model_dump())
        db.add(db_member)
        db.commit()
        db.refresh(db_member)

        return db_member

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create team member. Email may already exist."
        )


@router.get("/", response_model=List[TeamMemberResponse])
async def list_team_members(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all team members."""
    members = db.query(TeamMember).offset(skip).limit(limit).all()
    return members


@router.get("/{member_id}", response_model=TeamMemberResponse)
async def get_team_member(
    member_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific team member by ID."""
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team member with ID {member_id} not found"
        )
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(
    member_id: int,
    db: Session = Depends(get_db)
):
    """Delete a team member."""
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team member with ID {member_id} not found"
        )

    db.delete(member)
    db.commit()
    return None
