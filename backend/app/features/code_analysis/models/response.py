from pydantic import BaseModel, Field
from typing import List, Optional
from app.shared.models.base import BaseNode, BaseEdge

class Node(BaseNode):
    """Node model for code analysis graph."""
    pass

class Edge(BaseEdge):
    """Edge model for code analysis graph."""
    pass

class ImportStat(BaseModel):
    """Import statistics model."""
    import_: str = Field(..., alias="import")
    count: int

class Summary(BaseModel):
    """Summary statistics for code analysis."""
    totalFiles: int
    totalFunctions: int
    totalClasses: int
    topImports: List[ImportStat]

class RepoGraphResponse(BaseModel):
    """Response model for repository graph analysis."""
    nodes: List[Node]
    edges: List[Edge]
    summary: Optional[Summary] = None 