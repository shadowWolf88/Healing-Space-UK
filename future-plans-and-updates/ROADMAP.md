# Roadmap: Mobile App + Backend + Website Parity

Last updated: 2026-01-25
Branch: app-development-branch (created from Milestone-B-"DEV-options---trials-ready)")

Purpose
- Produce a clear, actionable plan to implement a cross-platform mobile app (Flutter) and a production-ready backend that reuses the Milestone‑B Python code and preserves all website features.
- Keep all changes isolated to this branch so the live Railway deployment on main is unaffected.

High-level recommendation
- Wrap the existing Python chatbot logic in a FastAPI backend (containerized) deployed from this branch to a non-Railway host (Render, Fly, or Cloud Run).
- Build a single cross-platform mobile client in Flutter that connects to the backend using REST + WebSocket or SSE for streaming responses.
- Leave main and the live Railway deployment untouched; develop and deploy from app-development-branch until ready to merge.

Repository audit (preliminary)
- Key files identified in Milestone‑B branch:
  - api.py — Core Python API/web entrypoint (large, ~215KB). Likely contains chat logic and request handling.
  - ai_trainer.py, train_model.py, training_data_manager.py, training_config.py — training & data management tools.
  - therapist_app.db — local database used for development or clinician tooling.
  - templates/ — web UI templates (empty in listing, but referenced).
  - .railway_deploy, railway.toml, RAILWAY_* files — Railway deployment config and documentation.
  - Various docs (ANDROID_APP_GUIDE.md, CLINICIAN_FEATURES_2025.md, FEATURE_STATUS.md) — useful requirements and feature definitions.
  - scripts and setup scripts — developer tooling.

Note: this is a preliminary audit from the branch listing. A full, file-by-file audit will be performed as part of the first implementation PR.

Scope: Website features to keep working
All features currently available on the website must continue to work after backend refactor. Based on repository artifacts and docs, ensure the following are preserved:
- Chat core: send/receive messages, conversation history, threads.
- Streaming responses: progressive token streaming to clients.
- Model selection and trial options UI/logic.
- Authentication and 2FA (2FA_SETUP.md present).
- Reminders/mood tracking features (send_mood_reminders.sh).
- Training/export pipelines (export_training_data.py, fhir_export.py).
- Clinician features (CLINICIAN_FEATURES_2025.md) such as clinician dashboards and exports.
- Admin/audit tooling (audit.py, test_anonymization.py).
- File attachments and secure transfer (secure_transfer.py).

Implementation plan (concrete tasks)
Phase 0 — Preparation (1–3 days)
- Create this branch (done): app-development-branch from Milestone‑B.
- Add this roadmap folder (done).
- Run the existing code locally to confirm current website behavior and tests. Record any runtime issues.

Phase 1 — Full code audit & minimal refactor (3–7 days)
- Task 1.1: File-by-file audit and mapping: identify which functions in api.py implement web endpoints and which parts are CLI/training-only.
- Task 1.2: Extract/chat logic into a clear module (chat_core.py) if necessary, leaving a thin web adapter.
- Task 1.3: Create a model adapter layer (adapters/) with a Groq adapter (adapters/groq_adapter.py) now and a therapy adapter placeholder for later.
- PR: Refactor api.py into api/ with FastAPI app structure (routes, models, services) and unit tests.

Phase 2 — Backend API & streaming (7–14 days)
- Task 2.1: Implement FastAPI app with endpoints:
  - POST /auth/token (JWT)
  - POST /conversations (create)
  - GET /conversations (list)
  - GET /conversations/{id}/messages
  - POST /conversations/{id}/messages (send)
  - /stream websocket or SSE: stream message tokens
  - Admin endpoints for model switching, trials, and exports (protected)
- Task 2.2: Adapter integration: call Groq API via adapters/groq_adapter.py; ensure streaming-compatible call or implement chunking.
- Task 2.3: Database: migrate to Postgres for production; provide Alembic migrations. Therapist_app.db can be used as a reference seed.
- Task 2.4: Containerize: Dockerfile, docker-compose for dev (Postgres + Redis for rate limit/state), and Helm/Cloud Run instructions for production.
- PR: Add api/ scaffold, Dockerfile, adapters, and migrations.

