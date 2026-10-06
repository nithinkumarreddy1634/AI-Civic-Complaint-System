"""AI Pipeline Orchestrator Facade."""
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.services.complaint_processing_service import complaint_processing_service, ComplaintProcessingService


class AIPipeline:
    """Facade for the complete multi-phase civic complaint AI pipeline."""

    def __init__(self, service: Optional[ComplaintProcessingService] = None):
        self._service = service or complaint_processing_service

    def process(
        self,
        complaint_id: uuid.UUID,
        image_path: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Execute complete AI processing pipeline."""
        return self._service.process_complaint(complaint_id=complaint_id, db=db)


ai_pipeline = AIPipeline()
