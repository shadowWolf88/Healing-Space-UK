import sqlite3
import os
import sys
import importlib.util

def get_db_path():
    candidates = [
        'therapist_app.db',
        os.path.join(os.getcwd(), 'therapist_app.db'),
        os.path.join(os.path.dirname(__file__), '..', 'therapist_app.db'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError('Could not find therapist_app.db in expected locations.')

# Dynamically import hash_password and hash_pin from api.py
api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'api.py'))
sys.path.insert(0, os.path.dirname(api_path))
spec = importlib.util.spec_from_file_location("api", api_path)
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)

def create_patient(cur, username, password, pin, full_name, dob, conditions, email, phone, country, area, postcode, nhs_number, clinician_id):
    hashed_password = api.hash_password(password)
    hashed_pin = api.hash_pin(pin)
    cur.execute("""
        INSERT OR IGNORE INTO users (username, password, pin, email, phone, full_name, dob, conditions, last_login, role, country, area, postcode, nhs_number, clinician_id, disclaimer_accepted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, hashed_password, hashed_pin, email, phone, full_name, dob, conditions, None, 'user', country, area, postcode, nhs_number, clinician_id, 1))
    # Create pending approval request
    cur.execute("""
        INSERT OR IGNORE INTO patient_approvals (patient_username, clinician_username, status)
        VALUES (?, ?, ?)
    """, (username, clinician_id, 'approved'))

def create_clinician(cur, username, password, pin, full_name, email, phone, country, area, professional_id):
    hashed_password = api.hash_password(password)
    hashed_pin = api.hash_pin(pin)
    cur.execute("""
        INSERT OR IGNORE INTO users (username, password, pin, role, full_name, email, phone, last_login, country, area, professional_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, hashed_password, hashed_pin, 'clinician', full_name, email, phone, None, country, area, professional_id))

def create_developer(cur, username, password, pin):
    hashed_password = api.hash_password(password)
    hashed_pin = api.hash_pin(pin)
    cur.execute("""
        INSERT OR IGNORE INTO users (username, password, pin, role, last_login)
        VALUES (?, ?, ?, ?, ?)
    """, (username, hashed_password, hashed_pin, 'developer', None))

def main():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # --- Main test suite users ---
    create_clinician(
        cur,
        username='test_clinician',
        password='testpass',
        pin='1234',
        full_name='Test Clinician',
        email='clinician@example.com',
        phone='07000000001',
        country='UK',
        area='London',
        professional_id='CLIN123456'
    )
    create_patient(
        cur,
        username='test_patient',
        password='testpass',
        pin='1234',
        full_name='Test Patient',
        dob='1990-01-01',
        conditions='Test Condition',
        email='patient@example.com',
        phone='07000000002',
        country='UK',
        area='London',
        postcode='N1 1AA',
        nhs_number='1234567890',
        clinician_id='test_clinician'
    )
    create_developer(
        cur,
        username='test_dev',
        password='testpass',
        pin='1234'
    )

    # --- Additional users for test_appointments.py ---
    create_patient(cur, 'patient1', 'testpass', '1234', 'Patient One', '1980-01-01', 'None', 'patient1@example.com', '07000000003', 'UK', 'London', 'N1 1AB', '1234567891', 'test_clinician')
    create_clinician(cur, 'dr_smith', 'testpass', '1234', 'Dr Smith', 'drsmith@example.com', '07000000004', 'UK', 'London', 'CLIN654321')
    create_patient(cur, 'patient2', 'testpass', '1234', 'Patient Two', '1985-01-01', 'None', 'patient2@example.com', '07000000005', 'UK', 'London', 'N1 1AC', '1234567892', 'dr_jones')
    create_clinician(cur, 'dr_jones', 'testpass', '1234', 'Dr Jones', 'drjones@example.com', '07000000006', 'UK', 'London', 'CLIN987654')

    # --- Users for integration/fhir/chat tests ---
    cur.execute("INSERT OR IGNORE INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)", ('u_fhir', api.hash_password('testpass'), 'user', 'FHIR User'))

    # --- Browser smoke test user ---
    cur.execute("INSERT OR IGNORE INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)", ('clin_browser', api.hash_password('testpass'), 'clinician', 'Browser Clin'))

    # --- Legacy user for migration test ---
    import hashlib
    legacy_pwd = 'legacytest'
    legacy_hash = hashlib.sha256(legacy_pwd.encode()).hexdigest()
    cur.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ('legacyuser', legacy_hash))

    # --- Encrypted profile user for FHIR export ---
    # Only add if encrypt_text is available
    if hasattr(api, 'encrypt_text'):
        cur.execute("INSERT OR IGNORE INTO users (username, full_name, dob, conditions) VALUES (?, ?, ?, ?)", ('u1', api.encrypt_text('Alice'), api.encrypt_text('1970-01-01'), api.encrypt_text('None')))
    else:
        cur.execute("INSERT OR IGNORE INTO users (username, full_name, dob, conditions) VALUES (?, ?, ?, ?)", ('u1', 'Alice', '1970-01-01', 'None'))
    conn.commit()
    conn.close()
    print('Test users created with hashed credentials.')

if __name__ == '__main__':
    main()
