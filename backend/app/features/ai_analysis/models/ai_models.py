# RepoLens Backend - Ai_Models
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

from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class AIAnalysisRequest(BaseModel):
    """Request model for AI analysis."""
    graph_data: Dict[str, Any]

class FunctionAnalysisRequest(BaseModel):
    """Request model for function-specific AI analysis."""
    function_node: Dict[str, Any]
    graph_data: Dict[str, Any]

class AskRequest(BaseModel):
    graph_data: Dict[str, Any]
    question: str

class AIAnalysisResponse(BaseModel):
    """Response model for AI analysis."""
    enabled: bool
    scores: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    error: Optional[str] = None

class AskResponse(BaseModel):
    answer: str
    error: Optional[str] = None

class AIStatusResponse(BaseModel):
    """Response model for AI service status."""
    enabled: bool
    openai_configured: bool
    model: str
    max_tokens: int
    temperature: float 