from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator


def _make_engine():
    from app.config import settings
    return create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    )


class _LazyEngine:
    _engine = None

    def __call__(self):
        if self._engine is None:
            self._engine = _make_engine()
        return self._engine

    def reset(self, url: str | None = None):
        from sqlalchemy import create_engine as _ce
        if url:
            self._engine = _ce(
                url,
                connect_args={"check_same_thread": False} if "sqlite" in url else {},
            )
        else:
            self._engine = None


_lazy = _LazyEngine()


def get_engine():
    return _lazy()


def get_session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from app.models.graph import Base
    Base.metadata.create_all(bind=get_engine())
