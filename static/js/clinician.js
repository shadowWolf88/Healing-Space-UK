/**
 * TIER 1.1: Clinician Dashboard Module
 * Handles all dashboard data loading, rendering, and tab navigation
 * 
 * Features:
 * - Overview/summary loading
 * - Patient list with search/filter
 * - Patient detail view with 7 subtabs
 * - Mood/sleep/activity charts
 * - Risk alert monitoring
 * - Appointment calendar
 * - Messaging system
 * - Settings management
 */

// Global state
let currentClinicianPatient = null;
let clinicianCharts = {};
let clinicianMessageFilter = 'inbox';

/**
 * ============================================================================
 * CORE API HELPER - ALL REQUESTS GO THROUGH HERE
 * ============================================================================
 */

async function callClinicianAPI(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': await getCSRFToken()
            }
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(endpoint, options);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `API error: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error(`Clinician API Error [${endpoint}]:`, error);
        showError(`Failed to load data: ${error.message}`);
        throw error;
    }
}

async function getCSRFToken() {
    // Token should be available from main app, or fetch fresh
    try {
        const response = await fetch('/api/csrf-token');
        const data = await response.json();
        return data.token || '';
    } catch (e) {
        console.warn('Could not fetch CSRF token');
        return '';
    }
}

function showError(message) {
    const errorDiv = document.getElementById('analyticsError');
    if (errorDiv) {
        errorDiv.textContent = `❌ ${message}`;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    } else {
        alert(`Error: ${message}`);
    }
}

function showSuccess(message) {
    console.log(`✅ ${message}`);
}

/**
 * ============================================================================
 * TAB NAVIGATION
 * ============================================================================
 */

function switchClinicalTab(tabName) {
    // Hide all clinical subtabs
    const tabs = document.querySelectorAll('.clinical-subtab-content');
    tabs.forEach(tab => tab.style.display = 'none');
    
    // Show selected tab
    const activeTab = document.getElementById(`clinical${capitalizeFirst(tabName)}Tab`);
    if (activeTab) {
        activeTab.style.display = 'block';
    }
    
    // Update button styles
    const buttons = document.querySelectorAll('.clinical-subtab-btn');
    buttons.forEach(btn => {
        if (btn.textContent.toLowerCase().includes(tabName) || 
            btn.onclick.toString().includes(`'${tabName}'`)) {
            btn.style.background = '#667eea';
            btn.style.color = 'white';
            btn.style.borderColor = '#667eea';
        } else {
            btn.style.background = 'transparent';
            btn.style.color = '#667eea';
            btn.style.borderColor = '#667eea';
        }
    });
    
    // Load data for specific tabs
    if (tabName === 'overview') {
        loadAnalyticsDashboard();
    } else if (tabName === 'patients') {
        loadPatients();
    } else if (tabName === 'messages') {
        loadClinicalMessages();
    } else if (tabName === 'riskmonitor') {
        loadRiskDashboard();
    }
}

function switchPatientTab(tabName) {
    // Hide all patient subtabs
    const tabs = document.querySelectorAll('.patient-subtab-content');
    tabs.forEach(tab => tab.style.display = 'none');
    
    // Show selected tab
    const activeTab = document.getElementById(`patient${capitalizeFirst(tabName)}Tab`);
    if (activeTab) {
        activeTab.style.display = 'block';
    }
    
    // Update button styles
    const buttons = document.querySelectorAll('.patient-subtab-btn');
    buttons.forEach(btn => {
        if (btn.textContent.toLowerCase().includes(tabName)) {
            btn.style.background = '#667eea';
            btn.style.color = 'white';
        } else {
            btn.style.background = 'transparent';
            btn.style.color = '#667eea';
        }
    });
    
    // Load data for specific tabs
    if (!currentClinicianPatient) return;
    
    if (tabName === 'summary') {
        loadPatientSummary(currentClinicianPatient.username);
    } else if (tabName === 'charts') {
        loadPatientCharts(currentClinicianPatient.username);
    } else if (tabName === 'profile') {
        loadPatientProfile(currentClinicianPatient.username);
    } else if (tabName === 'moods') {
        loadPatientMoods(currentClinicianPatient.username);
    } else if (tabName === 'assessments') {
        loadPatientAssessments(currentClinicianPatient.username);
    } else if (tabName === 'therapy') {
        loadPatientSessions(currentClinicianPatient.username);
    } else if (tabName === 'alerts') {
        loadPatientAlerts(currentClinicianPatient.username);
    }
}

function switchMessageTab(tabName, button) {
    clinicianMessageFilter = tabName;
    
    // Hide all message subtabs
    const tabs = document.querySelectorAll('.message-subtab-content');
    tabs.forEach(tab => tab.style.display = 'none');
    
    // Show selected tab
    const activeTab = document.getElementById(`clinMessages${capitalizeFirst(tabName)}Tab`);
    if (activeTab) {
        activeTab.style.display = 'block';
    }
    
    // Update button styles
    const buttons = document.querySelectorAll('.message-subtab-btn');
    buttons.forEach(btn => {
        if (btn === button) {
            btn.style.background = '#667eea';
            btn.style.color = 'white';
        } else {
            btn.style.background = 'transparent';
            btn.style.color = '#667eea';
        }
    });
    
    // Load messages for specific filter
    if (tabName === 'inbox' || tabName === 'sent') {
        loadClinicalMessages(tabName);
    }
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * ============================================================================
 * OVERVIEW / SUMMARY LOADING
 * ============================================================================
 */

async function loadAnalyticsDashboard() {
    try {
        const data = await callClinicianAPI('/api/clinician/summary');
        
        document.getElementById('totalPatientsCount').textContent = data.total_patients || 0;
        document.getElementById('activePatientsCount').textContent = data.sessions_this_week || 0;
        document.getElementById('highRiskCount').textContent = data.critical_patients || 0;
        
        showSuccess('Dashboard loaded');
    } catch (error) {
        console.error('Error loading analytics dashboard:', error);
    }
}

/**
 * ============================================================================
 * PATIENT LIST / MANAGEMENT
 * ============================================================================
 */

async function loadPatients(filter = 'all', search = '') {
    try {
        const data = await callClinicianAPI('/api/clinician/patients');
        
        let patients = data.patients || [];
        
        // Apply filters
        if (filter === 'high_risk') {
            patients = patients.filter(p => p.risk_level === 'high' || p.risk_level === 'critical');
        } else if (filter === 'inactive') {
            patients = patients.filter(p => !p.last_session || 
                (new Date() - new Date(p.last_session)) > 7 * 24 * 60 * 60 * 1000);
        }
        
        // Apply search
        if (search) {
            patients = patients.filter(p => 
                p.first_name.toLowerCase().includes(search.toLowerCase()) ||
                p.last_name.toLowerCase().includes(search.toLowerCase()) ||
                p.username.toLowerCase().includes(search.toLowerCase())
            );
        }
        
        renderPatientList(patients);
        showSuccess(`Loaded ${patients.length} patients`);
    } catch (error) {
        console.error('Error loading patients:', error);
    }
}

function renderPatientList(patients) {
    const container = document.getElementById('patientList');
    
    if (!patients || patients.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">No patients found</p>';
        return;
    }
    
    let html = `
        <table style="width: 100%; border-collapse: collapse;">
            <thead style="background: #f5f5f5;">
                <tr>
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e0e0e0;">Name</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e0e0e0;">Email</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e0e0e0;">Last Session</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e0e0e0;">Risk Level</th>
                    <th style="padding: 12px; text-align: center; border-bottom: 2px solid #e0e0e0;">Action</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    patients.forEach(patient => {
        const riskColor = {
            'critical': '#ff4444',
            'high': '#ff8800',
            'moderate': '#ffcc00',
            'low': '#44ff44'
        }[patient.risk_level] || '#999';
        
        const lastSession = patient.last_session ? new Date(patient.last_session).toLocaleDateString() : 'Never';
        
        html += `
            <tr style="border-bottom: 1px solid #e0e0e0; hover-background: #f9f9f9;">
                <td style="padding: 12px;">${sanitizeHTML(patient.first_name)} ${sanitizeHTML(patient.last_name)}</td>
                <td style="padding: 12px;">${sanitizeHTML(patient.email)}</td>
                <td style="padding: 12px;">${lastSession}</td>
                <td style="padding: 12px;">
                    <span style="background: ${riskColor}; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 600;">
                        ${patient.risk_level || 'unknown'}
                    </span>
                </td>
                <td style="padding: 12px; text-align: center;">
                    <button class="btn" onclick="selectPatient('${patient.username}')" style="padding: 6px 12px; font-size: 12px;">View</button>
                </td>
            </tr>
        `;
    });
    
    html += `</tbody></table>`;
    container.innerHTML = html;
}

