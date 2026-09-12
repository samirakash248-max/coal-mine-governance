from .base import OCRProvider, OCRResult
from typing import Optional
import random

class MockOCRProvider(OCRProvider):
    async def extract_text(
        self, 
        file_bytes: bytes,
        mime_type: str = "image/png",
        language: str = "eng"
    ) -> OCRResult:
        sample_text = (
            "SAFETY INSPECTION FORM\n"
            "Date: 2023-10-01\n"
            "Inspector: Ramesh Singh\n"
            "Site: Section B Pit\n"
            "Observations: Helmet compliance checked. Ventilation systems active.\n"
        )
        return OCRResult(
            text=sample_text,
            confidence=round(random.uniform(0.85, 0.95), 2),
            language=language,
            page_count=1,
            metadata={"source_mime": mime_type, "mocked": True},
            is_simulated=True
        )
    
    async def extract_from_pdf(
        self,
        file_bytes: bytes,
        pages: Optional[list[int]] = None
    ) -> OCRResult:
        sample_text = (
            "REGULATORY COMPLIANCE EXCERPT\n"
            "Article 42(a): All subsurface mining operations must maintain secondary egress routes.\n"
            "Audits must be logged quarterly.\n"
        )
        return OCRResult(
            text=sample_text,
            confidence=round(random.uniform(0.85, 0.99), 2),
            language="en",
            page_count=len(pages) if pages else 5,
            metadata={
                "mocked": True,
                "document_number": "REG-2023-42A",
                "issue_date": "2023-01-15T00:00:00Z",
                "expiry_date": "2024-01-15T00:00:00Z",
                "category": "Regulatory Guideline"
            },
            is_simulated=True
        )
