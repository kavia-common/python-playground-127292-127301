from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.database import get_db
from src.core.exec_runner import run_code
from src.core.models import Execution, Snippet, User
from src.core.schemas import RunRequest, RunResult
from src.core.security import get_current_user

router = APIRouter()
settings = get_settings()


@router.post(
    "",
    response_model=RunResult,
    status_code=status.HTTP_200_OK,
    summary="Run Python code",
    description="Execute Python code securely in a resource-limited subprocess. Returns stdout/stderr and exit status.",
)
# PUBLIC_INTERFACE
def run(payload: RunRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> RunResult:
    """
    Execute Python code in a sandboxed subprocess.

    Notes:
        - CPU time and memory usage are limited.
        - Networking and subprocess spawning are disabled inside the execution environment.
        - For robust isolation, consider container or VM sandboxes in production.

    Args:
        payload: Contains code and optional snippet_id to associate the run with.
    """
    # Validate snippet ownership if snippet_id is provided
    snippet_id = payload.snippet_id
    if snippet_id is not None:
        snip = db.get(Snippet, snippet_id)
        if not snip or snip.owner_id != current_user.id:
            raise HTTPException(status_code=404, detail="Snippet not found")

    result = run_code(payload.code, timeout_s=settings.EXEC_TIMEOUT_SECONDS, memory_limit_mb=settings.EXEC_MEMORY_MB)

    # Store execution record
    exec_rec = Execution(
        code=payload.code,
        stdout=result["stdout"],
        stderr=result["stderr"],
        exit_code=int(result["exit_code"]),
        duration_ms=int(result["duration_ms"]),
        user_id=current_user.id,
        snippet_id=snippet_id,
    )
    db.add(exec_rec)
    db.commit()
    db.refresh(exec_rec)

    return RunResult(
        stdout=exec_rec.stdout,
        stderr=exec_rec.stderr,
        exit_code=exec_rec.exit_code,
        duration_ms=exec_rec.duration_ms,
        timed_out=bool(result["timed_out"]),
    )
