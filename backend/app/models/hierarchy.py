import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy import JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Organization(BaseModel):
    __tablename__ = "organizations"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    subsidiaries: Mapped[list["Subsidiary"]] = relationship(back_populates="organization", cascade="all, delete-orphan")

class Subsidiary(BaseModel):
    __tablename__ = "subsidiaries"
    
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    organization: Mapped["Organization"] = relationship(back_populates="subsidiaries")
    regions: Mapped[list["Region"]] = relationship(back_populates="subsidiary", cascade="all, delete-orphan")

class Region(BaseModel):
    __tablename__ = "regions"
    
    subsidiary_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subsidiaries.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    subsidiary: Mapped["Subsidiary"] = relationship(back_populates="regions")
    mines: Mapped[list["Mine"]] = relationship(back_populates="region", cascade="all, delete-orphan")

class Mine(BaseModel):
    __tablename__ = "mines"
    
    region_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("regions.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    mine_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # e.g., open_cast, underground
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    operational_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    region: Mapped["Region"] = relationship(back_populates="mines")
    departments: Mapped[list["Department"]] = relationship(back_populates="mine", cascade="all, delete-orphan")

class Department(BaseModel):
    __tablename__ = "departments"
    
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    mine: Mapped["Mine"] = relationship(back_populates="departments")
