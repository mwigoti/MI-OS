# MwohaOS

> Personal Opportunity Intelligence and Execution Operating System

[![Milestone](https://img.shields.io/badge/Milestone-1%3A%20Profile%20%26%20Evidence-blue.svg)](#roadmap)
[![Django](https://img.shields.io/badge/Django-5.x-darkgreen.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7%2B-red.svg)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.x-green.svg)](https://docs.celeryq.dev/)

---

## 1. What it is

**MwohaOS** is a personal opportunity operating system designed to discover, extract, normalize, match, prepare, apply for, and track career and growth opportunities.

Unlike traditional job boards or generic ATS application extensions, MwohaOS is structured around the unified concept of an **Opportunity**—spanning:
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
Milestone 1 — Professional Profile & Evidence System
```

Milestone 1 establishes the **professional source of truth** used by future opportunity matching and application generation systems. 

### Core Architectural Principle
The user's professional identity is represented as **structured, factual, evidence-backed data**. Every professional claim is traceable to primary sources:
```text
CLAIM
  ↓
EVIDENCE
  ↓
SOURCE (Document / Repository / URL / Institutional Record)
```

No AI reasoning, hallucinated claims, or speculative proficiency guessing is allowed. The user has complete, deterministic control over their data.

---

## 3. Architecture & Data Models

MwohaOS follows a **Django modular monolith** architecture. All profile and evidence subsystems are organized into discrete apps:

```text
User (Authentication & Credentials)
 │
 └── Profile (Root Anchor for Career Identity)
      ├── Skills (Technical, Geospatial, AI/ML, Domain proficiencies)
      ├── Experiences (Employment, roles, and quantified outcomes)
      ├── Education (Academic credentials and degrees)
      ├── Projects (Applied deliverables, repositories, demos, and impact)
      ├── Achievements (Awards, honors, fellowships, and competition wins)
      ├── Certifications (Industry accreditations and credential IDs)
      ├── Publications (Journals, preprints, conference papers, DOIs)
      ├── Languages (Spoken and written proficiencies)
      ├── Preferences (Target opportunity types, sectors, work modes)
      ├── Versions (Audit log of profile state changes)
      ├── Documents (Secure Vault: CVs, resumes, transcripts, certs)
      └── Evidence Bank (Verifiable proof connecting claims to sources)
```

### Discrete Apps
- **`apps.profiles`**: Core profile entities, deterministic completeness engine, CRUD views, and evidence bank.
- **`apps.documents`**: Isolated document vault, path sanitization, MIME/size validation, and authorized file streaming.
- **`apps.accounts`**: User authentication, sessions, and timezone settings.
- **`apps.core`**: Health checks, abstract base models (`TimeStampedModel`), and logging.

---

## 4. Evidence Architecture

The **Evidence Bank** (`apps.profiles.models.Evidence`) substantiates assertions made on applications:
- **Direct Relations:** Explicit foreign keys link evidence to `Project`, `Experience`, `Education`, `Achievement`, `Certification`, and `Document` records.
- **Source Verification:** Supports direct URLs (e.g. GitHub repos, DOI links, demo servers, validation portals) and attached vault documents.
- **Verification States:** Safe default of `verified=False` until explicit validation notes and confirmation are recorded by the user.

---

## 5. Document Security Vault

Uploaded documents (resumes, academic transcripts, government IDs) are strictly protected:
- **Unguessable Paths:** Files are uploaded to isolated directory structures (`documents/user_<user_id>/<uuid>_<clean_filename>`).
- **Authorization Barrier:** Documents are not served through public static directories. The `/documents/<pk>/download/` endpoint strictly enforces that `request.user.profile == document.profile`.
- **Validation:** File uploads are limited to 10MB and restricted to allowed extensions (`.pdf`, `.docx`, `.txt`, `.rtf`, `.png`, `.jpg`, `.jpeg`, `.webp`).

---

## 6. Deterministic Profile Completeness

Profile completeness is calculated deterministically across 10 structured dimensions (weighted 0–100%):
- **Identity & Summary** (10%)
- **Contact & Links** (10%)
- **Experience** (15%)
- **Education** (10%)
- **Skills** (15%)
- **Projects** (15%)
- **Achievements & Certifications** (5%)
- **Documents** (10%)
- **Evidence Bank** (10%)
- **Preferences** (5%)

---

## 7. URL Routes

### Profile Subsystem (`/profile/`)
- `GET  /profile/` — Overview dashboard with completeness score and section snapshots
- `GET  /profile/edit/` — Update headline, summary, links, and work authorization
- `GET/POST /profile/skills/` — Skills inventory (`/skills/add/`, `/<pk>/edit/`, `/<pk>/delete/`)
- `GET/POST /profile/experience/` — Work history (`/experience/add/`, `/<pk>/edit/`, `/<pk>/delete/`)
- `GET/POST /profile/education/` — Education records (`/education/add/`, `/<pk>/edit/`, `/<pk>/delete/`)
- `GET/POST /profile/projects/` — Tangible projects (`/projects/add/`, `/<pk>/edit/`, `/<pk>/delete/`)
- `GET/POST /profile/achievements/` — Awards & honors (`/achievements/add/`, `/<pk>/edit/`, `/<pk>/delete/`)
- `GET/POST /profile/certifications/` — Accreditations (`/certifications/add/`, `/<pk>/edit/`, `/<pk>/delete/`)
- `GET/POST /profile/publications/` — Papers & preprints (`/publications/add/`, `/<pk>/edit/`, `/<pk>/delete/`)
- `GET/POST /profile/languages/` — Language competencies (`/languages/add/`, `/<pk>/edit/`, `/<pk>/delete/`)
- `GET/POST /profile/preferences/` — Target opportunity criteria & sector constraints
- `GET/POST /profile/evidence/` — Evidence bank & claim verification (`/evidence/add/`, `/<pk>/edit/`, `/<pk>/delete/`, `/<pk>/toggle-verify/`)

### Document Vault (`/documents/`)
- `GET  /documents/` — Document vault catalog with search and type filtering
- `POST /documents/upload/` — Secure upload form with size and extension validation
- `GET  /documents/<pk>/download/` — Authorized file streaming (User B cannot download User A's files)
- `POST /documents/<pk>/delete/` — Delete document record and purge stored file

---

## 8. Quickstart & Installation

### Step 1: Configure Environment
```bash
cp .env.example .env
```

### Step 2: Build & Start Services
```bash
docker compose up --build -d
```
Or via Makefile:
```bash
make setup
```

### Step 3: Run Migrations & Create Superuser
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### Step 4: Run Automated Tests
```bash
docker compose exec web pytest
```

---

## 9. Automated Test Suite

The automated test suite in `tests/` verifies:
- **Profile & Ownership:** Profile creation, editing, and version logging.
- **Skills CRUD:** Creation, update, duplicate prevention, and cross-user isolation.
- **Date Validation:** Enforces `end_date >= start_date` for experiences, education, and certifications.
- **Document Security:** Enforces allowed file extensions, file size limits, and verifies that User A cannot download User B's documents (HTTP 404).
- **Evidence Bank:** Relations to projects, experiences, and verification toggles.
- **Completeness:** Deterministic score computation on empty vs fully documented profiles.

---

## 10. Roadmap

```text
Milestone 0  — Foundation                                  [COMPLETE]
Milestone 1  — Professional Profile & Evidence System     [COMPLETE]
Milestone 2  — Opportunity Discovery & Ingestion          [NEXT]
Milestone 3  — Intelligence & Normalization
Milestone 4  — Matching & Scoring
Milestone 5  — Application Workspace
Milestone 6  — AI Preparation
Milestone 7  — Browser Agent
Milestone 8  — Submission Engine
Milestone 9  — Tracking & Status
Milestone 10 — Communication Intelligence
Milestone 11 — Opportunity Intelligence
Milestone 12 — Personal Agent
```
