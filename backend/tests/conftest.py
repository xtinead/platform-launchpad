import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401
from app.core.config import settings
from app.db.base import Base
from app.db.deps import get_db
from app.main import app
from app.models.user import User


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    """Create the test database engine and application schema."""

    if settings.test_database_url is None:
        pytest.fail(
            "TEST_DATABASE_URL must be configured before running tests."
        )

    if "platform_launchpad_test" not in settings.test_database_url:
        pytest.fail(
            "Refusing to run tests against a non-test database."
        )

    engine = create_engine(
        settings.test_database_url,
        pool_pre_ping=True,
    )

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(
    test_engine: Engine,
) -> Generator[Session, None, None]:
    """Provide a transaction-isolated database session."""

    connection: Connection = test_engine.connect()
    transaction = connection.begin()

    testing_session_factory = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    session = testing_session_factory()

    try:
        yield session
    finally:
        session.close()

        if transaction.is_active:
            transaction.rollback()

        connection.close()


@pytest.fixture
def client(
    db_session: Session,
) -> Generator[TestClient, None, None]:
    """Provide a FastAPI client using the isolated test session."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def registered_user_payload() -> dict[str, str]:
    """Return a valid user registration request body."""

    return {
        "email": "developer@example.com",
        "password": "ExamplePassword123!",
        "full_name": "Example Developer",
    }


@pytest.fixture
def registered_user(
    client: TestClient,
    registered_user_payload: dict[str, str],
) -> dict[str, object]:
    """Register and return a test user."""

    response = client.post(
        "/api/v1/auth/register",
        json=registered_user_payload,
    )

    assert response.status_code == 201

    return response.json()

@pytest.fixture
def test_user(
    db_session: Session,
    registered_user: dict[str, object],
) -> User:
    """Return the registered user as a SQLAlchemy model instance."""

    user = db_session.get(
        User,
        uuid.UUID(str(registered_user["id"])),
    )

    assert user is not None

    return user

@pytest.fixture
def access_token(
    client: TestClient,
    registered_user: dict[str, object],
    registered_user_payload: dict[str, str],
) -> str:
    """Authenticate the test user and return an access token."""

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user_payload["email"],
            "password": registered_user_payload["password"],
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]
    assert isinstance(token, str)

    return token