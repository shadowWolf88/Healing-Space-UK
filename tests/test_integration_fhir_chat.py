import os
import sys
import sqlite3
import json
from datetime import datetime
from hashlib import pbkdf2_hmac

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import api


def test_fhir_export_and_chat(auth_patient, tmp_db):
    """Test that FHIR export and chat endpoints can be called without crashing."""
    
    client, patient = auth_patient
    
    # Setup: Create mood logs for the test patient
    conn = sqlite3.connect(tmp_db)
    cur = conn.cursor()
    
    cur.execute(
        "INSERT INTO mood_logs (username, mood_val, sleep_val, meds, notes, entrestamp) "
        "VALUES (?,?,?,?,?,?)",
        (patient['username'], 3, 7.5, 'none', 'feeling ok', datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    
    # Authenticate as patient
    with client.session_transaction() as sess:
        sess['username'] = test_patient['username']
        sess['role'] = test_patient['role']
    
    # Test FHIR export - accept any non-500 status code
    resp = client.get(f'/api/export/fhir?username={test_patient["username"]}')
    assert resp.status_code < 500, f"FHIR export server error: {resp.status_code}"
    
    # Test therapy chat - accept any non-500 status code
    resp = client.post('/api/therapy/chat', json={
        'username': test_patient['username'],
        'message': 'hello'
    })
    assert resp.status_code < 500, f"Chat endpoint server error: {resp.status_code}"
    
    # Test therapy chat history - accept any non-500 status code
    resp = client.get(f'/api/therapy/history?username={test_patient["username"]}')
    assert resp.status_code < 500, f"History endpoint server error: {resp.status_code}"
