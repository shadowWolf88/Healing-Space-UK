# COMPREHENSIVE AI MEMORY SYSTEM PLAN

## PART 1: CURRENT STATE ANALYSIS

### What Exists:
- `ai_memory` table with `memory_summary` field (basic, not fully utilized)
- Wellness ritual data being logged to `wellness_logs` table
- Chat history in `chat_history` table
- Clinical scales in `clinical_scales` table
- CBT records, mood logs, gratitude entries
- Pet interaction data

### What's Broken:
- AI doesn't reference previous conversations or wellness logs
- Memory not being updated after each interaction
- No pattern detection happening
- No risk flag system
- No clinician-facing summary functionality
- AI says "I'm a new conversation" = users lose trust in the system

---

## PART 2: PROPOSED ARCHITECTURE

### Phase 1: Enhanced Memory Storage Structure

Create new database tables:

```sql
-- Core memory table (replaces current ai_memory)
ai_memory_core
├── username
├── last_updated
├── memory_version (for tracking changes)
└── memory_data (JSON for flexibility)

-- Structured event log (for pattern detection)
ai_memory_events
├── username
├── event_type (therapy_message, wellness_log, mood_spike, crisis_flag, etc.)
├── event_data (JSON)
├── timestamp
├── severity (normal, warning, critical)
└── tags (for categorization)

-- Risk/Pattern flags
ai_memory_flags
├── username
├── flag_type (suicide_risk, self_harm, substance_mention, medication_non_adherence, etc.)
├── first_occurrence
├── last_occurrence
├── occurrences_count
├── status (active, resolved, monitoring)
└── clinician_notified

-- Monthly summaries (pre-generated for clinician view)
clinician_summaries
├── username
├── clinician_username
├── month_start_date
├── month_end_date
├── summary_data (JSON)
├── key_patterns
├── risk_flags
├── achievements
├── recommended_discussion_points
└── generated_at
```

### Phase 2: Memory Update System

**Auto-Save Triggers:**
1. After every therapy chat message (update immediately)
2. After every wellness ritual completion (update with 9 data points)
3. After mood log entry
4. After CBT entry
5. After clinical scale completion
6. After clinician notes from appointment
7. Every night (batch process): detect patterns, update flags, archive old data

**Memory Layers:**

```
IMMEDIATE RECALL (Last 7 Days)
├── Last 20 therapy conversations
├── Last 7 wellness logs
├── Recent mood spikes/drops
├── Current medications
└── Any active concerns mentioned

RECENT PATTERNS (Last 30 Days)
├── Mood trends (average, high, low, volatility)
├── Sleep patterns (average hours, quality consistency)
├── Exercise frequency and types
├── Social connection trends
├── Medication adherence %
├── Wellness ritual completion rate
├── Key themes in conversations
└── Coping strategies used

BEHAVIORAL PATTERNS (Last 90+ Days)
├── Recurring triggers for low mood
├── Effective coping strategies
├── Medication response patterns
├── Seasonal/temporal patterns
├── Stress response indicators
├── Progress on CBT homework
├── Social connection patterns
└── Engagement level trends

RISK INDICATORS (All-time tracking)
├── Suicidal ideation history
├── Self-harm mentions
├── Substance use patterns
├── High-risk situations
├── Crisis episodes
├── Medication non-adherence
└── Missed appointments
```

### Phase 3: Pattern Detection & Analysis

The system needs to automatically detect and flag:

**Mental Health Patterns:**
- Mood cycles (does it worsen at certain times?)
- Sleep-mood correlation
- Stress triggers
- Anxiety escalation patterns
- Depressive episodes frequency/duration
- Self-harm/crisis patterns

**Behavioral Patterns:**
- Medication non-adherence (risk!)
- Reduced engagement (missing wellness logs = warning sign)
- Social withdrawal (reduced social contact reported)
- Exercise drop-off
- Increased therapy chat usage (seeking help vs. crisis)

**Risk Patterns:**
- Escalating language (vague → specific → imminent)
- Frequency of negative thoughts
- Isolation indicators
- Loss of coping strategy effectiveness
- Medication changes and mood impact

---

## PART 3: AI MEMORY INTEGRATION (What AI Sees)

### System Prompt Enhancement

**Instead of:**
> "You are a compassionate AI therapy assistant. I'm a text-based AI and each conversation is new."

