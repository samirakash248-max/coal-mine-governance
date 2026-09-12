import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.document import DocumentStatus

class DocumentResponse(BaseModel):
    id: uuid.UUID
    mine_id: uuid.UUID
    owner_id: Optional[uuid.UUID]
    title: str
    document_number: Optional[str]
    category: Optional[str]
    issue_date: Optional[datetime]
    expiry_date: Optional[datetime]
    file_path: str
    version: int
    status: DocumentStatus
    
    model_config = ConfigDict(from_attributes=True)

class VerifyDocumentRequest(BaseModel):
    title: str
    document_number: Optional[str]
    category: Optional[str]
    issue_date: Optional[datetime]
    expiry_date: Optional[datetime]
    # Optionally also pass corrected full text if we wanted

class CitationResponse(BaseModel):
    document_id: uuid.UUID
    title: str
    page: Optional[int]
    section: Optional[str]
    text_content: str
    
class SearchResponse(BaseModel):
    results: List[CitationResponse]
