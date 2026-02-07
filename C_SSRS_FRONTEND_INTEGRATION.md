# C-SSRS Frontend Integration & AI Risk Detection

**Status:** Design & Implementation Plan  
**Date:** February 7, 2026  

---

## 🎯 Overview

The C-SSRS assessment will be integrated into the Healing Space web interface in **three complementary ways**:

1. **Standalone Assessment Screen** - Formal scheduled C-SSRS evaluation
2. **In-Chat Risk Detection** - AI monitors therapy conversation for risk signs
3. **Contextual Assessment Trigger** - System prompts assessment if high-risk language detected

---

## 📍 Part 1: Standalone C-SSRS Assessment Screen

### Location in Interface
**New Tab: "Safety Check"** (between "Therapy" and "Mood Tracker")

```
┌─ Navigation Tabs ─────────────────────┐
│ Home | Therapy | Safety Check | Mood  │
│       (NEW)                            │
└────────────────────────────────────────┘
```

### UI/UX Flow

#### Step 1: Assessment Intro (5 seconds)
```
╔════════════════════════════════════╗
║   Safety & Risk Assessment         ║
║                                    ║
║  This is a 6-question assessment   ║
║  to help us understand how you're  ║
║  feeling and provide better support║
║                                    ║
║  ⏱️ Takes ~3 minutes               ║
║  🔒 Completely confidential        ║
║  📋 Results reviewed by clinician  ║
║                                    ║
║  [Start Assessment] [Maybe Later]  ║
╚════════════════════════════════════╝
```

#### Step 2: Individual Questions (6 screens)
```
╔════════════════════════════════════╗
║   Question 1 of 6                  ║
║                                    ║
║  Have you had any thoughts of      ║
║  killing yourself?                 ║
║                                    ║
║  ○ No, not at all                  ║
║  ○ Rare (1 day/month)              ║
║  ○ Infrequent (2-5 days/month)    ║
║  ○ Frequent (6+ days/month)        ║
║  ○ Almost every day                ║
║  ○ Every day or multiple times     ║
║                                    ║
║  [Back] [← Prev] [Next →]          ║
╚════════════════════════════════════╝
```

**Key Features:**
- One question per screen (focuses attention)
- Clear, non-judgmental language
- Visual progress bar (Q1/6, Q2/6, etc.)
- Back button to revise answers
- Estimated time: 3-4 minutes total

#### Step 3: Risk Result Screen

**If CRITICAL Risk:**
```
╔════════════════════════════════════╗
║   🚨 Assessment Complete           ║
║                                    ║
║   Risk Level: CRITICAL             ║
║   Score: 25/30                     ║
║                                    ║
║   ⚠️ You may be at immediate risk  ║
║                                    ║
║   Your clinician has been notified ║
║   and will contact you shortly.    ║
║                                    ║
║   In the meantime:                 ║
║   📞 Call Samaritans: 116 123      ║
║   🚨 Emergency: 999                ║
║                                    ║
║   [Complete Safety Plan]           ║
║   [Chat with Support]              ║
╚════════════════════════════════════╝
```

**If HIGH Risk:**
```
╔════════════════════════════════════╗
║   ⚠️ Assessment Complete           ║
║                                    ║
║   Risk Level: HIGH                 ║
║   Score: 13/30                     ║
║                                    ║
║   Your responses show elevated     ║
║   suicide risk. Your clinician     ║
║   will review this urgently.       ║
║                                    ║
║   [Create Safety Plan]             ║
║   [Chat with Support]              ║
║   [Manage Medications]             ║
╚════════════════════════════════════╝
```

**If MODERATE/LOW Risk:**
```
╔════════════════════════════════════╗
║   ✓ Assessment Complete            ║
║                                    ║
║   Risk Level: MODERATE             ║
║   Score: 5/30                      ║
║                                    ║
║   Your clinician will review your  ║
║   responses at your next visit.    ║
║                                    ║
║   Keep taking care of yourself.    ║
║                                    ║
║   [Return to Therapy]              ║
║   [Complete Mood Check]            ║
╚════════════════════════════════════╝
```

#### Step 4: Safety Planning (if HIGH/CRITICAL)

