from sqlmodel import Session, select

from api.models.posture_class import PostureClass


class PostureClassRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        posture_obj: PostureClass,
    ) -> PostureClass:

        self.db.add(posture_obj)
        self.db.commit()
        self.db.refresh(posture_obj)

        return posture_obj

    def get_all(self) -> list[PostureClass]:

        statement = select(PostureClass)

        return self.db.exec(statement).all()

    def get_one(
        self,
        posture_id: int,
    ) -> PostureClass | None:

        return self.db.get(
            PostureClass,
            posture_id,
        )

    def get_by_name(
        self,
        posture: str,
    ) -> PostureClass | None:

        statement = select(PostureClass).where(
            PostureClass.posture == posture
        )

        return self.db.exec(statement).first()

    def update(
        self,
        posture_obj: PostureClass,
    ) -> PostureClass:

        self.db.commit()
        self.db.refresh(posture_obj)

        return posture_obj

    def delete(
        self,
        posture_id: int,
    ) -> bool:

        posture_obj = self.get_one(posture_id)

        if not posture_obj:
            return False

        self.db.delete(posture_obj)
        self.db.commit()

        return True