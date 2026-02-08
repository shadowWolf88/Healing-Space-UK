# HEALING SPACE UK - MASTER ROADMAP
## Complete Priority-Ordered Development Plan
### Audit #2: February 8, 2026 | Full 7-Phase Codebase Audit

---

## AUDIT ITERATION LOG

| Audit # | Date | Tier 0 | Tier 1 | Tier 2 | Total | Fixed | New |
|---------|------|--------|--------|--------|-------|-------|-----|
| 1 | Feb 8, 2026 | 7 | 10 | 7 | 60+ | N/A | N/A |
| 2 | Feb 8, 2026 | 11 | 14 | 10 | 85+ | 0 | 25+ |

---

## PROJECT STATUS SNAPSHOT

| Metric | Value |
|--------|-------|
| **Backend** | api.py - 16,163 lines, Flask/PostgreSQL/Groq AI |
| **Frontend** | index.html - 16,687 lines, monolithic SPA (762KB) |
| **Supporting Modules** | 16 Python files, 2 JS files, 3 SQL schemas, 43 DB tables |
| **Test Coverage** | 12/13 passing (92%) - but major gaps in clinical features |
| **Security CVSS** | CRITICAL - live credentials exposed in git repo |
| **NHS Readiness** | 0/8 mandatory compliance items complete |
| **Clinical Features** | Schema exists, C-SSRS scoring non-standard, dashboard broken |
| **Files flagged for removal** | .env (live secrets), 33MB pandoc.deb, 4MB debug APK, 12 .db.bak files, signup_audit.log, cleanenv/ |

---

## TIER 0: CRITICAL SECURITY FIXES (Do Before ANYTHING Else)
> These are active vulnerabilities that could compromise patient safety or data

### 0.0 [NEW] LIVE CREDENTIALS EXPOSED IN GIT REPO
- **File**: .env (committed to repo despite .gitignore)
- **Exposed**: Railway PostgreSQL password (`cUXPYyAvRGZkgOeGXVmbnvUWjWwokeCY`), Groq API key (`gsk_5fphPggq...`), Encryption key, DB connection string
- **Risk**: Anyone who clones repo gets FULL production database access to all patient health data
- **Fix**: IMMEDIATELY rotate ALL credentials on Railway; scrub .env from git history with `git filter-repo`; verify .gitignore is working
- **Effort**: 2 hours (EMERGENCY)
- **Status**: NOT STARTED

### 0.1 Authentication Bypass via X-Username Header
- **File**: api.py:3711-3717
- **Risk**: Complete auth bypass if DEBUG=true in production
- **Fix**: Remove X-Username fallback entirely; enforce session-only auth
- **Effort**: 1 hour

### 0.2 Hardcoded Database Credentials
- **File**: api.py:93, api.py:2056
- **Risk**: `healing_space_dev_pass` visible in source/git history
- **Fix**: Remove all fallback passwords; require env vars; rotate credentials
- **Effort**: 1 hour

### 0.3 Weak SECRET_KEY Generation
- **File**: api.py:150-159
- **Risk**: SECRET_KEY derived from hostname (predictable); sessions forgeable
- **Fix**: Generate cryptographically random key; persist in env; fail-closed if missing
- **Effort**: 1 hour

### 0.4 SQL Syntax Errors in training_data_manager.py
- **File**: training_data_manager.py (9 instances - lines 94, 146, 154-156, 217, 281-282, 343-345, 367, 384)
- **Risk**: Duplicate `%s` placeholders cause crashes on any training data operation
- **Fix**: Audit and fix all SQL statements; add integration tests
- **Effort**: 3 hours

### 0.5 CBT Tools Hardcoded to SQLite (Non-Functional in Production)
- **Files**: cbt_tools/models.py, cbt_tools/routes.py
- **Risk**: Module uses `sqlite3.connect()` but app runs PostgreSQL; completely broken
- **Fix**: Migrate to PostgreSQL with `%s` params; fix deprecated `before_app_first_request`
- **Effort**: 4 hours

