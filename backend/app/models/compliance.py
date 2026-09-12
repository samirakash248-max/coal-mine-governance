import uuid
import enum
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Date, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class ComplianceStatus(str, enum.Enum):
    COMPLIANT = "COMPLIANT"
    DUE_SOON = "DUE_SOON"
    AT_RISK = "AT_RISK"
    NON_COMPLIANT = "NON_COMPLIANT"
    OVERDUE = "OVERDUE"

class ComplianceRequirement(BaseModel):
    __tablename__ = "compliance_requirements"
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    applicable_mine_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), nullable=True)
    
    records: Mapped[list["ComplianceRecord"]] = relationship(back_populates="requirement", cascade="all, delete-orphan")

class ComplianceRecord(BaseModel):
    __tablename__ = "compliance_records"
    
    requirement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("compliance_requirements.id", ondelete="CASCADE"), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ComplianceStatus] = mapped_column(SQLEnum(ComplianceStatus), nullable=False, default=ComplianceStatus.COMPLIANT)
    
    responsible_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    responsible_officer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    submission_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    requirement: Mapped["ComplianceRequirement"] = relationship(back_populates="records")
    evidence: Mapped[list["ComplianceEvidence"]] = relationship(back_populates="record", cascade="all, delete-orphan")

class ComplianceEvidence(BaseModel):
    __tablename__ = "compliance_evidence"
    
    record_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("compliance_records.id", ondelete="CASCADE"), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    record: Mapped["ComplianceRecord"] = relationship(back_populates="evidence")
