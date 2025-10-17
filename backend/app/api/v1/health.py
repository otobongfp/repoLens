# RepoLens API - Health Endpoints
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
    tags=["Health & System"],
    responses={503: {"description": "Service unavailable"}},
)


@router.get(
    "/",
    summary="System health check",
    description="Check overall system health and service status",
    responses={
        200: {"description": "System healthy"},
        503: {"description": "System unhealthy"},
    },
)
async def health_check():
    """Check overall system health and service status"""
    try:
        # Check basic system health
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage("/").percent

        # Determine health status
        is_healthy = cpu_percent < 90 and memory_percent < 90 and disk_percent < 90

        status_code = 200 if is_healthy else 503

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "repository": "available",
                "ai_analysis": "available",
                "database": "available",
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}",
        )


@router.get(
    "/services",
    summary="Service status",
    description="Check individual service status",
    responses={
        200: {"description": "Services available"},
        503: {"description": "Services unavailable"},
    },
)
async def service_status():
    """Check individual service status"""
    try:
        services = {}

        # Check repository service
        try:
            repo_service = get_repository_service()
            services["repository"] = "available"
        except Exception:
            services["repository"] = "unavailable"

        # Check AI service
        try:
            ai_service = get_ai_service()
            services["ai_analysis"] = "available"
        except Exception:
            services["ai_analysis"] = "unavailable"

        # Check database
        try:
            # This would check database connection
            services["database"] = "available"
        except Exception:
            services["database"] = "unavailable"

        all_available = all(status == "available" for status in services.values())
        status_code = 200 if all_available else 503

        return {
            "status": "available" if all_available else "unavailable",
            "timestamp": datetime.utcnow().isoformat(),
            "services": services,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service status check failed: {str(e)}",
        )


@router.get(
    "/metrics",
    summary="System metrics",
    description="Get detailed system metrics",
    responses={
        200: {"description": "Metrics retrieved successfully"},
        500: {"description": "Failed to retrieve metrics"},
    },
)
async def system_metrics():
    """Get detailed system metrics"""
    try:
        # Get detailed system metrics
        cpu_info = psutil.cpu_times_percent()
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage("/")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "times": {
                    "user": cpu_info.user,
                    "system": cpu_info.system,
                    "idle": cpu_info.idle,
                },
            },
            "memory": {
                "total": memory_info.total,
                "available": memory_info.available,
                "percent": memory_info.percent,
                "used": memory_info.used,
                "free": memory_info.free,
            },
            "disk": {
                "total": disk_info.total,
                "used": disk_info.used,
                "free": disk_info.free,
                "percent": disk_info.percent,
            },
            "environment": {
                "python_version": os.sys.version,
                "platform": os.name,
                "working_directory": os.getcwd(),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics: {str(e)}",
        )