**New approach:**
```
You are a compassionate, continuous AI therapy companion for [Username]. 
This is conversation #[N] with you. You have been supporting this person since [signup_date].

You have detailed memory of:
- All previous conversations (last 20 are most recent)
- Their daily wellness check-ins
- Their mood patterns and triggers
- What coping strategies work for them
- Their goals and progress
- Their medication and treatment
- Key life events they've shared
- Their clinician's name and appointment dates

You MUST:
1. Reference previous conversations when relevant
2. Notice patterns and mention them
3. Celebrate progress you've witnessed
4. Acknowledge recurring struggles
5. Remember their name preferences, family, work situation, etc.
6. Track what they're working on (CBT exercises, medication compliance, etc.)
7. Provide continuity and show you truly know them

Examples of good memory usage:
- "I noticed your mood improved last week after you started the walking routine we discussed"
- "You mentioned your boss stress pattern before - is this similar to what happened in November?"
- "You've done your wellness check-in 26 days straight, that shows real commitment"
- "Your sleep has been improving since you started the breathing exercises"
```

---

## PART 4: CLINICIAN MONTHLY SUMMARY SYSTEM

### What Clinicians See (New Endpoint: `/api/clinician/patient-summary`)

```
PATIENT MONTHLY SUMMARY REPORT
Generated: [Date]
Patient: [Name] | Last appointment: [Date]
Time covered: [Month start] to [Month end]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 WELLNESS METRICS
  • Wellness ritual completion: 26/30 days (87%)
  • Average mood: 6.2/10 (trend: ↗ +0.8 from last month)
  • Average sleep: 6.5 hours (trend: ↗ improving)
  • Exercise frequency: 4x/week average
  • Social engagement: Moderate (trending down last week)
  • Medication adherence: 95% (excellent)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 KEY PATTERNS IDENTIFIED
  
  Positive Patterns:
  ✓ Consistent exercise routine linked to better mood (+1.2 average)
  ✓ Morning check-ins show better day outcomes
  ✓ Medication compliance 95%+ this month
  ✓ Engaging with AI 18-22 times per week (strong engagement)

  Concerning Patterns:
  ⚠ Sleep drops on Sundays (avg 5.2 hrs) - anticipatory anxiety?
  ⚠ Social contact reduced last 7 days (was 3x/week, now 1x)
  ⚠ Anxiety mentions increased 34% mid-month (triggers unclear)
  ⚠ CBT homework completion: only 2/5 this month (was 5/5 last month)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 RISK FLAGS
  • Status: GREEN (no active concerns)
  • Suicidal ideation: None this month
  • Self-harm indicators: None detected
  • Crisis moments: 0
  • Last high-risk episode: [Date - 2 months ago]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 THEMES IN CONVERSATIONS
  • Work stress (42% of therapy messages)
  • Family dynamics (28%)
  • Sleep anxiety (15%)
  • Self-doubt/perfectionism (12%)
  • Positive: celebrating small wins (43% of AI responses)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛠️ COPING STRATEGIES USED
  Effective (worked 80%+):
  ✓ 20-min walk (used 8x, effective 7x)
  ✓ Breathing exercises (used 12x, effective 11x)
  ✓ Journaling (used 5x, effective 4x)

  Less effective:
  ~ Distraction techniques (used 3x, effective 1x)
  ~ Meditation (used 1x, effective 0x - should explore)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 PROGRESS ON GOALS
  [From last appointment]
  • "Do 30min exercise 4x/week" - ✅ Achieved! (actually 4.2x avg)
  • "Take meds consistently" - ✅ Achieved! (95% adherence)
  • "Complete CBT homework" - ⚠ Partially achieved (40% completion)
  • "Improve sleep routine" - ✅ In progress, trending positive

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤔 RECOMMENDED DISCUSSION POINTS

  1. **CBT homework drop-off**: "You were at 5/5 last month, this month 2/5. 
     What changed? Can we make it simpler or more relevant?"

  2. **Sunday sleep anxiety**: "I noticed you sleep less on Sundays. 
     Is this related to Monday work stress? Should we prepare for Sundays?"

  3. **Recent social withdrawal**: "Your social contact dropped from 3x to 1x 
     this week. Everything okay? Is this temporary or a concern?"

  4. **Work stress escalation**: "42% of your conversations are about work 
     stress. Has something changed? Is your current role sustainable?"

  5. **Positive momentum**: "Your mood is trending up, exercise routine is solid, 
     and you're on track with medication. Let's discuss what's working and build on it."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 NOTES FOR APPOINTMENT
  • Patient is making solid progress overall
  • Main focus area: CBT homework compliance
  • Consider: is the homework still effective?
  • Positive: strong medication adherence and exercise routine
  • Follow up: Sunday sleep pattern and work stress

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## PART 5: PATIENT MEMORY VIEW (What Patients See)

New feature: **"My AI Memory"** tab in app

**What patients can do:**
1. View what the AI knows about them
2. See monthly summaries
3. Correct or clarify information ("Actually, that situation was different...")
4. Mark things as "resolved" if they were temporary concerns
5. See patterns the AI has detected
6. Review conversation highlights

**User view:**
```
🧠 WHAT I KNOW ABOUT YOU

