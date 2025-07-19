from typing import Generator
from app.shared.services.git_service import GitService
from app.shared.services.file_service import FileService
from app.features.code_analysis.services.analysis_service import AnalysisService
from app.features.ai_analysis.services.ai_analyzer_service import AIAnalyzerService

def get_git_service() -> GitService:
    """Dependency for Git service."""
    return GitService()

def get_file_service() -> FileService:
    """Dependency for file service."""
    return FileService()

def get_analysis_service() -> AnalysisService:
    """Dependency for code analysis service."""
    return AnalysisService()

def get_ai_analyzer_service() -> AIAnalyzerService:
    """Dependency for AI analyzer service."""
    return AIAnalyzerService() 