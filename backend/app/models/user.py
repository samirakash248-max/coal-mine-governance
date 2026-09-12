import uuid
import enum
from typing import Optional
from sqlalchemy import String, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Role(str, enum.Enum):
    FIELD_INSPECTOR = "field_inspector"
    MINE_OFFICER = "mine_officer"
    MINE_MANAGER = "mine_manager"
    REGIONAL_MANAGER = "regional_manager"
    CORPORATE_MANAGER = "corporate_manager"
    REGULATORY_AUDITOR = "regulatory_auditor"
    SYSTEM_ADMIN = "system_admin"

class User(BaseModel):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), nullable=False, default=Role.FIELD_INSPECTOR)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Scope Assignments (Hierarchical)
    # A user typically has ONE of these set depending on their role level.
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    subsidiary_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("subsidiaries.id", ondelete="SET NULL"), nullable=True)
    region_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("regions.id", ondelete="SET NULL"), nullable=True)
    mine_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mines.id", ondelete="SET NULL"), nullable=True)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
