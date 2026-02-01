import sqlite3
import pytest
from datetime import datetime, timedelta, timezone

import sys
import pathlib

# Ensure repo root is on sys.path for imports
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import api


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Use a temporary DB for tests
    db_path = str(tmp_path / "test_therapist_app.db")
    monkeypatch.setattr(api, 'DB_PATH', db_path)
    # Ensure DB initialized
    api.init_db()
    app = api.app.test_client()
    yield app


def create_user(cur, username, role='user'):
    # Always use test_ usernames for rate limit bypass
    if not username.startswith('test_'):
        username = f'test_{username}'
    hashed_password = api.hash_password('testpass')
    hashed_pin = api.hash_pin('1234')
    if role == 'user':
        cur.execute("INSERT INTO users (username, password, pin, role, last_login, full_name, email, phone, dob, conditions, country, area, postcode, nhs_number, clinician_id, disclaimer_accepted) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (username, hashed_password, hashed_pin, role, datetime.now(timezone.utc).isoformat(), username, f'{username}@example.com', '07000000000', '1990-01-01', 'None', 'UK', 'London', 'N1 1AA', '1234567890', 'test_clinician', 1))
        # Ensure patient approval
        cur.execute("INSERT INTO patient_approvals (patient_username, clinician_username, status) VALUES (?,?,?)", (username, 'test_clinician', 'approved'))
    elif role == 'clinician':
        cur.execute("INSERT INTO users (username, password, pin, role, last_login, full_name, email, phone, country, area, professional_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (username, hashed_password, hashed_pin, role, datetime.now(timezone.utc).isoformat(), username, f'{username}@example.com', '07000000001', 'UK', 'London', f'PROF_{username}'))
        # Ensure clinician has at least one approved patient
        cur.execute("INSERT INTO patient_approvals (patient_username, clinician_username, status) VALUES (?,?,?)", ('test_patient1', username, 'approved'))
    elif role == 'developer':
        cur.execute("INSERT INTO users (username, password, pin, role, last_login) VALUES (?,?,?,?,?)",
            (username, hashed_password, hashed_pin, 'developer', datetime.now(timezone.utc).isoformat()))


def test_analytics_includes_appointments(client):
    # Prepare DB with a patient, clinician and appointments
    conn = sqlite3.connect(api.DB_PATH)
    cur = conn.cursor()
    create_user(cur, 'patient1', 'user')
    create_user(cur, 'dr_smith', 'clinician')

    # upcoming appointment
    appt_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    cur.execute("INSERT INTO appointments (clinician_username, patient_username, appointment_date, notes, patient_response) VALUES (?,?,?,?,?)",
                ('dr_smith', 'patient1', appt_date, 'Follow-up', 'pending'))
    # past appointment
    past_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    cur.execute("INSERT INTO appointments (clinician_username, patient_username, appointment_date, notes, patient_response) VALUES (?,?,?,?,?)",
                ('dr_smith', 'patient1', past_date, 'Last session', 'accepted'))
    conn.commit()
    conn.close()

    # Login as clinician to get token
    login_resp = client.post("/api/auth/login", json={
        "username": "dr_smith",
        "password": "testpass",
        "pin": "1234"
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json().get("token", "")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get(f"/api/analytics/patient/patient1?clinician=dr_smith", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'upcoming_appointments' in data
    assert 'recent_past_appointments' in data
    assert any(a['clinician_username'] == 'dr_smith' for a in data['upcoming_appointments'])
    assert any(a['clinician_username'] == 'dr_smith' for a in data['recent_past_appointments'])


def test_attendance_endpoint_updates_db_and_notifications(client):
    conn = sqlite3.connect(api.DB_PATH)
    cur = conn.cursor()
    create_user(cur, 'patient2', 'user')
    create_user(cur, 'dr_jones', 'clinician')

    appt_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    cur.execute("INSERT INTO appointments (clinician_username, patient_username, appointment_date, notes) VALUES (?,?,?,?)",
                ('dr_jones', 'patient2', appt_date, 'Check-in'))
    appt_id = cur.lastrowid
    conn.commit()

    # Login as clinician to get token
    login_resp = client.post("/api/auth/login", json={
        "username": "dr_jones",
        "password": "testpass",
        "pin": "1234"
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json().get("token", "")
    headers = {"Authorization": f"Bearer {token}"}
    # Call attendance endpoint as clinician
    client_resp = client.post(f"/api/appointments/{appt_id}/attendance", json={
        'clinician_username': 'dr_jones',
        'status': 'attended'
    }, headers=headers)
    assert client_resp.status_code == 200
    j = client_resp.get_json()
    assert j.get('success') is True

    # Verify appointment row updated
    r = cur.execute("SELECT attendance_status, attendance_confirmed_by, attendance_confirmed_at FROM appointments WHERE id=?", (appt_id,)).fetchone()
    assert r[0] == 'attended'
    assert r[1] == 'dr_jones'
    assert r[2] is not None

    # Verify notification created for patient
    note = cur.execute("SELECT recipient_username, message, notification_type FROM notifications WHERE recipient_username=? ORDER BY created_at DESC LIMIT 1", ('patient2',)).fetchone()
    assert note is not None
    assert note[0] == 'patient2'
    assert note[2] == 'appointment_attendance'

    conn.close()