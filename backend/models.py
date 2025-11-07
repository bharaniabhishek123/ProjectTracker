from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class TeamMember(Base):
    """Team member model."""

    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    status_updates = relationship("StatusUpdate", back_populates="team_member", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TeamMember(id={self.id}, name='{self.name}', email='{self.email}')>"


class StatusUpdate(Base):
    """Daily status update model."""

    __tablename__ = "status_updates"

    id = Column(Integer, primary_key=True, index=True)
    team_member_id = Column(Integer, ForeignKey("team_members.id"), nullable=False, index=True)
    status_text = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    team_member = relationship("TeamMember", back_populates="status_updates")

    def __repr__(self):
        return f"<StatusUpdate(id={self.id}, team_member_id={self.team_member_id}, date='{self.date}')>"
