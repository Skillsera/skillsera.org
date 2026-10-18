import os
import pytest

# Point to SQLite before any app modules are imported
TEST_DATABASE_URL = "sqlite:///./test.db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.models.graph import Base
from app.database import get_db, _lazy
from app.main import app

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Wire the lazy engine to our test engine
_lazy.reset(TEST_DATABASE_URL)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def client(setup_test_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seeded_db(db):
    """Seed minimal test data: one user, one question, one answer."""
    from sqlalchemy import text
    from app.models.graph import User, Question, Answer

    # Wipe all data cleanly (order matters for FK constraints)
    db.execute(text("DELETE FROM dependencies"))
    db.execute(text("DELETE FROM masteries"))
    db.execute(text("DELETE FROM views"))
    db.execute(text("DELETE FROM votes"))
    db.execute(text("DELETE FROM question_to_answers"))
    db.execute(text("DELETE FROM question_to_questions"))
    db.execute(text("DELETE FROM question_to_tags"))
    db.execute(text("DELETE FROM user_to_tags"))
    db.execute(text("DELETE FROM answers"))
    db.execute(text("DELETE FROM questions"))
    db.execute(text("DELETE FROM users"))
    db.execute(text("DELETE FROM tags"))
    db.commit()

    user = User(username="testuser", email="test@example.com")
    db.add(user)
    db.flush()

    question = Question(question="What is matter?", user_id=user.id)
    db.add(question)
    db.flush()

    answer = Answer(
        user_id=user.id,
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        start=0,
        stop=60,
    )
    db.add(answer)
    db.flush()
    question.answers.append(answer)
    db.commit()

    return {"user": user, "question": question, "answer": answer}