### 0.6 Activity Tracking Without Consent (GDPR Violation)
- **File**: static/js/activity-logger.js
- **Risk**: Tracks ALL clicks, tab changes, visibility without consent dialog
- **Fix**: Add consent check before initialization; provide opt-out; document retention
- **Effort**: 3 hours

### 0.7 Prompt Injection in TherapistAI
- **File**: api.py:2101-2310
- **Risk**: User-controlled fields (stressors, family, diagnoses, mood_narrative) injected directly into system prompt without sanitization
- **Fix**: Escape/quote all user context; add prompt injection detection; validate history message roles
- **Effort**: 6 hours

**TIER 0 TOTAL: ~19 hours**

---

## TIER 1: PRODUCTION BLOCKERS (Required Before Any Real Users)
> Structural issues that make the app unsafe or non-functional for clinical use

### 1.1 Fix Clinician Dashboard (20+ Broken Features)
- **Source**: docs/DEV_TO_DO.md - documented by developer
- **Broken items**: AI summary, charts tab, patient profile, mood logs, assessments, therapy history, alerts, appointment booking
- **Fix**: Systematically debug each feature; add test coverage per feature
- **Effort**: 20-25 hours

### 1.2 CSRF Protection - Apply Consistently
- **File**: api.py:351-380
- **Risk**: Only 1 endpoint uses `@CSRFProtection.require_csrf`; DEBUG mode disables CSRF entirely
- **Fix**: Apply CSRF decorator to ALL state-changing endpoints; remove DEBUG bypass
- **Effort**: 4 hours

### 1.3 Rate Limiting on Critical Endpoints
- **File**: api.py:168-174
- **Missing on**: Login (brute force), registration (spam), password reset (enumeration), clinical assessments
- **Fix**: Add per-endpoint rate limits; switch from fixed-window to sliding-window; add user-based limiting
- **Effort**: 4 hours

### 1.4 Input Validation Consistency
- **File**: api.py (InputValidator class exists at line 181 but rarely used)
- **Missing on**: Mood values (no range check), sleep values, exercise minutes, email format, phone numbers
- **Fix**: Apply InputValidator to ALL endpoints; add type/range validation for clinical data
- **Effort**: 8 hours

### 1.5 Session Management Hardening
- **File**: api.py:147-165
- **Issues**: 30-day session lifetime (too long for health data), no session rotation on login, no concurrent session controls, no inactivity timeout
- **Fix**: Reduce to 7 days max; rotate session ID on login; add 30-min inactivity timeout; invalidate sessions on password change
- **Effort**: 6 hours

### 1.6 Error Handling & Debug Cleanup
- **Files**: api.py (100+ bare `except Exception: pass`), audit.py, secrets_manager.py
- **Risk**: Silent failures hide bugs and security issues; debug print statements expose usernames/params in logs
- **Fix**: Replace bare exceptions with specific handlers; remove debug prints; add structured logging (Python logging module)
- **Effort**: 10 hours

### 1.7 Broken Access Control on Professional Endpoints
- **File**: api.py:10189-10221
- **Risk**: `/api/professional/ai-summary` takes `clinician_username` from request body (forgeable)
- **Fix**: Always derive clinician identity from session; never trust request body for identity
- **Effort**: 4 hours

### 1.8 XSS via innerHTML (138 Instances in Frontend)
- **File**: templates/index.html
- **Risk**: User-generated content (community posts, messages, pet names, safety plan entries) rendered via innerHTML
- **Fix**: Use textContent for user data; sanitize with DOMPurify for rich content; audit all 138 innerHTML uses
- **Effort**: 12 hours

