from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional, Any

T = TypeVar("T")

class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    version: str
    providers: dict

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None

from .auth import Token, TokenPayload, Login
from .user import UserResponse, UserCreate
from .hierarchy import OrganizationResponse, MineResponse
from .compliance import ComplianceRequirementResponse, ComplianceRecordResponse
from .dashboard import DashboardSummary
from .field import SafetyEventCreate, SafetyEventResponse, CorrectiveActionResponse
from .workflow import NotificationResponse, AuditLogResponse
from .document import DocumentResponse, VerifyDocumentRequest, CitationResponse, SearchResponse
from .secondary import ContractorResponse, WorkerResponse, EnvironmentReadingResponse, ProductionRecordResponse, GrievanceCreate, GrievanceResponse, ApplyAISuggestion
from .report import ReportResponse, ReportStatusUpdate, ReportGenerateRequest, TrendDataPoint, RegionalCompareData

__all__ = [
    "HealthResponse", "PaginatedResponse", "ErrorResponse", "SuccessResponse",
    "Token", "TokenPayload", "Login",
    "UserResponse", "UserCreate",
    "OrganizationResponse", "MineResponse",
    "ComplianceRequirementResponse", "ComplianceRecordResponse",
    "DashboardSummary",
    "SafetyEventCreate", "SafetyEventResponse", "CorrectiveActionResponse",
    "NotificationResponse", "AuditLogResponse",
    "DocumentResponse", "VerifyDocumentRequest", "CitationResponse", "SearchResponse",
    "ContractorResponse", "WorkerResponse", "EnvironmentReadingResponse", "ProductionRecordResponse", "GrievanceCreate", "GrievanceResponse", "ApplyAISuggestion",
    "ReportResponse", "ReportStatusUpdate", "ReportGenerateRequest", "TrendDataPoint", "RegionalCompareData"
]
