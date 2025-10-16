# RepoLens API - Security Endpoints
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

# Security assessment API routes
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from ...services.security_service import SecurityService
from ...services.audit_service import AuditService

from ...core.dependencies import get_tenant_id, get_security, get_audit, authenticate

router = APIRouter(
    prefix="/security",
    tags=["Security Assessment"],
    responses={404: {"description": "Repository not found"}}
)

@router.post(
    "/repositories/{repo_id}/assess",
    summary="Security Assessment",
    description="""
    **Perform comprehensive security assessment of a repository**
    
    This endpoint conducts security analysis including:
    - Vulnerability scanning
    - SAST (Static Application Security Testing)
    - Dependency security checks
    - Security metrics
    - Risk assessment
    
    **Perfect for**: Security audits, compliance checking, 
    vulnerability management, and risk assessment.
    """,
    responses={
        200: {"description": "Security assessment completed successfully"},
        404: {"description": "Repository not found"},
        401: {"description": "Authentication required"},
        500: {"description": "Security assessment failed"}
    }
)
async def assess_security(
    repo_id: str,
    tenant_id: str = Depends(get_tenant_id),
    security: SecurityService = Depends(get_security),
    audit: AuditService = Depends(get_audit),
    user: Dict[str, Any] = Depends(authenticate)
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
        details=result
    )
    
    return result
