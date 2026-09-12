from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional

class OCRResult(BaseModel):
    text: str
    confidence: float  # 0.0 to 1.0
    language: str = "en"
    page_count: int = 1
    metadata: dict = {}  # any additional extraction metadata
    is_simulated: bool = False

class OCRProvider(ABC):
    """Abstract interface for OCR/document digitization.
    
    Initially mock, then Tesseract, with abstraction for
    future replacement (e.g., cloud OCR services).
    """
    
    @abstractmethod
    async def extract_text(
        self, 
        file_bytes: bytes,
        mime_type: str = "image/png",
        language: str = "eng"
    ) -> OCRResult:
        ...
    
    @abstractmethod
    async def extract_from_pdf(
        self,
        file_bytes: bytes,
        pages: Optional[list[int]] = None
    ) -> OCRResult:
        ...
