"""
DocumentReviewService - Document Processing Workflows for Bill Ingestion

Handles document review workflows for bill processing and approval.
Essential for Phase 1 AP workflows where documents need human review before bill creation.

Enhanced for business_id tenant isolation and AP bill processing workflows.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import Float
from datetime import datetime
import logging

from domains.core.services.base_service import TenantAwareService
from domains.core.models.document import Document as DocumentModel
from infra.config.exceptions import ValidationError

logger = logging.getLogger(__name__)


class DocumentReviewService(TenantAwareService):
    """
    Service for managing document review workflows in bill processing.
    
    Handles the review queue for documents that require human validation
    before being converted to bills in the AP workflow.
    """
    
    def __init__(self, db: Session, business_id: str):
        """
        Initialize document review service with tenant isolation.
        
        Args:
            db: Database session
            business_id: Business identifier for tenant isolation
        """
        super().__init__(db, business_id)
        logger.info(f"Initialized DocumentReviewService for business {business_id}")

    def get_review_queue(self, batch_by: str = "type", limit: int = 50) -> List[DocumentModel]:
        """
        Get documents pending review for bill processing.
        
        Args:
            batch_by: How to sort documents ("type", "date", "confidence")
            limit: Maximum number of documents to return
            
        Returns:
            List of documents requiring review
        """
        try:
            query = self._base_query(DocumentModel).filter(
                DocumentModel.status == "review"
            )
            
            # Sort based on batch_by parameter
            if batch_by == "type":
                query = query.order_by(DocumentModel.type)
            elif batch_by == "date":
                query = query.order_by(DocumentModel.upload_date.desc())
            elif batch_by == "confidence":
                # Order by confidence score (lowest first for manual review)
                query = query.order_by(
                    DocumentModel.extracted_fields['confidence'].astext.cast(Float)
                )
            
            documents = query.limit(limit).all()
            logger.info(f"Retrieved {len(documents)} documents for review queue")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to get review queue: {str(e)}")
            raise ValidationError(f"Failed to retrieve review queue: {str(e)}")

    def review_document(self, document_id: int, review_data: Dict[str, Any], 
                       reviewer_user_id: str) -> DocumentModel:
        """
        Review and update document with human-validated data.
        
        Args:
            document_id: Document ID to review
            review_data: Human-validated extracted data
            reviewer_user_id: ID of user performing review
            
        Returns:
            Updated document
        """
        try:
            document = self._get_document_or_raise(document_id)
            
            if document.status != "review":
                raise ValidationError(f"Document {document_id} is not in review status")
            
            # Update extracted fields with reviewed data
            if document.extracted_fields:
                document.extracted_fields.update(review_data)
            else:
                document.extracted_fields = review_data
            
            # Mark as reviewed
            document.review_status = "confirmed"
            document.status = "processed"
            document.updated_at = datetime.utcnow()
            
            # Add review metadata
            document.extracted_fields["reviewed_by"] = reviewer_user_id
            document.extracted_fields["reviewed_at"] = datetime.utcnow().isoformat()
            
            self.db.commit()
            logger.info(f"Document {document_id} reviewed and processed")
            return document
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Document review failed: {str(e)}")
            raise

    def reject_document(self, document_id: int, rejection_reason: str, 
                       reviewer_user_id: str) -> DocumentModel:
        """
        Reject document and mark for reprocessing or removal.
        
        Args:
            document_id: Document ID to reject
            rejection_reason: Reason for rejection
            reviewer_user_id: ID of user performing rejection
            
        Returns:
            Updated document
        """
        try:
            document = self._get_document_or_raise(document_id)
            
            document.status = "rejected"
            document.review_status = "rejected"
            document.extracted_fields = document.extracted_fields or {}
            document.extracted_fields["rejection_reason"] = rejection_reason
            document.extracted_fields["rejected_by"] = reviewer_user_id
            document.extracted_fields["rejected_at"] = datetime.utcnow().isoformat()
            document.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Document {document_id} rejected: {rejection_reason}")
            return document
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Document rejection failed: {str(e)}")
            raise

    def get_review_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for document review queue.
        
        Returns:
            Dictionary with review queue statistics
        """
        try:
            base_query = self._base_query(DocumentModel)
            
            stats = {
                "pending_review": base_query.filter(DocumentModel.status == "review").count(),
                "processed_today": base_query.filter(
                    DocumentModel.status == "processed",
                    DocumentModel.updated_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
                ).count(),
                "rejected_today": base_query.filter(
                    DocumentModel.status == "rejected",
                    DocumentModel.updated_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
                ).count(),
                "total_documents": base_query.count()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get review summary: {str(e)}")
            return {"error": str(e)}

    def bulk_approve_high_confidence(self, confidence_threshold: float = 0.9) -> List[DocumentModel]:
        """
        Bulk approve documents with high confidence scores.
        
        Args:
            confidence_threshold: Minimum confidence score for auto-approval
            
        Returns:
            List of auto-approved documents
        """
        try:
            # Find high-confidence documents in review status
            documents = self._base_query(DocumentModel).filter(
                DocumentModel.status == "review",
                DocumentModel.extracted_fields['confidence'].astext.cast(Float) >= confidence_threshold
            ).all()
            
            approved_docs = []
            for doc in documents:
                doc.status = "processed"
                doc.review_status = "auto_approved"
                doc.extracted_fields["auto_approved_at"] = datetime.utcnow().isoformat()
                doc.extracted_fields["confidence_threshold"] = confidence_threshold
                doc.updated_at = datetime.utcnow()
                approved_docs.append(doc)
            
            self.db.commit()
            logger.info(f"Bulk approved {len(approved_docs)} high-confidence documents")
            return approved_docs
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Bulk approval failed: {str(e)}")
            raise ValidationError(f"Bulk approval failed: {str(e)}")

    def _get_document_or_raise(self, document_id: int) -> DocumentModel:
        """Get document by ID or raise ValidationError."""
        return self._get_by_id_or_raise(DocumentModel, document_id, f"Document {document_id} not found")
