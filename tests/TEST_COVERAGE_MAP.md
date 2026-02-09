# Healing Space - Test Coverage Map

## Test Suite Overview

| Metric | Value |
|--------|-------|
| Total test files | 20 |
| Backend unit test files | 17 |
| E2E journey test files | 3 |
| Estimated total test cases | 300+ |
| Feature coverage | 100% of API endpoints |

---

## Backend Test Files (tests/backend/)

### test_auth.py (~45 tests)
| Feature | Tests |
|---------|-------|
| Password hashing (Argon2/bcrypt/PBKDF2) | hash, verify, fallback chain |
| Password strength validation | length, uppercase, lowercase, digit, special, weak list |
| PIN hashing | hash, verify |
| Login endpoint | success, missing fields, wrong password, wrong PIN, user not found |
| Registration endpoint | success, duplicate username, duplicate email, missing fields, weak password |
| Unauthenticated access | protected endpoints return 401 |
| Session management | session creation, validation |
| CSRF tokens | generate, validate, one-time use |
| X-Username bypass logging | debug header logging |

### test_input_validation.py (~40 tests)
| Feature | Tests |
|---------|-------|
| validate_text | valid, empty, too long, XSS stripping |
| validate_message | valid, empty, too long |
| validate_note | valid, empty, max length |
| validate_integer | valid, out of range, non-numeric |
| validate_mood | 1-10 range, boundary values |
| validate_sleep | 0-24 range |
| validate_anxiety | 0-10 range |
| validate_title | valid, too long |
| validate_username | valid, special chars, too long |
| CSRF token lifecycle | generate, validate, require decorator |

### test_mood_wellness.py (~30 tests)
| Feature | Tests |
|---------|-------|
| POST /api/mood/log | success, unauth, missing mood_val, invalid values, duplicate today, medications, XSS sanitization |
| GET /api/mood/history | success, missing username, empty |
| POST /api/mood/check-reminder | forced, not 8pm |
| GET /api/mood/check-today | logged, not logged, missing username |
| POST /api/wellness/log | success, unauth, minimal data |
| GET /api/wellness/today | exists, none, unauth |
| GET /api/wellness/summary | with data, empty, unauth |
| POST /api/gratitude/log | success, missing entry, missing username, too long, empty |

### test_therapy_chat.py (~12 tests)
| Feature | Tests |
|---------|-------|
| POST /api/therapy/chat | success, missing username, missing message, empty message, XSS handling, session creation |
| GET /api/therapy/history | success, no username, session filter, empty |
| GET /api/therapy/sessions | success, no username, default creation |

### test_cbt_tools.py (~25 tests)
| Feature | Tests |
|---------|-------|
| POST /api/cbt/thought-record | success, missing fields, too long, evidence optional |
| GET /api/cbt/records | success, no username, empty |
| GET /api/cbt/summary | success, no username |
| GET /api/cbt/tool-history | success, unauth, filter |
| POST /api/clinical/phq9 | success, missing scores, wrong count, missing username |
| POST /api/clinical/gad7 | missing scores, wrong count |

### test_safety.py (~45 tests)
| Feature | Tests |
|---------|-------|
| C-SSRS assessment | start, submit, history, clinician response |
| Safety check | safe text, crisis keywords |
| Safety plan | create, retrieve |
| Risk scoring | calculate, history |
| Risk alerts | list, create, acknowledge, resolve |
| Risk dashboard | access |
| PHQ-9 | submit, severity levels |
| GAD-7 | submit, severity levels |

### test_community.py (~35 tests)
| Feature | Tests |
|---------|-------|
| GET /api/community/posts | success, with channel, empty |
| GET /api/community/channels | success |
| POST /api/community/posts | success, missing message, too long, unauth |
| POST /api/community/reply | success, missing fields, post not found |
| POST /api/community/like | success, unauth |
| POST /api/community/react | success |
| POST /api/community/pin | success, not author |
| DELETE /api/community/posts | success, not author |
| POST /api/community/report | success |
| GET /api/community/replies | success, empty |

### test_messaging_v2.py (~12 tests)
| Feature | Tests |
|---------|-------|
| POST /api/messages/send | success, unauth, missing fields, too long, self-send, not found, role restrictions |
| GET /api/messages/inbox | success, unauth |

### test_pet_system.py (~12 tests)
| Feature | Tests |
|---------|-------|
| GET /api/pet/status | exists, no pet, no username, user not found |
| POST /api/pet/create | success, missing name, user not found |
| POST /api/pet/feed | success, not enough coins, no pet |
| POST /api/pet/reward | unauth, user not found |

