"""Engine and session factory. One place that knows how to reach Postgres."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from propai_core.config import get_settings


def build_engine(echo: bool = False):
    settings = get_settings()
    return create_engine(
        str(settings.database_url),
        echo=echo,
        pool_pre_ping=True,  # containers restart; stale pooled sockets are normal
        future=True,
    )


_engine = None
_SessionLocal: sessionmaker[Session] | None = None


def session_factory() -> sessionmaker[Session]:
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = build_engine()
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
    return _SessionLocal


@contextmanager
def session_scope() -> Iterator[Session]:
    """Transactional scope. Commits on success, rolls back on any exception."""
    session = session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Iterator[Session]:
    """FastAPI dependency."""
    with session_scope() as session:
        yield session
