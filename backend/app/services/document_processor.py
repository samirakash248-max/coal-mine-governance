from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import json
from datetime import datetime

from app.models.document import Document, DocumentStatus, DocumentChunk
from app.providers.ocr.base import OCRProvider
from app.providers.ai.base import AIProvider

class DocumentProcessor:
    def __init__(self, db: AsyncSession, ocr_provider: OCRProvider, ai_provider: AIProvider):
        self.db = db
        self.ocr_provider = ocr_provider
        self.ai_provider = ai_provider
        
    async def process_new_document(self, document_id: uuid.UUID, file_bytes: bytes):
        """
        Background task: run OCR, extract metadata, set to PENDING_VERIFICATION.
        """
        doc = (await self.db.execute(select(Document).where(Document.id == document_id))).scalar_one_or_none()
        if not doc:
            return
            
        try:
            # 1. OCR Extraction
            ocr_result = await self.ocr_provider.extract_text(file_bytes)
            meta = ocr_result.metadata
            
            # 2. Speculative update
            doc.document_number = meta.get("document_number")
            if "issue_date" in meta:
                doc.issue_date = datetime.fromisoformat(meta["issue_date"].replace("Z", "+00:00"))
            if "expiry_date" in meta:
                doc.expiry_date = datetime.fromisoformat(meta["expiry_date"].replace("Z", "+00:00"))
                
            doc.category = meta.get("category", "Uncategorized")
            
            # We temporarily store the raw text in the DB or a file.
            # For this prototype, we'll just wait for human verification to chunk.
            # In a real app, we'd save `ocr_result.text` to cloud storage and reference it.
            
            doc.status = DocumentStatus.PENDING_VERIFICATION
            await self.db.commit()
            
        except Exception as e:
            doc.status = DocumentStatus.ERROR
            await self.db.commit()

    async def generate_embeddings_for_document(self, document_id: uuid.UUID, raw_text: str):
        """
        Triggered after human verification.
        """
        doc = (await self.db.execute(select(Document).where(Document.id == document_id))).scalar_one_or_none()
        if not doc or doc.status != DocumentStatus.VERIFIED:
            return
            
        # 1. Very crude chunking for prototype
        # Real system: RecursiveCharacterTextSplitter from langchain
        chunks = [raw_text[i:i+1000] for i in range(0, len(raw_text), 800)]
        
        for i, text_chunk in enumerate(chunks):
            # 2. Generate embedding
            vector = await self.ai_provider.generate_embeddings(text_chunk)
            
            # 3. Save to pgvector
            db_chunk = DocumentChunk(
                document_id=doc.id,
                page=i+1, # Mock page assignment
                section_clause=f"Section {i+1}",
                text_content=text_chunk,
                embedding=vector
            )
            self.db.add(db_chunk)
            
        await self.db.commit()
