import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel

class EnvironmentReading(BaseModel):
    __tablename__ = "environment_readings"
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), index=True, nullable=False)
    parameter: Mapped[str] = mapped_column(String(100), nullable=False) # Air, Dust, Water, Noise
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class ProductionRecord(BaseModel):
    __tablename__ = "production_records"
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), index=True, nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    target: Mapped[float] = mapped_column(Float, nullable=False)
    actual: Mapped[float] = mapped_column(Float, nullable=False)
    deviation: Mapped[float] = mapped_column(Float, nullable=False) # (actual - target) / target * 100
