# Frontend Integration Summary: Where & How C-SSRS Will Be Implemented

**Your Question:** On the website, how/where will C-SSRS be implemented? Can we integrate the AI?

**Answer:** Here's the complete picture...

---

## 📍 Three Implementation Points

### 1. **"Safety Check" Tab** (Primary Interface)
- **Location:** Main navigation (next to "Therapy" and "Mood Tracker")
- **What:** Formal C-SSRS assessment screen
- **When:** Patient initiates OR after AI detects risk
- **Duration:** 3-4 minutes
- **Outcome:** Risk level determined, safety plan if HIGH/CRITICAL

```
Navigation: Home | Therapy | Safety Check (NEW) | Mood | Settings
```

---

### 2. **Integrated AI Risk Detection** (During Therapy Chat)
- **Location:** Existing therapy chat interface
- **What:** Backend monitors every message for risk language
- **When:** Continuous, every time patient sends message
- **How:** SafetyMonitor analyzes + returns risk_score (0-100)
- **Outcome:** 🟢/🟠/🔴 indicator updates, assessment prompted if HIGH

```
User Message → AI Response + Risk Analysis → Display with Indicator
```

---

### 3. **Clinician Dashboard** (Backend Support)
- **Location:** Separate clinician portal
- **What:** Alerts for HIGH/CRITICAL assessments
- **When:** Real-time email + in-app notification
- **How:** C-SSRS score triggers alert → Clinician responds
- **Outcome:** Documented clinician action

```
Assessment → Score HIGH/CRITICAL → Email Alert → Clinician Review
```

---

## 🎨 Visual Layout: Where on Website

```
┌─────────────────────────────────────────────────────┐
│  Healing Space UK - Patient Portal                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Navigation Bar:                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │ 🏠 Home │ 💬 Therapy │ ✓ Safety Check │      │  │
│  │         │            │ (NEW)         │ ...  │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  THERAPY TAB (Existing)                             │
│  ┌──────────────────────────────────────────────┐  │
│  │ Your Therapy Session                         │  │
│  │ ───────────────────────────                  │  │
│  │                                              │  │
│  │ [Chat messages...]                           │  │
│  │                                              │  │
│  │ Patient: "I don't think I can go on..."     │  │
│  │                                              │  │
│  │ AI: "I hear you're struggling..."           │  │
│  │                                              │  │
│  │ 🟠 Risk Detected ← INDICATOR SHOWS HERE     │  │
│  │                                              │  │
│  │ [Prompt appears if HIGH]                    │  │
│  │ "⚠️ We're Concerned. Start Assessment?"     │  │
│  │                                              │  │
│  │ Text input: [type message...] [Send]        │  │
│  │                                              │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  SAFETY CHECK TAB (NEW)                             │
│  ┌──────────────────────────────────────────────┐  │
│  │ Safety Assessment                            │  │
│  │ ───────────────────────                      │  │
│  │                                              │  │
│  │ Question 1 of 6                              │  │
│  │ ▓▓▓░░░░░░░░░░░░░░░░░ 16%                   │  │
│  │                                              │  │
│  │ Have you had thoughts of killing yourself?  │  │
│  │                                              │  │
│  │ ○ No                                         │  │
│  │ ○ Rare                                       │  │
│  │ ○ Infrequent                                │  │
│  │ ○ Frequent                                  │  │
│  │ ○ Almost every day                          │  │
│  │ ○ Every day/multiple times                  │  │
│  │                                              │  │
│  │ [← Prev] [Skip] [Next →]                    │  │
│  │                                              │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  Results Screen (after Q6):                        │
│  ┌──────────────────────────────────────────────┐  │
│  │ ✓ Assessment Complete                       │  │
│  │                                              │  │
│  │ Risk Level: MODERATE                        │  │
│  │ Score: 5/30                                 │  │
│  │                                              │  │
│  │ Your clinician will review your responses   │  │
│  │ and contact you if needed.                  │  │
│  │                                              │  │
│  │ [If HIGH/CRITICAL]                          │  │
│  │ ↓                                            │  │
│  │ Safety Plan Form Appears:                   │  │
│  │ 1. Warning Signs [______]                  │  │
│  │ 2. Coping [______]                         │  │
│  │ 3. Distraction [______]                    │  │
│  │ 4. People [______]                         │  │
│  │ 5. Professionals [pre-filled]              │  │
│  │ 6. Environment [______]                    │  │
│  │                                              │  │
│  │ [Submit Safety Plan]                        │  │
│  │                                              │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 How the AI Integration Works

### The Flow:

```
1. Patient in Therapy Chat
   ↓
2. Types message: "I've been thinking about ending it..."
   ↓
3. Message sent to /api/therapy/chat
   ↓
4. Backend does TWO things simultaneously:
   
   A) TherapistAI generates helpful response
   B) SafetyMonitor analyzes for risk
      - Detects keywords: "ending it"
      - Calculates risk_score: 65 (HIGH)
   ↓
5. Returns to frontend:
   {
     "response": "I hear you're in pain...",
     "risk_score": 65,
     "risk_level": "high",
     "show_assessment_prompt": true
   }
   ↓
6. Frontend displays:
   - AI response (therapeutic value)
   - Risk indicator changes: 🟠 HIGH RISK
   - Modal: "⚠️ We're concerned. Take assessment?"
   ↓
