# RepoLens API - Repository Endpoints
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

# Repository analysis API routes
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime

from ...features.repository.models import (
    AnalyzeProjectRequest, EnhancedAnalyzeRequest, AnalyzeRequest,
    FileQuery, SearchQuery, RepoGraphResponse, EnhancedRepoGraphResponse,
    AnalyzeResponse, FileInfo, FileContent, Node
)
from ...features.repository.services import RepositoryAnalyzer
from ...core.dependencies import get_repository_service, validate_repository_path, validate_file_path

router = APIRouter(
    prefix="/repository",
    tags=["📊 Repository Analysis"],
    responses={404: {"description": "Repository not found"}}
)

@router.post(
    "/analyze/project", 
    response_model=RepoGraphResponse,
    summary="📊 Analyze Repository Structure",
    description="""
    **Analyze entire repository and generate comprehensive code graph**
    
    This endpoint performs deep analysis of your codebase, extracting:
    - 📁 File structure and organization
    - 🔧 Function definitions and signatures  
    - 📦 Class hierarchies and relationships
    - 🔗 Import dependencies and references
    - 📈 Code metrics and statistics
    
    **Perfect for**: Understanding large codebases, generating documentation, 
    code visualization, and architectural analysis.
    """,
    responses={
        200: {"description": "Repository analysis completed successfully"},
        400: {"description": "Invalid request parameters"},
        404: {"description": "Repository not found"},
        500: {"description": "Analysis failed"}
    }
)
async def analyze_project(
    request: AnalyzeProjectRequest,
    repo_service: RepositoryAnalyzer = Depends(get_repository_service)
):
    """📊 Analyze Repository Structure"""
    try:
        folder_path = validate_repository_path(request.folder_path or ".")
        result = await repo_service.analyze_repository(folder_path)
        
        # Add metadata
        result.meta = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "analyzed_path": folder_path,
            "parser_version": "2.0.0"
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Repository analysis failed: {str(e)}"
        )

@router.post(
    "/analyze/enhanced", 
    response_model=EnhancedRepoGraphResponse,
    summary="🚀 Enhanced Repository Analysis",
    description="""
    **Advanced repository analysis with technology stack detection**
    
    This enhanced endpoint provides deeper insights including:
    - 🏗️ Technology stack identification
    - 📚 Documentation analysis
    - ⚙️ Configuration file detection
    - 🔍 Dependency mapping
    - 📊 Advanced metrics and patterns
    
    **Perfect for**: Architecture reviews, technology audits, 
    migration planning, and comprehensive codebase documentation.
    """,
    responses={
        200: {"description": "Enhanced analysis completed successfully"},
        400: {"description": "Invalid request parameters"},
        404: {"description": "Repository not found"},
        500: {"description": "Enhanced analysis failed"}
    }
)
async def analyze_enhanced(
    request: EnhancedAnalyzeRequest,
    repo_service: RepositoryAnalyzer = Depends(get_repository_service)
):
    """🚀 Enhanced Repository Analysis"""
    try:
        folder_path = validate_repository_path(request.folder_path or ".")
        result = await repo_service.analyze_enhanced(folder_path)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced analysis failed: {str(e)}"
        )

@router.post(
    "/analyze", 
    response_model=AnalyzeResponse,
    summary="🔍 Analyze Individual File",
    description="""
    **Analyze a single file and extract its structure**
    
    This endpoint analyzes individual files to extract:
    - 🔧 Function definitions and signatures
    - 📦 Class definitions and methods
    - 📝 Documentation and comments
    - 🔗 Import statements
    - 📊 File metrics and statistics
    
    **Perfect for**: File-specific analysis, code review, 
    documentation generation, and debugging.
    """,
    responses={
        200: {"description": "File analysis completed successfully"},
        400: {"description": "Invalid file path or unsupported file type"},
        404: {"description": "File not found"},
        500: {"description": "File analysis failed"}
    }
)
async def analyze_file(
    request: AnalyzeRequest,
    repo_service: RepositoryAnalyzer = Depends(get_repository_service)
):
    """🔍 Analyze Individual File"""
    try:
        file_path = validate_file_path(request.file)
        result = await repo_service.analyze_file(file_path)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File analysis failed: {str(e)}"
        )

