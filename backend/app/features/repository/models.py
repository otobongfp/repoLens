# Repository analysis models
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum


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
    meta: Optional[Dict[str, Any]] = None


class Edge(BaseModel):
    from_node: str
    to_node: str
    type: EdgeType
    meta: Optional[Dict[str, Any]] = None


class FileInfo(BaseModel):
    path: str
    size: int
    language: Optional[str] = None
    functions: List[str] = []
    classes: List[str] = []


class FileContent(BaseModel):
    path: str
    content: str
    language: Optional[str] = None
    functions: List[Dict[str, Any]] = []


class FunctionSummary(BaseModel):
    name: str
    start_line: int
    end_line: int
    parameters: List[str] = []
    return_type: Optional[str] = None
    docstring: Optional[str] = None


class RepositorySummary(BaseModel):
    total_files: int
    total_functions: int
    total_classes: int
    languages: List[str] = []
    main_technologies: List[str] = []


class RepoGraphResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    summary: Optional[RepositorySummary] = None


class EnhancedRepoGraphResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    summary: Optional[RepositorySummary] = None
    technology_stack: Optional[List[str]] = None
    documentation: List[str] = []
    configurations: List[str] = []
    technologies: List[str] = []


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
    functions: List[FunctionSummary]
    error: Optional[str] = None


class FileQuery(BaseModel):
    path: Optional[str] = None


class SearchQuery(BaseModel):
    q: str
