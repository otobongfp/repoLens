from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class BaseNode(BaseModel):
    """Base model for graph nodes."""
    id: str
    label: str
    type: str
    path: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class BaseEdge(BaseModel):
    """Base model for graph edges."""
    from_: str = Field(..., alias="from")
    to: str
    type: str
    meta: Optional[Dict[str, Any]] = None

class BaseRequest(BaseModel):
    """Base model for API requests."""
    pass

class BaseResponse(BaseModel):
    """Base model for API responses."""
    pass 