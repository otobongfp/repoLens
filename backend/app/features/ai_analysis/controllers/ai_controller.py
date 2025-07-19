from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.features.ai_analysis.services.ai_analyzer_service import AIAnalyzerService
from app.features.ai_analysis.models.ai_models import (
    AIAnalysisRequest, 
    FunctionAnalysisRequest, 
    AIAnalysisResponse, 
    AIStatusResponse,
    AskRequest,
    AskResponse
)
from app.core.config import config
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Analysis"])

# Create service instance
ai_analyzer = AIAnalyzerService()

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_codebase(request: AIAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze the entire codebase using AI.
    
    Args:
        request: AI analysis request containing graph data
        
    Returns:
        AI analysis results with scores and insights
    """
    try:
        if not config.OPENAI_API_KEY:
            raise HTTPException(
                status_code=400, 
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        logger.info("Starting AI codebase analysis")
        result = ai_analyzer.analyze_codebase(request.graph_data)
        logger.info("AI codebase analysis completed")
        return result
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.post("/analyze-function", response_model=AIAnalysisResponse)
async def analyze_function(request: FunctionAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze a specific function using AI.
    
    Args:
        request: Function analysis request containing function node and graph data
        
    Returns:
        Function-specific AI analysis results
    """
    try:
        if not config.OPENAI_API_KEY:
            raise HTTPException(
                status_code=400, 
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        logger.info(f"Starting AI function analysis for: {request.function_node.get('label', 'Unknown')}")
        result = ai_analyzer.analyze_function(request.function_node, request.graph_data)
        logger.info("AI function analysis completed")
        return result
    except Exception as e:
        logger.error(f"Function analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Function analysis failed: {str(e)}")

@router.post("/ask", response_model=AskResponse)
async def ask_codebase_question(request: AskRequest) -> AskResponse:
    result = ai_analyzer.answer_question(request.graph_data, request.question)
    return AskResponse(**result)

@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status() -> Dict[str, Any]:
    """
    Get AI analysis service status.
    
    Returns:
        AI service status information
    """
    return {
        "enabled": ai_analyzer.enabled,
        "openai_configured": bool(config.OPENAI_API_KEY),
        "model": config.OPENAI_MODEL,
        "max_tokens": config.AI_MAX_TOKENS,
        "temperature": config.AI_TEMPERATURE
    }

@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get AI analysis cache statistics.
    
    Returns:
        Cache statistics
    """
    return ai_analyzer.get_cache_stats()

@router.post("/cache/clear")
async def clear_cache() -> Dict[str, str]:
    """
    Clear AI analysis cache.
    
    Returns:
        Success message
    """
    ai_analyzer.clear_cache()
    return {"message": "Cache cleared successfully"} 