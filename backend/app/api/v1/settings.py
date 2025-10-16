# RepoLens API - Settings Endpoints
#
# Copyright (C) 2024 RepoLens Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Settings Management API Routes
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime, timezone

from ...shared.models.project_models import (
    UserSettingsRequest, UserSettingsResponse, EnvironmentConfig
)

from ...core.dependencies import get_tenant_id, get_db, authenticate, require_permissions

router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
    responses={404: {"description": "Settings not found"}}
)

@router.get(
    "",
    response_model=UserSettingsResponse,
    summary="Get User Settings",
    description="""
    **Get user environment and configuration settings**
    
    This endpoint returns:
    - **API Keys**: OpenAI, AWS, Neo4j credentials
    - **Storage Config**: S3 bucket, region settings
    - **Backend Config**: Local vs cloud backend settings
    - **Security**: Encrypted credential storage
    
    **Perfect for**: Settings management, configuration display,
    and environment setup.
    """,
    responses={
        200: {"description": "Settings retrieved successfully"},
        401: {"description": "Authentication required"},
        500: {"description": "Failed to retrieve settings"}
    }
)
async def get_settings(
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Get user settings"""
    
    # Get settings from database
    settings = db.settings.get(tenant_id, {})
    
    # Default environment config
    default_config = EnvironmentConfig(
        use_local_backend=True,
        backend_url="http://localhost:8000"
    )
    
    # Merge with stored settings
    env_config = EnvironmentConfig(**settings.get("environment_config", default_config.dict()))
    
    return UserSettingsResponse(
        environment_config=env_config,
        tenant_id=tenant_id,
        updated_at=settings.get("updated_at", datetime.now(timezone.utc))
    )

@router.put(
    "",
    response_model=UserSettingsResponse,
    summary="Update User Settings",
    description="""
    **Update user environment and configuration settings**
    
    This endpoint allows updating:
    - **API Keys**: OpenAI, AWS, Neo4j credentials
    - **Storage Settings**: S3 bucket, region
    - **Backend Settings**: Local vs cloud configuration
    - **Security**: Encrypted credential storage
    
    **Perfect for**: Configuration management, environment setup,
    and credential updates.
    """,
    responses={
        200: {"description": "Settings updated successfully"},
        400: {"description": "Invalid settings data"},
        401: {"description": "Authentication required"},
        500: {"description": "Failed to update settings"}
    }
)
async def update_settings(
    request: UserSettingsRequest,
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(require_permissions(["admin"]))
):
    """Update user settings"""
    
    if request.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant mismatch"
        )
    
    # Validate environment config
    try:
        env_config = EnvironmentConfig(**request.environment_config.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid environment config: {str(e)}"
        )
    
    # Store settings
    settings_data = {
        "environment_config": env_config.dict(),
        "updated_at": datetime.now(timezone.utc)
    }
    
    db.settings[tenant_id] = settings_data
    
    await db.log_audit(
        actor_id=user["user_id"],
        action="update_settings",
        target_ids=[tenant_id],
        details={"updated_fields": list(request.environment_config.dict(exclude_unset=True).keys())}
    )
    
    return UserSettingsResponse(
        environment_config=env_config,
        tenant_id=tenant_id,
        updated_at=settings_data["updated_at"]
    )

@router.post(
    "/test-connection",
    summary="Test Connection",
    description="""
    **Test connection to configured services**
    
    This endpoint tests:
    - **OpenAI API**: Verify API key and connectivity
    - **AWS S3**: Test S3 bucket access
    - **Neo4j**: Test database connection
    - **Backend**: Test local/cloud backend connectivity
    
    **Perfect for**: Configuration validation, troubleshooting,
    and connection testing.
    """,
    responses={
        200: {"description": "Connection test completed"},
        400: {"description": "Invalid configuration"},
        401: {"description": "Authentication required"},
        500: {"description": "Connection test failed"}
    }
)
async def test_connection(
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Test connection to configured services"""
    
    settings = db.settings.get(tenant_id, {})
    env_config = EnvironmentConfig(**settings.get("environment_config", {}))
    
    results = {
        "openai": {"status": "not_configured", "message": "OpenAI API key not set"},
        "aws_s3": {"status": "not_configured", "message": "AWS credentials not set"},
        "neo4j": {"status": "not_configured", "message": "Neo4j credentials not set"},
        "backend": {"status": "not_configured", "message": "Backend URL not set"}
    }
    
    # Test OpenAI connection
    if env_config.openai_api_key:
        try:
            import openai
            client = openai.OpenAI(api_key=env_config.openai_api_key)
            # Simple test - list models
            models = client.models.list()
            results["openai"] = {
                "status": "success",
                "message": f"Connected successfully, {len(models.data)} models available"
            }
        except Exception as e:
            results["openai"] = {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }
    
    # Test AWS S3 connection
    if env_config.aws_access_key_id and env_config.aws_secret_access_key:
        try:
            import boto3
            s3_client = boto3.client(
                's3',
                aws_access_key_id=env_config.aws_access_key_id,
                aws_secret_access_key=env_config.aws_secret_access_key,
                region_name=env_config.aws_region or 'us-east-1'
            )
            # Test by listing buckets
            response = s3_client.list_buckets()
            results["aws_s3"] = {
                "status": "success",
                "message": f"Connected successfully, {len(response['Buckets'])} buckets available"
            }
        except Exception as e:
            results["aws_s3"] = {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }
    
    # Test Neo4j connection
    if env_config.neo4j_uri and env_config.neo4j_user and env_config.neo4j_password:
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                env_config.neo4j_uri,
                auth=(env_config.neo4j_user, env_config.neo4j_password)
            )
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            driver.close()
            results["neo4j"] = {
                "status": "success",
                "message": "Connected successfully"
            }
        except Exception as e:
            results["neo4j"] = {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }
    
    # Test backend connection
    if env_config.backend_url:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{env_config.backend_url}/api/v1/health")
                if response.status_code == 200:
                    results["backend"] = {
                        "status": "success",
                        "message": "Backend is reachable"
                    }
                else:
                    results["backend"] = {
                        "status": "error",
                        "message": f"Backend returned status {response.status_code}"
                    }
        except Exception as e:
            results["backend"] = {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }
    
    await db.log_audit(
        actor_id=user["user_id"],
        action="test_connection",
        target_ids=[tenant_id],
        details={"results": results}
    )
    
    return {
        "results": results,
        "overall_status": "success" if all(r["status"] in ["success", "not_configured"] for r in results.values()) else "error"
    }

