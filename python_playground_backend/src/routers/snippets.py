from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.models import Snippet, User
from src.core.schemas import SnippetCreate, SnippetOut, SnippetUpdate
from src.core.security import get_current_user

router = APIRouter()


@router.get(
    "",
    response_model=List[SnippetOut],
    summary="List snippets",
    description="List all snippets owned by the current user.",
)
# PUBLIC_INTERFACE
def list_snippets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[SnippetOut]:
    """Return all snippets for the authenticated user."""
    return db.query(Snippet).filter(Snippet.owner_id == current_user.id).order_by(Snippet.updated_at.desc()).all()


@router.post(
    "",
    response_model=SnippetOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create snippet",
    description="Create a new code snippet for the current user.",
)
# PUBLIC_INTERFACE
def create_snippet(payload: SnippetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> SnippetOut:
    """Create a snippet owned by the current user."""
    snip = Snippet(title=payload.title, code=payload.code, owner_id=current_user.id)
    db.add(snip)
    db.commit()
    db.refresh(snip)
    return snip


@router.get(
    "/{snippet_id}",
    response_model=SnippetOut,
    summary="Get snippet",
    description="Retrieve a specific snippet owned by the current user.",
)
# PUBLIC_INTERFACE
def get_snippet(
    snippet_id: int = Path(..., description="Snippet ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SnippetOut:
    """Get a single snippet by ID for the authenticated user."""
    snip = db.get(Snippet, snippet_id)
    if not snip or snip.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return snip


@router.put(
    "/{snippet_id}",
    response_model=SnippetOut,
    summary="Update snippet",
    description="Update title and/or code for an owned snippet.",
)
# PUBLIC_INTERFACE
def update_snippet(
    payload: SnippetUpdate,
    snippet_id: int = Path(..., description="Snippet ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SnippetOut:
    """Update an existing snippet. Only the owner may update."""
    snip = db.get(Snippet, snippet_id)
    if not snip or snip.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Snippet not found")
    if payload.title is not None:
        snip.title = payload.title
    if payload.code is not None:
        snip.code = payload.code
    db.add(snip)
    db.commit()
    db.refresh(snip)
    return snip


@router.delete(
    "/{snippet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete snippet",
    description="Delete a snippet owned by the current user.",
)
# PUBLIC_INTERFACE
def delete_snippet(
    snippet_id: int = Path(..., description="Snippet ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete an existing snippet. Only the owner may delete."""
    snip = db.get(Snippet, snippet_id)
    if not snip or snip.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Snippet not found")
    db.delete(snip)
    db.commit()
    return None
