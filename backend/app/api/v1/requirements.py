# RepoLens API - Requirements Endpoints
# Requirements management API routes
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime, timezone
import uuid

from ...services.requirement_service import RequirementService
from ...services.audit_service import AuditService
from ...shared.models.api_models import (
    RequirementExtractRequest,
    RequirementExtractResponse,
    RequirementMatchRequest,
    RequirementMatchResponse,
    RequirementVerifyRequest,
    RequirementVerifyResponse,
)

from ...core.dependencies import (
    get_requirement,
    get_audit,
    authenticate,
    require_permissions,
    get_tenant_id,
    get_db,
)

router = APIRouter(
    prefix="/requirements",
    tags=["Requirements Management"],
    responses={404: {"description": "Requirement not found"}},
)


@router.post(
    "/extract",
    response_model=RequirementExtractResponse,
    summary="Extract Requirements",
    description="Extract requirements from documents",
    responses={
        400: {"description": "Invalid document format"},
        401: {"description": "Authentication required"},
        500: {"description": "Extraction failed"},
    },
)
async def extract_requirements(
    request: RequirementExtractRequest,
    requirement: RequirementService = Depends(get_requirement),
    audit: AuditService = Depends(get_audit),
    user: Dict[str, Any] = Depends(authenticate),
):
    """Extract requirements from documents"""
    try:
        # Get tenant ID from user
        tenant_id = user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID required"
            )

        # Extract requirements
        result = await requirement.extract_requirements(
            document_content=request.document_content,
            document_type=request.document_type,
            tenant_id=tenant_id,
        )

        # Log the extraction
        await audit.log_action(
            user_id=user.get("user_id"),
            action="requirements_extracted",
            resource_id=result.extraction_id,
            details={"document_type": request.document_type},
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )


@router.post(
    "/match",
    response_model=RequirementMatchResponse,
    summary="Match Requirements",
    description="Match requirements to code implementation",
    responses={
        200: {"description": "Requirements matched successfully"},
        404: {"description": "Requirement not found"},
        400: {"description": "Invalid match parameters"},
        500: {"description": "Matching failed"},
    },
)
async def match_requirement(
    req_id: str,
    request: RequirementMatchRequest,
    requirement: RequirementService = Depends(get_requirement),
    audit: AuditService = Depends(get_audit),
    user: Dict[str, Any] = Depends(authenticate),
):
    """Match requirements to code implementation"""
    try:
        # Get tenant ID from user
        tenant_id = user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID required"
            )

        # Match requirements
        result = await requirement.match_requirements(
            requirement_id=req_id,
            code_content=request.code_content,
            tenant_id=tenant_id,
        )

        # Log the matching
        await audit.log_action(
            user_id=user.get("user_id"),
            action="requirements_matched",
            resource_id=req_id,
            details={"match_score": result.match_score},
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching failed: {str(e)}",
        )


@router.post(
    "/verify",
    response_model=RequirementVerifyResponse,
    summary="Verify Requirements",
    description="Verify requirement implementation",
    responses={
        200: {"description": "Requirements verified successfully"},
        404: {"description": "Requirement not found"},
        403: {"description": "Insufficient permissions"},
        500: {"description": "Verification failed"},
    },
)
async def verify_requirement(
    req_id: str,
    request: RequirementVerifyRequest,
    requirement: RequirementService = Depends(get_requirement),
    audit: AuditService = Depends(get_audit),
    user: Dict[str, Any] = Depends(require_permissions(["admin", "developer"])),
):
    """Verify requirement implementation"""
    try:
        # Get tenant ID from user
        tenant_id = user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID required"
            )

        # Verify requirements
        result = await requirement.verify_requirements(
            requirement_id=req_id,
            verification_criteria=request.verification_criteria,
            tenant_id=tenant_id,
        )

        # Log the verification
        await audit.log_action(
            user_id=user.get("user_id"),
            action="requirements_verified",
            resource_id=req_id,
            details={"verification_status": result.verification_status},
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
        )
