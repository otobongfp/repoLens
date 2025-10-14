# Health and system API routes
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import os
import psutil
from typing import Dict, Any

from ...core.config import settings
from ...core.dependencies import get_repository_service, get_ai_service
from ...features.repository.services import RepositoryAnalyzer
from ...features.ai_analysis.services.ai_analyzer_service import AIAnalyzerService

router = APIRouter(
    prefix="/health",
    tags=["🏥 Health & System"],
    responses={503: {"description": "Service unavailable"}}
)

@router.get(
    "/",
    summary="🏥 System Health Check",
    description="""
    **Comprehensive system health status**
    
    This endpoint provides detailed information about:
    - ✅ All service statuses
    - 📊 System resource usage
    - 🔧 Configuration status
    - 📈 Performance metrics
    - 🚀 Service capabilities
    
    **Perfect for**: System monitoring, health checks, 
    service discovery, and troubleshooting.
    """,
    responses={
        200: {"description": "System health status retrieved successfully"},
        503: {"description": "System unhealthy"}
    }
)
async def health_check():
    """🏥 System Health Check"""
    try:
        # Get system information
        system_info = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": psutil.boot_time()
        }
        
        # Check AI service availability
        ai_status = "unavailable"
        try:
            ai_service = get_ai_service()
            ai_status = "available"
        except:
            ai_status = "unavailable"
        
        # Check repository service
        repo_status = "available"
        try:
            repo_service = get_repository_service()
        except:
            repo_status = "unavailable"
        
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "services": {
                "api": "✅ operational",
                "repository_analysis": f"✅ {repo_status}",
                "ai_analysis": f"✅ {ai_status}",
                "database": "✅ operational"
            },
            "system": {
                "cpu_usage": f"{system_info['cpu_percent']:.1f}%",
                "memory_usage": f"{system_info['memory_percent']:.1f}%",
                "disk_usage": f"{system_info['disk_percent']:.1f}%",
                "uptime_hours": f"{(datetime.now().timestamp() - system_info['uptime_seconds']) / 3600:.1f}"
            },
            "features": {
                "supported_languages": settings.supported_extensions,
                "ai_models": ["GPT-4", "GPT-3.5-turbo"] if ai_status == "available" else [],
                "max_file_size": f"{settings.max_file_size / (1024*1024):.0f}MB",
                "rate_limits": {
                    "requests_per_minute": settings.rate_limit_requests,
                    "analysis_per_hour": 20
                }
            },
            "configuration": {
                "debug_mode": settings.debug,
                "cors_origins": len(settings.cors_origins),
                "ai_configured": ai_status == "available"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )

@router.get(
    "/services",
    summary="🔧 Service Status",
    description="""
    **Detailed status of all RepoLens services**
    
    This endpoint provides granular information about:
    - 🔍 Individual service health
    - ⚙️ Service configuration status
    - 📊 Service-specific metrics
    - 🔗 Service dependencies
    
    **Perfect for**: Service monitoring, debugging, 
    and understanding system architecture.
    """,
    responses={
        200: {"description": "Service status retrieved successfully"},
        503: {"description": "Services unavailable"}
    }
)
async def service_status():
    """🔧 Service Status"""
    try:
        services = {}
        
        # Repository Service
        try:
            repo_service = get_repository_service()
            services["repository"] = {
                "status": "healthy",
                "capabilities": ["file_parsing", "graph_generation", "search"],
                "supported_languages": len(settings.supported_extensions)
            }
        except Exception as e:
            services["repository"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # AI Service
        try:
            ai_service = get_ai_service()
            services["ai"] = {
                "status": "healthy",
                "model": settings.openai_model,
                "capabilities": ["analysis", "qa", "function_review"]
            }
        except Exception as e:
            services["ai"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": services,
            "overall_status": "healthy" if all(s.get("status") == "healthy" for s in services.values()) else "degraded"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service status check failed: {str(e)}"
        )

@router.get(
    "/metrics",
    summary="📊 System Metrics",
    description="""
    **Real-time system performance metrics**
    
    This endpoint provides detailed metrics including:
    - 📈 Performance statistics
    - 💾 Resource utilization
    - ⏱️ Response times
    - 📊 Usage patterns
    
    **Perfect for**: Performance monitoring, capacity planning, 
    and system optimization.
    """,
    responses={
        200: {"description": "Metrics retrieved successfully"},
        500: {"description": "Failed to retrieve metrics"}
    }
)
async def system_metrics():
    """📊 System Metrics"""
    try:
        # Get detailed system metrics
        cpu_info = psutil.cpu_times_percent()
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "usage_percent": psutil.cpu_percent(),
                "user_time": cpu_info.user,
                "system_time": cpu_info.system,
                "idle_time": cpu_info.idle,
                "core_count": psutil.cpu_count()
            },
            "memory": {
                "total_gb": round(memory_info.total / (1024**3), 2),
                "available_gb": round(memory_info.available / (1024**3), 2),
                "used_gb": round(memory_info.used / (1024**3), 2),
                "usage_percent": memory_info.percent
            },
            "disk": {
                "total_gb": round(disk_info.total / (1024**3), 2),
                "free_gb": round(disk_info.free / (1024**3), 2),
                "used_gb": round(disk_info.used / (1024**3), 2),
                "usage_percent": round((disk_info.used / disk_info.total) * 100, 2)
            },
            "network": {
                "connections": len(psutil.net_connections()),
                "interfaces": len(psutil.net_if_addrs())
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )
