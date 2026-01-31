CREATE TABLE users 
                      (username TEXT PRIMARY KEY, password TEXT, pin TEXT, last_login TIMESTAMP, 
                       full_name TEXT, dob TEXT, conditions TEXT, role TEXT DEFAULT 'user', 
                       clinician_id TEXT, disclaimer_accepted INTEGER DEFAULT 0, email TEXT, phone TEXT, reset_token TEXT, reset_token_expiry DATETIME, country TEXT, area TEXT, postcode TEXT, nhs_number TEXT, professional_id TEXT);
CREATE TABLE sessions 
                      (session_id TEXT PRIMARY KEY, username TEXT, title TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE gratitude_logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, entry TEXT, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE mood_logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, mood_val INTEGER, 
                       sleep_val REAL, meds TEXT, notes TEXT, sentiment TEXT,
                       exercise_mins INTEGER DEFAULT 0, outside_mins INTEGER DEFAULT 0, water_pints REAL DEFAULT 0,
                       entrestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE safety_plans
                      (username TEXT PRIMARY KEY, triggers TEXT, coping TEXT, contacts TEXT);
CREATE TABLE ai_memory 
                      (username TEXT PRIMARY KEY, memory_summary TEXT, last_updated DATETIME);
CREATE TABLE cbt_records 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, situation TEXT, thought TEXT, evidence TEXT, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE clinical_scales
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, scale_name TEXT, score INTEGER, severity TEXT, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE community_posts
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, message TEXT, likes INTEGER DEFAULT 0, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE audit_logs
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, actor TEXT, action TEXT, details TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE alerts
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, alert_type TEXT, details TEXT, status TEXT DEFAULT 'open', created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE patient_approvals
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_username TEXT, clinician_username TEXT, 
                       status TEXT DEFAULT 'pending', request_date DATETIME DEFAULT CURRENT_TIMESTAMP, 
                       approval_date DATETIME);
CREATE TABLE notifications
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, recipient_username TEXT, message TEXT, 
                       notification_type TEXT, read INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE chat_history 
                      (session_id TEXT, sender TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, chat_session_id INTEGER);
CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE community_likes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, UNIQUE(post_id, username));
CREATE TABLE community_replies
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE clinician_notes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, clinician_username TEXT, patient_username TEXT, note_text TEXT, 
                       is_highlighted INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE appointments
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       clinician_username TEXT, 
                       patient_username TEXT,
                       appointment_date DATETIME, 
                       appointment_type TEXT DEFAULT 'consultation',
                       notes TEXT,
                       pdf_generated INTEGER DEFAULT 0,
                       pdf_path TEXT,
                       notification_sent INTEGER DEFAULT 0,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP, patient_acknowledged INTEGER DEFAULT 0, patient_response TEXT, patient_response_date DATETIME, attendance_status TEXT DEFAULT 'scheduled', attendance_confirmed_by TEXT, attendance_confirmed_at DATETIME);
CREATE TABLE chat_sessions
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT,
                       session_name TEXT,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                       is_active INTEGER DEFAULT 0);
CREATE TABLE verification_codes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       identifier TEXT,
                       code TEXT,
                       method TEXT,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       expires_at DATETIME,
                       verified INTEGER DEFAULT 0);
CREATE TABLE dev_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_username TEXT,
        to_username TEXT,
        message TEXT,
        message_type TEXT DEFAULT 'info',
        read INTEGER DEFAULT 0,
        parent_message_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_message_id) REFERENCES dev_messages(id)
    );
CREATE TABLE dev_terminal_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        command TEXT,
        output TEXT,
        exit_code INTEGER,
        duration_ms INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE dev_ai_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        session_id TEXT,
        role TEXT,
        message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_clinician_id ON users(clinician_id);
CREATE INDEX idx_mood_logs_username ON mood_logs(username);
CREATE INDEX idx_mood_logs_entrestamp ON mood_logs(entrestamp);
CREATE INDEX idx_mood_logs_username_entrestamp ON mood_logs(username, entrestamp);
CREATE INDEX idx_sessions_username ON sessions(username);
CREATE INDEX idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX idx_chat_history_chat_session_id ON chat_history(chat_session_id);
CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp);
CREATE INDEX idx_chat_sessions_username ON chat_sessions(username);
CREATE INDEX idx_chat_sessions_username_active ON chat_sessions(username, is_active);
CREATE INDEX idx_alerts_username ON alerts(username);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_username_status ON alerts(username, status);
CREATE INDEX idx_patient_approvals_clinician ON patient_approvals(clinician_username);
CREATE INDEX idx_patient_approvals_patient ON patient_approvals(patient_username);
CREATE INDEX idx_patient_approvals_status ON patient_approvals(status);
CREATE INDEX idx_patient_approvals_clinician_status ON patient_approvals(clinician_username, status);
CREATE INDEX idx_clinical_scales_username ON clinical_scales(username);
CREATE INDEX idx_clinical_scales_entry_timestamp ON clinical_scales(entry_timestamp);
CREATE INDEX idx_notifications_recipient ON notifications(recipient_username);
CREATE INDEX idx_notifications_read ON notifications(read);
CREATE INDEX idx_notifications_recipient_read ON notifications(recipient_username, read);
CREATE INDEX idx_appointments_clinician ON appointments(clinician_username);
CREATE INDEX idx_appointments_patient ON appointments(patient_username);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_audit_logs_username ON audit_logs(username);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_gratitude_logs_username ON gratitude_logs(username);
CREATE INDEX idx_cbt_records_username ON cbt_records(username);
CREATE INDEX idx_community_posts_username ON community_posts(username);
CREATE INDEX idx_community_posts_timestamp ON community_posts(entry_timestamp);
CREATE INDEX idx_community_replies_post_id ON community_replies(post_id);
CREATE INDEX idx_clinician_notes_clinician ON clinician_notes(clinician_username);
CREATE INDEX idx_clinician_notes_patient ON clinician_notes(patient_username);
CREATE INDEX idx_verification_codes_identifier ON verification_codes(identifier);