### 1.9 Database Connection Pooling
- **File**: api.py (100+ individual `get_db_connection()` calls without pooling)
- **Risk**: Connection exhaustion under load; no connection reuse
- **Fix**: Implement psycopg2.pool.ThreadedConnectionPool; use context managers
- **Effort**: 6 hours

### 1.10 Anonymization Salt Hardcoded
- **File**: training_data_manager.py
- **Risk**: Default salt in source code undermines anonymization
- **Fix**: Generate random salt on first run; store securely; document rotation
- **Effort**: 2 hours

**TIER 1 TOTAL: ~76-81 hours**

---

## TIER 2: CLINICAL FEATURE COMPLETION (Required for Clinical Deployment)
> Features that have schema/docs but missing implementation

### 2.1 C-SSRS Assessment - Backend Implementation
- **Status**: Database schema exists (8 tables), frontend UI exists, NO API endpoints
- **Tables ready**: risk_assessments, risk_alerts, risk_keywords, crisis_contacts, risk_reviews, enhanced_safety_plans, ai_monitoring_consent
- **Need**: POST/GET/PUT endpoints for assessment CRUD, scoring algorithm, clinician notification
- **Clinical requirement**: Scoring must be validated against published C-SSRS protocol
- **Effort**: 20-30 hours

### 2.2 Crisis Alert System
- **Status**: CRISIS_RESPONSE_PROTOCOL.md documents 3-tier alert system; NO code implements it
- **Need**: Real-time alert pipeline (within 1 minute for critical), email/SMS/webhook notifications, clinician acknowledgment tracking, escalation if unacknowledged
- **Effort**: 15-20 hours

### 2.3 Safety Planning Workflow
- **Status**: Frontend has safety plan builder; backend storage incomplete
- **Need**: Full CRUD for safety plans, versioning, clinician review workflow, safety plan enforcement (require plan after high-risk assessment)
- **Effort**: 10-15 hours

### 2.4 Treatment Goals Module
- **Status**: Listed in roadmap, NOT started
- **Need**: SMART goal creation, progress tracking, clinician collaboration, milestone celebrations
- **Effort**: 15-20 hours

### 2.5 Session Notes & Homework
- **Status**: Listed in roadmap, NOT started
- **Need**: Clinician session note templates, homework assignment/tracking, patient acknowledgment, outcome measurement
- **Effort**: 18-24 hours

### 2.6 CORE-OM/ORS Outcome Measures
- **Status**: Listed in roadmap, NOT started
- **Need**: Validated outcome measurement tools, pre/post comparison, clinical change detection, graphing
- **Effort**: 12-18 hours

### 2.7 Relapse Prevention Planning
- **Status**: Listed in roadmap, NOT started
- **Need**: Relapse warning signs tracker, early intervention triggers, maintenance plan, support network mapping
- **Effort**: 16-20 hours

**TIER 2 TOTAL: ~106-147 hours**

---

## TIER 3: COMPLIANCE & GOVERNANCE (Required for NHS/University Deployment)
> Regulatory requirements that BLOCK deployment

### 3.1 Clinical Governance Structure
- **Status**: NHS_COMPLIANCE_FRAMEWORK.md documents requirements; NONE in place
- **Need**: Recruit Clinical Lead (OVERDUE - was due Feb 10), appoint DPO, ISS Officer, Patient Safety Lead
- **Effort**: Ongoing organizational (not code)

### 3.2 Legal Review & Insurance
- **Status**: NOT started (was due Feb 14)
- **Need**: NHS solicitor engagement, Professional Indemnity Insurance, Data Processing Agreements
- **Effort**: Ongoing organizational

### 3.3 Ethics Approval
- **Status**: DPIA is DRAFT; Clinical Safety Case unsigned; no REC submission
- **Need**: Finalize DPIA with DPO sign-off, complete Clinical Safety Case, submit to Research Ethics Committee
- **Effort**: 20-30 hours documentation + review cycles

