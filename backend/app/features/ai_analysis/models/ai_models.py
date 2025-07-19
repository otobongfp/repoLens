from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class AIAnalysisRequest(BaseModel):
    """Request model for AI analysis."""
    graph_data: Dict[str, Any]

class FunctionAnalysisRequest(BaseModel):
    """Request model for function-specific AI analysis."""
    function_node: Dict[str, Any]
    graph_data: Dict[str, Any]

class AskRequest(BaseModel):
    graph_data: Dict[str, Any]
    question: str

class AIAnalysisResponse(BaseModel):
    """Response model for AI analysis."""
    enabled: bool
    scores: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    error: Optional[str] = None

class AskResponse(BaseModel):
    answer: str
    error: Optional[str] = None

class AIStatusResponse(BaseModel):
    """Response model for AI service status."""
    enabled: bool
    openai_configured: bool
    model: str
    max_tokens: int
    temperature: float 