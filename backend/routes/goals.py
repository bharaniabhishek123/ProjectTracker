from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.models import Goal, Task, GoalStatus, TaskStatus
from backend.schemas import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalWithTasks,
    GoalProgressResponse
)

router = APIRouter(prefix="/api/goals", tags=["Goals"])


def calculate_goal_progress(goal: Goal, db: Session) -> dict:
    """Calculate progress metrics for a goal."""
    total_tasks = db.query(func.count(Task.id)).filter(Task.goal_id == goal.id).scalar() or 0
    completed_tasks = db.query(func.count(Task.id)).filter(
        Task.goal_id == goal.id,
        Task.status == TaskStatus.COMPLETED
    ).scalar() or 0

    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    return {
        'task_count': total_tasks,
        'completed_task_count': completed_tasks,
        'progress_percentage': round(progress_percentage, 2)
    }


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db)
):
    """Create a new goal."""
    db_goal = Goal(**goal.model_dump())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)

    # Add progress metrics
    progress = calculate_goal_progress(db_goal, db)
    for key, value in progress.items():
        setattr(db_goal, key, value)

    return db_goal


@router.get("/", response_model=List[GoalResponse])
async def list_goals(
    status_filter: Optional[GoalStatus] = Query(None, description="Filter by status"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all goals with progress metrics."""
    query = db.query(Goal)

    if status_filter:
        query = query.filter(Goal.status == status_filter)

    query = query.order_by(Goal.created_at.desc())
    goals = query.offset(skip).limit(limit).all()

    # Add progress metrics to each goal
    result = []
    for goal in goals:
        progress = calculate_goal_progress(goal, db)
        for key, value in progress.items():
            setattr(goal, key, value)
        result.append(goal)

    return result


@router.get("/{goal_id}", response_model=GoalWithTasks)
async def get_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific goal with its tasks."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )

    # Add progress metrics
    progress = calculate_goal_progress(goal, db)
    for key, value in progress.items():
        setattr(goal, key, value)

    # Calculate update count for each task
    for task in goal.tasks:
        task.update_count = len(task.status_updates)

    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    db: Session = Depends(get_db)
):
    """Update a goal."""
    db_goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not db_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )

    # Update fields
    update_data = goal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_goal, field, value)

    # Auto-set completed_date if status changed to completed
    if goal_update.status == GoalStatus.COMPLETED and not db_goal.completed_date:
        db_goal.completed_date = datetime.utcnow()

    db.commit()
    db.refresh(db_goal)

    # Add progress metrics
    progress = calculate_goal_progress(db_goal, db)
    for key, value in progress.items():
        setattr(db_goal, key, value)

    return db_goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """Delete a goal and all its tasks."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )

    db.delete(goal)
    db.commit()
    return None


@router.get("/{goal_id}/progress", response_model=GoalProgressResponse)
async def get_goal_progress(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed progress report for a goal."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )

    # Calculate detailed metrics
    total_tasks = db.query(func.count(Task.id)).filter(Task.goal_id == goal.id).scalar() or 0
    completed_tasks = db.query(func.count(Task.id)).filter(
        Task.goal_id == goal.id,
        Task.status == TaskStatus.COMPLETED
    ).scalar() or 0
    in_progress_tasks = db.query(func.count(Task.id)).filter(
        Task.goal_id == goal.id,
        Task.status == TaskStatus.IN_PROGRESS
    ).scalar() or 0
    blocked_tasks = db.query(func.count(Task.id)).filter(
        Task.goal_id == goal.id,
        Task.status == TaskStatus.BLOCKED
    ).scalar() or 0

    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    # Calculate if on track
    on_track = True
    days_remaining = None
    if goal.target_date:
        days_remaining = (goal.target_date - datetime.utcnow()).days
        if days_remaining > 0 and total_tasks > 0:
            expected_progress = ((datetime.utcnow() - goal.start_date).days /
                                 (goal.target_date - goal.start_date).days * 100) if goal.start_date else 50
            on_track = progress_percentage >= expected_progress

    # Add progress to goal
    progress = calculate_goal_progress(goal, db)
    for key, value in progress.items():
        setattr(goal, key, value)

    return GoalProgressResponse(
        goal=goal,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        blocked_tasks=blocked_tasks,
        progress_percentage=round(progress_percentage, 2),
        on_track=on_track,
        days_remaining=days_remaining
    )
