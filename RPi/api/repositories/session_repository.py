from sqlmodel import Session, select

from api.models.session import Session as SessionModel


class SessionRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        session_obj: SessionModel,
    ) -> SessionModel:
        self.db.add(session_obj)
        self.db.commit()
        self.db.refresh(session_obj)
        return session_obj

    def get_all(self) -> list[SessionModel]:
        return self.db.exec(
            select(SessionModel)
        ).all()

    def get_one(
        self,
        session_id: int,
    ) -> SessionModel | None:
        return self.db.get(
            SessionModel,
            session_id,
        )

    def update(
        self,
        session_id: int,
        updated_session: SessionModel,
    ) -> SessionModel | None:

        session_obj = self.get_one(session_id)

        if not session_obj:
            return None

        for key, value in updated_session.model_dump().items():
            setattr(session_obj, key, value)

        self.db.commit()
        self.db.refresh(session_obj)

        return session_obj

    def delete(
        self,
        session_id: int,
    ) -> bool:

        session_obj = self.get_one(session_id)

        if not session_obj:
            return False

        self.db.delete(session_obj)
        self.db.commit()

        return True