from fastapi import APIRouter, HTTPException
from app.models.request import AnalyzeRequest
from app.models.response import RepoGraphResponse
from app.services.analyze_service import analyze_repo

router = APIRouter()

@router.post("/analyze", response_model=RepoGraphResponse)
async def analyze_endpoint(req: AnalyzeRequest):
    try:
        return analyze_repo(req.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 