Phase 3 — Mobile app (Flutter) MVP (10–20 days)
- Task 3.1: Create Flutter project with these screens:
  - Sign-in / Sign-up
  - Conversation list
  - Chat screen with streaming messages
  - Settings (model/options/trials)
  - Clinician/admin screens (for clinician features if required separately)
- Task 3.2: Networking: implement REST client + WebSocket/SSE for streaming.
- Task 3.3: Local storage: implement encrypted local DB (sqflite + flutter_secure_storage) for caching and offline viewing.
- Task 3.4: Push notifications setup using Firebase for dev testing (FCM + APNs), routed via backend.
- Task 3.5: Build and test on iOS and Android simulators. Prepare TestFlight and internal Play Store testing builds.
- PR: Add flutter/ client skeleton in repo or in separate mobile repo (recommended). For monorepo, place under mobile/flutter_app/.

Phase 4 — Website parity & integration testing (5–10 days)
- Task 4.1: Ensure website UI (templates or web client) uses the new API endpoints and streaming method.
- Task 4.2: Run end-to-end tests: create a test user, simulate conversation, stream tokens to web and mobile clients, and verify database persistence and exports.
- Task 4.3: Validate 2FA flows and mood reminder cron jobs against new backend.
- PR: Update website templates and front-end code to the new API.

Phase 5 — Security, monitoring, and production deploy (3–7 days)
- Task 5.1: Secrets management: move env secrets to platform-managed secrets (Render/Fly/GCP Secret Manager).
- Task 5.2: Monitoring: Sentry for errors, Prometheus/Cloud monitoring for metrics.
- Task 5.3: Add rate limiting and abuse-prevention (Redis + limiter middleware).
- Task 5.4: Content moderation hooks for therapy scope and logging/audit with opt-out options.
- Deploy: push Docker images from app-development-branch to registry and deploy to chosen host (non-Railway) from that branch.

Phase 6 — Polishing & app store submission (2–4 weeks)
- Final QA, accessibility adjustments, privacy policy and legal review for therapy use.
- Implement in-app purchases/subscriptions if monetizing.
- Submit to App Store and Play Store (expect review cycles).

Estimated effort
- Single experienced full-stack dev: MVP (backend + Flutter MVP + website parity) 6–10 weeks.
- Small team (2–3 devs): 3–6 weeks.
- Additional time for clinic-specific features, regulatory compliance, and app store reviews.

Branching & workflow recommendations
- Continue development on app-development-branch. Do not merge to main until you validate on staging and confirm readiness.
- Use feature branches off app-development-branch for each major task (eg. api-refactor, flutter-skeleton, groq-adapter).
- CI: GitHub Actions for lint/tests, container image build and push, and optional auto-deploy to a staging environment from app-development-branch.

CI/CD & hosting (non‑Railway)
- Backend: Container registry (GHCR), Host options: Render, Fly, Cloud Run, or AWS ECS/Fargate.
- Mobile builds: use Codemagic or GitHub Actions to produce iOS/Android builds and upload to TestFlight/Play Console.
- Keep production deployments tied to a release branch and require manual promotion from staging.

Per-feature developer TODO (initial PR list)
1. PR #1 (api-refactor): Extract chat core, add adapters folder, and scaffold FastAPI app (tests + Dockerfile).
2. PR #2 (db-migration): Add Postgres models and Alembic migrations; include seed script from therapist_app.db.
3. PR #3 (groq-adapter): Implement Groq API adapter and streaming support.
4. PR #4 (flutter-skeleton): Add Flutter project skeleton with basic chat UI and streaming client.
5. PR #5 (web-integration): Update existing web UI to use new API endpoints.
6. PR #6 (ci-cd): Add GitHub Actions workflows for backend build/deploy and mobile builds.

Security & compliance notes
- Therapy applications require clear privacy policy and data handling descriptions. Consider a legal review.
- Allow users to delete/export their data and opt out of logging training data.
- Implement role-based access control for clinician/admin functions.

Costs & scaling considerations
- Groq / Hosted LLM costs are per-use. Add quotas and throttles for new users. Consider caching common responses or using smaller models for non-critical flows.
- Hosting: budget $20–200+/mo for small deployments; increase with traffic and GPU needs.
