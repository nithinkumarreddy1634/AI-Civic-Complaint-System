"""Master orchestrator for AI-powered duplicate complaint detection and grouping."""
import uuid
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.complaint import Complaint, ComplaintStatus
from app.models.duplicate import ComplaintEmbedding, DuplicateGroup, ComplaintDuplicateLink
from app.models.ai_analysis import AIAnalysis
from app.models.severity import SeverityAnalysis
from .config import duplicate_config
from .embedding_service import EmbeddingService
from .geospatial_similarity import calculate_location_similarity
from .image_similarity import calculate_image_similarity
from .text_similarity import calculate_text_similarity
from .scoring import calculate_category_similarity, compute_duplicate_score
from .candidate_search import find_duplicate_candidates
from .explainer import generate_duplicate_explanation


class DuplicateDetectionService:
    """End-to-end duplicate detection, candidate ranking, and group management service."""

    def __init__(self):
        self.config = duplicate_config
        self.embedding_service = EmbeddingService()

    def get_or_generate_embedding(
        self,
        complaint: Complaint,
        db: Session,
        force_recompute: bool = False,
    ) -> ComplaintEmbedding:
        """
        Retrieve existing complaint embeddings from database or generate and persist new ones.
        """
        rec = db.query(ComplaintEmbedding).filter(ComplaintEmbedding.complaint_id == complaint.id).first()

        if rec and not force_recompute:
            # Check model version compatibility
            if (
                rec.image_model_version == self.config.image_model.version
                and rec.text_model_version == self.config.text_model.version
            ):
                return rec

        # Generate fresh visual embedding
        img_emb = self.embedding_service.generate_image_embedding(complaint.image_path)
        # Generate fresh semantic text embedding
        txt_emb = self.embedding_service.generate_text_embedding(complaint.description)

        if not rec:
            rec = ComplaintEmbedding(
                complaint_id=complaint.id,
                image_embedding=img_emb,
                text_embedding=txt_emb,
                image_model=self.config.image_model.name,
                image_model_version=self.config.image_model.version,
                text_model=self.config.text_model.name,
                text_model_version=self.config.text_model.version,
                dimension=len(img_emb),
            )
            db.add(rec)
        else:
            rec.image_embedding = img_emb
            rec.text_embedding = txt_emb
            rec.image_model_version = self.config.image_model.version
            rec.text_model_version = self.config.text_model.version

        db.commit()
        db.refresh(rec)
        return rec

    def compare_complaints(
        self,
        complaint_a: Complaint,
        emb_a: ComplaintEmbedding,
        complaint_b: Complaint,
        emb_b: ComplaintEmbedding,
    ) -> Dict[str, Any]:
        """
        Compute multi-modal similarities between two complaints.
        """
        # 1. Geographic distance & location similarity
        loc_res = calculate_location_similarity(
            complaint_a.latitude,
            complaint_a.longitude,
            complaint_b.latitude,
            complaint_b.longitude,
        )

        # 2. Visual similarity
        img_res = calculate_image_similarity(emb_a.image_embedding, emb_b.image_embedding)

        # 3. Text semantic similarity
        txt_res = calculate_text_similarity(emb_a.text_embedding, emb_b.text_embedding)

        # 4. Category compatibility
        cat_a = complaint_a.category.value if hasattr(complaint_a.category, "value") else str(complaint_a.category)
        cat_b = complaint_b.category.value if hasattr(complaint_b.category, "value") else str(complaint_b.category)
        cat_sim = calculate_category_similarity(cat_a, cat_b)

        # 5. Composite score & decision
        score_res = compute_duplicate_score(
            location_sim=loc_res["location_similarity"],
            image_sim=img_res["image_similarity"],
            text_sim=txt_res["text_similarity"],
            category_sim=cat_sim,
            distance_meters=loc_res["distance_meters"],
        )

        score_res["complaint_id"] = complaint_b.id
        score_res["category"] = cat_b
        score_res["status"] = complaint_b.status.value if hasattr(complaint_b.status, "value") else str(complaint_b.status)

        return score_res

    def detect_duplicates(
        self,
        complaint_id: uuid.UUID,
        db: Session,
        force_recompute: bool = False,
    ) -> Dict[str, Any]:
        """
        Run the complete duplicate detection pipeline for a given complaint.
        """
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise ValueError(f"Complaint not found: {complaint_id}")

        # Check existing link for caching
        existing_link = db.query(ComplaintDuplicateLink).filter(ComplaintDuplicateLink.complaint_id == complaint.id).first()
        if existing_link and not force_recompute:
            group = db.query(DuplicateGroup).filter(DuplicateGroup.id == existing_link.group_id).first()
            if group:
                return {
                    "complaint_id": complaint.id,
                    "decision": "LIKELY_DUPLICATE" if existing_link.similarity_score >= self.config.thresholds.likely_duplicate else "POSSIBLE_DUPLICATE",
                    "duplicate_score": existing_link.similarity_score,
                    "is_duplicate": True,
                    "best_match": None,
                    "candidates": [],
                    "explanation": ["Retrieved from existing verified duplicate group."],
                    "duplicate_group_id": group.id,
                    "representative_complaint_id": group.representative_complaint_id,
                    "cached": True,
                }

        # Step 1: Embed current complaint
        current_emb = self.get_or_generate_embedding(complaint, db, force_recompute=force_recompute)

        # Step 2: Retrieve candidate complaints
        cat_str = complaint.category.value if hasattr(complaint.category, "value") else str(complaint.category)
        candidates = find_duplicate_candidates(
            db=db,
            current_complaint_id=complaint.id,
            category=cat_str,
            latitude=complaint.latitude,
            longitude=complaint.longitude,
            max_candidates=self.config.max_candidates_to_compare,
        )

        if not candidates:
            explanation = generate_duplicate_explanation("NEW", 0.0, None)
            return {
                "complaint_id": complaint.id,
                "decision": "NEW",
                "duplicate_score": 0.0,
                "is_duplicate": False,
                "best_match": None,
                "candidates": [],
                "explanation": explanation,
                "duplicate_group_id": None,
                "representative_complaint_id": None,
                "cached": False,
            }

        # Step 3: Compare against candidates
        matches = []
        for cand in candidates:
            cand_emb = self.get_or_generate_embedding(cand, db)
            match_res = self.compare_complaints(complaint, current_emb, cand, cand_emb)
            matches.append(match_res)

        # Sort candidates descending by duplicate_score
        matches.sort(key=lambda m: m["duplicate_score"], reverse=True)
        top_candidates = matches[:self.config.max_candidates_to_return]
        best_match = matches[0] if matches else None

        decision = best_match["decision"] if best_match else "NEW"
        duplicate_score = best_match["duplicate_score"] if best_match else 0.0
        is_duplicate = decision in ["LIKELY_DUPLICATE", "POSSIBLE_DUPLICATE"]

        # Step 4: Group management and linking
        group_id = None
        representative_id = None

        if decision == "LIKELY_DUPLICATE" and best_match:
            best_cand_id = best_match["complaint_id"]
            best_cand = db.query(Complaint).filter(Complaint.id == best_cand_id).first()

            # Check if candidate is already in a group
            cand_link = db.query(ComplaintDuplicateLink).filter(ComplaintDuplicateLink.complaint_id == best_cand_id).first()
            if cand_link:
                group = db.query(DuplicateGroup).filter(DuplicateGroup.id == cand_link.group_id).first()
            else:
                # Create a new DuplicateGroup
                group = DuplicateGroup(
                    representative_complaint_id=best_cand.id,
                    report_count=1,
                    unique_users_count=1,
                    status="ACTIVE",
                )
                db.add(group)
                db.commit()
                db.refresh(group)

                # Link initial candidate
                db.add(ComplaintDuplicateLink(
                    group_id=group.id,
                    complaint_id=best_cand.id,
                    similarity_score=100.0,
                ))

            # Link current complaint to the group if not already linked
            my_link = db.query(ComplaintDuplicateLink).filter(ComplaintDuplicateLink.complaint_id == complaint.id).first()
            if not my_link:
                db.add(ComplaintDuplicateLink(
                    group_id=group.id,
                    complaint_id=complaint.id,
                    similarity_score=duplicate_score,
                ))
                group.report_count += 1
                if complaint.user_id != best_cand.user_id:
                    group.unique_users_count += 1

            # Update complaint duplicate fields
            complaint.is_duplicate = True
            complaint.duplicate_of = group.representative_complaint_id

            # Elect best representative
            self._update_representative_complaint(group, db)

            db.commit()
            db.refresh(group)
            group_id = group.id
            representative_id = group.representative_complaint_id

        explanation = generate_duplicate_explanation(decision, duplicate_score, best_match)

        return {
            "complaint_id": complaint.id,
            "decision": decision,
            "duplicate_score": duplicate_score,
            "is_duplicate": is_duplicate,
            "best_match": best_match,
            "candidates": top_candidates,
            "explanation": explanation,
            "duplicate_group_id": group_id,
            "representative_complaint_id": representative_id,
            "cached": False,
        }

    def _update_representative_complaint(self, group: DuplicateGroup, db: Session):
        """
        Elect the best representative complaint for a DuplicateGroup.
        Criteria:
        1. Highest verification confidence
        2. Highest severity score
        3. Earliest report creation date
        """
        links = db.query(ComplaintDuplicateLink).filter(ComplaintDuplicateLink.group_id == group.id).all()
        complaint_ids = [l.complaint_id for l in links]
        if not complaint_ids:
            return

        complaints = db.query(Complaint).filter(Complaint.id.in_(complaint_ids)).all()

        best_comp = None
        best_rank = (-1.0, -1.0, 0.0)

        for c in complaints:
            ai_rec = db.query(AIAnalysis).filter(AIAnalysis.complaint_id == c.id).first()
            sev_rec = db.query(SeverityAnalysis).filter(SeverityAnalysis.complaint_id == c.id).first()

            conf = ai_rec.confidence if ai_rec and ai_rec.confidence else 0.5
            sev = sev_rec.severity_score if sev_rec else 50.0
            # Earlier timestamp preferred (negative timestamp value for max sort)
            ts = -c.created_at.timestamp() if c.created_at else 0.0

            rank = (conf, sev, ts)
            if best_comp is None or rank > best_rank:
                best_comp = c
                best_rank = rank

        if best_comp:
            group.representative_complaint_id = best_comp.id
