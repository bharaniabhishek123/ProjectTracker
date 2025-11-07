from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


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
    date: Optional[datetime] = None


class StatusUpdateResponse(StatusUpdateBase):
    """Schema for status update response."""
    id: int
    team_member_id: int
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