Modal form appears:
```
╔════════════════════════════════════╗
║   Create Your Safety Plan          ║
║                                    ║
║  1. Warning Signs (What tells you  ║
║     a crisis is developing?)       ║
║     [Text input]                   ║
║                                    ║
║  2. Internal Coping (What can you  ║
║     do alone?)                     ║
║     [Text input]                   ║
║                                    ║
║  3. Distraction Resources (Who &   ║
║     where to get away?)            ║
║     [Text input]                   ║
║                                    ║
║  4. People to Contact (Who can     ║
║     you call?)                     ║
║     [Add contacts - name/phone]    ║
║                                    ║
║  5. Professional Help (Emergency   ║
║     & clinician details)           ║
║     [Pre-filled with clinician     ║
║      contact info + 999]           ║
║                                    ║
║  6. Environment Safety (Remove     ║
║     access to means)               ║
║     [Text input]                   ║
║                                    ║
║  [Save Plan] [Save & Email]        ║
╚════════════════════════════════════╝
```

---

## 🤖 Part 2: AI Risk Detection During Chat

### How It Works

**Every message the patient sends is analyzed by the AI** for suicide risk indicators while providing therapy responses.

### Architecture

```
Patient Message
    ↓
┌─────────────────────────────────────┐
│ Therapy Chat API (/api/therapy/chat)│
└──────────────┬──────────────────────┘
               ↓
    ┌─────────────────────┐
    │  TherapistAI        │
    │  (Groq LLM)         │
    │  - Generate therapy │
    │    response         │
    │  - Score risk level │
    │    (0-100 scale)    │
    └──────────┬──────────┘
               ↓
    ┌─────────────────────┐
    │  SafetyMonitor      │
    │  - Check risk score │
    │  - Pattern detect   │
    │  - Trigger alerts   │
    └──────────┬──────────┘
               ↓
    If Risk Detected:
    - Log to database
    - Notify clinician
    - Trigger UI prompt
               ↓
    Return to Frontend:
    - Therapy response
    - Risk indicator
    - Suggested actions
```

### Risk Indicators Detected

The AI monitors for language suggesting:

**Suicidal Ideation:**
- "Want to kill myself"
- "Can't go on"
- "Hopeless/worthless"
- "Everyone would be better off without me"
- "How to end it"

**Planning/Intent:**
- "I have a plan"
- "I've decided when/how"
- "I've prepared"
- "I've said goodbye"
- "This is my last chance"

**Behavioral Changes:**
- "I've stopped taking meds"
- "Giving things away"
- "Saying goodbye"
- "Visit will be last time"

**Severe Distress:**
- "Can't breathe"
- "Chest pain"
- "Panic attack"
- "Losing control"

### Risk Score Algorithm

```javascript
// In therapy API response
{
    "response": "AI therapy message...",
    "risk_score": 35,           // 0-100 scale
    "risk_level": "moderate",   // low/moderate/high/critical
    "risk_indicators": [
        "mentions hopelessness",
        "expresses suicidal ideation"
    ],
    "suggested_action": "offer_assessment",
    "show_safety_banner": true
}
```

---

## 💻 Part 3: Frontend Implementation

### A. Chat Interface Enhancement

#### Real-time Risk Indicator

**During conversation, a subtle indicator appears:**

```
Chat Area (existing)
┌────────────────────────────────┐
│                                │
│ [Chat messages...]             │
│                                │
│ 🟢 Low Risk                    │ ← Realtime indicator
│ (Green dot for normal)          │
│                                │
└────────────────────────────────┘

Chat Area (if risk detected)
┌────────────────────────────────┐
│                                │
│ [Chat messages...]             │
│                                │
│ 🟠 Possible Risk Detected      │ ← Changes to orange
│ (Orange dot for concern)        │
│                                │
└────────────────────────────────┘
```

#### Code Location

**File:** `templates/index.html` (around line 9548, `sendMessage()` function)

**Current code:**
```javascript
const response = await fetch('/api/therapy/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
});

const data = await response.json();
```

**Enhanced code:**
```javascript
const response = await fetch('/api/therapy/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
});

const data = await response.json();

// NEW: Handle risk detection
if (data.risk_score && data.risk_score > 50) {
    updateRiskIndicator(data.risk_level);  // Update UI dot
    
    if (data.risk_level === 'high' || data.risk_level === 'critical') {
        showRiskPrompt(data);  // Offer assessment
    }
}
```

### B. Risk Prompt Modal

**When HIGH/CRITICAL risk detected in chat:**

```
╔════════════════════════════════════╗
║   ⚠️ We're Concerned              ║
║                                    ║
║  Your recent messages suggest     ║
║  you may be at risk.              ║
║                                    ║
║  Would you be willing to complete ║
║  a brief safety assessment so we  ║
║  can better understand and help?  ║
║                                    ║
║  [Yes, Start Assessment]          ║
║  [Remind Me Later]                ║
║  [I'm Safe, Dismiss]              ║
║                                    ║
║  If you're in immediate danger:   ║
║  📞 Call 999 or 116 123           ║
╚════════════════════════════════════╝
```

