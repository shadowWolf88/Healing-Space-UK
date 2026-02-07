# C-SSRS Frontend Implementation - Visual Guide

---

## 🎯 Three Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                   Healing Space Patient Interface                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📱 Navigation Tabs                                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Home │ Therapy │ Safety Check (NEW) │ Mood │ Settings    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │  🎯 INTEGRATION POINT 1: Chat with AI Detection           │ │
│  │  ────────────────────────────────────────────            │ │
│  │                                                            │ │
│  │  Patient: "I don't think I can go on anymore"            │ │
│  │                                                            │ │
│  │  [Background: AI analyzes risk_score = 65]               │ │
│  │                                                            │ │
│  │  🟠 Risk Detected (indicator shows)                      │ │
│  │                                                            │ │
│  │  AI: "I hear that you're struggling. Many people feel    │ │
│  │  this way, and there is help available..."              │ │
│  │                                                            │ │
│  │  [Assessment Prompt Modal]                               │ │
│  │  ┌──────────────────────────────────────┐                │ │
│  │  │ ⚠️ We're Concerned                   │                │ │
│  │  │ Your messages suggest you might be   │                │ │
│  │  │ at risk. Would you like to complete │                │ │
│  │  │ a safety assessment?                 │                │ │
│  │  │                                      │                │ │
│  │  │ [Yes] [Dismiss] [Call 999]          │                │ │
│  │  └──────────────────────────────────────┘                │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │  🎯 INTEGRATION POINT 2: Safety Check Tab                 │ │
│  │  ────────────────────────────────────────               │ │
│  │  (Also accessible from main nav)                        │ │
│  │                                                            │ │
│  │  ┌─ Safety Assessment ──────────────────┐                │ │
│  │  │                                      │                │ │
│  │  │  Question 1 of 6                     │                │ │
│  │  │  ▓▓▓░░░░░░░░░░░░░░░░░ 16% Progress  │                │ │
│  │  │                                      │                │ │
│  │  │  Have you had any thoughts of        │                │ │
│  │  │  killing yourself?                   │                │ │
│  │  │                                      │                │ │
│  │  │  ○ No, not at all                    │                │ │
│  │  │  ○ Rare (1 day/month)                │                │ │
│  │  │  ● Infrequent (2-5 days/month)      │                │ │
│  │  │  ○ Frequent (6+ days/month)          │                │ │
│  │  │  ○ Almost every day                  │                │ │
│  │  │  ○ Every day or multiple times       │                │ │
│  │  │                                      │                │ │
│  │  │  [← Prev] [Skip] [Next →]           │                │ │
│  │  └─────────────────────────────────────┘                │ │
│  │                                                            │ │
│  │  After Q6: Risk Result                                   │ │
│  │  ┌─────────────────────────────────────┐                │ │
│  │  │ ✓ Assessment Complete               │                │ │
│  │  │                                     │                │ │
│  │  │ Risk Level: MODERATE (5/30)         │                │ │
│  │  │                                     │                │ │
│  │  │ Your clinician will review your     │                │ │
│  │  │ responses and contact you with any  │                │ │
│  │  │ next steps.                         │                │ │
│  │  │                                     │                │ │
│  │  │ [Return to Therapy]                 │                │ │
│  │  └─────────────────────────────────────┘                │ │
│  │                                                            │ │
│  │  If HIGH/CRITICAL: Safety Plan Form Appears              │ │
│  │  ┌─────────────────────────────────────┐                │ │
│  │  │ Create Your Safety Plan             │                │ │
│  │  │                                     │                │ │
│  │  │ 1. Warning Signs                    │                │ │
│  │  │    [Can't sleep, increased drinking]│                │ │
│  │  │                                     │                │ │
│  │  │ 2. Internal Coping                  │                │ │
│  │  │    [Call therapist, take a walk]    │                │ │
│  │  │                                     │                │ │
│  │  │ 3. Distraction Resources            │                │ │
│  │  │    [Visit friend, go to pub]        │                │ │
│  │  │                                     │                │ │
│  │  │ 4. People to Contact                │                │ │
│  │  │    [Add: Mum, GP, Crisis Team]      │                │ │
│  │  │                                     │                │ │
│  │  │ 5. Professional Help (pre-filled)   │                │ │
│  │  │    [Your Clinician: 01234 999999]   │                │ │
│  │  │    [Emergency: 999]                 │                │ │
│  │  │                                     │                │ │
│  │  │ 6. Environment Safety               │                │ │
│  │  │    [Ask mum to hold meds]           │                │ │
│  │  │                                     │                │ │
│  │  │ [Save Plan] [Email to Clinician]   │                │ │
│  │  └─────────────────────────────────────┘                │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │  🎯 INTEGRATION POINT 3: Clinician View                   │ │
│  │  ────────────────────────────────────                   │ │
│  │  (Separate clinician dashboard)                         │ │
│  │                                                            │ │
│  │  ┌─ Clinician Dashboard ──────────────┐                │ │
│  │  │                                    │                │ │
│  │  │ 🚨 Pending Alerts (2)              │                │ │
│  │  │                                    │                │ │
│  │  │ Patient: John Doe                  │                │ │
│  │  │ Risk: CRITICAL                     │                │ │
│  │  │ Score: 25/30                       │                │ │
│  │  │ Time: 5 minutes ago                │                │ │
│  │  │ Status: Awaiting response          │                │ │
│  │  │ [View Full Assessment] [Respond]   │                │ │
│  │  │                                    │                │ │
│  │  │ Patient: Jane Smith                │                │ │
│  │  │ Risk: HIGH                         │                │ │
│  │  │ Score: 13/30                       │                │ │
│  │  │ Time: 2 hours ago                  │                │ │
│  │  │ Status: Awaiting response          │                │ │
│  │  │ [View Full Assessment] [Respond]   │                │ │
│  │  │                                    │                │ │
│  │  └────────────────────────────────────┘                │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Architecture

```
┌──────────────┐
│ Patient      │
│ Types in     │
│ Chat Message │
└──────┬───────┘
       │
       ↓
┌──────────────────────────────────┐
│  Frontend (templates/index.html)  │
│  - sendMessage()                  │
│  - Display "Thinking..."          │
│  - Show risk indicator            │
└──────┬───────────────────────────┘
       │
       ├─ POST /api/therapy/chat
       │  (with message content)
       │
       ↓
┌──────────────────────────────────┐
│  Backend (api.py)                │
│  - TherapistAI.generate_response()│
│  - SafetyMonitor.analyze_message()│
│  - Check risk thresholds          │
└──────┬───────────────────────────┘
       │
       ├─ Returns JSON:
       │  {
       │    "response": "AI message...",
       │    "risk_score": 65,
       │    "risk_level": "high",
       │    "risk_indicators": [...],
       │    "show_safety_banner": true
       │  }
       │
       ↓
┌──────────────────────────────────┐
│  Frontend (templates/index.html)  │
│  - Display AI response            │
│  - updateRiskIndicator()          │
│  - showRiskPrompt() if > 50       │
└──────┬───────────────────────────┘
       │
       ├─ If HIGH/CRITICAL risk:
       │
       ↓
┌──────────────────────────────────┐
│  Risk Prompt Modal               │
│  "We're concerned..."            │
│  [Start Assessment] [Dismiss]    │
└──────┬───────────────────────────┘
       │
       ├─ User clicks "Start Assessment"
       │
       ↓
┌──────────────────────────────────┐
│  Safety Check Tab                │
│  - Question 1-6                  │
│  - One per screen                │
└──────┬───────────────────────────┘
       │
       ├─ User answers all 6 questions
       │
       ↓
┌──────────────────────────────────┐
│  Frontend: submitAssessment()    │
│  - POST /api/c-ssrs/submit       │
│  - Include all 6 responses       │
└──────┬───────────────────────────┘
       │
       ↓
┌──────────────────────────────────┐
│  Backend (api.py)                │
│  - Calculate C-SSRS score        │
│  - Determine risk level          │
│  - If HIGH/CRITICAL:             │
│    - Send alert email            │
│    - Flag for clinician review   │
└──────┬───────────────────────────┘
       │
       ├─ Returns JSON:
       │  {
       │    "risk_level": "critical",
       │    "total_score": 25,
       │    "alert_sent": true,
       │    "requires_safety_plan": true
       │  }
       │
       ↓
┌──────────────────────────────────┐
│  Frontend:                       │
│  - Show result screen            │
│  - If HIGH/CRITICAL:             │
│    - Show safety plan form       │
│  - Log to database               │
│  - Notify clinician              │
└──────────────────────────────────┘
```

---

## 📊 Risk Level Visual Indicators

### Color Coding System

```
Low Risk
┌─────────────────┐
│ 🟢 Low Risk     │
│ Score: 0-4      │
│ Status: Normal  │
└─────────────────┘

Moderate Risk
┌─────────────────┐
│ 🟡 Moderate     │
│ Score: 5-9      │
│ Status: Routine │
└─────────────────┘

High Risk
┌─────────────────┐
│ 🟠 High Risk    │
│ Score: 10-14    │
│ Action: Alert   │
└─────────────────┘

Critical Risk
┌─────────────────┐
│ 🔴 CRITICAL     │
│ Score: 15-30    │
│ Action: URGENT  │
│ 📍 Flashing     │
└─────────────────┘
```

---

## 🎬 User Journey Maps

### Scenario A: Patient Proactively Takes Assessment

```
START
  │
  ├─ Patient logs in
  │
  ├─ Navigates to "Safety Check" tab
  │
  ├─ Reads intro: "This is a 6-question assessment..."
  │
  ├─ Clicks [Start Assessment]
  │
  ├─ Answers Q1: "Any thoughts of killing yourself?" → No
  │
  ├─ [Next] → Answers Q2: "How many days?" → 0
  │
  ├─ [Next] → Answers Q3-6...
  │
  ├─ Completes all 6 questions
  │
  ├─ Receives Result: "LOW RISK - 0/30"
  │
  ├─ Message: "Your clinician will review. You're doing well."
  │
  └─ END ✓
```

### Scenario B: AI Detects Risk During Chat

```
START
  │
  ├─ Patient in therapy chat
  │
  ├─ Types: "I can't do this anymore. Too much pain."
  │
  ├─ [AI receives message]
  │    └─ risk_score = 62 (detected)
  │
  ├─ AI responds: "I hear you're in pain. Let's explore..."
  │
  ├─ Frontend shows: 🟠 "Possible Risk Detected"
  │
  ├─ Risk Prompt appears: "We're concerned. Would you like
  │   to complete a safety assessment?"
  │
  ├─ Patient clicks [Yes, Start Assessment]
  │
  ├─ Safety Check tab opens
  │
  ├─ Q1-6: Patient answers
  │
  ├─ Result: "HIGH RISK - 13/30"
  │
  ├─ ⚠️ Safety Plan form appears automatically
  │
  ├─ Patient fills 6 sections
  │
  ├─ [Submit Safety Plan]
  │
  ├─ ✓ "Plan saved. Clinician notified."
  │
  ├─ Email sent to clinician
  │
  └─ END ✓
```

### Scenario C: Patient Dismisses Risk Prompt

```
START
  │
  ├─ AI detects risk_score = 55
  │
  ├─ Risk prompt appears
  │
  ├─ Patient clicks [Dismiss] / "I'm safe"
  │
  ├─ System logs: "User dismissed risk prompt"
  │
  ├─ Continues monitoring chat
  │
  ├─ If risk increases (score > 70):
  │  └─ Escalates to clinician email
  │     (Override user dismissal)
  │
  └─ END
```

---

## 💻 Implementation Checklist

### Phase 1: HTML Structure
- [ ] Add Safety Check tab to navigation
- [ ] Create assessment container div
- [ ] Create risk indicator element
- [ ] Create risk prompt modal
- [ ] Create safety plan form

### Phase 2: JavaScript Logic
```javascript
// Assessment flow
initAssessment()        // Load 6 questions
displayQuestion()       // Show current question
nextQuestion()          // Move to Q+1
prevQuestion()          // Move to Q-1
submitAssessment()      // Send to API

// Risk detection
updateRiskIndicator()   // Show 🟢/🟠/🔴
showRiskPrompt()        // Modal "We're concerned"
handlePromptResponse()  // User clicks Yes/No

// Safety planning
startSafetyPlan()       // Show form
savePlanSection()       // Save each section
submitSafetyPlan()      // POST to API
```

### Phase 3: CSS Styling
```css
/* Colors */
.risk-low {}        /* 🟢 Green */
.risk-moderate {}   /* 🟡 Yellow */
.risk-high {}       /* 🟠 Orange */
.risk-critical {}   /* 🔴 Red - with pulse */

/* Animations */
.pulse {}           /* Heartbeat for CRITICAL */
.slide-in {}        /* Risk prompt entrance */
.fade-out {}        /* Question transition */
```

### Phase 4: API Integration
- [ ] Connect to /api/c-ssrs/start
- [ ] Connect to /api/c-ssrs/submit
- [ ] Handle risk_score in therapy response
- [ ] Trigger alerts if HIGH/CRITICAL

---

## 🎯 Key Points

**The C-SSRS will be woven into the user experience naturally:**

1. **Available anywhere** - "Safety Check" tab in main nav
2. **Proactive screening** - Available when patient wants it
3. **Passive detection** - AI monitors during therapy chat
4. **Contextual prompts** - "We noticed... would you take assessment?"
5. **Safety planning** - Automatic for high-risk patients
6. **Clinician integration** - Real-time alerts to support team

**This creates a comprehensive safety net while keeping the interface friendly and non-stigmatizing.**

