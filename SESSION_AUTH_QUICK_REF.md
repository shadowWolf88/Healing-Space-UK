# Quick Reference: Session Authentication Pattern

**TL;DR** - If you need to authenticate a fetch call to your backend:

## Frontend (JavaScript)

```javascript
// ✅ CORRECT - Session-based authentication
const response = await fetch('/api/some-endpoint', {
    method: 'GET',  // or POST, PUT, DELETE
    credentials: 'include',  // ← REQUIRED for session auth
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ /* data */ })  // Only for POST/PUT
});

if (!response.ok) {
    if (response.status === 401) {
        console.error('Not authenticated - please login');
    } else if (response.status === 403) {
        console.error('Not authorized to access this resource');
    }
}
```

## Backend (Python/Flask)

```python
from flask import request, jsonify

@app.route('/api/some-endpoint', methods=['GET', 'POST'])
def some_endpoint():
    # Step 1: Get authenticated user from session
    authenticated_user = get_authenticated_username()
    if not authenticated_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Step 2: Check authorization
    if not user_has_permission(authenticated_user):
        return jsonify({'error': 'Not authorized'}), 403
    
    # Step 3: Process request
    return jsonify({'success': True, 'data': result})
```

---

## Common Mistakes

### ❌ Missing `credentials: 'include'`
```javascript
// This will FAIL - session cookies not sent
fetch('/api/endpoint', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
    // Missing credentials!
});
```

### ❌ Using URL parameters for auth
```python
# This is WRONG - auth should not be in URL
@app.route('/api/endpoint?user=<user>')
def endpoint(user):  # ❌ Should use session instead
    return jsonify({})
```

### ❌ Not checking authentication
```python
# This is WRONG - no auth check
@app.route('/api/endpoint')
def endpoint():
    data = get_user_data()  # Who is the user???
    return jsonify(data)
```

---

## When to Use This Pattern

Use **session authentication** (with `credentials: 'include'`) when:
- ✅ User is already logged in with a session
- ✅ Endpoint is same-origin (same domain)
- ✅ User's identity matters (patient, clinician, etc.)
- ✅ Different users have different permissions
- ✅ You want secure server-side auth state

## When NOT to Use This Pattern

Don't use this when:
- ❌ Cross-origin requests (different domain) - use CORS headers and API keys
- ❌ Public API endpoints that don't need auth
- ❌ Third-party integrations - use tokens instead
- ❌ Mobile apps - use Authorization header with tokens

---

## Related Endpoints (Already Fixed)

All of these endpoints properly use session authentication:

- `/api/insights` - Patient/clinician insights
- `/api/therapy/chat` - Send therapy messages
- `/api/wellness/log` - Log wellness entries
- `/api/user/preferred-name` - Get user's preferred name
- `/api/gratitude/log` - Log gratitude entries
- `/api/goals/log` - Log goals
- `/api/medication/adherence` - Log medication adherence
- `/api/safety-plan/log` - Log safety plan access

All of these properly:
1. Call `get_authenticated_username()` on backend
2. Include `credentials: 'include'` on frontend
3. Return 401 if not authenticated
4. Return 403 if not authorized

---

## Debugging Session Auth Issues

### If you get 401 "Authentication required":
1. Check if you're logged in (session exists)
2. Verify `credentials: 'include'` is in fetch call
3. Check cookies are being sent (DevTools → Network → Headers)
4. Verify session cookie is not expired

### If you get 403 "Not authorized":
1. Check user's role/permissions
2. Verify authorization checks in backend
3. Check if user has access to requested resource
4. For clinicians: verify patient_approvals record exists

### If data doesn't load but no error appears:
1. Check browser console for errors
2. Check Network tab in DevTools
3. Verify fetch response.ok before processing data
4. Add error handling: `if (!response.ok) { ... }`

---

## Testing This Pattern

### Unit Test Example
```python
def test_authenticated_endpoint(client, session):
    # Login first
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    # Now fetch should work
    response = client.get('/api/endpoint')
    assert response.status_code == 200

def test_unauthenticated_endpoint(client):
    # No session - should fail
    response = client.get('/api/endpoint')
    assert response.status_code == 401
```

### Integration Test Example
```javascript
// Login first
await fetch('/api/auth/login', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, pin })
});

// Now authenticated fetch should work
const response = await fetch('/api/endpoint', {
    method: 'GET',
    credentials: 'include'
});
assert(response.ok);
```

---

## Key Files

- [INSIGHTS_FIX_REPORT.md](INSIGHTS_FIX_REPORT.md) - Detailed fix documentation
- [SESSION_AUTHENTICATION_REVIEW.md](SESSION_AUTHENTICATION_REVIEW.md) - Full auth review
- [test_insights_fix.py](test_insights_fix.py) - Automated test suite
- [api.py](api.py) - Backend implementation (use Ctrl+F for `get_authenticated_username()`)

---

## Questions?

See the Copilot instructions in [.github/copilot-instructions.md](.github/copilot-instructions.md) for full architecture overview.
