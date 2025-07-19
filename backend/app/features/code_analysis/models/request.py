from app.shared.models.base import BaseRequest

class AnalyzeRequest(BaseRequest):
    """Request model for code analysis."""
    url: str 