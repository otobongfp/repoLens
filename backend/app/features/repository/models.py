# Repository analysis models
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class NodeType(str, Enum):
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    IMPORT = "import"
    VARIABLE = "variable"


class EdgeType(str, Enum):
    CALLS = "calls"
    IMPORTS = "imports"
    INHERITS = "inherits"
    USES = "uses"


class Node(BaseModel):
    id: str
    label: str
    type: NodeType
    path: str
    meta: Optional[dict[str, Any]] = None


class Edge(BaseModel):
    from_node: str
    to_node: str
    type: EdgeType
    meta: Optional[dict[str, Any]] = None


class FileInfo(BaseModel):
    path: str
    size: int
    language: Optional[str] = None
    functions: list[str] = []
    classes: list[str] = []


class FileContent(BaseModel):
    path: str
    content: str
    language: Optional[str] = None
    functions: list[dict[str, Any]] = []


class FunctionSummary(BaseModel):
    name: str
    start_line: int
    end_line: int
    parameters: list[str] = []
    return_type: Optional[str] = None
    docstring: Optional[str] = None


class RepositorySummary(BaseModel):
    total_files: int
    total_functions: int
    total_classes: int
    languages: list[str] = []
    main_technologies: list[str] = []


class RepoGraphResponse(BaseModel):
    nodes: list[Node]
    edges: list[Edge]
    summary: Optional[RepositorySummary] = None


class EnhancedRepoGraphResponse(BaseModel):
    nodes: list[Node]
    edges: list[Edge]
    summary: Optional[RepositorySummary] = None
    technology_stack: Optional[list[str]] = None
    documentation: list[str] = []
    configurations: list[str] = []
    technologies: list[str] = []


# Request models
class AnalyzeProjectRequest(BaseModel):
    url: Optional[str] = None
    folder_path: Optional[str] = None


class EnhancedAnalyzeRequest(BaseModel):
    folder_path: Optional[str] = None


class AnalyzeRequest(BaseModel):
    file: str


class AnalyzeResponse(BaseModel):
    file: str
    functions: list[FunctionSummary]
    error: Optional[str] = None


class FileQuery(BaseModel):
    path: Optional[str] = None


class SearchQuery(BaseModel):
    q: str
