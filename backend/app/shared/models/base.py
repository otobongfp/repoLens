# RepoLens Backend - Base
from typing import Any, Optional

from pydantic import BaseModel, Field


class BaseNode(BaseModel):
    """Base model for graph nodes."""

    id: str
    label: str
    type: str
    path: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class BaseEdge(BaseModel):
    """Base model for graph edges."""

    from_: str = Field(..., alias="from")
    to: str
    type: str
    meta: Optional[dict[str, Any]] = None


class BaseRequest(BaseModel):
    """Base model for API requests."""

    pass


class BaseResponse(BaseModel):
    """Base model for API responses."""

    pass
