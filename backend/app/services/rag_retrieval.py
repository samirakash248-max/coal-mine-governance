from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any

from app.models.document import DocumentChunk, Document
from app.providers.ai.base import AIProvider

class RAGRetrievalService:
    def __init__(self, db: AsyncSession, ai_provider: AIProvider):
        self.db = db
        self.ai_provider = ai_provider
        
    async def retrieve_context(self, query: str, top_k: int = 3, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Generates an embedding for the query and retrieves the closest DocumentChunks using pgvector cosine distance.
        """
        # 1. Embed query
        query_vector = await self.ai_provider.generate_embeddings(query)
        
        # 2. Vector search using pgvector's cosine distance operator `<=>`
        # cosine distance = 1 - cosine similarity. So smaller is more similar.
        # We want distance < (1 - threshold)
        max_distance = 1.0 - threshold
        
        stmt = (
            select(DocumentChunk, Document)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(DocumentChunk.embedding.cosine_distance(query_vector) < max_distance)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(top_k)
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        # 3. Format exact citations
        citations = []
        for chunk, doc in rows:
            citations.append({
                "document_id": doc.id,
                "title": doc.title,
                "page": chunk.page,
                "section": chunk.section_clause,
                "text_content": chunk.text_content
            })
            
        return citations
