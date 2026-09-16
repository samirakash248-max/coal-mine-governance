import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Index, DateTime, ForeignKey, Text, Float, Integer, Enum as SQLEnum
from sqlalchemy import JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pgvector.sqlalchemy import Vector

from enum import Enum
from .base import BaseModel

class DocumentStatus(str, Enum):
    PENDING_OCR = "PENDING_OCR"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    ERROR = "ERROR"

class Document(BaseModel):
    __tablename__ = "documents"
    
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), index=True, nullable=False)
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    document_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    issue_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(SQLEnum(DocumentStatus, native_enum=False, length=50), default=DocumentStatus.PENDING_OCR, nullable=False)
    
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete")

class DocumentChunk(BaseModel):
    __tablename__ = "document_chunks"
    
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    section_clause: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # pgvector embedding
    embedding = mapped_column(Vector(1536), nullable=False)
    
    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index(
            'idx_document_chunks_embedding',
            'embedding',
            postgresql_using='hnsw',
            postgresql_with={'m': 16, 'ef_construction': 64},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
        ),
    )