### 3.4 GDPR Implementation Gaps
- **Current gaps**:
  - No comprehensive data export (Article 20) - missing AI insights, clinician notes, risk assessments from export
  - No data retention policies enforced (chat history indefinite)
  - No breach notification mechanism
  - Consent tracking only for training data (not activity tracking, clinician access, research)
  - PII stripping patterns only cover en-US formats (need UK formats)
- **Fix**: Implement auto-deletion schedules, comprehensive export, consent management UI, breach logging
- **Effort**: 20-30 hours

### 3.5 Field-Level Encryption for Sensitive Data
- **Status**: Fernet encryption available but not applied to clinical data
- **Need**: Encrypt at rest: C-SSRS responses, therapy chat content, diagnoses, safety plans
- **Effort**: 15-20 hours

### 3.6 Comprehensive Audit Logging
- **Status**: audit.py exists but silently swallows exceptions
- **Need**: Structured logging (who accessed what data when), 7-year retention, tamper-evident logs, regulatory reporting capability
- **Effort**: 10-15 hours

### 3.7 CI/CD Pipeline
- **Status**: No automated testing/deployment pipeline
- **Need**: GitHub Actions for linting, tests, security scans (pip-audit, bandit), automated staging deployment, test coverage reporting
- **Effort**: 8-12 hours

**TIER 3 TOTAL: ~73-107 hours (code) + ongoing organizational work**

---

## TIER 4: ARCHITECTURE & QUALITY (Production Maturity)
> Technical debt and architecture improvements for long-term sustainability

### 4.1 Frontend Architecture Refactor
- **Current**: 15,800-line monolithic HTML file with all JS/CSS inline
- **Need**: Component-based architecture (React/Vue/Svelte or Web Components), CSS modules, bundling (Vite/webpack), code splitting
- **Impact**: Maintainability, performance, testability, developer experience
- **Effort**: 80-120 hours (major refactor)

### 4.2 Backend Modularization
- **Current**: 13,600-line api.py monolith
- **Need**: Flask blueprints per domain (auth, therapy, clinical, community, admin), service layer, repository pattern, proper ORM (SQLAlchemy)
- **Impact**: Maintainability, testability, onboarding new developers
- **Effort**: 60-80 hours

### 4.3 Test Coverage Expansion
- **Current**: 12/13 tests passing, but NO tests for: C-SSRS, crisis response, safety planning, clinician dashboard, GDPR operations
- **Need**: Unit tests for all clinical logic, integration tests for critical flows, E2E tests for user journeys, target >90% coverage on critical paths
- **Effort**: 40-60 hours

### 4.4 Database Schema Cleanup
- **Issues**: Inconsistent timestamp columns (entrestamp vs entry_timestamp vs created_at), TEXT fields for JSON data (should be JSONB), username as PK instead of UUID, no soft delete on all tables, denormalized like counts
- **Fix**: Migration to normalize naming, add proper types, implement UUID PKs
- **Effort**: 20-30 hours

### 4.5 API Documentation
- **Current**: No OpenAPI/Swagger documentation
- **Need**: Auto-generated API docs, request/response schemas, authentication docs, rate limit docs
- **Effort**: 10-15 hours

### 4.6 Remove Dead Code & Unused Modules
- **Dead code identified**: fhir_export.py (deprecated), ai_trainer.py (non-functional SQLite), cbt_tools/utils.py (unused), training_config.py (unclear purpose), multiple fix_*.py scripts, 30+ orphaned .md files in root
- **Fix**: Archive or delete; clean requirements.txt (remove customtkinter, pygame, plyer)
- **Effort**: 4-6 hours

### 4.7 Performance Optimization
- **Issues**: N+1 query patterns (patient detail endpoint runs 5+ queries), no pagination on list endpoints, safety_monitor regex performance, no caching layer, 762KB page load
- **Fix**: Query optimization with JOINs/CTEs, add pagination, add Redis cache for frequent reads, lazy-load frontend tabs
- **Effort**: 20-30 hours

