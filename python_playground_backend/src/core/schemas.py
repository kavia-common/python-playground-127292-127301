from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Auth schemas
class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (e.g., 'bearer')")


class TokenPayload(BaseModel):
    sub: str | None = Field(None, description="Subject (user ID)")
    exp: int | None = Field(None, description="Expiry timestamp")


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="Password for the new account")


class UserOut(UserBase):
    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


# Snippets
class SnippetBase(BaseModel):
    title: str = Field(..., description="Snippet title", min_length=1, max_length=255)
    code: str = Field(..., description="Python code content")


class SnippetCreate(SnippetBase):
    pass


class SnippetUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Snippet title", min_length=1, max_length=255)
    code: Optional[str] = Field(None, description="Python code content")


class SnippetOut(SnippetBase):
    id: int = Field(..., description="Snippet ID")
    owner_id: int = Field(..., description="Owner user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# Execution
class RunRequest(BaseModel):
    code: str = Field(..., description="Python code to execute")
    snippet_id: Optional[int] = Field(None, description="Optional snippet ID to associate with the run")


class RunResult(BaseModel):
    stdout: str = Field(..., description="Captured standard output")
    stderr: str = Field(..., description="Captured standard error")
    exit_code: int = Field(..., description="Process exit code")
    duration_ms: int = Field(..., description="Execution duration in milliseconds")
    timed_out: bool = Field(..., description="Whether the execution timed out")


class ExecutionOut(RunResult):
    id: int = Field(..., description="Execution ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    user_id: int = Field(..., description="User ID")
    snippet_id: Optional[int] = Field(None, description="Associated snippet ID (if any)")

    class Config:
        from_attributes = True
