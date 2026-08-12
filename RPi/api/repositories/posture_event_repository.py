from sqlmodel import Session, select

from api.models.posture_event import PostureEvent


class PostureEventRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        event_obj: PostureEvent,
    ) -> PostureEvent:

        self.db.add(event_obj)
        self.db.commit()
        self.db.refresh(event_obj)

        return event_obj

    def get_all(self) -> list[PostureEvent]:

        statement = select(PostureEvent)

        return self.db.exec(statement).all()

    def get_one(
        self,
        event_id: int,
    ) -> PostureEvent | None:

        return self.db.get(
            PostureEvent,
            event_id,
        )

    def update(
        self,
        event_obj: PostureEvent,
    ) -> PostureEvent:

        self.db.commit()
        self.db.refresh(event_obj)

        return event_obj

    def delete(
        self,
        event_id: int,
    ) -> bool:

        event_obj = self.get_one(event_id)

        if not event_obj:
            return False

        self.db.delete(event_obj)
        self.db.commit()

        return True

    def get_by_session(
        self,
        session_id: int,
    ) -> list[PostureEvent]:

        statement = select(PostureEvent).where(
            PostureEvent.session_id == session_id
        )

        return self.db.exec(statement).all()

    def get_by_posture(
        self,
        posture_id: int,
    ) -> list[PostureEvent]:

        statement = select(PostureEvent).where(
            PostureEvent.posture_id == posture_id
        )

        return self.db.exec(statement).all()