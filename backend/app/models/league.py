from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class League(Base):
    """
    Represents a fantasy football league connected to the application.

    A league can be from various platforms (ESPN, Sleeper, Yahoo, etc.)
    and contains teams, matchups, and other league-specific data.
    """

    __tablename__ = "leagues"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # League identification
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # League configuration stored as JSON
    # This can include: scoring settings, roster positions, playoff format, etc.
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    teams: Mapped[list["Team"]] = relationship(
        "Team", back_populates="league", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<League(id={self.id}, name='{self.name}', platform='{self.platform}')>"
