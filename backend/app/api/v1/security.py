# RepoLens API - Security Endpoints
# Security assessment API routes
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from ...services.security_service import SecurityService
from ...services.audit_service import AuditService

from ...core.dependencies import get_tenant_id, get_security, get_audit, authenticate

router = APIRouter(
    prefix="/security",
    tags=["Security Assessment"],
    responses={404: {"description": "Repository not found"}},
)


@router.post(
    "/repositories/{repo_id}/assess",
    summary="Security Assessment",
    description="Perform security assessment on repository",
    responses={
        200: {"description": "Security assessment completed"},
        404: {"description": "Repository not found"},
        401: {"description": "Authentication required"},
        500: {"description": "Security assessment failed"},
    },
)
async def assess_security(
    repo_id: str,
    tenant_id: str = Depends(get_tenant_id),
    security: SecurityService = Depends(get_security),
    audit: AuditService = Depends(get_audit),
    user: Dict[str, Any] = Depends(authenticate),
):
    """Perform security assessment"""

    # Perform security assessment
    result = security.assess_repository(repo_id, tenant_id)

    # Log audit event
    audit.log_security_operation(
        tenant_id=tenant_id,
        repo_id=repo_id,
        actor_id=user["user_id"],
        scan_type="comprehensive",
        details=result,
    )

    return result