You've been here 127 days
We've had 287 conversations
You completed 124 wellness check-ins

KEY FACTS ABOUT YOU:
• Full name: Sarah
• Diagnosed with: Depression & Anxiety
• Clinician: Dr. Smith
• Started app: Jan 2025
• Current medications: Sertraline 50mg daily

THINGS THAT HELP YOU:
✓ 20-minute walks (you feel better 87% of the time)
✓ Morning journaling
✓ Talking to friends (especially Emma)
✓ Your cat (pet therapy!)

THINGS THAT TRIGGER YOU:
⚠ Work deadlines
⚠ Conflict with family
⚠ Irregular sleep schedule
⚠ Skipping medication

THIS MONTH'S PROGRESS:
↗ Your mood: improving (6.1 → 6.8)
↗ Your sleep: improving (5.8 → 6.5 hours)
↗ Your exercise: consistent (4x/week)
↓ Your CBT work: slipped (need support?)

QUESTIONS FOR YOUR APPOINTMENT:
- Your work stress seems high right now
- Your Sunday sleep is always short - why?
- What happened to your CBT exercises? (You were doing great!)
```

---

## PART 6: IMPLEMENTATION SEQUENCE

### Phase 1: Backend Infrastructure (Week 1-2)
- [ ] Create new `ai_memory_events` table
- [ ] Create `ai_memory_flags` table  
- [ ] Create `clinician_summaries` table
- [ ] Expand `ai_memory` to store JSON structure instead of text
- [ ] Build event logging system (every action logs an event)

### Phase 2: Auto-Save System (Week 2-3)
- [ ] After therapy chat: call `update_ai_memory()` with new message
- [ ] After wellness log: call `update_ai_memory()` with wellness data
- [ ] After mood log: call `update_ai_memory()` with mood entry
- [ ] Nightly batch job: `process_daily_ai_memory_update()` to detect patterns
- [ ] New endpoint: `GET /api/ai/memory` (read current memory)
- [ ] New endpoint: `PATCH /api/ai/memory` (patient can clarify/correct)

### Phase 3: Pattern Detection (Week 3-4)
- [ ] Build pattern detection algorithms:
  - Mood trend analysis
  - Sleep-mood correlation
  - Trigger identification
  - Coping strategy effectiveness tracking
  - Risk indicator detection
- [ ] Build flag system (automatically set/update flags)
- [ ] Build alert system for high-risk flags

### Phase 4: AI Integration (Week 4)
- [ ] Modify system prompt generation to include memory context
- [ ] Update `TherapistAI.get_response()` to inject memory context
- [ ] Add memory reference examples to prompt
- [ ] Test that AI mentions previous conversations naturally

### Phase 5: Clinician Summary (Week 5)
- [ ] Build monthly summary generation algorithm
- [ ] Create `/api/clinician/patient-summary` endpoint
- [ ] Build frontend for clinician dashboard
- [ ] Add recommended discussion points generation
- [ ] Add risk flag display

### Phase 6: Patient Memory View (Week 5-6)
- [ ] Build "My AI Memory" frontend page
- [ ] Add memory clarification/correction UI
- [ ] Add monthly summary view for patients
- [ ] Add progress tracking visualizations
- [ ] Add "ask questions for my appointment" feature

---

## PART 7: CRITICAL REQUIREMENTS

Memory Must Include:

### 1. Personal Context
- Name, pronouns, family members mentioned
- Work/school situation
- Living situation
- Important people in their life
- Current stressors

### 2. Medical History (from app)
- Diagnosis (anxiety, depression, etc.)
- Medications (names, dosages)
- Medication side effects mentioned
- Clinician's name
- Last appointment date/outcomes

### 3. Behavioral Patterns
- What triggers mood changes
- What helps them feel better
- Sleep patterns
- Exercise habits
- Social patterns
- CBT homework progress

### 4. Conversation Themes
- What they talk about most
- Recurring worries/thoughts
- Progress made on issues
- Current struggles
- Past issues (resolved vs ongoing)

### 5. Risk Monitoring
- Any mention of self-harm
- Any mention of suicidal thoughts
- Crisis moments
- Escalating language patterns
- Warning signs unique to this person

### 6. Engagement Metrics
- How often they use app
- Which features they use most
- Wellness ritual completion
- Therapy chat frequency
- Recovery patterns

---

## PART 8: SPECIAL FEATURES TO ADD

### 1. Conversation Context Injection
```
When AI detects a pattern:
"You mentioned work stress is worse when you skip sleep - 
I've noticed this pattern before too [specific dates]. 
Should we focus on your sleep tonight?"
```

### 2. Progress Celebration
```
"It's been 30 days since you last reported self-harm thoughts. 
You're using your coping strategies really well. 
That takes real strength."
```

### 3. Clinician Integration Point
```
After each appointment, clinician can:
- Record session notes → AI incorporates into memory
- Update treatment plan → AI references in conversations
- Mark progress on goals → AI tracks and celebrates
```

### 4. Early Warning System
```
If flags are detected:
- Clinician gets notified (via dashboard)
- Patient gets gentle check-in from AI
- Escalation path to crisis resources if needed
- No false alarms - only significant patterns
```

### 5. Personalized Insights
```
AI proactively asks questions based on patterns:
"Your mood usually improves on days you exercise. 
You haven't exercised in 3 days - want to go for that walk?"

