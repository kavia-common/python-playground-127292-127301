from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.models import Execution, User
from src.core.schemas import ExecutionOut
from src.core.security import get_current_user

router = APIRouter()


@router.get(
    "",
    response_model=List[ExecutionOut],
    summary="List execution history",
    description="List recent execution results for the current user.",
)
# PUBLIC_INTERFACE
def list_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ExecutionOut]:
    """Return a paginated list of executions for the authenticated user."""
    return (
        db.query(Execution)
        .filter(Execution.user_id == current_user.id)
        .order_by(Execution.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get(
    "/{execution_id}",
    response_model=ExecutionOut,
    summary="Get a specific execution",
    description="Retrieve a specific execution record owned by the current user.",
)
# PUBLIC_INTERFACE
def get_execution(
    execution_id: int = Path(..., description="Execution ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExecutionOut:
    """Return a single execution record by ID if it belongs to the user."""
    rec = db.get(Execution, execution_id)
    if not rec or rec.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Execution not found")
    return rec