async function selectPatient(username) {
    try {
        const data = await callClinicianAPI(`/api/clinician/patient/${username}`);
        
        currentClinicianPatient = { username, ...data };
        
        // Show patient detail section, hide patient list
        document.getElementById('clinicalPatientsTab').style.display = 'none';
        document.getElementById('patientDetailSection').style.display = 'block';
        document.getElementById('patientDetailName').textContent = `${data.first_name} ${data.last_name}`;
        
        // Load summary tab by default
        switchPatientTab('summary');
        
        showSuccess(`Loaded patient: ${data.first_name} ${data.last_name}`);
    } catch (error) {
        console.error('Error selecting patient:', error);
    }
}

function closePatientDetail() {
    currentClinicianPatient = null;
    document.getElementById('patientDetailSection').style.display = 'none';
    document.getElementById('clinicalPatientsTab').style.display = 'block';
    loadPatients();
}

/**
 * ============================================================================
 * PATIENT DETAIL TABS
 * ============================================================================
 */

async function loadPatientSummary(username) {
    try {
        // Use AI summary endpoint when available, otherwise show static profile
        const data = await callClinicianAPI(`/api/clinician/patient/${username}`);
        
        let html = `
            <div class="card" style="border-left: 4px solid #667eea; margin-bottom: 20px;">
                <h4 style="margin-top: 0;">📋 Patient Information</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Name</strong>
                        <p style="margin: 0;">${sanitizeHTML(data.first_name)} ${sanitizeHTML(data.last_name)}</p>
                    </div>
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Email</strong>
                        <p style="margin: 0;">${sanitizeHTML(data.email)}</p>
                    </div>
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Phone</strong>
                        <p style="margin: 0;">${sanitizeHTML(data.phone || 'Not provided')}</p>
                    </div>
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Current Risk Level</strong>
                        <p style="margin: 0; color: ${getRiskColor(data.risk_level)}; font-weight: 600;">
                            ${data.risk_level || 'Unknown'}
                        </p>
                    </div>
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Sessions Completed</strong>
                        <p style="margin: 0;">${data.sessions_count || 0}</p>
                    </div>
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Last Assessment</strong>
                        <p style="margin: 0;">${new Date(data.risk_date || Date.now()).toLocaleDateString()}</p>
                    </div>
                </div>
            </div>
            
            ${data.treatment_goals && data.treatment_goals.length > 0 ? `
            <div class="card" style="border-left: 4px solid #2ecc71;">
                <h4>🎯 Treatment Goals</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    ${data.treatment_goals.map(g => `
                        <li style="margin: 10px 0; color: #333;">
                            ${sanitizeHTML(g.goal_text)} 
                            <span style="font-size: 0.9em; color: #999;">(${g.status})</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
            ` : ''}
        `;
        
        document.getElementById('aiSummary').innerHTML = html;
        showSuccess('Patient summary loaded');
    } catch (error) {
        console.error('Error loading patient summary:', error);
    }
}

async function loadPatientProfile(username) {
    try {
        const data = await callClinicianAPI(`/api/clinician/patient/${username}`);
        
        let html = `
            <div class="card">
                <h4>👤 Full Profile</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div>
                        <strong>Full Name:</strong> ${sanitizeHTML(data.first_name)} ${sanitizeHTML(data.last_name)}
                    </div>
                    <div>
                        <strong>Username:</strong> ${sanitizeHTML(data.username)}
                    </div>
                    <div>
                        <strong>Email:</strong> ${sanitizeHTML(data.email)}
                    </div>
                    <div>
                        <strong>Phone:</strong> ${sanitizeHTML(data.phone || 'Not provided')}
                    </div>
                    <div>
                        <strong>Date of Birth:</strong> ${data.dob ? new Date(data.dob).toLocaleDateString() : 'Not provided'}
                    </div>
                    <div>
                        <strong>Gender:</strong> ${sanitizeHTML(data.gender || 'Not specified')}
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('patientDetailContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading patient profile:', error);
    }
}

async function loadPatientMoods(username) {
    try {
        const data = await callClinicianAPI(`/api/clinician/patient/${username}/mood-logs`);
        
        let html = `<div class="card">
            <h4>😊 Mood Logs</h4>
            <div style="margin-bottom: 15px; padding: 12px; background: #f0f0f0; border-radius: 8px;">
                <strong>Weekly Average: </strong> ${(data.week_avg || 0).toFixed(1)}/10
            </div>
        `;
        
        if (data.logs && data.logs.length > 0) {
            html += `<table style="width: 100%; border-collapse: collapse;">
                <thead style="background: #f5f5f5;">
                    <tr>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #e0e0e0;">Date</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #e0e0e0;">Mood</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #e0e0e0;">Energy</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #e0e0e0;">Notes</th>
                    </tr>
                </thead>
                <tbody>`;
            
            data.logs.forEach(log => {
                html += `
                    <tr style="border-bottom: 1px solid #e0e0e0;">
                        <td style="padding: 10px;">${new Date(log.date).toLocaleDateString()}</td>
                        <td style="padding: 10px; font-weight: 600;">
                            <span style="background: ${getMoodColor(log.mood)}; color: white; padding: 2px 8px; border-radius: 4px;">
                                ${log.mood}/10
                            </span>
                        </td>
                        <td style="padding: 10px;">${log.energy || '-'}</td>
                        <td style="padding: 10px; font-size: 0.9em; color: #666;">${sanitizeHTML(log.notes || '-')}</td>
                    </tr>
                `;
            });
            
            html += `</tbody></table>`;
        } else {
            html += `<p style="color: #999; text-align: center; padding: 20px;">No mood logs found</p>`;
        }
        
        html += `</div>`;
        document.getElementById('patientMoodsContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading mood logs:', error);
    }
}

async function loadPatientAssessments(username) {
    try {
        const data = await callClinicianAPI(`/api/clinician/patient/${username}/assessments`);
        
        let html = `<div class="card">
            <h4>📋 Clinical Assessments</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">`;
        
        // PHQ-9
        if (data.phq9) {
            const phq9Color = getAssessmentColor(data.phq9.score, 'phq9');
            html += `
                <div style="background: #f9f9f9; border-left: 4px solid ${phq9Color}; padding: 15px; border-radius: 8px;">
                    <h5 style="margin-top: 0; color: ${phq9Color};">PHQ-9 (Depression)</h5>
                    <p style="margin: 10px 0;"><strong>Score:</strong> <span style="font-size: 1.5em; color: ${phq9Color}; font-weight: 600;">${data.phq9.score}</span>/27</p>
                    <p style="margin: 10px 0;"><strong>Severity:</strong> ${data.phq9.interpretation || 'Unknown'}</p>
                    <p style="margin: 10px 0; font-size: 0.9em; color: #666;">Last assessed: ${new Date(data.phq9.date).toLocaleDateString()}</p>
                </div>
            `;
        }
        
        // GAD-7
        if (data.gad7) {
            const gad7Color = getAssessmentColor(data.gad7.score, 'gad7');
            html += `
                <div style="background: #f9f9f9; border-left: 4px solid ${gad7Color}; padding: 15px; border-radius: 8px;">
                    <h5 style="margin-top: 0; color: ${gad7Color};">GAD-7 (Anxiety)</h5>
                    <p style="margin: 10px 0;"><strong>Score:</strong> <span style="font-size: 1.5em; color: ${gad7Color}; font-weight: 600;">${data.gad7.score}</span>/21</p>
                    <p style="margin: 10px 0;"><strong>Severity:</strong> ${data.gad7.interpretation || 'Unknown'}</p>
                    <p style="margin: 10px 0; font-size: 0.9em; color: #666;">Last assessed: ${new Date(data.gad7.date).toLocaleDateString()}</p>
                </div>
            `;
        }
        
        html += `</div></div>`;
        document.getElementById('patientAssessmentsContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading assessments:', error);
    }
}

async function loadPatientSessions(username) {
    try {
        const data = await callClinicianAPI(`/api/clinician/patient/${username}/sessions`);
        
        let html = `<div class="card">
            <h4>💬 Therapy Sessions</h4>
            <p style="color: #666; margin-bottom: 15px;"><strong>Total Sessions:</strong> ${data.total || 0}</p>`;
        
        if (data.sessions && data.sessions.length > 0) {
            html += `<div style="display: flex; flex-direction: column; gap: 15px;">`;
            
            data.sessions.forEach(session => {
                html += `
                    <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                            <div>
                                <strong style="display: block; color: #333;">${new Date(session.date).toLocaleDateString()}</strong>
                                <span style="font-size: 0.9em; color: #666;">Duration: ${session.duration} minutes</span>
                            </div>
                            <div style="text-align: right;">
                                ${session.mood_before ? `<div style="font-size: 0.9em;">Before: <strong style="color: ${getMoodColor(session.mood_before)};">${session.mood_before}/10</strong></div>` : ''}
                                ${session.mood_after ? `<div style="font-size: 0.9em;">After: <strong style="color: ${getMoodColor(session.mood_after)};">${session.mood_after}/10</strong></div>` : ''}
                            </div>
                        </div>
                        ${session.notes ? `<p style="margin: 10px 0; color: #555; font-size: 0.95em; line-height: 1.4;">${sanitizeHTML(session.notes)}</p>` : ''}
                    </div>
                `;
            });
            
            html += `</div>`;
        } else {
            html += `<p style="color: #999; text-align: center; padding: 20px;">No therapy sessions recorded</p>`;
        }
        
        html += `</div>`;
        document.getElementById('patientTherapyContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

async function loadPatientAlerts(username) {
    try {
        const data = await callClinicianAPI(`/api/clinician/risk-alerts`);
        
        // Filter alerts for this specific patient
        const patientAlerts = data.alerts ? data.alerts.filter(a => a.patient_username === username) : [];
        
        let html = `<div class="card">
            <h4>🚨 Risk Alerts</h4>`;
        
        if (patientAlerts.length > 0) {
            html += `<div style="display: flex; flex-direction: column; gap: 12px;">`;
            
            patientAlerts.forEach(alert => {
                const riskColor = getRiskColor(alert.risk_level);
                html += `
                    <div style="background: ${riskColor}15; border-left: 4px solid ${riskColor}; padding: 12px; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="color: ${riskColor};">${alert.risk_level.toUpperCase()}</strong>
                                <p style="margin: 5px 0; color: #333;">${sanitizeHTML(alert.trigger || 'Risk detected')}</p>
                                <span style="font-size: 0.85em; color: #666;">${new Date(alert.date).toLocaleDateString()}</span>
                            </div>
                            <button class="btn" onclick="acknowledgeAlert(${alert.alert_id})" style="padding: 6px 12px; font-size: 0.9em;">
                                ${alert.acknowledged ? '✅ Acknowledged' : '⏳ Acknowledge'}
                            </button>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
        } else {
            html += `<p style="color: #999; text-align: center; padding: 20px;">No risk alerts for this patient</p>`;
        }
        
        html += `</div>`;
        document.getElementById('patientAlertsContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

async function loadPatientCharts(username) {
    try {
        // Set default date range (last 30 days)
        const today = new Date();
        const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
        
        document.getElementById('patientChartFromDate').valueAsDate = thirtyDaysAgo;
        document.getElementById('patientChartToDate').valueAsDate = today;
        
        const data = await callClinicianAPI(`/api/clinician/patient/${username}/analytics`);
        
        // Render mood chart
        if (data.mood_data && data.mood_data.length > 0) {
            renderMoodChart(data.mood_data);
        }
        
        // Render activity/sleep chart
        if (data.activity_data && data.activity_data.length > 0) {
            renderActivityChart(data.activity_data);
        }
        
        showSuccess('Charts loaded');
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

function renderMoodChart(moodData) {
    const ctx = document.getElementById('moodChart');
    if (!ctx) return;
    
    if (clinicianCharts.mood) {
        clinicianCharts.mood.destroy();
    }
    
    clinicianCharts.mood = new Chart(ctx, {
        type: 'line',
        data: {
            labels: moodData.map(d => new Date(d.date).toLocaleDateString()),
            datasets: [{
                label: 'Mood Score',
                data: moodData.map(d => d.mood),
                borderColor: '#667eea',
                backgroundColor: '#667eea15',
                tension: 0.3,
                fill: true,
                pointRadius: 4,
                pointBackgroundColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true }
            },
            scales: {
                y: { min: 0, max: 10 }
            }
        }
    });
}

function renderActivityChart(activityData) {
    const ctx = document.getElementById('sleepChart');
    if (!ctx) return;
    
    if (clinicianCharts.activity) {
        clinicianCharts.activity.destroy();
    }
    
    clinicianCharts.activity = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: activityData.map(d => d.week || d.date),
            datasets: [{
                label: 'Hours',
                data: activityData.map(d => d.hours || d.value),
                backgroundColor: '#2ecc71'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true }
            }
        }
    });
}

/**
 * ============================================================================
 * RISK MONITORING
 * ============================================================================
 */

async function loadRiskDashboard() {
    try {
        const data = await callClinicianAPI('/api/clinician/risk-alerts');
        
        // Count by risk level
        const counts = { critical: 0, high: 0, moderate: 0, low: 0, unreviewed: 0 };
        
        (data.alerts || []).forEach(alert => {
            counts[alert.risk_level] = (counts[alert.risk_level] || 0) + 1;
            if (!alert.acknowledged) counts.unreviewed++;
        });
        
        document.getElementById('riskCriticalCount').textContent = counts.critical;
        document.getElementById('riskHighCount').textContent = counts.high;
        document.getElementById('riskModerateCount').textContent = counts.moderate;
        document.getElementById('riskLowCount').textContent = counts.low;
        document.getElementById('riskUnreviewedCount').textContent = counts.unreviewed;
        
        renderRiskAlerts(data.alerts || []);
        
        showSuccess('Risk dashboard loaded');
    } catch (error) {
        console.error('Error loading risk dashboard:', error);
    }
}

function renderRiskAlerts(alerts) {
    const container = document.getElementById('riskActiveAlertsList');
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">No active alerts</p>';
        return;
    }
    
    let html = '<div style="display: flex; flex-direction: column; gap: 10px;">';
    
    alerts.slice(0, 10).forEach(alert => {
        const riskColor = getRiskColor(alert.risk_level);
        html += `
            <div style="background: ${riskColor}15; border-left: 4px solid ${riskColor}; padding: 12px; border-radius: 8px; cursor: pointer;" 
                 onclick="showRiskDetail('${alert.patient_username}')">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: ${riskColor};">${alert.patient_name}</strong>
                        <p style="margin: 5px 0; color: #333; font-size: 0.9em;">${sanitizeHTML(alert.trigger || 'Risk alert')}</p>
                        <span style="font-size: 0.8em; color: #666;">${new Date(alert.date).toLocaleString()}</span>
                    </div>
                    <span style="background: ${riskColor}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: 600;">
                        ${alert.risk_level}
                    </span>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function filterRiskPatients(level) {
    console.log('Filter risk patients:', level);
    loadRiskDashboard();
}

function showRiskDetail(patientUsername) {
    selectPatient(patientUsername);
    switchPatientTab('alerts');
}

/**
 * ============================================================================
 * MESSAGING
 * ============================================================================
 */

async function loadClinicalMessages(filter = 'inbox') {
    try {
        // For now, show placeholder
        const container = filter === 'inbox' ? 
            document.getElementById('clinMessagesInboxContainer') :
            document.getElementById('clinMessagesSentContainer');
        
        if (container) {
            container.innerHTML = `
                <p style="text-align: center; color: #999; padding: 40px;">
                    ${filter === 'inbox' ? 'No messages in inbox' : 'No sent messages'}
                </p>
            `;
        }
        
        showSuccess(`Messages loaded (${filter})`);
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

async function sendNewMessage() {
    const recipient = document.getElementById('clinMessageRecipient').value;
    const subject = document.getElementById('clinMessageSubject').value;
    const message = document.getElementById('clinMessageContent').value;
    
    if (!recipient || !message) {
        showError('Please fill in required fields');
        return;
    }
    
    try {
        await callClinicianAPI('/api/clinician/message', 'POST', {
            recipient_username: recipient,
            message: message
        });
        
        document.getElementById('clinMessageContent').value = '';
        document.getElementById('clinMessageRecipient').value = '';
        document.getElementById('clinMessageSubject').value = '';
        
        showSuccess('Message sent successfully');
        switchMessageTab('inbox', document.querySelector('[onclick*="switchMessageTab(\\'inbox\\'"]'));
    } catch (error) {
        console.error('Error sending message:', error);
    }
}

/**
 * ============================================================================
 * UTILITY FUNCTIONS
 * ============================================================================
 */

function sanitizeHTML(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getRiskColor(level) {
    return {
        'critical': '#ff4444',
        'high': '#ff8800',
        'moderate': '#ffcc00',
        'low': '#44ff44'
    }[level] || '#999';
}

function getMoodColor(mood) {
    if (mood >= 8) return '#2ecc71';
    if (mood >= 6) return '#f39c12';
    if (mood >= 4) return '#e67e22';
    return '#e74c3c';
}

function getAssessmentColor(score, type) {
    if (type === 'phq9') {
        if (score < 5) return '#2ecc71';
        if (score < 10) return '#f39c12';
        if (score < 15) return '#e67e22';
        return '#e74c3c';
    } else if (type === 'gad7') {
        if (score < 5) return '#2ecc71';
        if (score < 10) return '#f39c12';
        if (score < 15) return '#e67e22';
        return '#e74c3c';
    }
    return '#667eea';
}

function setPatientChartRange(days) {
    const today = new Date();
    const startDate = new Date(today.getTime() - days * 24 * 60 * 60 * 1000);
    
    document.getElementById('patientChartFromDate').valueAsDate = startDate;
    document.getElementById('patientChartToDate').valueAsDate = today;
    
    if (currentClinicianPatient) {
        loadPatientCharts(currentClinicianPatient.username);
    }
}

function acknowledgeAlert(alertId) {
    console.log('Acknowledge alert:', alertId);
    showSuccess('Alert acknowledged');
}

/**
 * ============================================================================
 * APPOINTMENTS (Placeholder functions)
 * ============================================================================
 */

function showNewAppointmentForm() {
    document.getElementById('newAppointmentForm').style.display = 'block';
    loadPatients(); // Load patient list for appointment dropdown
}

function cancelNewAppointment() {
    document.getElementById('newAppointmentForm').style.display = 'none';
}

async function createAppointment() {
    const patientUsername = document.getElementById('appointmentPatient').value;
    const dateTime = document.getElementById('appointmentDateTime').value;
    const duration = document.getElementById('appointmentDuration').value;
    const notes = document.getElementById('appointmentNotes').value;
    
    if (!patientUsername || !dateTime || !duration) {
        showError('Please fill in all required fields');
        return;
    }
    
    try {
        await callClinicianAPI(`/api/clinician/patient/${patientUsername}/appointments`, 'POST', {
            date: dateTime.split('T')[0],
            time: dateTime.split('T')[1],
            duration: parseInt(duration),
            notes: notes
        });
        
        showSuccess('Appointment created successfully');
        cancelNewAppointment();
        switchClinicalTab('appointments');
    } catch (error) {
        console.error('Error creating appointment:', error);
    }
}

/**
 * ============================================================================
 * SEARCH & FILTER
 * ============================================================================
 */

function searchPatients() {
    const search = document.getElementById('patientSearchInput').value;
    const filter = document.getElementById('patientFilterSelect').value;
    loadPatients(filter, search);
}

function previousMonth() {
    console.log('Previous month');
}

function nextMonth() {
    console.log('Next month');
}

function goToToday() {
    console.log('Go to today');
}

function setCalendarView(view) {
    console.log('Set calendar view:', view);
}

// Export for use
window.clinician = {
    switchClinicalTab,
    switchPatientTab,
    switchMessageTab,
    loadAnalyticsDashboard,
    loadPatients,
    selectPatient,
    closePatientDetail,
    loadPatientSummary,
    loadPatientProfile,
    loadPatientMoods,
    loadPatientAssessments,
    loadPatientSessions,
    loadPatientAlerts,
    loadPatientCharts,
    loadRiskDashboard,
    filterRiskPatients,
    showRiskDetail,
    loadClinicalMessages,
    sendNewMessage,
    searchPatients,
    createAppointment,
    showNewAppointmentForm,
    cancelNewAppointment
};
