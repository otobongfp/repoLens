# RepoLens API - Repository Endpoints
# Repository analysis API routes

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...core.dependencies import get_repository_service
from ...features.repository.models import (
    AnalyzeProjectRequest,
    AnalyzeRequest,
    AnalyzeResponse,
    EnhancedAnalyzeRequest,
    EnhancedRepoGraphResponse,
    FileContent,
    FileInfo,
    RepoGraphResponse,
    SearchQuery,
)
from ...features.repository.services import RepositoryAnalyzer


router = APIRouter(
    prefix="/repository",
    tags=["Repository Analysis"],
    responses={404: {"description": "Repository not found"}},
)


@router.post(
    "/analyze/project",
    response_model=RepoGraphResponse,
    summary="Analyze project structure",
    description="Analyze project structure and dependencies",
    responses={
        400: {"description": "Invalid request parameters"},
        404: {"description": "Repository not found"},
        500: {"description": "Analysis failed"},
    },
)
async def analyze_project(
    request: AnalyzeProjectRequest,
    repo_service: RepositoryAnalyzer = Depends(get_repository_service),
):
    """Analyze project structure and dependencies"""
    try:
        result = await repo_service.analyze_project(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@router.post(
    "/analyze/enhanced",
    response_model=EnhancedRepoGraphResponse,
    summary="Enhanced project analysis",
    description="Perform enhanced analysis with AI insights",
    responses={
        400: {"description": "Invalid request parameters"},
        404: {"description": "Repository not found"},
        500: {"description": "Enhanced analysis failed"},
    },
)
async def analyze_enhanced(
    request: EnhancedAnalyzeRequest,
    repo_service: RepositoryAnalyzer = Depends(get_repository_service),
):
    """Perform enhanced analysis with AI insights"""
    try:
        result = await repo_service.analyze_enhanced(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced analysis failed: {str(e)}",
        )


@router.post(
    "/analyze/file",
    response_model=AnalyzeResponse,
    summary="Analyze single file",
    description="Analyze a single file for patterns and issues",
    responses={
        400: {"description": "Invalid file path or unsupported file type"},
        404: {"description": "File not found"},
        500: {"description": "File analysis failed"},
    },
)
async def analyze_file(
    request: AnalyzeRequest,
    repo_service: RepositoryAnalyzer = Depends(get_repository_service),
):
    """Analyze a single file for patterns and issues"""
    try:
        result = await repo_service.analyze_file(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File analysis failed: {str(e)}",
        )


@router.get(
    "/files",
    response_model=list[FileInfo],
    summary="List repository files",
    description="Get list of files in repository with metadata",
    responses={
        404: {"description": "Repository not found"},
        500: {"description": "Failed to list files"},
    },
)
async def list_files(
    repo_path: str = Query(..., description="Repository path"),
    repo_service: RepositoryAnalyzer = Depends(get_repository_service),
):
    """Get list of files in repository with metadata"""
    try:
        files = await repo_service.list_files(repo_path)
        return files
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}",
        )


@router.get(
    "/file/content",
    response_model=FileContent,
    summary="Get file content",
    description="Get content of a specific file",
    responses={
        400: {"description": "Invalid file path"},
        404: {"description": "File not found"},
        500: {"description": "Failed to read file"},
    },
)
async def get_file_content(
    file_path: str = Query(..., description="File path"),
    repo_service: RepositoryAnalyzer = Depends(get_repository_service),
):
    """Get content of a specific file"""
    try:
        content = await repo_service.get_file_content(file_path)
        return content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {str(e)}",
        )


@router.post(
    "/search",
    response_model=list[FileInfo],
    summary="Search repository",
    description="Search for files and content in repository",
    responses={
        400: {"description": "Invalid search query"},
        500: {"description": "Search failed"},
    },
)
async def search_repository(
    query: SearchQuery,
    repo_service: RepositoryAnalyzer = Depends(get_repository_service),
):
    """Search for files and content in repository"""
    try:
        results = await repo_service.search_repository(query)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get(
    "/health",
    summary="Repository service health",
    description="Check repository service health status",
)
async def health_check():
    """Check repository service health status"""
    return {"status": "healthy", "service": "repository"}
