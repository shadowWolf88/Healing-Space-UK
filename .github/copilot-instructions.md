
# Healing Space – AI Agent Guide

## Overview
This project is a dual-mode mental health therapy app: a Flask REST API (production) and a legacy Tkinter desktop GUI. It uses three SQLite databases for app data, gamification, and GDPR-compliant AI training data. Deployment is via Railway (see [Procfile](Procfile)), with DB path logic in [api.py](api.py) to support ephemeral filesystems.

## Architecture
- **Web API**: [api.py](api.py) – 65+ Flask endpoints, DB init, auth, TherapistAI (Groq LLM), SafetyMonitor (crisis detection)
- **Desktop GUI**: [legacy_desktop/main.py](legacy_desktop/main.py) – Tkinter, not deployed to Railway
- **Databases**:
    - `therapist_app.db`: users, chat, mood, clinical, appointments, audit, etc.
    - `pet_game.db`: gamification state
    - `ai_training_data.db`: anonymized, GDPR-compliant
- **Key modules**: [secrets_manager.py](secrets_manager.py) (Vault/env), [fhir_export.py](fhir_export.py) (FHIR/HMAC), [training_data_manager.py](training_data_manager.py) (GDPR/consent), [audit.py](audit.py) (logging)

## Security & Auth
- Passwords: Argon2 → bcrypt → PBKDF2 fallback; legacy SHA256 auto-migrates on login
- PINs: bcrypt or PBKDF2 with `PIN_SALT` env var
- Encryption: Fernet (`ENCRYPTION_KEY`), see [api.py](api.py)
- Secrets: [secrets_manager.py](secrets_manager.py) (Vault/env fallback)
- Optional deps: `HAS_ARGON2`, `HAS_BCRYPT`, `HAS_PARAMIKO`, `HAS_VAULT` feature flags

## Developer Workflows
- **Local dev**: Set `DEBUG=1`, generate Fernet key, set `PIN_SALT`, `GROQ_API_KEY`. Run `python3 api.py` (web) or `python3 legacy_desktop/main.py` (desktop)
- **Testing**: `pytest -v tests/` with `DEBUG=1`, isolated tmp dirs, see [tests/](tests/)
- **DB migrations**: Add columns in `init_db()` (try/except), never drop columns, update both [api.py](api.py) and [legacy_desktop/main.py](legacy_desktop/main.py)
- **Backups**: Auto-backup to [backups/](backups/) on launch

## API & Patterns
- Endpoints: Auth, therapy, clinical, data, exports, pet (see [api.py](api.py))
- Request pattern: Validate input, try/except DB ops, return `jsonify` with error/success
- Logging: Use `log_event()` ([audit.py](audit.py)) for exports, alerts, password changes, GDPR actions; never raise from logger
- GDPR: Consent via `TrainingDataManager.give_consent()`, anonymization, export ([export_training_data.py](export_training_data.py)), right to erasure
- Crisis: `SafetyMonitor.is_high_risk()` → `send_crisis_alert()` → `alerts` table, optional webhook

## Integration Points
- Groq LLM: `TherapistAI`, needs `GROQ_API_KEY`
- Email: `send_reset_email()` (optional)
- SFTP: `secure_transfer.sftp_upload()` (needs paramiko, SFTP_* env)
- Webhooks: Crisis alerts POST to `ALERT_WEBHOOK_URL`
- Vault: HashiCorp Vault for secrets (optional)

## Conventions & Gotchas
- Never import desktop code in [api.py](api.py) (Tkinter not on Railway)
- Always use try/except for DB migrations, never drop columns
- Encryption key must be valid Fernet (44 chars)
- Use feature flags for optional deps
- Test isolation: use `tmp_path`, set env before import
- Pet DB: separate schema, see [legacy_desktop/pet_game.py](legacy_desktop/pet_game.py)

## Key Files
- [api.py](api.py): API, DB, auth, AI, safety
- [legacy_desktop/main.py](legacy_desktop/main.py): Desktop GUI
- [secrets_manager.py](secrets_manager.py): Secrets
- [fhir_export.py](fhir_export.py): FHIR/HMAC
- [training_data_manager.py](training_data_manager.py): GDPR
- [audit.py](audit.py): Logging
- [tests/](tests/): Test suite
- [documentation/00_INDEX.md](documentation/00_INDEX.md): Doc index

---
If any section is unclear or missing, please provide feedback for further refinement.
