from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from backend.models import GoalStatus, TaskStatus, TaskPriority


# Team Member Schemas
class TeamMemberBase(BaseModel):
    """Base team member schema."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: Optional[str] = Field(None, max_length=100)


class TeamMemberCreate(TeamMemberBase):
    """Schema for creating a team member."""
    pass


class TeamMemberResponse(TeamMemberBase):
    """Schema for team member response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Status Update Schemas
class StatusUpdateBase(BaseModel):
    """Base status update schema."""
    status_text: str = Field(..., min_length=1)


class StatusUpdateCreate(StatusUpdateBase):
    """Schema for creating a status update."""
    team_member_id: int
    task_id: Optional[int] = None  # Optional link to task
    date: Optional[datetime] = None


class StatusUpdateResponse(StatusUpdateBase):
    """Schema for status update response."""
    id: int
    team_member_id: int
    task_id: Optional[int] = None
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class StatusUpdateWithMember(StatusUpdateResponse):
    """Status update with team member info."""
    team_member: TeamMemberResponse

    class Config:
        from_attributes = True


# Query Schemas
class SemanticSearchRequest(BaseModel):
    """Schema for semantic search request."""
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)


class SemanticSearchResult(BaseModel):
    """Schema for semantic search result."""
    status_update: StatusUpdateWithMember
    relevance_score: float


class WeeklySummaryRequest(BaseModel):
    """Schema for weekly summary request."""
    start_date: datetime
    end_date: Optional[datetime] = None
    team_member_id: Optional[int] = None


class WeeklySummaryResponse(BaseModel):
    """Schema for weekly summary response."""
    start_date: datetime
    end_date: datetime
    team_member: Optional[str] = None
    summary: str
    status_count: int

# Goal Schemas
class GoalBase(BaseModel):
    """Base goal schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: GoalStatus = GoalStatus.NOT_STARTED
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None


class GoalCreate(GoalBase):
    """Schema for creating a goal."""
    pass


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[GoalStatus] = None
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None


class GoalResponse(GoalBase):
    """Schema for goal response."""
    id: int
    completed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    task_count: int = 0
    completed_task_count: int = 0
    progress_percentage: float = 0.0

    class Config:
        from_attributes = True


class GoalWithTasks(GoalResponse):
    """Goal with its tasks."""
    tasks: List['TaskResponse'] = []

    class Config:
        from_attributes = True


# Task Schemas
class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    goal_id: int


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int
    goal_id: int
    completed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    update_count: int = 0

    class Config:
        from_attributes = True


class TaskWithDetails(TaskResponse):
    """Task with goal and assignee details."""
    goal: Optional[GoalResponse] = None
    assignee: Optional[TeamMemberResponse] = None
    recent_updates: List[StatusUpdateResponse] = []

    class Config:
        from_attributes = True


# Progress Schemas
class GoalProgressResponse(BaseModel):
    """Schema for goal progress report."""
    goal: GoalResponse
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    progress_percentage: float
    on_track: bool
    days_remaining: Optional[int] = None


class TeamMemberProgressResponse(BaseModel):
    """Schema for team member progress report."""
    team_member: TeamMemberResponse
    assigned_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    overdue_tasks: int
    completion_rate: float
