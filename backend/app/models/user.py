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
    
    # Newly explicitly requested roles
    ADMIN = "admin"
    SAFETY_OFFICER = "safety_officer"
    INSPECTOR = "inspector"
    ENVIRONMENT_OFFICER = "environment_officer"
    CONTRACTOR = "contractor"
    REGULATOR = "regulator"
    FIELD_OFFICER = "field_officer"

from app.core.permissions import get_role_permissions

class User(BaseModel):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role, native_enum=False, length=50), nullable=False, default=Role.FIELD_INSPECTOR)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Scope Assignments (Hierarchical)
    # A user typically has ONE of these set depending on their role level.
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), index=True, nullable=True)
    subsidiary_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("subsidiaries.id", ondelete="SET NULL"), index=True, nullable=True)
    region_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("regions.id", ondelete="SET NULL"), index=True, nullable=True)
    mine_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mines.id", ondelete="SET NULL"), index=True, nullable=True)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), index=True, nullable=True)


    @property
    def permissions(self) -> list[str]:
        return [p.value for p in get_role_permissions(self.role)]

