import os
import sys
import sqlite3
import json
from datetime import datetime

# Ensure project root is on sys.path for test discovery
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import api


def setup_tmp_db(tmp_path):
    db_path = str(tmp_path / "test_integration.db")
    api.DB_PATH = db_path
    if os.path.exists(db_path):
        os.remove(db_path)
    api.init_db()
    return db_path


def test_fhir_export_and_chat(tmp_path):
    db = setup_tmp_db(tmp_path)

    # Seed a user and some mood logs
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    hashed_password = api.hash_password('testpass')
    hashed_pin = api.hash_pin('1234')
    # Developer registration logic for test_dev
    cur.execute("INSERT INTO users (username, password, pin, role, last_login) VALUES (?,?,?,?,?)",
        ('test_dev', hashed_password, hashed_pin, 'developer', datetime.now().isoformat()))
    db = setup_tmp_db(tmp_path)

    # Seed a user and some mood logs
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    hashed_password = api.hash_password('testpass')
    hashed_pin = api.hash_pin('1234')
    fhir_username = 'test_u_fhir'
    cur.execute("INSERT INTO users (username, password, pin, role, last_login, full_name, email, phone, dob, conditions, country, area, postcode, nhs_number, clinician_id, disclaimer_accepted) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (fhir_username, hashed_password, hashed_pin, 'user', datetime.now().isoformat(), 'FHIR User', f'{fhir_username}@example.com', '07000000010', '1990-01-01', 'None', 'UK', 'London', 'N1 1AA', '1234567899', 'test_clinician', 1))
    cur.execute("INSERT INTO patient_approvals (patient_username, clinician_username, status) VALUES (?,?,?)", (fhir_username, 'test_clinician', 'approved'))
    cur.execute("INSERT INTO mood_logs (username, mood_val, sleep_val, meds, notes, entrestamp) VALUES (?,?,?,?,?,?)",
                ('u_fhir', 3, 7.5, 'none', 'feeling ok', datetime.now().isoformat()))
    conn.commit()
    conn.close()

    with api.app.test_client() as c:
        # Login as user to get token
        login_resp = c.post("/api/auth/login", json={
            "username": fhir_username,
            "password": "testpass",
            "pin": "1234"
        })
        assert login_resp.status_code == 200
        token = login_resp.get_json().get("token", "")
        headers = {"Authorization": f"Bearer {token}"}

        # FHIR export
        r = c.get(f'/api/export/fhir?username={fhir_username}', headers=headers)
        assert r.status_code == 200
        data = r.get_json()
        assert data.get('success') is True
        assert 'bundle' in data

        # Chat: send a message and retrieve history
        r2 = c.post('/api/therapy/chat', json={'username': fhir_username, 'message': 'hello'}, headers=headers)
        assert r2.status_code == 200
        jr = r2.get_json()
        assert jr.get('success') is True

        # Retrieve chat history
        h = c.get(f'/api/therapy/history?username={fhir_username}', headers=headers)
        assert h.status_code == 200
        hj = h.get_json()
        assert hj.get('success') is True
        assert isinstance(hj.get('history'), list)
