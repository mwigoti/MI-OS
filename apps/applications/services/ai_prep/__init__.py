"""
MwohaOS AI Preparation Module — Milestone 6: AI Preparation
Orchestrates tailored cover letter synthesis, CV tailoring and ATS alignment,
evidence-grounded essay/question drafting, and version control.
"""
from .cover_letter import generate_tailored_cover_letter
from .cv_tailor import generate_cv_tailoring
from .question_answering import draft_question_answer
from .evidence_grounding import gather_candidate_evidence, audit_grounding_evidence
from .ai_prep_service import AIPreparationService

__all__ = [
    "generate_tailored_cover_letter",
    "generate_cv_tailoring",
    "draft_question_answer",
    "gather_candidate_evidence",
    "audit_grounding_evidence",
    "AIPreparationService",
]