@router.get(
    "/environment-info",
    summary="ℹ️ Environment Information",
    description="""
    **Get information about the current environment**
    
    This endpoint returns:
    - 🖥️ **System Info**: OS, Python version, dependencies
    - 🔧 **Configuration**: Current settings and defaults
    - 📊 **Status**: Service availability and health
    - 🔍 **Diagnostics**: Environment-specific information
    
    **Perfect for**: Environment diagnostics, troubleshooting,
    and system information display.
    """,
    responses={
        200: {"description": "Environment information retrieved"},
        401: {"description": "Authentication required"},
        500: {"description": "Failed to retrieve environment info"}
    }
)
async def get_environment_info(
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Get environment information"""
    
    import platform
    import sys
    
    info = {
        "system": {
            "platform": platform.platform(),
            "python_version": sys.version,
            "architecture": platform.architecture()[0]
        },
        "services": {
            "neo4j_available": "neo4j" in str(sys.modules.keys()),
            "boto3_available": "boto3" in str(sys.modules.keys()),
            "openai_available": "openai" in str(sys.modules.keys()),
            "git_available": "git" in str(sys.modules.keys())
        },
        "configuration": {
            "use_local_backend": True,  # Default
            "storage_path": "storage/",
            "max_file_size": "100MB",
            "supported_languages": ["python", "javascript", "typescript", "java", "go", "rust"]
        }
    }
    
    # Add tenant-specific info
    settings = db.settings.get(tenant_id, {})
    if settings:
        env_config = settings.get("environment_config", {})
        info["configuration"].update({
            "use_local_backend": env_config.get("use_local_backend", True),
            "backend_url": env_config.get("backend_url", "http://localhost:8000"),
            "has_openai_key": bool(env_config.get("openai_api_key")),
            "has_aws_credentials": bool(env_config.get("aws_access_key_id")),
            "has_neo4j_credentials": bool(env_config.get("neo4j_uri"))
        })
    
    return info
