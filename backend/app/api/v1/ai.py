from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from ...core.dependencies import get_ai_service
from ...features.ai_analysis.models.ai_models import (
    AIAnalysisRequest,
    AIAnalysisResponse,
    AIStatusResponse,
    AskRequest,
    AskResponse,
    FunctionAnalysisRequest,
)
from ...features.ai_analysis.services.ai_analyzer_service import AIAnalyzerService


router = APIRouter(prefix="/ai", tags=["AI Analysis"])


@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_codebase(
    request: AIAnalysisRequest, ai_service: AIAnalyzerService = Depends(get_ai_service)
):
    try:
        result = await ai_service.analyze_codebase(request.graph_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}",
        )


@router.post("/analyze/function", response_model=dict[str, Any])
async def analyze_function(
    request: FunctionAnalysisRequest,
    ai_service: AIAnalyzerService = Depends(get_ai_service),
):
    try:
        result = await ai_service.analyze_function(
            request.function_node, request.graph_data
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function analysis failed: {str(e)}",
        )


@router.post("/ask", response_model=AskResponse)
async def ask_codebase_question(
    request: AskRequest, ai_service: AIAnalyzerService = Depends(get_ai_service)
):
    try:
        result = await ai_service.answer_question(request.graph_data, request.question)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question processing failed: {str(e)}",
        )


@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status(ai_service: AIAnalyzerService = Depends(get_ai_service)):
    try:
        status_info = await ai_service.get_status()
        return status_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI status: {str(e)}",
        )


@router.get("/cache/stats")
async def get_cache_stats(ai_service: AIAnalyzerService = Depends(get_ai_service)):
    try:
        stats = await ai_service.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache statistics: {str(e)}",
        )


@router.post("/cache/clear")
async def clear_cache(ai_service: AIAnalyzerService = Depends(get_ai_service)):
    try:
        await ai_service.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}",
        )
