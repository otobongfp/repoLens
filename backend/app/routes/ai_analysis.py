from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.ai_analyzer import AIAnalyzer
from app.core.config import config

router = APIRouter(prefix="/ai", tags=["AI Analysis"])


ai_analyzer = AIAnalyzer()

@router.post("/analyze")
async def analyze_codebase(graph_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the entire codebase using AI."""
    try:
        if not config.OPENAI_API_KEY:
            raise HTTPException(
                status_code=400, 
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        result = ai_analyzer.analyze_codebase(graph_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.post("/analyze-function")
async def analyze_function(function_node: Dict[str, Any], graph_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a specific function using AI."""
    try:
        if not config.OPENAI_API_KEY:
            raise HTTPException(
                status_code=400, 
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        result = ai_analyzer.analyze_function(function_node, graph_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Function analysis failed: {str(e)}")

@router.get("/status")
async def get_ai_status() -> Dict[str, Any]:
    """Get AI analysis service status."""
    return {
        "enabled": ai_analyzer.enabled,
        "openai_configured": bool(config.OPENAI_API_KEY),
        "model": config.OPENAI_MODEL,
        "max_tokens": config.AI_MAX_TOKENS,
        "temperature": config.AI_TEMPERATURE
    } 