**Code to add:**
```javascript
function showRiskPrompt(riskData) {
    const modal = document.getElementById('riskPromptModal');
    const reason = riskData.risk_indicators.join(', ');
    
    document.getElementById('riskReason').innerText = reason;
    
    modal.style.display = 'block';
}

function acceptRiskAssessment() {
    // Hide chat, show C-SSRS assessment
    document.getElementById('therapyTab').style.display = 'none';
    document.getElementById('safetyCheckTab').style.display = 'block';
    
    // Scroll to safety tab
    document.getElementById('safetyCheckBtn').scrollIntoView();
}
```

### C. Safety Check Tab HTML

**Add to templates/index.html** (after therapyTab section):

```html
<div id="safetyCheckTab" class="tab-content" style="display:none;">
    <h3>Safety Assessment</h3>
    <p style="color: #666; margin-bottom: 20px;">
        A brief assessment to help us understand how you're feeling.
    </p>
    
    <!-- Assessment Progress -->
    <div class="progress-bar">
        <div id="assessmentProgress" class="progress-fill" style="width: 0%"></div>
    </div>
    <span id="progressText">Question 1 of 6</span>
    
    <!-- Question Container -->
    <div id="assessmentContainer" style="margin: 30px 0;">
        <!-- Dynamically populated by JavaScript -->
    </div>
    
    <!-- Navigation Buttons -->
    <div style="display: flex; gap: 10px; justify-content: space-between;">
        <button id="prevBtn" onclick="prevQuestion()" class="btn btn-secondary" style="display:none;">← Previous</button>
        <button id="skipBtn" onclick="skipAssessment()" class="btn btn-secondary">Maybe Later</button>
        <button id="nextBtn" onclick="nextQuestion()" class="btn">Next →</button>
    </div>
</div>
```

---

## 🔄 Part 4: Backend Integration Points

### 1. Therapy Chat API Enhancement

**File:** `api.py` (existing `/api/therapy/chat` endpoint around line 7000+)

**Add risk detection:**
```python
@app.route('/api/therapy/chat', methods=['POST'])
def therapy_chat():
    # ... existing code ...
    
    # NEW: Analyze for risk
    risk_analysis = SafetyMonitor.analyze_message(message)
    
    ai_response = TherapistAI.generate_response(message, wellness_data)
    
    return jsonify({
        'response': ai_response,
        'risk_score': risk_analysis['score'],        # 0-100
        'risk_level': risk_analysis['level'],        # low/moderate/high/critical
        'risk_indicators': risk_analysis['indicators'],
        'suggested_action': risk_analysis['action'],  # 'none'/'offer_assessment'/'require_assessment'
        'show_safety_banner': risk_analysis['show_banner']
    })
```

### 2. C-SSRS Assessment Start Endpoint

**File:** `api.py` - Use existing `/api/c-ssrs/start` endpoint

```python
@app.route('/api/c-ssrs/start', methods=['POST'])
def start_c_ssrs_assessment():
    # Returns 6 questions + assessment_id
```

### 3. C-SSRS Submit Endpoint

**File:** `api.py` - Use existing `/api/c-ssrs/submit` endpoint

```python
@app.route('/api/c-ssrs/submit', methods=['POST'])
def submit_c_ssrs_assessment():
    # Saves assessment, calculates risk, triggers alerts if HIGH/CRITICAL
```

---

## 🎨 Part 5: UI Components to Create

### JavaScript Functions Needed

```javascript
// 1. Assessment UI Management
function initSafetyCheckTab();
function displayQuestion(questionNum);
function nextQuestion();
function prevQuestion();
function skipAssessment();
function submitAssessment();

// 2. Risk Detection Display
function updateRiskIndicator(riskLevel);
function showRiskPrompt(riskData);
function dismissRiskPrompt();

// 3. Safety Plan Management
function startSafetyPlan();
function saveSafetyPlanSection(sectionId, content);
function submitSafetyPlan();

// 4. Assessment History
function loadAssessmentHistory();
function viewAssessment(assessmentId);
```

### CSS Styles Needed

```css
/* Safety Check Tab */
#safetyCheckTab { ... }

/* Risk Indicator */
.risk-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
}

.risk-indicator.low {
    background-color: #d4edda;
    color: #155724;
}

.risk-indicator.moderate {
    background-color: #fff3cd;
    color: #856404;
}

.risk-indicator.high {
    background-color: #f8d7da;
    color: #721c24;
}

.risk-indicator.critical {
    background-color: #f5c6cb;
    color: #721c24;
    animation: pulse 2s infinite;
}

/* Assessment Modal */
.assessment-question {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
}

.assessment-options {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin: 20px 0;
}

.assessment-option {
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s;
}

.assessment-option:hover {
    border-color: #667eea;
    background-color: #f5f5f5;
}

.assessment-option.selected {
    border-color: #667eea;
    background-color: #f0f4ff;
}
```

