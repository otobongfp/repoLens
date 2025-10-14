# Action proposals API routes
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime, timezone
import uuid

from ...shared.models.api_models import (
    ActionProposalRequest, ActionProposalResponse, ActionApprovalRequest,
    ProposalStatus
)

# Import dependencies from core
from ...core.dependencies import get_tenant_id, get_db, authenticate, require_permissions

router = APIRouter(
    prefix="/action-proposals",
    tags=["🚀 Action Proposals"],
    responses={404: {"description": "Proposal not found"}}
)

@router.post(
    "",
    response_model=ActionProposalResponse,
    summary="📝 Create Action Proposal",
    description="""
    **Create a new action proposal for code changes**
    
    This endpoint allows users to propose:
    - 🔧 Code improvements
    - 🐛 Bug fixes
    - ⚡ Performance optimizations
    - 🔒 Security enhancements
    - 📝 Documentation updates
    
    **Perfect for**: Code review workflows, improvement suggestions, 
    collaborative development, and change management.
    """,
    responses={
        200: {"description": "Action proposal created successfully"},
        400: {"description": "Invalid proposal data"},
        401: {"description": "Authentication required"},
        500: {"description": "Proposal creation failed"}
    }
)
async def create_proposal(
    request: ActionProposalRequest,
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(authenticate)
):
    """Create action proposal"""
    
    if request.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant mismatch"
        )
    
    proposal_id = str(uuid.uuid4())
    
    proposal = {
        "proposal_id": proposal_id,
        "tenant_id": request.tenant_id,
        "repo_id": request.repo_id,
        "proposer_id": request.proposer_id,
        "patch_s3": request.patch_s3,
        "rationale": request.rationale,
        "tests": request.tests,
        "status": ProposalStatus.SUBMITTED,
        "created_at": datetime.now(timezone.utc)
    }
    
    db.proposals[proposal_id] = proposal
    
    await db.log_audit(
        actor_id=user["user_id"],
        action="create_proposal",
        target_ids=[proposal_id],
        details={"repo_id": request.repo_id}
    )
    
    return ActionProposalResponse(
        proposal_id=proposal_id,
        status=ProposalStatus.SUBMITTED
    )

@router.post(
    "/{proposal_id}/approve",
    summary="✅ Approve Action Proposal",
    description="""
    **Approve an action proposal for implementation**
    
    This endpoint handles proposal approval including:
    - ✅ Approval workflow
    - 📝 Approval notes
    - 👤 Approver tracking
    - 🕒 Approval timestamp
    - 🔄 Status updates
    
    **Perfect for**: Code review processes, change approval, 
    quality gates, and workflow management.
    """,
    responses={
        200: {"description": "Proposal approved successfully"},
        404: {"description": "Proposal not found"},
        403: {"description": "Insufficient permissions"},
        500: {"description": "Approval failed"}
    }
)
async def approve_proposal(
    proposal_id: str,
    request: ActionApprovalRequest,
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_db),
    user: Dict[str, Any] = Depends(require_permissions(["approve"]))
):
    """Approve action proposal"""
    
    if proposal_id not in db.proposals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    proposal = db.proposals[proposal_id]
    if proposal["tenant_id"] != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    proposal["status"] = ProposalStatus.APPROVED
    proposal["approved_by"] = request.approver_id
    proposal["approved_at"] = datetime.now(timezone.utc)
    
    await db.log_audit(
        actor_id=user["user_id"],
        action="approve_proposal",
        target_ids=[proposal_id],
        details={"approver": request.approver_id}
    )
    
    return {"message": "Proposal approved"}
