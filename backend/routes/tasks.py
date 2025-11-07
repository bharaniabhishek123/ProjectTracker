from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.models import Task, Goal, TeamMember, StatusUpdate, TaskStatus, TaskPriority
from backend.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskWithDetails,
    TeamMemberProgressResponse
)

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new task."""
    # Verify goal exists
    goal = db.query(Goal).filter(Goal.id == task.goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {task.goal_id} not found"
        )

    # Verify team member exists if assigned
    if task.assigned_to:
        member = db.query(TeamMember).filter(TeamMember.id == task.assigned_to).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team member with ID {task.assigned_to} not found"
            )

    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Add update count
    db_task.update_count = 0
    return db_task


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    goal_id: Optional[int] = Query(None, description="Filter by goal ID"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned team member"),
    status_filter: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of tasks with filters."""
    query = db.query(Task)

    if goal_id:
        query = query.filter(Task.goal_id == goal_id)

    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    if status_filter:
        query = query.filter(Task.status == status_filter)

    if priority:
        query = query.filter(Task.priority == priority)

    query = query.order_by(Task.created_at.desc())
    tasks = query.offset(skip).limit(limit).all()

    # Add update count
    for task in tasks:
        task.update_count = len(task.status_updates)

    return tasks


@router.get("/{task_id}", response_model=TaskWithDetails)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific task with details."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    # Add update count and recent updates
    task.update_count = len(task.status_updates)
    task.recent_updates = task.status_updates[-5:]  # Last 5 updates

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update a task."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    # Verify team member if changing assignment
    if task_update.assigned_to is not None:
        member = db.query(TeamMember).filter(TeamMember.id == task_update.assigned_to).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team member with ID {task_update.assigned_to} not found"
            )

    # Update fields
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    # Auto-set completed_date if status changed to completed
    if task_update.status == TaskStatus.COMPLETED and not db_task.completed_date:
        db_task.completed_date = datetime.utcnow()

    db.commit()
    db.refresh(db_task)

    # Add update count
    db_task.update_count = len(db_task.status_updates)
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Delete a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    db.delete(task)
    db.commit()
    return None


@router.get("/member/{member_id}/assigned", response_model=List[TaskResponse])
async def get_member_tasks(
    member_id: int,
    status_filter: Optional[TaskStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get all tasks assigned to a team member."""
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team member with ID {member_id} not found"
        )

    query = db.query(Task).filter(Task.assigned_to == member_id)

    if status_filter:
        query = query.filter(Task.status == status_filter)

    tasks = query.order_by(Task.due_date.asc()).all()

    # Add update count
    for task in tasks:
        task.update_count = len(task.status_updates)

    return tasks


@router.get("/member/{member_id}/progress", response_model=TeamMemberProgressResponse)
async def get_member_progress(
    member_id: int,
    db: Session = Depends(get_db)
):
    """Get progress report for a team member."""
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team member with ID {member_id} not found"
        )

    assigned_tasks = db.query(func.count(Task.id)).filter(Task.assigned_to == member_id).scalar() or 0
    completed_tasks = db.query(func.count(Task.id)).filter(
        and_(Task.assigned_to == member_id, Task.status == TaskStatus.COMPLETED)
    ).scalar() or 0
    in_progress_tasks = db.query(func.count(Task.id)).filter(
        and_(Task.assigned_to == member_id, Task.status == TaskStatus.IN_PROGRESS)
    ).scalar() or 0
    overdue_tasks = db.query(func.count(Task.id)).filter(
        and_(
            Task.assigned_to == member_id,
            Task.due_date < datetime.utcnow(),
            Task.status != TaskStatus.COMPLETED
        )
    ).scalar() or 0

    completion_rate = (completed_tasks / assigned_tasks * 100) if assigned_tasks > 0 else 0.0

    return TeamMemberProgressResponse(
        team_member=member,
        assigned_tasks=assigned_tasks,
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        overdue_tasks=overdue_tasks,
        completion_rate=round(completion_rate, 2)
    )
