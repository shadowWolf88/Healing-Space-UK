Purpose
- Help AI coding agents become productive quickly in this repository.

Overview
- Desktop-first Python app (Tkinter + CustomTkinter) with local SQLite storage and optional cloud integrations.
- Key runtime entry: [main.py](main.py) — UI + auth, DB setup (`init_db()`), SafetyMonitor, encryption and AI client glue.
- **App architecture**: Single `App(ctk.CTk)` class handles auth flow, UI tabs (therapy, mood logs, CBT tools, progress insights), and session management. `TherapistAI` class manages LLM interactions with persistent memory context.
- Gamification module: [pet_game.py](pet_game.py) uses a separate `pet_game.db` and contains in-file schema migrations.
- Secrets: [secrets_manager.py](secrets_manager.py) prefers HashiCorp Vault (`hvac`) and falls back to environment variables.
- Export: [fhir_export.py](fhir_export.py) builds and HMAC-signs FHIR bundles using `ENCRYPTION_KEY`.
- Transfer: [secure_transfer.py](secure_transfer.py) wraps SFTP (paramiko optional).
- Auditing: [audit.py](audit.py) provides a best-effort `log_event()` that writes to `audit_logs`.
- **Backups**: Auto-created in `backups/` dir with timestamp pattern `therapist_app_YYYYMMDD_HHMMSS.db.bak`.

What to know before editing
- The code tolerates missing optional dependencies (argon2, bcrypt, paramiko, hvac, cryptography). Keep fallbacks rather than force-installing in code.
- **Password hashing hierarchy**: Argon2 (preferred) > bcrypt > PBKDF2 fallback. See `hash_password()` and `verify_password()` in [main.py](main.py). Legacy SHA256 hashes are auto-migrated on login.
- **PIN hashing**: Uses bcrypt or PBKDF2 with `PIN_SALT`. See `hash_pin()` and `check_pin()` functions.
- Secrets and keys: prefer `SecretsManager.get_secret()` or `require_secret()` for production secrets. Tests and local runs often set `DEBUG=1` to permit env fallbacks.
- Encryption: code uses `cryptography.Fernet`. `ENCRYPTION_KEY` must be a valid Fernet key for signing/export in production.
- DB files: `therapist_app.db` (primary), `pet_game.db` (pet state). Migrations are inline (see `init_db()` and `PetGame._check_and_update_schema`). When adding schema changes, update both migration code and tests.
- **UI Monkeypatching**: `main.py` wraps `ctk.CTkToplevel` to force topmost/transient behavior and bind Escape key. It also patches `messagebox` functions to auto-use root as parent. Avoid bypassing these wrappers.

Developer workflows & quick commands
- Run app locally (dev):
  - export DEBUG=1 PIN_SALT=dev_salt
  - (optional) export ENCRYPTION_KEY=$(python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY)
  - python3 main.py
- Run tests:
  - pip install -r requirements.txt
  - pytest -q
  - Tests use `DEBUG` env var and dynamic temp DBs (see `tests/test_app.py`).
- Lint/format: this repo does not include a formatter config — preserve existing style when possible.

Conventions & patterns (repo-specific)
- Secrets: Use `SecretsManager(debug=DEBUG)` and `secrets.get_secret('NAME')`. Avoid directly reading os.environ unless explicit fallback is intended.
- Runtime flags: `DEBUG` controls permissive behavior (temporary keys, skipping required secret checks). Tests rely on setting `DEBUG=1`.
- Optional libs: check feature flags like `HAS_PARAMIKO`, `HAS_VAULT`, `HAS_ARGON2`, `HAS_BCRYPT` before using the library.
- Encryption helpers are centralized in top-level modules: `encrypt_text()` / `decrypt_text()` in `main.py` and `_decrypt()` in `fhir_export.py`; reuse those helpers for consistent behavior.
- Audit: call `log_event(username, actor, action, details)` for any data export or sensitive action; it's best-effort and must never raise.
- UI: `customtkinter` is monkeypatched (CTkToplevel wrapper) in `main.py`; take care when creating modal dialogs and Toplevel windows.
- SFTP helper: `secure_transfer.sftp_upload(local, remote, host, ...)` raises `RuntimeError` if `paramiko` isn't installed — tests assert this behavior.
- **AI Memory**: `TherapistAI.get_memory()` loads user context from `ai_memory` table plus decrypted profile fields and recent alerts. Use `update_memory()` after therapy sessions to persist context.

Integration points to watch
- External secrets: HashiCorp Vault via `hvac` if env vars `VAULT_ADDR` & `VAULT_TOKEN` present (see `SecretsManager`).
- AI/LLM: `main.py` loads `GROQ_API_KEY` and calls an external API via `API_URL`; follow its header pattern (`Authorization: Bearer ...`).
- FHIR: `export_patient_fhir()` signs bundles with HMAC using `ENCRYPTION_KEY`. Don't change the signing format without updating consumers.
- SFTP/Webhooks: `SFTP_*` env vars and `ALERT_WEBHOOK_URL` are optional runtime integrations used for exports/alerts.

Tests & expectations
- Tests live in `tests/test_app.py`. They expect:
  - `DEBUG=1` to avoid production-only checks.
  - `PIN_SALT` and `ENCRYPTION_KEY` to be set (tests set placeholders).
  - DB initialization via `main.init_db()` to create required tables and migration behavior.

How to safely modify this repo
- When adding DB fields: add migration logic to `init_db()` and mirror any pet-related changes to `pet_game.py` schema helper.
- When introducing new secrets: prefer using `SecretsManager.require_secret()` if it's mandatory, or `get_secret()` with a clear fallback and warnings.
- Preserve the permissive fallback behavior of optional dependencies; failing fast in production is acceptable but keep tests/dev smooth with `DEBUG`.
- Update `audit.log_event()` calls whenever introducing data exports, record access, or safety escalations.

Where to look next (key files)
- [main.py](main.py) — runtime, DB migrations, encryption, UI patches
- [secrets_manager.py](secrets_manager.py) — Vault vs env fallback
- [fhir_export.py](fhir_export.py) — FHIR bundle creation & signing
- [secure_transfer.py](secure_transfer.py) — SFTP helper (paramiko)
- [pet_game.py](pet_game.py) — local game DB + UI logic
- [tests/test_app.py](tests/test_app.py) — canonical tests and examples of env setup
- [DEPLOYMENT.md](DEPLOYMENT.md) — GitHub and Railway deployment guide
- [README.md](README.md) — project overview and quick start

Deployment & distribution
- This is a **desktop GUI app** (Tkinter/CustomTkinter), not a web service
- Railway deployment requires either: (1) web conversion, (2) headless API mode, or (3) skip Railway and use PyInstaller for desktop distribution
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Railway setup, environment variables, and database persistence strategies
- For desktop distribution: use PyInstaller and GitHub Releases instead of Railway
- Database persistence on Railway requires volumes or PostgreSQL migration (SQLite is ephemeral on Railway's filesystem)

If something is unclear
- Ask for which area you'd like deeper examples (DB migration, secret flow, FHIR signing, or deployment). I'll iterate on this file.
