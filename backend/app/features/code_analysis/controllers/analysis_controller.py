from fastapi import APIRouter, HTTPException
from app.features.code_analysis.models.request import AnalyzeRequest
from app.features.code_analysis.models.response import RepoGraphResponse
from app.features.code_analysis.services.analysis_service import AnalysisService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Create service instance
analysis_service = AnalysisService()

@router.post("/analyze", response_model=RepoGraphResponse)
async def analyze_endpoint(req: AnalyzeRequest):
    """
    Analyze a repository and return its structure graph.
    
    Args:
        req: Analysis request containing repository URL
        
    Returns:
        Repository graph response with nodes, edges, and summary
    """
    try:
        logger.info(f"Received analysis request for repository: {req.url}")
        result = analysis_service.analyze_repo(req.url)
        logger.info(f"Analysis completed successfully for: {req.url}")
        return result
    except Exception as e:
        logger.error(f"Analysis failed for {req.url}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 