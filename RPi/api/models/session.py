from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class SessionBase(SQLModel):
    started_at: datetime
    ended_at: Optional[datetime] = None


class Session(SessionBase, table=True):
    
    __tablename__ = "sessions"
    
    session_id: Optional[int] = Field(default=None, primary_key=True)


class SessionCreate(SessionBase):
    pass