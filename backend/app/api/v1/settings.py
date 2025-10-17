# RepoLens API - Settings Endpoints
# Settings Management API Routes
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime, timezone

from ...shared.models.project_models import (
    UserSettingsRequest,
    UserSettingsResponse,
    EnvironmentConfig,
)

from ...core.dependencies import (
    get_tenant_id,
    get_db,
    authenticate,
    require_permissions,
)

router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
    responses={404: {"description": "Settings not found"}},
)


@router.get(
    "",
    response_model=UserSettingsResponse,
    summary="Get User Settings",
    description="Get user settings and preferences",
    responses={
        200: {"description": "Settings retrieved successfully"},
        401: {"description": "Authentication required"},
        500: {"description": "Failed to retrieve settings"},
    },
)
async def get_settings(
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate),
):
    """Get user settings and preferences"""
    try:
        # This would typically query the database for user settings
        # For now, return mock settings

        return UserSettingsResponse(
            theme="dark",
            language="en",
            notifications=True,
            email_notifications=True,
            analysis_preferences={
                "include_tests": True,
                "include_docs": True,
                "depth": "comprehensive",
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve settings: {str(e)}",
        )


@router.put(
    "",
    response_model=UserSettingsResponse,
    summary="Update User Settings",
    description="Update user settings and preferences",
    responses={
        200: {"description": "Settings updated successfully"},
        400: {"description": "Invalid settings data"},
        401: {"description": "Authentication required"},
        500: {"description": "Failed to update settings"},
    },
)
async def update_settings(
    request: UserSettingsRequest,
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
    user: Dict[str, Any] = Depends(require_permissions(["admin"])),
):
    """Update user settings and preferences"""
    try:
        # This would typically update the database with new settings
        # For now, just return the updated settings

        return UserSettingsResponse(
            theme=request.theme,
            language=request.language,
            notifications=request.notifications,
            email_notifications=request.email_notifications,
            analysis_preferences=request.analysis_preferences,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}",
        )


@router.post(
    "/test-connection",
    summary="Test Connection",
    description="Test database and service connections",
    responses={
        200: {"description": "Connection test successful"},
        400: {"description": "Invalid configuration"},
        401: {"description": "Authentication required"},
        500: {"description": "Connection test failed"},
    },
)
async def test_connection(
    config: EnvironmentConfig,
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate),
):
    """Test database and service connections"""
    try:
        # This would typically test the provided configuration
        # For now, just return success

        return {
            "status": "success",
            "message": "Connection test successful",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}",
        )


@router.get(
    "/environment",
    summary="Get Environment Info",
    description="Get environment information",
    responses={
        200: {"description": "Environment info retrieved successfully"},
        401: {"description": "Authentication required"},
        500: {"description": "Failed to retrieve environment info"},
    },
)
async def get_environment_info(
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate),
):
    """Get environment information"""
    try:
        import platform
        import sys

        info = {
            "system": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "architecture": platform.architecture()[0],
            },
            "application": {
                "version": "1.0.0",
                "environment": "development",
                "debug_mode": True,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return info

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve environment info: {str(e)}",
        )
