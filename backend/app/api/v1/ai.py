# AI analysis API routes
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from ...features.ai_analysis.models.ai_models import (
    AIAnalysisRequest, FunctionAnalysisRequest, AskRequest,
    AIAnalysisResponse, AskResponse, AIStatusResponse
)
from ...features.ai_analysis.services.ai_analyzer_service import AIAnalyzerService
from ...core.dependencies import get_ai_service

router = APIRouter(
    prefix="/ai",
    tags=["🤖 AI Analysis"],
    responses={404: {"description": "AI service not found"}}
)

@router.post(
    "/analyze",
    response_model=AIAnalysisResponse,
    summary="🤖 AI Codebase Analysis",
    description="""
    **Get comprehensive AI-powered analysis of your codebase**
    
    This endpoint provides intelligent analysis including:
    - 🧠 Complexity analysis and recommendations
    - 🔒 Security vulnerability detection
    - 🏗️ Architecture pattern recognition
    - 📊 Code quality metrics and scoring
    - 💡 Improvement suggestions and best practices
    
    **Perfect for**: Code reviews, quality assurance, 
    technical debt analysis, and development guidance.
    """,
    responses={
        200: {"description": "AI analysis completed successfully"},
        400: {"description": "Invalid request data"},
        503: {"description": "AI service unavailable"},
        500: {"description": "AI analysis failed"}
    }
)
async def analyze_codebase(
    request: AIAnalysisRequest,
    ai_service: AIAnalyzerService = Depends(get_ai_service)
):
    """🤖 AI Codebase Analysis"""
    try:
        result = await ai_service.analyze_codebase(request.graph_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )

@router.post(
    "/analyze/function",
    response_model=Dict[str, Any],
    summary="🔧 AI Function Analysis",
    description="""
    **Get detailed AI analysis of a specific function**
    
    This endpoint provides deep function analysis including:
    - 🔍 Function complexity and readability
    - 🐛 Potential bugs and edge cases
    - ⚡ Performance optimization suggestions
    - 📝 Documentation recommendations
    - 🧪 Test case suggestions
    
    **Perfect for**: Function-level code review, 
    debugging assistance, and optimization guidance.
    """,
    responses={
        200: {"description": "Function analysis completed successfully"},
        400: {"description": "Invalid function data"},
        503: {"description": "AI service unavailable"},
        500: {"description": "Function analysis failed"}
    }
)
async def analyze_function(
    request: FunctionAnalysisRequest,
    ai_service: AIAnalyzerService = Depends(get_ai_service)
):
    """🔧 AI Function Analysis"""
    try:
        result = await ai_service.analyze_function(request.function_node, request.graph_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function analysis failed: {str(e)}"
        )

@router.post(
    "/ask",
    response_model=AskResponse,
    summary="💬 Ask AI About Codebase",
    description="""
    **Ask questions about your codebase and get intelligent answers**
    
    This conversational endpoint allows you to:
    - ❓ Ask specific questions about code functionality
    - 🔍 Get explanations of complex algorithms
    - 📚 Request documentation and examples
    - 🛠️ Get help with debugging and troubleshooting
    - 💡 Receive suggestions for improvements
    
    **Perfect for**: Learning codebases, debugging assistance, 
    documentation generation, and development support.
    """,
    responses={
        200: {"description": "Question answered successfully"},
        400: {"description": "Invalid question or data"},
        503: {"description": "AI service unavailable"},
        500: {"description": "Question processing failed"}
    }
)
async def ask_codebase_question(
    request: AskRequest,
    ai_service: AIAnalyzerService = Depends(get_ai_service)
):
    """💬 Ask AI About Codebase"""
    try:
        result = await ai_service.answer_question(request.graph_data, request.question)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question processing failed: {str(e)}"
        )

@router.get(
    "/status",
    response_model=AIStatusResponse,
    summary="🏥 AI Service Status",
    description="""
    **Check AI service status and configuration**
    
    This endpoint provides information about:
    - ✅ AI service availability
    - 🔧 Current model configuration
    - 📊 Usage statistics and limits
    - 🚀 Service performance metrics
    
    **Perfect for**: Service monitoring, configuration verification, 
    and troubleshooting AI-related issues.
    """,
    responses={
        200: {"description": "AI service status retrieved successfully"},
        503: {"description": "AI service unavailable"}
    }
)
async def get_ai_status(
    ai_service: AIAnalyzerService = Depends(get_ai_service)
):
    """🏥 AI Service Status"""
    try:
        status_info = await ai_service.get_status()
        return status_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI status: {str(e)}"
        )

@router.get(
    "/cache/stats",
    summary="📊 AI Cache Statistics",
    description="""
    **Get AI analysis cache statistics**
    
    This endpoint provides information about:
    - 📈 Cache hit/miss ratios
    - 💾 Cache size and usage
    - ⏰ Cache expiration times
    - 🧹 Cache cleanup statistics
    
    **Perfect for**: Performance monitoring, cache optimization, 
    and understanding AI service efficiency.
    """,
    responses={
        200: {"description": "Cache statistics retrieved successfully"},
        500: {"description": "Failed to get cache statistics"}
    }
)
async def get_cache_stats(
    ai_service: AIAnalyzerService = Depends(get_ai_service)
):
    """📊 AI Cache Statistics"""
    try:
        stats = await ai_service.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache statistics: {str(e)}"
        )

@router.post(
    "/cache/clear",
    summary="🧹 Clear AI Cache",
    description="""
    **Clear all cached AI analysis results**
    
    This endpoint allows you to:
    - 🗑️ Clear all cached analysis results
    - 🔄 Force fresh analysis on next request
    - 💾 Free up memory and storage
    - 🚀 Reset cache performance metrics
    
    **Perfect for**: Cache management, memory optimization, 
    and ensuring fresh analysis results.
    """,
    responses={
        200: {"description": "Cache cleared successfully"},
        500: {"description": "Failed to clear cache"}
    }
)
async def clear_cache(
    ai_service: AIAnalyzerService = Depends(get_ai_service)
):
    """🧹 Clear AI Cache"""
    try:
        await ai_service.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )
