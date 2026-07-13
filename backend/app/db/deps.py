from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide one SQLAlchemy session for the duration of a request."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


DatabaseSession = Annotated[Session, Depends(get_db)]