7. Patient clicks "Start Assessment"
   ↓
8. Safety Check tab opens
   ↓
9. Patient answers Q1-6
   ↓
10. Score shows: HIGH (13/30)
    ↓
11. Safety plan form appears automatically
    ↓
12. Clinician gets alert email
```

---

## 💡 Key Implementation Details

### A. Assessment Screen Features
- **One question per screen** - Reduces cognitive load
- **Progress bar** - Shows Q1/6, Q2/6, etc.
- **Back button** - Can revise answers
- **Skip option** - "Maybe later" without penalty
- **Risk feedback** - Immediate result after Q6

### B. Risk Indicator
- **Always visible** in chat area
- **Color coded:**
  - 🟢 Green = Low Risk (normal state)
  - 🟡 Yellow = Moderate Risk (watch)
  - 🟠 Orange = High Risk (alert shown)
  - 🔴 Red = Critical Risk (urgent, flashing)

### C. Risk Prompt Modal
- **Triggers when:** risk_score > 50
- **Says:** "We noticed concerning language..."
- **Options:** 
  - ✅ Yes, start assessment
  - ⏰ Remind me later
  - ✓ I'm safe, dismiss
- **Also shows:** Emergency contact numbers

### D. Safety Plan (if HIGH/CRITICAL)
- **6 sections auto-triggered:**
  1. Warning Signs - What tells you crisis is coming?
  2. Coping Strategies - What can you do alone?
  3. Distraction Resources - Who/where to get away?
  4. People to Contact - Who can you call?
  5. Professional Help - Pre-filled with clinician + 999
  6. Environment Safety - Remove access to means

---

## 🔌 Backend Code Changes Needed

### Minimal Changes to Existing Code:

**File:** `api.py` (route `/api/therapy/chat`)

**Current:**
```python
response = TherapistAI.generate_response(message)
return jsonify({'response': response})
```

**Enhanced:**
```python
# 1. Generate AI response (existing)
response = TherapistAI.generate_response(message)

# 2. NEW: Analyze for risk
risk_analysis = SafetyMonitor.analyze_message(message)

# 3. NEW: Return both
return jsonify({
    'response': response,
    'risk_score': risk_analysis['score'],
    'risk_level': risk_analysis['level'],
    'risk_indicators': risk_analysis['indicators']
})
```

**File:** `c_ssrs_assessment.py` (already created)

- ✅ Scoring algorithm complete
- ✅ Risk classification complete
- ✅ Safety plan sections ready
- ✅ Just need to hook up to UI

### New Components to Create:

**Safety Monitor (risk detection):**
```python
class SafetyMonitor:
    @staticmethod
    def analyze_message(message):
        # Returns risk_score, level, indicators
```

---

## 📱 Frontend Files to Modify

### `templates/index.html` - Three sections:

**1. Add Safety Check Tab**
```html
<div id="safetyCheckTab" class="tab-content">
    <!-- Assessment UI -->
</div>
```

**2. Modify sendMessage() function**
```javascript
// Add risk handling
if (data.risk_score > 50) {
    updateRiskIndicator(data.risk_level);
    showRiskPrompt(data);
}
```

**3. Add Risk Modal HTML**
```html
<div id="riskPromptModal" class="modal">
    <!-- "We're concerned..." modal -->
</div>
```

### New JavaScript Functions:
```javascript
// Assessment
initAssessment()
displayQuestion(num)
submitAssessment()

// Risk display
updateRiskIndicator(level)
showRiskPrompt(data)

// Safety plan
showSafetyPlanForm()
saveSafetyPlan()
```

---

## 🎯 Summary Table

| Feature | Location | Trigger | Action |
|---------|----------|---------|--------|
| **Assessment** | "Safety Check" tab | Manual or AI prompt | Calculates risk score |
| **Risk Indicator** | Chat area | Every message | 🟢/🟠/🔴 color |
| **Risk Prompt** | Modal | score > 50 | Offers assessment |
| **Safety Plan** | Form | HIGH/CRITICAL | 6 sections |
| **Clinician Alert** | Email + Dashboard | HIGH/CRITICAL | Real-time notification |

---

## ✨ The Result

**Patient Experience:**
- Uses chat normally
- AI provides therapy + safety monitoring
- If risk detected, option to take assessment
- Results shown immediately
- Safety plan auto-created if needed
- Never feels intrusive or stigmatizing

**Clinician Experience:**
- Gets alerts for concerning conversations
- Can review full assessment details
- Can respond with action (called, contacted emergency, documented)
- Full audit trail of all interactions

**Technical Reality:**
- All code exists (C-SSRS module ready)
- Just need to wire it into UI
- Minimal changes to existing code
- Reuses existing authentication, database, alert system

---

## 🚀 Next Steps

1. **Design** - UI mockups for Safety Check tab ✓ (provided above)
2. **Frontend** - Add HTML/CSS/JS for assessment interface
3. **Backend** - Create SafetyMonitor class for risk detection
4. **Integration** - Wire therapy chat to include risk data
5. **Testing** - Test with sample conversations
6. **Deploy** - Roll out to staging for Lincoln review

---

**The bottom line:** C-SSRS will be **seamlessly woven into the therapy chat experience**, providing safety monitoring that's always on but never intrusive, with clinician support triggered automatically when needed.