### test_notifications.py (~8 tests)
| Feature | Tests |
|---------|-------|
| GET /api/notifications | success, no username, empty |
| POST /api/notifications/<id>/read | success |
| DELETE /api/notifications/<id> | success |
| POST /api/notifications/clear-read | success, missing username |

### test_appointments.py (~18 tests)
| Feature | Tests |
|---------|-------|
| GET /api/appointments | clinician view, patient view, missing params, empty |
| POST /api/appointments | success, missing fields |
| DELETE /api/appointments/<id> | success, not found |
| POST /api/appointments/<id>/respond | accept, decline, missing fields, invalid response, not found |
| POST /api/appointments/<id>/attendance | attended, no_show, missing fields, invalid status, wrong clinician, not found |

### test_wins.py (~14 tests)
| Feature | Tests |
|---------|-------|
| POST /api/wins/log | success, unauth, invalid type, empty text, too long, all valid types |
| GET /api/wins/recent | success, unauth, custom limit |
| GET /api/wins/stats | own stats, unauth, clinician views patient, unauthorized for other user |

### test_clinician.py (~35 tests)
| Feature | Tests |
|---------|-------|
| Patient list | list, detail, AI summary |
| Clinical notes | create, retrieve |
| Export summary | success |
| Analytics dashboard | success |
| Active patients | list |
| Patient analytics | individual analytics |
| Report generation | generate report |
| Patient search | search |
| Clinician listing | list |
| Access control | patient cannot access clinician routes |

### test_ai_memory.py (~20 tests)
| Feature | Tests |
|---------|-------|
| POST /api/activity/log | success, unauth, no consent, empty, batch cap |
| GET/POST /api/activity/consent | get status, grant, revoke, missing field, unauth |
| POST /api/ai/memory/update | success, unauth, missing event_type, no data |
| GET /api/ai/memory | success, unauth |
| POST /api/ai/patterns/detect | success |

### test_developer.py (~12 tests)
| Feature | Tests |
|---------|-------|
| POST /api/developer/register | success, wrong key, already exists, weak password |
| POST /api/developer/terminal/execute | allowed command, blocked command, non-developer, blocked args, empty |
| POST /api/developer/ai/chat | non-developer blocked |
| GET /api/developer/stats | success |

### test_security.py (~15 tests)
| Feature | Tests |
|---------|-------|
| GET /api/export/fhir | success, missing username |
| GET/PUT /api/patient/profile | success, missing username, not found |
| POST /api/auth/disclaimer/accept | success, missing username |
| SQL injection | parameterized query safety |
| XSS | input sanitization |
| Oversized payloads | handled gracefully |
| Null byte injection | handled |
| Unicode | proper handling |
| Auth enforcement | 13 protected endpoints verified |

### test_data_export.py (~8 tests)
| Feature | Tests |
|---------|-------|
| POST /api/therapy/export | txt, json, csv formats, missing fields, empty history, session filter |

---

## E2E Journey Tests (tests/e2e/)

### test_patient_journey.py
- Registration flow
- Login flow
- Mood logging journey
- Gratitude logging journey
- Win logging journey
- Notifications journey
- Duplicate mood log prevention
- Unauthenticated access blocking

### test_clinician_journey.py
- View patient list
- Create appointment
- Confirm attendance
- Send message to patient
- View appointments
- Patient cannot access clinician endpoints

### test_developer_journey.py
- Developer registration
- Safe terminal commands
- Dangerous commands blocked
- Patient cannot execute terminal
- Clinician cannot execute terminal

---

## Running Tests

```bash
# All tests
./run_tests.sh

# Backend only
./run_tests.sh backend

# E2E only
./run_tests.sh e2e

# With coverage report
./run_tests.sh coverage

# Quick parallel run
./run_tests.sh quick

# Security tests only
./run_tests.sh security

# Clinical safety tests only
./run_tests.sh clinical

# Specific test file
python -m pytest tests/backend/test_auth.py -v

# Specific test class
python -m pytest tests/backend/test_auth.py::TestLoginEndpoint -v

# Specific test
python -m pytest tests/backend/test_auth.py::TestLoginEndpoint::test_login_success -v
```

## CI/CD

GitHub Actions workflow at `.github/workflows/tests.yml`:
- Runs on push to main/develop and PRs to main
- Backend tests with coverage
- E2E tests
- Security-focused test suite
- Coverage and test result artifacts uploaded
