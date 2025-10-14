# Repository analysis controller
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import os
from pathlib import Path
from .models import (
    AnalyzeProjectRequest, EnhancedAnalyzeRequest, AnalyzeRequest,
    FileQuery, SearchQuery, RepoGraphResponse, EnhancedRepoGraphResponse,
    AnalyzeResponse, FileInfo, FileContent, Node
)
from .services import RepositoryAnalyzer, CodeParser

router = APIRouter()

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
        200: {
            "description": "Repository analysis completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "nodes": [
                            {
                                "id": "file_main_py",
                                "label": "main.py", 
                                "type": "file",
                                "path": "src/main.py",
                                "meta": {"size": 1024, "language": "python"}
                            }
                        ],
                        "edges": [
                            {
                                "from_node": "file_main_py",
                                "to_node": "func_main_py_hello",
                                "type": "uses"
                            }
                        ],
                        "summary": {
                            "total_files": 15,
                            "total_functions": 42,
                            "total_classes": 8,
                            "languages": ["python", "javascript"],
                            "main_technologies": ["python", "fastapi"]
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid request parameters"},
        404: {"description": "Repository not found"},
        500: {"description": "Analysis failed"}
    }
)
async def analyze_project(request: AnalyzeProjectRequest):
    """📊 Analyze Repository Structure"""
    try:
        folder_path = request.folder_path or "."
        
        # Validate folder path
        if not os.path.exists(folder_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository path not found: {folder_path}"
            )
        
        # Check if it's a directory
        if not os.path.isdir(folder_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path must be a directory: {folder_path}"
            )
        
        analyzer = RepositoryAnalyzer(folder_path)
        result = analyzer.analyze_repository()
        
        # Add metadata to response
        result.meta = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "analyzed_path": folder_path,
            "analysis_duration_ms": 0,  # TODO: Add timing
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
async def analyze_enhanced(request: EnhancedAnalyzeRequest):
    """🚀 Enhanced Repository Analysis"""
    try:
        folder_path = request.folder_path or "."
        
        # Validate folder path
        if not os.path.exists(folder_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository path not found: {folder_path}"
            )
        
        analyzer = RepositoryAnalyzer(folder_path)
        result = analyzer.analyze_repository()
        
        # Convert to enhanced response
        enhanced_result = EnhancedRepoGraphResponse(
            nodes=result.nodes,
            edges=result.edges,
            summary=result.summary,
            technology_stack=result.summary.main_technologies if result.summary else None,
            documentation=[],
            configurations=[],
            technologies=result.summary.languages if result.summary else []
        )
        
        return enhanced_result
        
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
async def analyze_file(request: AnalyzeRequest):
    """🔍 Analyze Individual File"""
    try:
        parser = CodeParser()
        language = parser.get_language_from_extension(request.file)
        
        if not language:
            return AnalyzeResponse(
                file=request.file,
                functions=[],
                error=f"Unsupported file type: {request.file}"
            )
        
        # Validate file exists
        if not os.path.exists(request.file):
            return AnalyzeResponse(
                file=request.file,
                functions=[],
                error=f"File not found: {request.file}"
            )
        
        # Read file content
        try:
            with open(request.file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return AnalyzeResponse(
                file=request.file,
                functions=[],
                error=f"Failed to read file: {str(e)}"
            )
        
        # Parse functions
        functions = parser.parse_file(request.file, content)
        
        return AnalyzeResponse(
            file=request.file,
            functions=functions,
            error=None
        )
        
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
async def get_files():
    """📁 List Repository Files"""
    try:
        analyzer = RepositoryAnalyzer(".")
        files = analyzer.get_files()
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
async def get_file_content(path: Optional[str] = Query(None, description="Relative path to the file")):
    """📄 Get File Content"""
    try:
        if not path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File path parameter is required"
            )
        
        analyzer = RepositoryAnalyzer(".")
        content = analyzer.get_file_content(path)
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
async def search_symbols(q: str = Query(..., description="Search query for symbols, functions, or files")):
    """🔍 Search Code Symbols"""
    try:
        if not q.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        
        analyzer = RepositoryAnalyzer(".")
        results = analyzer.search_symbols(q)
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
async def get_supported_languages():
    """🏷️ Supported Languages"""
    parser = CodeParser()
    extensions = list(parser.supported_extensions.keys())
    languages = list(set(parser.supported_extensions.values()))
    
    return {
        "supported_extensions": extensions,
        "languages": languages,
        "language_details": [
            {
                "extension": ext, 
                "language": lang,
                "parser_type": "AST" if lang == "python" else "Regex" if lang in ["javascript", "typescript"] else "Basic"
            }
            for ext, lang in parser.supported_extensions.items()
        ],
        "total_languages": len(languages),
        "total_extensions": len(extensions),
        "parser_capabilities": {
            "python": "Full AST parsing with functions, classes, imports",
            "javascript": "Regex-based function detection",
            "typescript": "Regex-based function detection", 
            "other": "Basic file structure analysis"
        }
    }
