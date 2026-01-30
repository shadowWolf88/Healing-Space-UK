from flask import Blueprint, request, jsonify, session
from .models import init_cbt_tools_schema
import sqlite3
import json

cbt_tools_bp = Blueprint('cbt_tools', __name__)

@cbt_tools_bp.before_app_first_request
def setup():
    init_cbt_tools_schema()

@cbt_tools_bp.route('/api/cbt-tools/save', methods=['POST'])
def save_cbt_tool():
    data = request.json
    username = session.get('username')
    tool_type = data.get('tool_type')
    entry_data = json.dumps(data.get('data', {}))
    mood_rating = data.get('mood_rating')
    notes = data.get('notes', '')
    conn = sqlite3.connect("therapist_app.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO cbt_tool_entries (username, tool_type, data, mood_rating, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (username, tool_type, entry_data, mood_rating, notes))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@cbt_tools_bp.route('/api/cbt-tools/load', methods=['GET'])
def load_cbt_tool():
    username = session.get('username')
    tool_type = request.args.get('tool_type')
    conn = sqlite3.connect("therapist_app.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT id, data, mood_rating, notes, created_at, updated_at
        FROM cbt_tool_entries
        WHERE username=? AND tool_type=?
        ORDER BY updated_at DESC
        LIMIT 1
    """, (username, tool_type))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify({
            'id': row[0],
            'data': json.loads(row[1]),
            'mood_rating': row[2],
            'notes': row[3],
            'created_at': row[4],
            'updated_at': row[5]
        })
    else:
        return jsonify({'data': None})
