from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Integer,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
import uuid

# String constants
PROJECT_STATUSES = ["created", "cloning", "ready", "analyzing", "completed", "error"]


# Project model
class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(
        String(50), nullable=False
    )  # 'local', 'github', 'gitlab', etc.
    source_url = Column(String(500), nullable=True)
    source_path = Column(String(500), nullable=True)
    status = Column(String(20), default="created", nullable=False)
    file_count = Column(Integer, nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    analysis_count = Column(Integer, default=0, nullable=False)
    last_analyzed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="projects")
    owner = relationship("User", back_populates="projects")
    analyses = relationship(
        "Analysis", back_populates="project", cascade="all, delete-orphan"
    )

    __table_args__ = {"extend_existing": True}
