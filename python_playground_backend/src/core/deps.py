from __future__ import annotations

from sqlalchemy.orm import Session

from src.core.database import get_db

# PUBLIC_INTERFACE
def db_session() -> Session:
    """Alias dependency for obtaining a database session."""
    yield from get_db()
