
# Healing Space – AI Agent Guide

## Overview
This project is a **web-only** mental health therapy app using Flask REST API and PostgreSQL. Deployment is via Railway (see [Procfile](Procfile)), with auto-table creation logic in [api.py](api.py) for ephemeral filesystems.

## Architecture
- **Web API**: [api.py](api.py) – 200+ Flask endpoints, DB init, auth, TherapistAI (Groq LLM), SafetyMonitor (crisis detection)
- **Database**: PostgreSQL with 43 auto-created tables on startup
- **Key modules**: [secrets_manager.py](secrets_manager.py) (Vault/env), [fhir_export.py](fhir_export.py) (FHIR/HMAC), [training_data_manager.py](training_data_manager.py) (GDPR/consent), [audit.py](audit.py) (logging)

## Security & Auth
- Passwords: Argon2 → bcrypt → PBKDF2 fallback; legacy SHA256 auto-migrates on login
- PINs: bcrypt or PBKDF2 with `PIN_SALT` env var
- Encryption: Fernet (`ENCRYPTION_KEY`), see [api.py](api.py)
- Secrets: [secrets_manager.py](secrets_manager.py) (Vault/env fallback)
- Optional deps: `HAS_ARGON2`, `HAS_BCRYPT`, `HAS_PARAMIKO`, `HAS_VAULT` feature flags

## Developer Workflows
- **Local dev**: Set `DEBUG=1`, generate Fernet key, set `PIN_SALT`, `GROQ_API_KEY`. Run `python3 api.py`
- **Testing**: `pytest -v tests/` with `DEBUG=1`, PostgreSQL connection required, see [tests/](tests/)
- **DB migrations**: Add columns in `init_db()` (try/except), never drop columns, use PostgreSQL syntax
- **Backups**: Auto-backup to [backups/](backups/) on launch

## API & Patterns
- Endpoints: Auth, therapy, clinical, data, exports (203 routes total, see [api.py](api.py))
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
- Web-only platform: all code is Flask-based, no desktop/Tkinter dependencies
- Always use try/except for DB migrations, never drop columns
- Use PostgreSQL syntax: `%s` placeholders, not SQLite `?`
- Encryption key must be valid Fernet (44 chars)
- Use feature flags for optional deps
- Test isolation: use `tmp_path`, set env before import

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
