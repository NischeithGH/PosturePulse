from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from database import get_session
from models.posture_event import (
    PostureEvent,
    PostureEventCreate,
)
from repositories.posture_event_repository import (
    PostureEventRepository,
)

router = APIRouter(
    prefix="/posture-events",
    tags=["Posture Events"],
)


def get_repo(db: Session = Depends(get_session)):
    return PostureEventRepository(db)


@router.get("/", response_model=list[PostureEvent])
def get_all(
    repo: PostureEventRepository = Depends(get_repo),
):
    return repo.get_all()


@router.get("/{event_id}", response_model=PostureEvent)
def get_one(
    event_id: int,
    repo: PostureEventRepository = Depends(get_repo),
):
    event = repo.get_one(event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Posture event not found",
        )

    return event


@router.post("/", response_model=PostureEvent)
def create(
    event: PostureEventCreate,
    repo: PostureEventRepository = Depends(get_repo),
):
    event_obj = PostureEvent(
        **event.model_dump()
    )

    return repo.create(event_obj)


@router.put("/{event_id}", response_model=PostureEvent)
def update(
    event_id: int,
    updated_event: PostureEventCreate,
    repo: PostureEventRepository = Depends(get_repo),
):
    event = repo.get_one(event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Posture event not found",
        )

    for key, value in updated_event.model_dump().items():
        setattr(event, key, value)

    return repo.update(event)


@router.delete("/{event_id}")
def delete(
    event_id: int,
    repo: PostureEventRepository = Depends(get_repo),
):
    success = repo.delete(event_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Posture event not found",
        )

    return {
        "detail": "Posture event deleted successfully"
    }


@router.get("/session/{session_id}")
def get_by_session(
    session_id: int,
    repo: PostureEventRepository = Depends(get_repo),
):
    return repo.get_by_session(session_id)


@router.get("/posture/{posture_id}")
def get_by_posture(
    posture_id: int,
    repo: PostureEventRepository = Depends(get_repo),
):
    return repo.get_by_posture(posture_id)