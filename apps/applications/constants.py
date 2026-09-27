"""
MwohaOS Applications Constants — Milestone 5: Application Workspace
Defines application lifecycle stages, priorities, submission methods, and document roles.
"""
from django.db import models


class ApplicationStatus(models.TextChoices):
    SAVED = "SAVED", "Saved / Considering"
    PREPARING = "PREPARING", "Preparing Materials"
    READY_FOR_REVIEW = "READY_FOR_REVIEW", "Ready for Final Review"
    READY_TO_SUBMIT = "READY_TO_SUBMIT", "Ready to Submit"
    SUBMITTED = "SUBMITTED", "Submitted"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    INTERVIEWING = "INTERVIEWING", "Interviewing / Assessment"
    OFFERED = "OFFERED", "Offered / Accepted"
    REJECTED = "REJECTED", "Not Selected"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"
    ARCHIVED = "ARCHIVED", "Archived"


class ApplicationPriority(models.TextChoices):
    LOW = "LOW", "Low Priority"
    MEDIUM = "MEDIUM", "Medium Priority"
    HIGH = "HIGH", "High Priority"
    URGENT = "URGENT", "Urgent / Immediate"


class SubmissionMethod(models.TextChoices):
    PORTAL = "PORTAL", "Online Application Portal"
    EMAIL = "EMAIL", "Email Submission"
    MANUAL_FORM = "MANUAL_FORM", "Web Form"
    DIRECT = "DIRECT", "Direct Upload / API"
    OTHER = "OTHER", "Other Submission Channel"


class DocumentRole(models.TextChoices):
    CV = "CV", "Curriculum Vitae (CV)"
    RESUME = "RESUME", "Resume"
    COVER_LETTER = "COVER_LETTER", "Cover Letter / Letter of Intent"
    TRANSCRIPT = "TRANSCRIPT", "Academic Transcript"
    PORTFOLIO = "PORTFOLIO", "Portfolio / Work Samples"
    CERTIFICATE = "CERTIFICATE", "Certificate / Accreditation"
    PROPOSAL = "PROPOSAL", "Project Proposal / Concept Note"
    RECOMMENDATION = "RECOMMENDATION", "Letter of Recommendation"
    IDENTIFICATION = "IDENTIFICATION", "Identification / Passport"
    OTHER = "OTHER", "Other Attachment"


class DocumentAttachmentStatus(models.TextChoices):
    MISSING = "MISSING", "Required / Missing"
    DRAFT = "DRAFT", "Draft in Progress"
    ATTACHED = "ATTACHED", "Attached & Ready"
    VERIFIED = "VERIFIED", "Verified & Checked"


class QuestionStatus(models.TextChoices):
    NOT_STARTED = "NOT_STARTED", "Not Started"
    IN_PROGRESS = "IN_PROGRESS", "Drafting"
    READY_FOR_REVIEW = "READY_FOR_REVIEW", "Draft Ready"
    FINAL = "FINAL", "Finalized"


class QuestionCategory(models.TextChoices):
    MOTIVATION = "MOTIVATION", "Motivation & Fit"
    TECHNICAL = "TECHNICAL", "Technical Expertise"
    EXPERIENCE = "EXPERIENCE", "Experience & Background"
    LEADERSHIP = "LEADERSHIP", "Leadership & Impact"
    PROJECT = "PROJECT", "Project Proposal"
    LOGISTICS = "LOGISTICS", "Logistics & Compensation"
    OTHER = "OTHER", "General / Other"


class NoteCategory(models.TextChoices):
    GENERAL = "GENERAL", "General Notes"
    RESEARCH = "RESEARCH", "Organization & Opportunity Research"
    CONTACT = "CONTACT", "Key Contacts & Outreach"
    INTERVIEW_PREP = "INTERVIEW_PREP", "Interview Preparation"
    FEEDBACK = "FEEDBACK", "Reviewer / Recruiter Feedback"


class ActivityType(models.TextChoices):
    CREATED = "CREATED", "Workspace Created"
    STATUS_CHANGE = "STATUS_CHANGE", "Stage Changed"
    PRIORITY_CHANGE = "PRIORITY_CHANGE", "Priority Updated"
    DOCUMENT_ATTACHED = "DOCUMENT_ATTACHED", "Document Attached"
    DOCUMENT_REMOVED = "DOCUMENT_REMOVED", "Document Removed"
    QUESTION_UPDATED = "QUESTION_UPDATED", "Question Response Updated"
    REVIEW_SIGNED_OFF = "REVIEW_SIGNED_OFF", "User Review Signed Off"
    SUBMISSION_RECORDED = "SUBMISSION_RECORDED", "Submission Recorded"
    NOTE_ADDED = "NOTE_ADDED", "Note Added"
    AI_GENERATION = "AI_GENERATION", "AI Preparation Generated"
    AI_APPLIED = "AI_APPLIED", "AI Draft Applied"


class AITone(models.TextChoices):
    STAR_METHOD = "STAR_METHOD", "STAR Method (Situation, Task, Action, Result)"
    CONCISE = "CONCISE", "Concise & Direct"
    EXECUTIVE = "EXECUTIVE", "Executive & Strategic"
    ACADEMIC = "ACADEMIC", "Academic & Research-Oriented"


class AIPrepStatus(models.TextChoices):
    NOT_STARTED = "NOT_STARTED", "Not Started"
    GENERATING = "GENERATING", "Generating"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"