**TIER 4 TOTAL: ~234-341 hours**

---

## TIER 5: FEATURE ENHANCEMENTS (Competitive Advantage)
> Features that elevate the app beyond basic functionality

### 5.1 Accessibility (WCAG 2.1 AA)
- **Current**: 290+ interactive elements missing ARIA labels, no keyboard navigation, no focus management in modals, no skip links, contrast failures on secondary text
- **Need**: Full WCAG audit and remediation, screen reader testing (NVDA/JAWS), keyboard navigation throughout
- **Effort**: 30-40 hours

### 5.2 Multi-Language Support (i18n)
- **Status**: Not started
- **Need**: Translation framework, RTL support, locale-aware date/number formatting, clinical terminology translation review
- **Effort**: 20-30 hours

### 5.3 Native Mobile Apps
- **Status**: Capacitor config exists, debug APK generated, but not production-ready
- **Need**: iOS + Android builds, push notifications, offline mode, biometric auth
- **Effort**: 6-8 weeks

### 5.4 Advanced AI Features
- **Ideas**:
  - Sentiment trend analysis over time
  - Predictive risk modeling (early warning)
  - Personalized coping strategy recommendations
  - Natural language understanding for mood logging
  - AI-powered session summaries for clinicians
  - Therapeutic alliance measurement
- **Effort**: 40-60 hours

### 5.5 Enhanced Community Features
- **Ideas**:
  - AI-powered content moderation
  - Peer support matching
  - Group therapy coordination
  - Resource library with clinician-curated content
  - Anonymous mode for sensitive topics
- **Effort**: 30-40 hours

### 5.6 Integration Ecosystem
- **Ideas**:
  - NHS Spine integration (patient demographics)
  - GP Connect (appointment sharing)
  - Electronic Health Record (EHR) export/import
  - Wearable device data (Fitbit, Apple Health)
  - External crisis helpline API integration
  - Calendar sync (Google Calendar, Outlook)
- **Effort**: 40-60 hours

### 5.7 Trauma-Informed Design Improvements
- **Current gaps**: Alert() used for errors (jarring), auto-advance on C-SSRS (removes agency), artificial AI thinking delay (patronizing to some), crisis messaging could be warmer
- **Need**: Grounding exercises accessible from anywhere, content warnings before sensitive topics, user-controlled pacing, customizable UI (colors, fonts, density), session wind-down prompts
- **Effort**: 15-20 hours

### 5.8 Offline & Progressive Web App (PWA)
- **Need**: Service worker for offline access, local data sync, install prompt, background sync for mood logs
- **Effort**: 15-20 hours

### 5.9 Analytics & Reporting Dashboard
- **Need**: Admin analytics (usage patterns, engagement metrics, outcome trends), clinician caseload reports, organizational compliance reports, exportable summaries
- **Effort**: 20-30 hours

### 5.10 Video/Voice Therapy Sessions
- **Need**: WebRTC integration, session recording (with consent), transcription, AI-assisted note-taking
- **Effort**: 40-60 hours

**TIER 5 TOTAL: ~256-368 hours**

---

## TIER 6: INFRASTRUCTURE & OPERATIONS
> DevOps, monitoring, and operational excellence

### 6.1 Monitoring & Alerting
- **Need**: Application performance monitoring (APM), error tracking (Sentry), uptime monitoring, database performance dashboards, clinical alert delivery confirmation
- **Effort**: 10-15 hours

### 6.2 Backup & Disaster Recovery
- **Need**: Automated database backups (hourly), point-in-time recovery, tested restore procedures, geo-redundancy for NHS
- **Effort**: 8-12 hours

### 6.3 Load Testing
- **Need**: Define capacity requirements, load test critical paths (chat, mood logging, assessments), identify breaking points, document scaling strategy
- **Effort**: 8-12 hours

