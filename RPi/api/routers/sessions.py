from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from database import get_session
from models.session import Session as SessionModel
from models.session import SessionCreate
from repositories.session_repository import SessionRepository

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


def get_repo(db: Session = Depends(get_session)):
    return SessionRepository(db)


@router.post("/start", response_model=SessionModel)
def start_session(
    repo: SessionRepository = Depends(get_repo),
):
    session = SessionModel(
        started_at=datetime.now(timezone.utc),
        ended_at=None,
    )

    return repo.create(session)


@router.get("/", response_model=list[SessionModel])
def get_all(
    repo: SessionRepository = Depends(get_repo),
):
    return repo.get_all()


@router.get("/{session_id}", response_model=SessionModel)
def get_one(
    session_id: int,
    repo: SessionRepository = Depends(get_repo),
):
    session = repo.get_one(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return session


@router.put("/{session_id}", response_model=SessionModel)
def update(
    session_id: int,
    updated_session: SessionCreate,
    repo: SessionRepository = Depends(get_repo),
):
    session_obj = SessionModel(
        **updated_session.model_dump()
    )

    updated = repo.update(
        session_id,
        session_obj,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return updated


@router.put("/{session_id}/end", response_model=SessionModel)
def end_session(
    session_id: int,
    repo: SessionRepository = Depends(get_repo),
):
    session = repo.get_one(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    session.ended_at = datetime.now(timezone.utc)

    return repo.update(
        session_id,
        session,
    )


@router.delete("/{session_id}")
def delete(
    session_id: int,
    repo: SessionRepository = Depends(get_repo),
):
    success = repo.delete(session_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {
        "detail": "Session deleted successfully"
    }