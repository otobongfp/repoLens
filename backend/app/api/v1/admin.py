# Admin and tenant management API routes
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from ...shared.models.api_models import UsageMetrics

from ...core.dependencies import get_db, require_permissions

router = APIRouter(
    prefix="/admin",
    tags=["👑 Admin & Tenant Management"],
    responses={403: {"description": "Admin access required"}}
)

@router.get(
    "/tenants/{tenant_id}/usage",
    response_model=UsageMetrics,
    summary="📊 Tenant Usage Metrics",
    description="""
    **Get comprehensive usage metrics for a tenant**
    
    This endpoint provides detailed usage information:
    - 📁 Active repositories
    - 💾 Storage usage
    - 🔍 Vector database usage
    - 📈 API request counts
    - 🎯 Plan limits and usage
    
    **Perfect for**: Billing, usage monitoring, capacity planning, 
    and tenant management.
    """,
    responses={
        200: {"description": "Usage metrics retrieved successfully"},
        404: {"description": "Tenant not found"},
        403: {"description": "Admin access required"},
        500: {"description": "Failed to retrieve metrics"}
    }
)
async def get_usage(
    tenant_id: str,
    user: Dict[str, Any] = Depends(require_permissions(["admin"])),
    db = Depends(get_db)
):
    """Get tenant usage metrics"""
    
    tenant = await db.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return UsageMetrics(
        active_repos=tenant.active_repos,
        vector_count=0,  # TODO: Query vector store
        storage_bytes=0,  # TODO: Query S3
        api_requests=0,  # TODO: Query logs
        limits={
            "max_repos": 3 if tenant.plan == Plan.PRO else 10 if tenant.plan == Plan.BUSINESS else float('inf')
        }
    )
