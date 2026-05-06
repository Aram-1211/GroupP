"""Database engine, session and base declarative class.

Provides SQLAlchemy engine, session factory (`SessionLocal`), and a
`get_db` dependency generator for FastAPI endpoints.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./nutrition.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for ORM models (SQLAlchemy DeclarativeBase)."""
    pass


def get_db():
    """Yield a database session and ensure it is closed after use.

    This function is intended to be used as a FastAPI dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