### 6.4 Security Hardening
- **Need**: Regular dependency scanning, penetration testing, security headers (CSP, HSTS, X-Frame-Options), certificate pinning for mobile, vulnerability disclosure program
- **Effort**: 15-20 hours

### 6.5 Documentation Site
- **Need**: Consolidated docs site (MkDocs/Docusaurus), user guides, clinician training materials, API reference, architecture decision records
- **Effort**: 15-20 hours

**TIER 6 TOTAL: ~56-79 hours**

---

## GRAND TOTAL ESTIMATE

| Tier | Description | Hours | Priority |
|------|-------------|-------|----------|
| **0** | Critical Security Fixes | ~19 | **THIS WEEK** |
| **1** | Production Blockers | ~76-81 | **Next 2-3 weeks** |
| **2** | Clinical Feature Completion | ~106-147 | **Next 1-2 months** |
| **3** | Compliance & Governance | ~73-107 + org work | **Next 2-3 months** |
| **4** | Architecture & Quality | ~234-341 | **Next 3-6 months** |
| **5** | Feature Enhancements | ~256-368 | **Next 6-12 months** |
| **6** | Infrastructure & Operations | ~56-79 | **Ongoing** |
| **TOTAL** | | **~820-1,142 hours** | **6-12 months** |

---

## RECOMMENDED EXECUTION ORDER (Week by Week)

### Week 1 (Feb 8-14): Emergency Security
- [ ] Tier 0: All critical security fixes (19 hours)
- [ ] Start: Clinical governance recruitment

### Week 2-3 (Feb 15-28): Stabilization
- [ ] Tier 1.1: Fix clinician dashboard (20-25 hours)
- [ ] Tier 1.2-1.5: CSRF, rate limiting, validation, sessions (22 hours)

### Week 4-5 (Mar 1-14): Hardening
- [ ] Tier 1.6-1.10: Error handling, access control, XSS, DB pooling, anonymization (34 hours)
- [ ] Tier 4.6: Remove dead code (4-6 hours)

### Month 2-3 (Mar 15 - Apr 30): Clinical Features
- [ ] Tier 2.1-2.3: C-SSRS, crisis alerts, safety planning (45-65 hours)
- [ ] Tier 3.3-3.4: Ethics prep, GDPR fixes (40-60 hours)

### Month 3-4 (May - Jun): Compliance
- [ ] Tier 2.4-2.7: Treatment goals, session notes, outcomes, relapse prevention (61-82 hours)
- [ ] Tier 3.5-3.7: Encryption, audit logging, CI/CD (33-47 hours)

### Month 4-8 (Jul - Oct): Architecture
- [ ] Tier 4.1-4.5: Frontend refactor, backend modularization, tests, schema, API docs
- [ ] Tier 5.1-5.2: Accessibility, i18n

### Month 8-12 (Nov - Feb 2027): Enhancement
- [ ] Tier 5.3-5.10: Mobile apps, AI features, community, integrations
- [ ] Tier 6: Full infrastructure & operations

---

## KEY CONTRADICTIONS FOUND IN AUDIT

| # | Contradiction | Impact |
|---|--------------|--------|
| 1 | README says "Clinician Features: Complete" but DEV_TO_DO lists 20+ broken features | Stakeholders misled about readiness |
| 2 | ROADMAP Phase 4 = Clinical Features (not started) vs ACTIVE_STATUS Phase 4 = Database Constraints (complete) | Naming collision causes confusion |
| 3 | Privacy panel says conversations NOT used for training, but training_data_manager.py collects them (with consent) | User trust issue |
| 4 | C-SSRS has schema (8 tables) + docs + frontend UI, but no backend endpoints | Feature appears complete but isn't |
| 5 | NHS compliance blocking items were due Feb 10-17, none are started | Timeline slipping without acknowledgment |

---

*This roadmap was generated from a full codebase audit of every file in the project. It should be re-run after each major milestone to track progress and discover new issues.*
