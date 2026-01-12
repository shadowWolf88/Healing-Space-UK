"""
Flask API wrapper for Healing Space Therapy App
Provides REST API endpoints while keeping desktop app intact
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime
import sys

# Import existing modules (no changes to them)
from secrets_manager import SecretsManager
from audit import log_event
from fhir_export import export_patient_fhir
import main

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize with same settings as main app
DEBUG = os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes')

# Initialize database on startup
try:
    main.init_db()
except Exception as e:
    print(f"Database initialization: {e}")

@app.route('/')
def index():
    """Serve simple web interface"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'service': 'Healing Space Therapy API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        pin = data.get('pin')
        
        if not username or not password or not pin:
            return jsonify({'error': 'Username, password, and PIN required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        
        # Check if user exists
        if cur.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone():
            conn.close()
            return jsonify({'error': 'Username already exists'}), 409
        
        # Hash credentials
        hashed_password = main.hash_password(password)
        hashed_pin = main.hash_pin(pin)
        
        # Create user
        cur.execute("INSERT INTO users (username, password, pin, last_login) VALUES (?,?,?,?)",
                   (username, hashed_password, hashed_pin, datetime.now()))
        conn.commit()
        conn.close()
        
        log_event(username, 'api', 'user_registered', 'Registration via API')
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'username': username
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        user = cur.execute("SELECT username, password FROM users WHERE username=?", (username,)).fetchone()
        conn.close()
        
        if not user or not main.verify_password(user[1], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        log_event(username, 'api', 'user_login', 'Login via API')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'username': username
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/therapy/chat', methods=['POST'])
def therapy_chat():
    """AI therapy chat endpoint"""
    try:
        data = request.json
        username = data.get('username')
        message = data.get('message')
        
        if not username or not message:
            return jsonify({'error': 'Username and message required'}), 400
        
        # Use existing TherapistAI class
        ai = main.TherapistAI(username)
        
        # Get conversation history
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        history = cur.execute(
            "SELECT sender, message FROM chat_history WHERE session_id=? ORDER BY timestamp DESC LIMIT 10",
            (f"{username}_session",)
        ).fetchall()
        conn.close()
        
        # Get AI response using existing logic
        response = ai.get_response(message, history[::-1])
        
        # Save to chat history
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO chat_history (session_id, sender, message) VALUES (?,?,?)",
                   (f"{username}_session", "user", message))
        cur.execute("INSERT INTO chat_history (session_id, sender, message) VALUES (?,?,?)",
                   (f"{username}_session", "ai", response))
        conn.commit()
        conn.close()
        
        log_event(username, 'api', 'therapy_chat', 'Chat message sent')
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mood/log', methods=['POST'])
def log_mood():
    """Log mood entry"""
    try:
        data = request.json
        username = data.get('username')
        mood_val = data.get('mood_val')
        sleep_val = data.get('sleep_val', 0)
        meds = data.get('meds', '')
        notes = data.get('notes', '')
        
        if not username or mood_val is None:
            return jsonify({'error': 'Username and mood_val required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO mood_logs (username, mood_val, sleep_val, meds, notes, sentiment) VALUES (?,?,?,?,?,?)",
            (username, mood_val, sleep_val, meds, notes, 'Neutral')
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()
        
        log_event(username, 'api', 'mood_logged', f'Mood: {mood_val}')
        
        return jsonify({
            'success': True,
            'message': 'Mood logged successfully',
            'log_id': log_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mood/history', methods=['GET'])
def mood_history():
    """Get mood history for user"""
    try:
        username = request.args.get('username')
        limit = request.args.get('limit', 30)
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        logs = cur.execute(
            "SELECT id, mood_val, sleep_val, meds, notes, entry_timestamp FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?",
            (username, limit)
        ).fetchall()
        conn.close()
        
        result = [{
            'id': log[0],
            'mood_val': log[1],
            'sleep_val': log[2],
            'meds': log[3],
            'notes': log[4],
            'timestamp': log[5]
        } for log in logs]
        
        return jsonify({
            'success': True,
            'logs': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gratitude/log', methods=['POST'])
def log_gratitude():
    """Log gratitude entry"""
    try:
        data = request.json
        username = data.get('username')
        entry = data.get('entry')
        
        if not username or not entry:
            return jsonify({'error': 'Username and entry required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO gratitude_logs (username, entry) VALUES (?,?)", (username, entry))
        conn.commit()
        log_id = cur.lastrowid
        conn.close()
        
        log_event(username, 'api', 'gratitude_logged', 'Gratitude entry added')
        
        return jsonify({
            'success': True,
            'message': 'Gratitude logged successfully',
            'log_id': log_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/fhir', methods=['GET'])
def export_fhir():
    """Export user data in FHIR format"""
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Use existing FHIR export function
        bundle = export_patient_fhir(username)
        
        log_event(username, 'api', 'fhir_export', 'FHIR data exported via API')
        
        return jsonify({
            'success': True,
            'bundle': json.loads(bundle)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/safety/check', methods=['POST'])
def safety_check():
    """Check text for safety concerns"""
    try:
        data = request.json
        text = data.get('text')
        username = data.get('username')
        
        if not text:
            return jsonify({'error': 'Text required'}), 400
        
        # Use existing SafetyMonitor
        monitor = main.SafetyMonitor()
        is_high_risk = monitor.is_high_risk(text)
        
        if is_high_risk and username:
            monitor.send_crisis_alert(username)
            log_event(username, 'api', 'crisis_alert', 'High risk detected via API')
        
        return jsonify({
            'success': True,
            'is_high_risk': is_high_risk,
            'crisis_resources': main.CRISIS_RESOURCES if is_high_risk else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
