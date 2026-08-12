from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class PostureClassBase(SQLModel):
    posture: str


class PostureClass(PostureClassBase, table=True):
    
    __tablename__ = "posture_classes"
    
    posture_id: Optional[int] = Field(default=None, primary_key=True)


class PostureClassCreate(PostureClassBase):
    pass