@router.get(
    "/files", 
    response_model=List[FileInfo],
    summary="📁 List Repository Files",
    description="""
    **Get comprehensive list of all files in the repository**
    
    This endpoint scans the repository and returns:
    - 📁 All supported code files
    - 📊 File sizes and metadata
    - 🏷️ Programming language detection
    - 📍 Relative file paths
    - 🔍 File type categorization
    
    **Perfect for**: File browsing, project overview, 
    language statistics, and file management.
    """,
    responses={
        200: {"description": "File list retrieved successfully"},
        500: {"description": "Failed to retrieve files"}
    }
)
async def get_files(
    repo_service: RepositoryAnalyzer = Depends(get_repository_service)
):
    """📁 List Repository Files"""
    try:
        files = await repo_service.get_files()
        return files
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get files: {str(e)}"
        )

@router.get(
    "/file", 
    response_model=FileContent,
    summary="📄 Get File Content",
    description="""
    **Retrieve file content with parsing and analysis**
    
    This endpoint provides:
    - 📄 Complete file content
    - 🔧 Parsed function definitions
    - 🏷️ Language detection
    - 📊 File metadata
    - 🔍 Syntax highlighting support
    
    **Perfect for**: Code viewing, file analysis, 
    syntax highlighting, and content inspection.
    """,
    responses={
        200: {"description": "File content retrieved successfully"},
        400: {"description": "Invalid file path"},
        404: {"description": "File not found"},
        500: {"description": "Failed to retrieve file content"}
    }
)
async def get_file_content(
    path: Optional[str] = Query(None, description="Relative path to the file"),
    repo_service: RepositoryAnalyzer = Depends(get_repository_service)
):
    """📄 Get File Content"""
    try:
        if not path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File path parameter is required"
            )
        
        file_path = validate_file_path(path)
        content = await repo_service.get_file_content(file_path)
        return content
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file content: {str(e)}"
        )

@router.get(
    "/search", 
    response_model=List[Node],
    summary="🔍 Search Code Symbols",
    description="""
    **Search for functions, classes, and symbols across the repository**
    
    This powerful search endpoint allows you to find:
    - 🔧 Function definitions and signatures
    - 📦 Class names and methods
    - 📁 File names and paths
    - 🏷️ Variable names and constants
    - 🔗 Import statements
    
    **Perfect for**: Code navigation, symbol lookup, 
    refactoring assistance, and code discovery.
    """,
    responses={
        200: {"description": "Search completed successfully"},
        400: {"description": "Invalid search query"},
        500: {"description": "Search failed"}
    }
)
async def search_symbols(
    q: str = Query(..., description="Search query for symbols, functions, or files"),
    repo_service: RepositoryAnalyzer = Depends(get_repository_service)
):
    """🔍 Search Code Symbols"""
    try:
        if not q.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        
        results = await repo_service.search_symbols(q)
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get(
    "/languages",
    summary="🏷️ Supported Languages",
    description="""
    **Get comprehensive list of supported programming languages**
    
    This endpoint provides information about:
    - 🏷️ All supported programming languages
    - 📁 File extensions for each language
    - 🔧 Parser capabilities per language
    - 📊 Language-specific features
    
    **Perfect for**: Language detection, parser configuration, 
    and understanding analysis capabilities.
    """,
    responses={
        200: {"description": "Supported languages retrieved successfully"}
    }
)
async def get_supported_languages(
    repo_service: RepositoryAnalyzer = Depends(get_repository_service)
):
    """🏷️ Supported Languages"""
    try:
        languages_info = await repo_service.get_supported_languages()
        return languages_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported languages: {str(e)}"
        )
