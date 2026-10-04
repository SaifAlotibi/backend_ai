import pytest

from sqlmodel import Session, create_engine, SQLModel
from fastapi.testclient import TestClient

from database import get_session
from main import app


import os

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://ai_user:ai_password@postgres:5432/test_database"
)

test_engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture
def client():

    SQLModel.metadata.create_all(test_engine)

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    yield TestClient(app)

    app.dependency_overrides.clear()

    SQLModel.metadata.drop_all(test_engine)