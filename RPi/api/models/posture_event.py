from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from api.models.session import Session
from api.models.posture_class import PostureClass


class PostureEventBase(SQLModel):
    detected_at: datetime
    confidence: float = Field(ge=0, le=1)

    sensor_presence: bool
    alert_triggered: bool


class PostureEvent(PostureEventBase, table=True):
    __tablename__ = "posture_events"

    event_id: Optional[int] = Field(default=None, primary_key=True)

    session_id: int = Field(foreign_key="sessions.session_id")
    posture_id: int = Field(foreign_key="posture_classes.posture_id")

    # session: Optional[Session] = Relationship()
    # posture_class: Optional[PostureClass] = Relationship()


class PostureEventCreate(PostureEventBase):
    session_id: int
    posture_id: int