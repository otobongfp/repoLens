# RepoLens Backend - Base
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

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class BaseNode(BaseModel):
    """Base model for graph nodes."""
    id: str
    label: str
    type: str
    path: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class BaseEdge(BaseModel):
    """Base model for graph edges."""
    from_: str = Field(..., alias="from")
    to: str
    type: str
    meta: Optional[Dict[str, Any]] = None

class BaseRequest(BaseModel):
    """Base model for API requests."""
    pass

class BaseResponse(BaseModel):
    """Base model for API responses."""
    pass 