---

## 📱 Part 6: User Experience Flow

### Scenario 1: Patient Initiates Assessment

```
Patient clicks "Safety Check" tab
    ↓
Intro screen (3 seconds)
    ↓
Questions 1-6 (one per screen)
    ↓
Risk result displayed
    ↓
If HIGH/CRITICAL: Safety plan form opens
    ↓
Complete plan
    ↓
Clinician notified
```

### Scenario 2: AI Detects Risk During Chat

```
Patient says: "I don't see the point anymore"
    ↓
AI generates helpful response
    ↓
Backend detects risk language (risk_score = 65)
    ↓
Returns response + risk data
    ↓
Frontend shows risk indicator (🟠)
    ↓
If score > 60: Prompt appears
    ↓
Patient clicks "Start Assessment"
    ↓
[Same as Scenario 1 from here]
```

### Scenario 3: Patient Dismisses Risk Prompt

```
Risk prompt shows
    ↓
Patient clicks "Dismiss"
    ↓
System logs dismissal
    ↓
Continues monitoring
    ↓
If risk worsens: Escalates to clinician notification
```

---

## 🔐 Part 7: Privacy & Safety

### What Data is Collected?

✅ **Stored in Database:**
- Assessment responses (C-SSRS answers)
- Risk level
- Timestamp
- Clinician response

❌ **NOT Stored:**
- Chat message content (only metadata: length, timestamp, risk_score)
- Voice recordings (discarded after transcription)
- Patient notes (only wellness data if shared)

### GDPR Compliance

- Patient can export all C-SSRS assessments
- Patient can request deletion (with notice)
- Clinician can only see assigned patients
- Audit trail for all access

---

## 📊 Part 8: Clinician Dashboard

### What Clinicians See

**Dashboard View:**
```
┌─ Clinician Dashboard ─────────────┐
│                                   │
│ 🚨 Pending Alerts (2)             │
│ ├─ John Doe - CRITICAL            │
│ │  Risk Score: 25/30              │
│ │  Assessment: 5 min ago          │
│ │  [Review] [Respond]             │
│ │                                 │
│ └─ Jane Smith - HIGH              │
│    Risk Score: 13/30              │
│    Assessment: 2 hours ago        │
│    [Review] [Respond]             │
│                                   │
│ 📋 Recent Assessments             │
│ ├─ Patient A: MODERATE (3 days)   │
│ ├─ Patient B: LOW (5 days)        │
│ └─ Patient C: HIGH (1 day)        │
│                                   │
│ 📈 Risk Trends                    │
│ [Pie chart: Low/Moderate/High]    │
│                                   │
└───────────────────────────────────┘
```

---

## 🚀 Implementation Timeline

### Week 1: Frontend Structure
- [ ] Add "Safety Check" tab to HTML
- [ ] Create assessment UI components
- [ ] Create risk indicator components
- [ ] Add CSS styling

### Week 2: JavaScript Logic
- [ ] Build assessment question flow
- [ ] Build result display logic
- [ ] Build safety plan form logic
- [ ] Add localStorage for draft saves

### Week 3: API Integration
- [ ] Connect to /api/c-ssrs/start
- [ ] Connect to /api/c-ssrs/submit
- [ ] Add risk score handling
- [ ] Test all endpoints

### Week 4: AI Risk Detection
- [ ] Enhance therapy chat API
- [ ] Add SafetyMonitor analysis
- [ ] Build risk prompt modal
- [ ] Test with sample conversations

### Week 5: Testing & Polish
- [ ] UX testing with sample users
- [ ] Cross-browser testing
- [ ] Mobile responsiveness
- [ ] Performance optimization

---

## 📋 Summary

The C-SSRS assessment will be integrated as:

1. **Standalone Tab** - Formal scheduled assessments (Safety Check)
2. **AI Detection** - Background monitoring during therapy chat
3. **Contextual Trigger** - Prompts assessment when risk detected
4. **Safety Planning** - Automated for HIGH/CRITICAL cases
5. **Clinician Dashboard** - Alerts & response tracking

This provides **both active assessment (patient initiates) AND passive monitoring (AI detects)**, ensuring comprehensive coverage of suicide risk in the platform.

