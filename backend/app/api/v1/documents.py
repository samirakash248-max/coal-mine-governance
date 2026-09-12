from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.api.deps import get_current_user, get_ocr_provider_dep, get_ai_provider_dep
from app.providers.ocr.base import OCRProvider
from app.providers.ai.base import AIProvider
from app.schemas.document import DocumentResponse, VerifyDocumentRequest, SearchResponse
from app.services.document_processor import DocumentProcessor
from app.services.rag_retrieval import RAGRetrievalService

router = APIRouter()

@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Document).where(Document.mine_id == current_user.mine_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Document).where(Document.id == document_id, Document.mine_id == current_user.mine_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ocr_provider: OCRProvider = Depends(get_ocr_provider_dep),
    ai_provider: AIProvider = Depends(get_ai_provider_dep)
):
    # 1. Create record
    doc = Document(
        mine_id=current_user.mine_id,
        owner_id=current_user.id,
        title=title,
        file_path=f"local_storage/{file.filename}",
        status=DocumentStatus.PENDING_OCR
    )
    db.add(doc)
    await db.flush()
    
    file_bytes = await file.read()
    
    # 2. Trigger OCR (In a real app, send to Celery/arq, but we will await it here for prototype ease)
    processor = DocumentProcessor(db, ocr_provider, ai_provider)
    await processor.process_new_document(doc.id, file_bytes)
    
    await db.refresh(doc)
    return doc

@router.put("/{document_id}/verify", response_model=DocumentResponse)
async def verify_document(
    document_id: uuid.UUID,
    req: VerifyDocumentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ocr_provider: OCRProvider = Depends(get_ocr_provider_dep),
    ai_provider: AIProvider = Depends(get_ai_provider_dep)
):
    stmt = select(Document).where(Document.id == document_id, Document.mine_id == current_user.mine_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    
    if not doc or doc.status != DocumentStatus.PENDING_VERIFICATION:
        raise HTTPException(400, "Document not ready for verification")
        
    doc.title = req.title
    doc.document_number = req.document_number
    doc.category = req.category
    doc.issue_date = req.issue_date.replace(tzinfo=timezone.utc) if req.issue_date else None
    doc.expiry_date = req.expiry_date.replace(tzinfo=timezone.utc) if req.expiry_date else None
    doc.status = DocumentStatus.VERIFIED
    
    await db.commit()
    
    # Trigger embeddings background task
    processor = DocumentProcessor(db, ocr_provider, ai_provider)
    # Fake raw text since we didn't persist it in Phase 7 prototype
    raw_text = "Article 42(a): All subsurface mining operations must maintain secondary egress routes. Audits must be logged quarterly."
    await processor.generate_embeddings_for_document(doc.id, raw_text)
    
    await db.refresh(doc)
    return doc

@router.post("/search", response_model=SearchResponse)
async def search_documents(
    query: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_provider: AIProvider = Depends(get_ai_provider_dep)
):
    service = RAGRetrievalService(db, ai_provider)
    # Using threshold 0.0 for prototype to ensure results are returned despite mock zeroed vectors
    citations = await service.retrieve_context(query, threshold=0.0) 
    
    return SearchResponse(results=citations)
