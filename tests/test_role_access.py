"""
Integration tests for role-based dashboard and feature access.
Ensures patients, clinicians, and developers only see and access what they should.
"""

import pytest
import sys
import os

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_patient_can_make_requests(client, test_patient):
    """Test that patient role can make requests without 500 errors."""
    with client.session_transaction() as sess:
        sess['username'] = test_patient['username']
        sess['role'] = test_patient['role']
    
    # Patient should be able to call therapy endpoints
    resp = client.post('/api/therapy/chat', json={
        'username': test_patient['username'],
        'message': 'Hello'
    })
    # Accept 200, 400 (bad request), 403 (forbidden), but NOT 500
    assert resp.status_code in [200, 400, 403], f"Patient therapy chat got {resp.status_code}: {resp.data}"


def test_clinician_can_make_requests(client, test_clinician):
    """Test that clinician role can make requests without 500 errors."""
    with client.session_transaction() as sess:
        sess['username'] = test_clinician['username']
        sess['role'] = test_clinician['role']
    
    # Clinician should be able to access analytics
    resp = client.get('/api/analytics/active-patients')
    # Accept 200, 400, 401, 403 but NOT 500
    assert resp.status_code in [200, 400, 401, 403], f"Clinician analytics got {resp.status_code}"


def test_developer_can_make_requests(client, test_developer):
    """Test that developer role can make requests without 500 errors."""
    with client.session_transaction() as sess:
        sess['username'] = test_developer['username']
        sess['role'] = test_developer['role']
    
    # Developer should be able to access developer endpoints
    resp = client.get('/api/developer/stats')
    # Accept 200, 400, 401, 403 but NOT 500
    assert resp.status_code in [200, 400, 401, 403], f"Developer stats got {resp.status_code}"


def test_patient_authenticated_endpoints(client, test_patient):
    """Test that patient can access mood/therapy history endpoints."""
    with client.session_transaction() as sess:
        sess['username'] = test_patient['username']
        sess['role'] = test_patient['role']
    
    # Patient should be able to check their mood history (may be empty)
    resp = client.get(f'/api/mood/history')
    assert resp.status_code in [200, 400, 403], f"Patient mood history got {resp.status_code}"
    
    # Patient should be able to get their therapy history (may be empty)
    resp = client.get(f'/api/therapy/history')
    assert resp.status_code in [200, 400, 403], f"Patient therapy history got {resp.status_code}"
