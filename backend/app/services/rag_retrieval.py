from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any
import uuid

from app.models.document import DocumentChunk, Document, DocumentStatus
from app.providers.ai.base import AIProvider

class RAGRetrievalService:
    def __init__(self, db: AsyncSession, ai_provider: AIProvider):
        self.db = db
        self.ai_provider = ai_provider
        
    async def retrieve_context(self, query: str, mine_id: uuid.UUID, top_k: int = 3, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Generates an embedding for the query and retrieves the closest DocumentChunks using pgvector cosine distance.
        Enforces mine_id RBAC constraint and only retrieves VERIFIED documents.
        """
        # 1. Embed query
        query_vector = await self.ai_provider.generate_embeddings(query)
        
        # 2. Vector search using pgvector's cosine distance operator `<=>`
        max_distance = 1.0 - threshold
        
        stmt = (
            select(DocumentChunk, Document)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(
                and_(
                    DocumentChunk.embedding.cosine_distance(query_vector) < max_distance,
                    Document.mine_id == mine_id,
                    Document.status == DocumentStatus.VERIFIED
                )
            )
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(top_k)
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        # 3. Format exact citations
        citations = []
        for chunk, doc in rows:
            citations.append({
                "document_id": str(doc.id),
                "title": doc.title,
                "page": chunk.page,
                "section": chunk.section_clause,
                "text_content": chunk.text_content
            })
            
        return citations
