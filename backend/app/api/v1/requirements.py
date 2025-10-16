# RepoLens API - Requirements Endpoints
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

# Requirements management API routes
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime, timezone
import uuid

from ...services.requirement_service import RequirementService
from ...services.audit_service import AuditService
from ...shared.models.api_models import (
    RequirementExtractRequest, RequirementExtractResponse,
    RequirementMatchRequest, RequirementMatchResponse,
    RequirementVerifyRequest, RequirementVerifyResponse
)

from ...core.dependencies import get_requirement, get_audit, authenticate, require_permissions, get_tenant_id, get_db

router = APIRouter(
    prefix="/requirements",
    tags=["📋 Requirements Management"],
    responses={404: {"description": "Requirement not found"}}
)

@router.post(
    "/extract",
    response_model=RequirementExtractResponse,
    summary="📝 Extract Requirements",
    description="""
    **Extract requirements from text using LLM**
    
    This endpoint processes requirement documents to extract:
    - 📋 Functional requirements
    - 🔧 Technical specifications
    - 📊 Business rules
    - 🎯 Acceptance criteria
    - 🔗 Requirement relationships
    
    **Perfect for**: Document processing, requirement analysis, 
    specification extraction, and compliance tracking.
    """,
    responses={
        200: {"description": "Requirements extracted successfully"},
        400: {"description": "Invalid document format"},
        401: {"description": "Authentication required"},
        500: {"description": "Extraction failed"}
    }
)
async def extract_requirements(
    request: RequirementExtractRequest,
    requirement: RequirementService = Depends(get_requirement),
    audit: AuditService = Depends(get_audit),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Extract requirements from text using LLM"""
    
    # Process requirement document
    result = requirement.process_requirement_document(
        document_text=request.text,
        tenant_id=request.tenant_id,
        repo_id=request.repo_id,
        source=request.source
    )
    
    # Log audit event
    audit.log_requirement_operation(
        tenant_id=request.tenant_id,
        req_id="batch_extraction",
        actor_id=user["user_id"],
        operation="extract",
        details={
            "source": request.source,
            "requirements_extracted": result["requirements_extracted"],
            "matches_found": result["matches_found"]
        }
    )
    
    return RequirementExtractResponse(
        requirements=[{
            "req_id": f"req_{i}",
            "title": f"Requirement {i}",
            "text": request.text,
            "source": request.source,
            "confidence": 0.8
        } for i in range(result["requirements_extracted"])]
    )

@router.post(
    "/{req_id}/match",
    response_model=RequirementMatchResponse,
    summary="🔗 Match Requirements to Code",
    description="""
    **Match requirements to implementation code**
    
    This endpoint finds code implementations for requirements:
    - 🔧 Function matches
    - 📦 Class implementations
    - 🔗 Dependency relationships
    - 📊 Confidence scores
    - 🎯 Evidence snippets
    
    **Perfect for**: Traceability analysis, compliance checking, 
    code review, and requirement validation.
    """,
    responses={
        200: {"description": "Requirement matches found successfully"},
        404: {"description": "Requirement not found"},
        400: {"description": "Invalid match parameters"},
        500: {"description": "Matching failed"}
    }
)
async def match_requirement(
    req_id: str,
    request: RequirementMatchRequest,
    tenant_id: str = Depends(get_tenant_id),  # Will need to import this
    db = Depends(get_db)  # Will need to import this
):
    """Match requirement to code"""
    
    if req_id not in db.requirements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    
    # TODO: Implement vector search
    candidates = [
        {
            "function_id": str(uuid.uuid4()),
            "confidence": 0.85,
            "path": "src/auth.py",
            "signature": "def authenticate_user(username: str, password: str) -> bool:"
        }
    ]
    
    return RequirementMatchResponse(candidates=candidates)

@router.post(
    "/{req_id}/verify",
    response_model=RequirementVerifyResponse,
    summary="✅ Verify Requirement Match",
    description="""
    **Verify requirement-to-code matches**
    
    This endpoint handles human verification of:
    - ✅ Requirement implementations
    - 🔍 Code quality assessment
    - 📝 Verification notes
    - 🎯 Approval workflows
    - 📊 Verification tracking
    
    **Perfect for**: Quality assurance, compliance verification, 
    code review workflows, and requirement validation.
    """,
    responses={
        200: {"description": "Requirement verification recorded successfully"},
        404: {"description": "Requirement not found"},
        403: {"description": "Insufficient permissions"},
        500: {"description": "Verification failed"}
    }
)
async def verify_requirement(
    req_id: str,
    request: RequirementVerifyRequest,
    tenant_id: str = Depends(get_tenant_id),  # Will need to import this
    db = Depends(get_db),  # Will need to import this
    user: Dict[str, Any] = Depends(require_permissions(["verify"]))
):
    """Verify requirement match"""
    
    if req_id not in db.requirements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    
    verification_id = str(uuid.uuid4())
    
    verification = {
        "verification_id": verification_id,
        "req_id": req_id,
        "function_id": request.function_id,
        "user_id": request.user_id,
        "status": request.status,
        "note": request.note,
        "created_at": datetime.now(timezone.utc)
    }
    
    db.verifications[verification_id] = verification
    
    await db.log_audit(
        actor_id=user["user_id"],
        action="verify_requirement",
        target_ids=[req_id, request.function_id],
        details={"status": request.status}
    )
    
    return RequirementVerifyResponse(verification_id=verification_id)
