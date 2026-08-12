from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from database import get_session
from models.posture_class import (
    PostureClass,
    PostureClassCreate,
)
from repositories.posture_class_repository import (
    PostureClassRepository,
)

router = APIRouter(
    prefix="/posture-classes",
    tags=["Posture Classes"],
)


def get_repo(db: Session = Depends(get_session)):
    return PostureClassRepository(db)


@router.get("/", response_model=list[PostureClass])
def get_all(
    repo: PostureClassRepository = Depends(get_repo),
):
    return repo.get_all()


@router.get("/{posture_id}", response_model=PostureClass)
def get_one(
    posture_id: int,
    repo: PostureClassRepository = Depends(get_repo),
):
    posture = repo.get_one(posture_id)

    if not posture:
        raise HTTPException(
            status_code=404,
            detail="Posture class not found",
        )

    return posture


@router.post("/", response_model=PostureClass)
def create(
    posture_class: PostureClassCreate,
    repo: PostureClassRepository = Depends(get_repo),
):
    existing = repo.get_by_name(
        posture_class.posture
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Posture already exists",
        )

    posture_obj = PostureClass(
        **posture_class.model_dump()
    )

    return repo.create(posture_obj)


@router.put("/{posture_id}", response_model=PostureClass)
def update(
    posture_id: int,
    updated_posture: PostureClassCreate,
    repo: PostureClassRepository = Depends(get_repo),
):
    posture = repo.get_one(posture_id)

    if not posture:
        raise HTTPException(
            status_code=404,
            detail="Posture class not found",
        )

    posture.posture = updated_posture.posture

    return repo.update(posture)


@router.delete("/{posture_id}")
def delete(
    posture_id: int,
    repo: PostureClassRepository = Depends(get_repo),
):
    success = repo.delete(posture_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Posture class not found",
        )

    return {
        "detail": "Posture class deleted successfully"
    }