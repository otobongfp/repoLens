from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Node(BaseModel):
    id: str
    label: str
    type: str
    path: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class Edge(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    type: str
    meta: Optional[Dict[str, Any]] = None

class ImportStat(BaseModel):
    import_: str = Field(..., alias="import")
    count: int

class Summary(BaseModel):
    totalFiles: int
    totalFunctions: int
    totalClasses: int
    topImports: List[ImportStat]

class RepoGraphResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    summary: Optional[Summary] = None
