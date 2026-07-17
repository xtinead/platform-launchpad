import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Data-access operations for application users."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        statement = select(User).where(User.id == user_id)

        return self.session.scalar(statement)

    def get_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()

        statement = select(User).where(
            User.email == normalized_email,
        )

        return self.session.scalar(statement)

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)

        return user