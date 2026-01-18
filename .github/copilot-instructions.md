# Healing Space - AI Agent Guide

## Purpose
Help AI coding agents understand this mental health therapy application's architecture and become immediately productive.

## Architecture Overview

**Dual-mode application**: Flask web API + legacy desktop GUI
- **Production runtime**: [api.py](api.py) — Flask REST API with 65+ endpoints, serves [templates/index.html](templates/index.html)
- **Legacy desktop**: [legacy_desktop/main.py](legacy_desktop/main.py) — Tkinter GUI (desktop-only, not deployed to Railway)
- **Deployment**: Railway via [Procfile](Procfile) runs `gunicorn api:app`

### Database Architecture (3 SQLite databases)
1. **therapist_app.db** (20 tables) — primary app data: users, chat_history, mood_logs, clinical_scales, appointments, patient_approvals, notifications, community_posts, alerts, audit_logs
2. **pet_game.db** — gamification state: pet stats, inventory, adventures
3. **ai_training_data.db** — GDPR-compliant anonymized dataset: data_consent, training_chats, training_patterns, anonymized_conversations

**Critical**: DB path logic in [api.py](api.py#L48-53) checks `/app/data` (Railway volume) before falling back to local paths. Railway filesystem is ephemeral — use volumes or PostgreSQL for persistence.

### Key System Classes
- **SafetyMonitor** ([api.py](api.py#L284)): Crisis keyword detection, alert creation in `alerts` table
- **TherapistAI** ([api.py](api.py#L311)): Groq LLM wrapper, loads context from `ai_memory` + clinician notes, persists conversation history
- **TrainingDataManager** ([training_data_manager.py](training_data_manager.py)): GDPR consent tracking, anonymization pipeline, user hash generation

## Security & Auth Patterns

### Password Hashing Hierarchy
Argon2 (preferred) → bcrypt → PBKDF2 fallback. Functions: `hash_password()` / `verify_password()` in both [api.py](api.py#L64-96) and [legacy_desktop/main.py](legacy_desktop/main.py).
- Legacy SHA256 hashes auto-migrate on login (tests verify in [tests/test_app.py](tests/test_app.py#L40-56))
- PIN hashing: bcrypt or PBKDF2 with `PIN_SALT` env var (see `hash_pin()` / `check_pin()`)

### Encryption & Secrets
- Fernet encryption: `encrypt_text()` / `decrypt_text()` functions in [api.py](api.py#L132-155)
- SecretsManager ([secrets_manager.py](secrets_manager.py)): HashiCorp Vault (`hvac`) → env vars fallback
- Required secrets: `GROQ_API_KEY`, `ENCRYPTION_KEY` (Fernet key), `PIN_SALT`
- FHIR exports ([fhir_export.py](fhir_export.py)): HMAC-signed bundles using `ENCRYPTION_KEY`

### Optional Dependencies Pattern
Code gracefully handles missing packages: `HAS_ARGON2`, `HAS_BCRYPT`, `HAS_PARAMIKO`, `HAS_VAULT` feature flags. Example: `secure_transfer.sftp_upload()` raises `RuntimeError` if paramiko missing (tested in [tests/test_app.py](tests/test_app.py#L98)).

## Critical Developer Workflows

### Local Development
```bash
export DEBUG=1 PIN_SALT=dev_salt
export ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
export GROQ_API_KEY=your_key

# Web API (production mode)
python3 api.py  # http://localhost:5000

# Desktop app (legacy)
python3 legacy_desktop/main.py
```

### Testing
```bash
pip install -r requirements.txt
export DEBUG=1 PIN_SALT=testsalt
export ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
pytest -v tests/
```
Tests use isolated tmp dirs (see [tests/test_app.py](tests/test_app.py#L1-25)) and require `DEBUG=1` to bypass production checks.

### Database Migrations
**Inline migrations**: `init_db()` in [api.py](api.py#L158-280) uses `ALTER TABLE ADD COLUMN` wrapped in try/except. When adding schema:
1. Add column with try/except in `init_db()`
2. Update corresponding code in [legacy_desktop/main.py](legacy_desktop/main.py) `init_db()` if feature shared
3. Update tests to verify table creation
4. **Never drop columns** — app must handle old data gracefully

Auto-backups: `backups/therapist_app_YYYYMMDD_HHMMSS.db.bak` created on launch.

## API Architecture Patterns

### Endpoint Structure (65 endpoints in [api.py](api.py))
- Auth: `/api/auth/register`, `/api/auth/login` (2FA PIN), `/api/auth/forgot-password`
- Therapy: `/api/therapy/chat`, `/api/therapy/history`, `/api/therapy/initialize`
- Clinical: `/api/scales/submit`, `/api/clinicians/list`, `/api/approvals/*`
- Data: `/api/mood/log`, `/api/gratitude/log`, `/api/cbt/record`
- Exports: `/api/export/fhir`, `/api/training-data/*` (GDPR endpoints)
- Pet: `/api/pet/create`, `/api/pet/status`, `/api/pet/feed`

### Request/Response Pattern
```python
@app.route('/api/endpoint', methods=['POST'])
def handler():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Missing field'}), 400
    # DB operations with try/except
    return jsonify({'success': True, 'data': result}), 200
```

## Project-Specific Conventions

### Audit Logging
Call `log_event(username, actor, action, details)` ([audit.py](audit.py)) for:
- Data exports (FHIR, CSV)
- Crisis alerts
- Password changes
- GDPR deletions
Never raise exceptions from `log_event()` — it's best-effort logging.

### GDPR Training Data Flow
1. User opts in via UI → `TrainingDataManager.give_consent(username)`
2. Therapy chats auto-collected → `collect_therapy_session(username, messages)`
3. Anonymization: PII stripped, SHA256 user hashing, no reversible identifiers
4. Export: [export_training_data.py](export_training_data.py) generates CSV/JSON
5. Deletion: Right to erasure via `delete_training_data(username)`

### Crisis Detection & Alerts
`SafetyMonitor.is_high_risk(text)` checks keywords → `send_crisis_alert(username)` → inserts to `alerts` table → optional webhook to `ALERT_WEBHOOK_URL`.

## Integration Points

- **AI/LLM**: Groq API via `TherapistAI` class, requires `GROQ_API_KEY`
- **Email**: SMTP via `send_reset_email()` for password recovery (optional)
- **SFTP**: `secure_transfer.sftp_upload()` with `SFTP_*` env vars (requires paramiko)
- **Webhooks**: Crisis alerts POST to `ALERT_WEBHOOK_URL` if set
- **Vault**: Optional HashiCorp Vault for secrets (requires `hvac` + `VAULT_ADDR`/`VAULT_TOKEN`)

## Testing Expectations

- Tests import `main` (desktop) module via `importlib` to avoid tkinter on Railway
- `DEBUG=1` required to skip production secret validation
- Fixtures use `tmp_path` for isolated DB files
- Tests verify: DB migrations, password hashing, legacy SHA256 migration, alert persistence, FHIR signing, SFTP error handling

## Where to Start (Key Files)

**Web API (production)**:
- [api.py](api.py) — Flask routes, DB init, auth, TherapistAI, SafetyMonitor
- [templates/index.html](templates/index.html) — Single-page web app
- [Procfile](Procfile) — Railway deployment config

**Shared modules**:
- [secrets_manager.py](secrets_manager.py) — Vault/env secret loading
- [fhir_export.py](fhir_export.py) — FHIR bundle generation + HMAC signing
- [training_data_manager.py](training_data_manager.py) — GDPR consent & anonymization
- [audit.py](audit.py) — Best-effort logging to `audit_logs` table

**Desktop (legacy)**:
- [legacy_desktop/main.py](legacy_desktop/main.py) — Tkinter GUI (not for Railway)
- [legacy_desktop/pet_game.py](legacy_desktop/pet_game.py) — Pet UI + schema migrations

**Documentation**:
- [documentation/00_INDEX.md](documentation/00_INDEX.md) — Complete doc index
- [FEATURE_STATUS.md](FEATURE_STATUS.md) — 65 endpoints, feature checklist
- [documentation/DEPLOYMENT.md](documentation/DEPLOYMENT.md) — Railway setup, volumes, PostgreSQL migration

## Safe Modification Guidelines

1. **Adding API endpoints**: Follow existing pattern with try/except, return jsonify errors, validate inputs
2. **DB schema changes**: Use `ALTER TABLE ADD COLUMN` in try/except, never drop columns, update both api.py and legacy_desktop/main.py
3. **New secrets**: Use `SecretsManager.get_secret()` with fallback warnings, document in README
4. **Optional features**: Add `HAS_*` feature flags, raise clear errors with install instructions
5. **Crisis keywords**: Update `SafetyMonitor.risk_keywords`, test with mock data
6. **GDPR changes**: Update TrainingDataManager, ensure audit trail via `log_event()`

## Common Gotchas

- **Railway DB persistence**: SQLite resets on deploy unless using `/app/data` volume or PostgreSQL
- **Desktop imports**: Never import [legacy_desktop/main.py](legacy_desktop/main.py) in [api.py](api.py) — tkinter not available on Railway
- **Encryption key format**: Must be valid 44-char Fernet key, not arbitrary string
- **DEBUG mode**: Production must set `DEBUG=0`, otherwise uses temporary keys
- **Test isolation**: Always use `tmp_path` fixture, set env vars before imports
- **Pet DB**: Separate `pet_game.db` file, has its own schema migrations
