from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class AIAnalysisRequest(BaseModel):
    repository_url: str
    analysis_type: str = "comprehensive"
    include_tests: bool = True
    include_docs: bool = True


class FunctionAnalysisRequest(BaseModel):
    function_code: str
    language: str
    context: Optional[str] = None


class AskRequest(BaseModel):
    question: str
    context: Optional[str] = None


class AIAnalysisResponse(BaseModel):
    enabled: bool
    scores: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    error: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    error: Optional[str] = None


class AIStatusResponse(BaseModel):
    enabled: bool
    openai_configured: bool
    model: str
    max_tokens: int
    temperature: float
