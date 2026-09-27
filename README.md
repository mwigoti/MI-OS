# MwohaOS

> Personal Opportunity Intelligence and Execution Operating System

[![Milestone](https://img.shields.io/badge/Milestone-6%3A%20AI%20Preparation-blue.svg)](#roadmap)
[![Django](https://img.shields.io/badge/Django-5.x-darkgreen.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7%2B-red.svg)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.x-green.svg)](https://docs.celeryq.dev/)

---

## 1. What it is

**MwohaOS** is a personal opportunity operating system designed to discover, extract, normalize, match, prepare, apply for, and track career and growth opportunities.

Unlike traditional job boards, MwohaOS manages multi-spectrum opportunities across an entire professional lifecycle:
- Full-time & contract jobs
- Fellowships & research grants
- Accelerators & incubator cohorts
- Scholarships & academic residencies
- Competitions, hackathons, and innovation challenges
- Consulting & freelance engagements

The end-to-end lifecycle architecture encompasses:
```text
DISCOVER → EXTRACT → NORMALIZE → DEDUPLICATE → CHECK ELIGIBILITY 
→ MATCH → EXPLAIN → PREPARE → VALIDATE → USER REVIEW 
→ AUTOMATE → USER APPROVAL → SUBMIT → TRACK → LEARN
```

---

## 2. Current Milestone

```text
Milestone 4 — Matching & Recommendations
```

Milestone 4 builds a transparent, evidence-grounded matching engine answering:

> **"How well does this opportunity align with my professional profile, and why?"**

```text
PROFILE (Experience, Education, Skills, Projects, Preferences)
      ↓
PROFILE NORMALIZATION & SNAPSHOT HASH
      ↓
OPPORTUNITY INTELLIGENCE (Structured Eligibility, Requirements, Skills)
      ↓
DETERMINISTIC ELIGIBILITY CHECK (Nationality, Location, Deadlines, Hard Constraints)
      ↓
SKILL MATCHING (Exact, Normalized Aliases, Related Competencies)
      ↓
EXPERIENCE & PROJECT EVIDENCE CORRELATION
      ↓
EDUCATION & PROFILE PREFERENCE ALIGNMENT
      ↓
DETERMINISTIC WEIGHTED SCORING & HARD OVERRIDE
      ↓
EVIDENCE-GROUNDED FACTUAL EXPLANATION
      ↓
OPPORTUNITY MATCH RECORD
```

---

## 3. Important Product Principle & Disclaimer

> **Match scores describe alignment between available profile evidence and opportunity requirements. They are not guarantees of selection, employment, funding, admission, or application success.**

MwohaOS never acts as an opaque black box claiming "AI says you are a 92% fit". Instead, it reveals:
1. Exact requirements satisfied by verified profile evidence.
2. Requirements missing or unestablished in current records.
3. Unconclusive or ambiguous requirements (distinguishing missing data from unqualified candidates).
4. Factual reasons explaining eligibility determinations.

---

## 4. Matching Dimensions & Scoring Weights

Transparent default weights summing to 100%:
- **Eligibility (25%)**: Mandatory legal/geographic constraints.
- **Required Skills (25%)**: Core technical and domain proficiencies.
- **Experience (20%)**: Cumulative verified professional years and role alignment.
- **Education (10%)**: Degree level (BSc, MSc, PhD) and field relevance.
- **Sector Alignment (8%)**: Thematic synergy (e.g., Earth Observation, Geospatial, Climate, Agriculture).
- **Opportunity Type (5%)**: Match against user target types (Fellowship, Grant, Job, Accelerator).
- **Location & Remote (5%)**: Work mode and geographic preferences.
- **Preferences (2%)**: Specific constraints and notes.

### Hard Constraint Enforcement
If explicit eligibility fails (e.g. candidate is in Kenya, but opportunity strictly requires Canadian work authorization or the deadline has passed):
- `eligibility_status` is marked **`INELIGIBLE`**.
- The overall score is capped to a **maximum of 35%**, preventing misleading recommendations regardless of technical skill alignment.

---

## 5. Data Model (`OpportunityMatch`)

One-to-one between `Profile` and `Opportunity`:
- **`match_status`**: `PENDING`, `PROCESSING`, `COMPLETED`, `PARTIAL`, `FAILED`, `STALE`.
- **`overall_score`**: Weighted 0–100 score with descriptive band labels (`Very strong alignment`, `Strong`, `Moderate`, `Partial`, `Limited`).
- **`eligibility_status`**: `ELIGIBLE`, `INELIGIBLE`, `UNCERTAIN`, `NOT_ASSESSED`.
- **Component Scores**: Separate fields for `skill_score`, `experience_score`, `education_score`, `sector_score`, `opportunity_type_score`, `location_score`, `preference_score`.
- **Breakdowns**: `required_requirements_met`, `required_requirements_missing`, `matching_skills` (with `match_type` and evidence), `matching_experience`, `matching_projects`.
- **`explanation`**: Traceable, human-readable breakdown of strengths and gaps.
- **Stale Detection Hashes**: `profile_snapshot_hash`, `opportunity_snapshot_hash`, `intelligence_snapshot_hash` ensuring matches automatically detect updates.

---

## 6. Celery Background Tasks & Management Commands

### Celery Tasks (`apps/matching/tasks.py`)
- `match_opportunity_task`: Evaluates a single profile-opportunity pair asynchronously.
- `match_pending_opportunities`: Bounded scheduled task evaluating newly ingested opportunities against active profiles.
- `rematch_stale_matches`: Recomputes matches flagged as `STALE`.
- `rematch_profile`: Recalculates all matches for a user when their profile is updated.

### Management Commands
```bash
# Match pending active opportunities
python manage.py match_opportunities --pending --limit 20

# Match single opportunity by UUID
python manage.py match_opportunities --opportunity <uuid>

# Force recalculation for all opportunities
python manage.py match_opportunities --all --force

# Recalculate match for a specific opportunity across profiles
python manage.py rematch_opportunity <opportunity_uuid>
```

---

## 7. Automated Test Suite

- `tests/test_milestone_1.py`: 17 tests (Profile, Skills, Experiences, Evidence Bank).
- `tests/test_milestone_2.py`: 16 tests (Opportunity Ingestion, Connectors, Deduplication, SSRF).
- `tests/test_milestone_3.py`: 12 tests (Opportunity Intelligence, Hosted Providers, Prompt Injection Defense).
- `tests/test_milestone_4.py`: 11 tests (Exact/Normalized/Related Skills, Hard Eligibility Constraints, Experience & Project Evidence, Degree Matching, Weighted Scoring, Idempotency, Management Commands, Dashboard & Detail Views).

Run all tests:
```bash
docker compose exec web pytest
```

---

## 8. Milestone 5 — Application Workspace

Milestone 5 provides a structured preparation, material tailoring, question answering, and review workspace for opportunities before execution:

```text
OPPORTUNITY MATCH / INBOX
      ↓
APPLICATION WORKSPACE INITIALIZATION
      ↓
REQUIRED DOCUMENTS AUTO-POPULATION (From OpportunityIntelligence)
      ↓
VAULT DOCUMENT LINKAGE & TAILORED ATTACHMENTS
      ↓
APPLICATION QUESTIONNAIRE & ESSAY DRAFTING (Limits & Counts)
      ↓
DETERMINISTIC READINESS SCORING & BLOCKER AUDITING (0–100%)
      ↓
USER REVIEW SIGNOFF & SUBMISSION RECORDING
      ↓
ACTIVITY AUDIT TRAIL
```

### Key Capabilities
- **Lifecycle Stages**: `SAVED`, `PREPARING`, `READY_FOR_REVIEW`, `READY_TO_SUBMIT`, `SUBMITTED`, `UNDER_REVIEW`, `INTERVIEWING`, `OFFERED`, `REJECTED`, `WITHDRAWN`, `ARCHIVED`.
- **Auto-Populated Materials**: Evaluates `OpportunityIntelligence.required_documents` to generate required attachment slots and auto-links verified primary documents from the user's Document Vault.
- **Application Questionnaire**: Structured prompt management with category tagging, draft status, and strict real-time character/word limit enforcement.
- **Deterministic Readiness Engine**: Evaluates mandatory document attachments, question answers, overdue deadlines, and explicit user signoff into an explainable 0–100% readiness score with submission blockers.
- **Submission Verification**: Records submission timestamps, official portal confirmation IDs, submission method, and follow-up notes.
- **Audit Logging**: Comprehensive `ApplicationActivity` log tracking all stage changes, uploads, and edits.

---

## 9. Automated Test Suite

- `tests/test_milestone_1.py`: 17 tests (Profile, Skills, Experiences, Evidence Bank).
- `tests/test_milestone_2.py`: 16 tests (Opportunity Ingestion, Connectors, Deduplication, SSRF).
- `tests/test_milestone_3.py`: 12 tests (Opportunity Intelligence, Hosted Providers, Prompt Injection Defense).
- `tests/test_milestone_4.py`: 11 tests (Skills Matching, Hard Constraints, Evidence Corroboration, Scoring).
- `tests/test_milestone_5.py`: 10 tests (Workspace Init, Auto-Populated Documents, Lifecycle Transitions, Readiness Engine, Word Limits, Isolation, Management Command).
- `tests/test_milestone_6.py`: 10 tests (Evidence Grounding, Anti-Hallucination Audit, Tailored Cover Letter, CV Tailoring & ATS Alignment, STAR Question Answering, Word/Char Limits, Version History & Rollback, Prompt Injection Boundaries, Management Command, Access Isolation).

Run all tests:
```bash
docker compose exec web pytest
```

---

## 10. Milestone 6 — AI Preparation

Milestone 6 builds an evidence-grounded AI preparation studio synthesizing tailored application materials with zero hallucinations:

```text
OPPORTUNITY INTELLIGENCE + CANDIDATE PROFILE EVIDENCE
                      ↓
INJECTION-SAFE BOUNDARY ENCAPSULATION & ANTI-HALLUCINATION AUDIT
                      ↓
      ┌───────────────┼───────────────┐
      ↓               ↓               ↓
TAILORED COVER    CV TAILORING &    STRUCTURED QUESTION
LETTER ENGINE     ATS OPTIMIZATION  ANSWERING (STAR METHOD)
      ↓               ↓               ↓
DOCUMENT VERSION  MATCH COVERAGE &  STRICT WORD & CHAR
HISTORY & DIFFS   SELECTED PROJECTS LIMIT ENFORCEMENT
      └───────────────┬───────────────┘
                      ↓
WORKSPACE DOCUMENT ATTACHMENT & READINESS ENGINE RECALCULATION
                      ↓
ACTIVITY AUDIT LOG (AI_GENERATION) & USER REVIEW WORKSPACE
```

### Key Capabilities
- **Strict Evidence Grounding & Anti-Hallucination**: Materials cite only verified facts from candidate profile records (skills, experiences, projects, degrees).
- **Prompt Injection Defense**: Boundary markers (`BEGIN UNTRUSTED OPPORTUNITY CONTENT` / `BEGIN CANDIDATE PROFILE EVIDENCE`) safeguard LLM execution.
- **Tailored Cover Letter Synthesis**: Role-specific opening, core technical alignment, quantified achievement proof, and professional closing with version history and 1-click rollback.
- **CV Tailoring & ATS Optimization**: Targeted summary, prioritized skill rankings (exact vs related), tailored accomplishment bullets with action verbs, and ATS keyword match scoring.
- **STAR Framework Question Answering**: Situation, Task, Action, Result structured answers with guaranteed compliance to strict word and character limits.
- **Interactive AI Studio UI & CLI Management**: Dedicated preparation studio tab and `python manage.py ai_prep_application --application <uuid> --all` CLI command.

---

## 11. Roadmap

```text
Milestone 0  — Foundation                                  [COMPLETE]
Milestone 1  — Professional Profile & Evidence System     [COMPLETE]
Milestone 2  — Opportunity Discovery & Ingestion          [COMPLETE]
Milestone 3  — Intelligence & AI-Assisted Extraction      [COMPLETE]
Milestone 4  — Matching & Recommendations                 [COMPLETE]
Milestone 5  — Application Workspace                      [COMPLETE]
Milestone 6  — AI Preparation                              [COMPLETE]
Milestone 7  — Browser Agent                              [NEXT]
Milestone 8  — Submission Engine
Milestone 9  — Tracking & Status
Milestone 10 — Communication Intelligence
Milestone 11 — Opportunity Intelligence
Milestone 12 — Personal Agent
```