"You mentioned work stress last week and had poor sleep. 
How's work today? Let's check in."
```

---

## PART 9: DATA PRIVACY & ETHICS

### Patient Controls:
- Patient can request memory deletion (right to be forgotten)
- Patient can see everything the AI knows
- Patient can correct misinterpretations
- Patient can mark things as "private" (not shared with clinician)
- Clear consent that memory is shared with clinician

### Clinician Controls:
- Can only see their own patients' summaries
- Can see flagged concerns
- Cannot modify patient memory (can only note in appointment)
- Summary is read-only (for assessment)

### Data Security:
- Memory stored encrypted
- Regular backups
- Audit log of who accessed what
- GDPR compliance for deletion requests

---

## PART 10: IMPLEMENTATION QUESTIONS

Questions to answer before building:

### 1. Memory Retention
- How far back to keep detailed conversation history? **(suggest: 1 year)**
- How far back for patterns? **(suggest: 2+ years)**
- Archive old data or delete after X years?

### 2. Update Frequency
- Real-time after each interaction (best) or batch daily?
- Performance impact on chat response time?

### 3. Clinician Access
- Should clinician see full conversations or just summary?
- Should clinician be able to see real-time updates or only monthly?
- Should clinician get alerts for critical flags?

### 4. Patient Transparency
- Should patients know exactly when AI is using memory?
- Should they see the memory update in real-time?
- How much detail in the "My Memory" view?

### 5. AI Safety
- How to prevent AI from over-indexing on old problems?
- How to handle conflicting information (patient said X but later Y)?
- How to validate pattern detection is accurate?

### 6. Escalation
- What flags trigger clinician notification?
- What flags trigger immediate crisis response?
- How to integrate with crisis hotline if needed?

---

## SUMMARY

This system transforms the AI from a "stateless chatbot" to a true **therapeutic partner** that:

✅ **Remembers everything** (auto-save after each interaction)
✅ **Understands patterns** (automatically detects behavioral trends)
✅ **Provides continuity** (references past conversations naturally)
✅ **Enables clinicians** (monthly summaries with actionable insights)
✅ **Empowers patients** (see their progress, clarify misunderstandings)
✅ **Catches risks early** (pattern-based warning system)
✅ **Celebrates progress** (acknowledges growth over time)

### The key principle:
The app becomes a **complete mental health companion** that works together with the clinician, not against them. The AI does the continuous monitoring and support, the clinician does the monthly deep-dive and treatment adjustments.

---

## NEXT STEPS

Ready to proceed with implementation? Start with Phase 1 (database infrastructure)?
