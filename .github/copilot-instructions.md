# Healing Space – AI Agent Guide

## Quick Facts
- **Type**: Mental health therapy web app (Flask REST API + PostgreSQL)
- **Size**: 16,000+ line `api.py`, 16,000+ line frontend, 43 DB tables
- **Status**: Production-ready backend with critical security gaps (see TIER 0)
- **Deployment**: Railway via `Procfile`, auto-DB-init on startup
- **Test Coverage**: 92% (12/13 passing) but missing clinical features

---

## Critical Security Issues (TIER 0 – DO THESE FIRST)
These are active vulnerabilities blocking real users:

1. **Live credentials in git** (`.env` file): PostgreSQL password, Groq key, encryption key exposed
   - Fix: Rotate all credentials on Railway; run `git filter-repo` to scrub history
   - Impact: Anyone cloning repo gets production database access to all patient data

2. **Prompt injection in TherapistAI** (line 2101): User fields (stressors, diagnoses) injected unsanitized
   - Location: [api.py#L2150-L2310](api.py#L2150-L2310)
   - Fix: Escape user context; add sanitization layer before Groq API call

3. **SQL syntax errors** (line 94, 146, 154+): Duplicate `%s` placeholders in `training_data_manager.py`
   - Impact: Any training data operation crashes
   - Fix: Audit & test all SQL statements

4. **XSS via innerHTML** (138+ instances in frontend): User content (posts, pet names, plans) rendered unsanitized
   - Location: `templates/index.html`
   - Fix: Use `textContent` for user data; sanitize with DOMPurify for rich content

---

## Architecture Map
```
api.py (16k lines)
├─ Flask app + 210+ routes
├─ TherapistAI (Groq LLM integration)
├─ RiskScoringEngine (clinical + behavioral + conversational scoring)
├─ SafetyMonitor (crisis keyword detection)
└─ PostgreSQL helpers (get_db_connection, init_db)

Frontend
├─ templates/index.html (16k lines, monolithic SPA)
├─ static/js/*.js (activity logging, DOM manipulation)
└─ static/css/*.css

Supporting Modules
├─ secrets_manager.py (Vault/env var secrets)
├─ audit.py (event logging)
├─ training_data_manager.py (GDPR + consent)
├─ fhir_export.py (HL7 FHIR export with HMAC)
├─ safety_monitor.py (legacy risk detection)
└─ c_ssrs_assessment.py (Columbia-Suicide Severity Rating Scale)

Database
├─ 43 tables auto-created in init_db() [line 3081]
├─ therapy: chat_history, insights, therapy_notes
├─ clinical: risk_assessments, risk_alerts, clinical_scales
├─ cbt: goals, values_clarification, coping_cards, core_beliefs, sleep_diary
└─ user: users, sessions, clinician_patients, training_data_consent
```

---

## Database Connection Pattern
**CRITICAL**: Always use PostgreSQL, never SQLite in production

```python
# Pattern used throughout api.py (line 2037)
conn = get_db_connection()  # Supports both DATABASE_URL (Railway) and individual env vars
cur = get_wrapped_cursor(conn)  # Returns psycopg2 cursor with method chaining

# Always close after use
cur.execute('SELECT * FROM users WHERE username=%s', (username,))
result = cur.fetchone()
conn.commit()
conn.close()

# WRONG (will fail):
cur.execute('SELECT * FROM users WHERE username=?', (username,))  # SQLite syntax
```

---

## API Endpoint Patterns
All endpoints follow this structure (see examples at line ~500 onwards):

```python
@app.route('/api/<resource>/<action>', methods=['GET|POST|PUT|DELETE'])
def handler():
    # 1. Get authenticated user from session
    username = get_authenticated_username()
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    # 2. Validate input
    data = request.json
    if not data.get('required_field'):
        return jsonify({'error': 'Field required'}), 400
    
    # 3. DB operation with try/except
    try:
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        cur.execute('INSERT INTO table (...) VALUES (%s, ...)', (...))
        conn.commit()
        log_event(username, 'category', 'action', 'details')  # ALWAYS log user actions
        return jsonify({'success': True}), 201
    except Exception as e:
        return handle_exception(e, 'handler_name')  # Safe error response
    finally:
        conn.close()
```

Key conventions:
- **Validate input**: Use `InputValidator` class (line 181) for mood/sleep/text/integer ranges
- **Log everything**: Use `log_event(username, category, action, details)` (line ~200, imported from audit.py)
- **Return jsonify**: Always return Flask `jsonify()` with status code, never raw dicts
- **Handle exceptions**: Use `handle_exception(e, context)` to avoid leaking error details
- **Auth check first**: Every endpoint must verify session before DB access
- **Database safety**: Never interpolate user input into SQL; always use `%s` with params

---

## Authentication & Session Flow
Session-based (Flask session), NOT token-based:

```python
# Login flow (line ~3400):
# 1. Verify password: verify_password(stored_hash, user_password)
# 2. Set session: session['username'] = username; session.permanent = True
# 3. Generate CSRF token: CSRFProtection.generate_csrf_token(username)

# In requests:
# 1. Check session: username = session.get('username')
# 2. Validate CSRF: X-CSRF-Token header (line ~210)
# 3. Access data: cur.execute(..., (username,))

# Password hashing priority:
# Argon2 > bcrypt > PBKDF2 (fallback) > SHA256 (legacy, auto-migrates on login)
```

**Critical**: Always derive identity from session, NEVER from request body (line 3711 has a bypass vulnerability)

---

## AI Integration (Groq LLM)
TherapistAI class (line 2101):

```python
# Init with user context
ai = TherapistAI(username)

# Get response with memory context (see RiskScoringEngine)
response = ai.get_response(
    user_message,
    history=[(role, text), ...],      # Recent chat history
    wellness_data={'mood': 7, ...},   # From mood logs
    memory_context={'personal_context': {...}, 'recent_events': [...]},  # AI memory
    risk_context='critical'            # 'none'|'moderate'|'high'|'critical'
)

# Groq API details:
# - Endpoint: https://api.groq.com/openai/v1/chat/completions
# - Model: llama-3.3-70b-versatile
# - Prompt injection risk: User fields (stressors, diagnoses) need sanitization
# - Missing memory: Each response recreates context (no persistent vector DB)
```

---

## Risk Assessment System
`RiskScoringEngine.calculate_risk_score()` (line ~1650):

```python
# Composite risk score (0-100):
# - Clinical score (0-40): PHQ-9, GAD-7 assessments + recent alerts
# - Behavioral score (0-30): Mood trends, engagement, CBT tool use
# - Conversational score (0-30): Keyword detection in chat

# Risk levels:
# - 0-25: low (green)
# - 26-50: moderate (yellow)
# - 51-75: high (orange)
# - 76-100: critical (red)

# Usage:
risk = RiskScoringEngine.calculate_risk_score(username)
if risk['risk_level'] == 'critical':
    # Auto-create risk alerts for clinician
    # Run crisis response protocol
```

**Critical keywords** managed in database table `risk_keywords` (add via admin UI, not hardcoded)

---

## CBT Tools Endpoints
Full CRUD for therapy exercises (goals, values, coping cards, exposures, etc.):

```python
# Pattern (all similar):
@app.route('/api/cbt/<tool>', methods=['POST|GET|PUT|DELETE'])
# POST: Create with InputValidator
# GET: List with pagination
# PUT: Update only provided fields
# DELETE: Soft delete (recommended) or hard delete

# Examples: /api/cbt/goals, /api/cbt/values, /api/cbt/coping-card
# Each has summarize_*() helper for AI memory context
```

---

## Environment Variables
**REQUIRED** for production:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db    # Railway provides this
GROQ_API_KEY=gsk_...                                 # From https://console.groq.com
ENCRYPTION_KEY=<44-char Fernet key>                  # Generate: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
SECRET_KEY=<32+ random chars>                         # Session encryption
PIN_SALT=<random string>                              # PIN hashing salt
DEBUG=0                                               # Disable in production (enables CORS, skips HTTPS)

# OPTIONAL:
ALERT_WEBHOOK_URL=https://...                        # Crisis alert webhook
ALLOWED_ORIGINS=https://healing-space.org.uk,...     # CORS whitelist
DISABLE_CSRF=0                                        # For testing only
```

---

## Testing
Run tests with: `.venv/bin/python -m pytest -v tests/` (requires PostgreSQL)

Test structure:
- tests/test_app.py: Auth, session, basic endpoints
- tests/test_postgresql_api.py: DB operations
- tests/test_messaging.py: Clinician messaging
- tests/test_role_access.py: Access control

**Gotchas**:
- Must set `DEBUG=1` for tests to pass
- Tests need live PostgreSQL connection
- No C-SSRS, crisis, GDPR export tests (major coverage gap)
- Isolated test data: use fixtures, clean up after

---

## Common Tasks

### Add a new API endpoint
1. Get authenticated user: `username = get_authenticated_username()`
2. Validate input: Use `InputValidator` class methods
3. DB operation: `get_db_connection()` + `try/except` + `conn.commit()` + `conn.close()`
4. Log action: `log_event(username, 'category', 'action', 'details')`
5. Return response: `jsonify({'success': True})` with appropriate status code

### Add a database column
1. Write migration in api.py line 3081 `init_db()` function
2. Use `try/except` for safety (table might already have column)
3. Commit transaction: `conn.commit()`
4. **NEVER drop columns** (data destruction risk)

### Fix a security issue
1. Identify the vulnerability type (XSS, injection, auth bypass, etc.)
2. Check docs/MASTER_ROADMAP.md TIER 0/1 for priority
3. Write a test first to reproduce the issue
4. Implement fix + test + verify existing tests still pass
5. Log critical fixes: `log_event('system', 'security', 'fix_applied', 'description')`

### Deploy to Railway
1. Push changes to git
2. Railway auto-deploys from main branch
3. Check Railway logs for DB migration status
4. Run smoke tests: `pytest tests/ -v` in Railway environment

---

## Debugging Tips

1. **Check logs**: `log_event()` writes to audit_log table (line ~200)
2. **Enable DEBUG mode**: `export DEBUG=1` (relaxes CSRF, enables error details, skips HTTPS)
3. **Database queries**: Use psql or Railway's web console to check table data
4. **Session issues**: Check Flask session cookie validity, timeout (30 days default)
5. **AI issues**: Verify GROQ_API_KEY format (gsk_ prefix), check Groq API status
6. **Encryption issues**: Ensure ENCRYPTION_KEY is valid Fernet format (44 chars base64)

---

## Worst Gotchas

1. **SQLite vs PostgreSQL**: Code uses `%s` placeholders (PostgreSQL), not `?` (SQLite)
2. **Credential leakage**: .env file was committed to git – rotate all secrets immediately
3. **Prompt injection**: User fields in wellness_data are unsanitized in LLM prompt
4. **XSS in frontend**: 138+ uses of .innerHTML with user content
5. **SQL errors in training module**: Duplicate %s placeholders crash operations
6. **GDPR gaps**: No export of AI insights, no consent for activity tracking
7. **Monolithic frontend**: 16k-line HTML file with inline JS/CSS (very hard to maintain)

---

## Key References
- docs/MASTER_ROADMAP.md: Detailed priority-ordered bug/feature list (TIER 0-4)
- README.md: User-facing overview + deployment guides
- secrets_manager.py: Secret retrieval (Vault/env var fallback)
- audit.py: Event logging system
- training_data_manager.py: GDPR consent + anonymization

---

Updated: Feb 8, 2026 | Version: 2.0 (PostgreSQL) | For detailed roadmap, see docs/MASTER_ROADMAP.md
