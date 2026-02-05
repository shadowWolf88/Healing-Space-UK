# Daily Wellness Ritual - Quick Reference Guide

## 🎯 Feature Overview
A 10-step, 2-3 minute conversational wellness ritual that replaces fragmented mood logging. Captures 12+ wellness data points while feeling like a warm AI check-in.

## 📍 How to Access

### User Flow
```
Home Tab → Modal Auto-Opens (if not logged today)
         → Click "💙 Start Your Daily Wellness Check-in"
         → Complete 10 steps
         → Click "✓ Complete Ritual"
         → Data saved, modal closes
```

## 🧬 The 10-Step Ritual

| Step | Question | Input Type | Time-Aware? |
|------|----------|-----------|-------------|
| 1 | How is your mood? | 5-emoji scale (😢-😄) | No |
| 2 | What's affecting your mood? | 5 presets + custom text | No |
| 3 | How was your sleep? | 1-10 slider + notes | Skip afternoon/evening |
| 4 | How's your hydration? | Cups + level dropdown | Time-aware msg |
| 5 | Any movement today? | 5 activity levels | No |
| 6 | Social connections? | 5 contact levels | No |
| 7 | Did you take your meds? | Yes/No + reason if missed | No |
| 8 | What's your energy level? | 5-scale + capacity 1-10 | No |
| 9 | CBT homework progress? | Yes/No + blockers | No |
| 10 | That's it! | AI reflection message | No |

## 💾 Data Captured

**24 Fields Per Ritual**:
- Mood (1-10), context, narrative
- Sleep quality (1-10), notes
- Hydration (cups, level)
- Exercise type, duration
- Social contact level
- Medication adherence
- Energy (1-5), capacity (1-10)
- Homework completion
- Session duration

## 🔌 API Endpoints

### POST /api/wellness/log
Save daily ritual - **Required fields**: mood, time_of_day_category, session_duration_seconds
```bash
curl -X POST http://localhost:5000/api/wellness/log \
  -H "Content-Type: application/json" \
  -d '{"mood": 7, "time_of_day_category": "morning", "session_duration_seconds": 120, ...}'
```

### GET /api/wellness/today
Check if already logged - **No required fields**
```bash
curl http://localhost:5000/api/wellness/today
# Returns: {"exists": true/false}
```

### GET /api/wellness/summary?days=7
Get wellness statistics - **Optional params**: days (7 or 30)
```bash
curl http://localhost:5000/api/wellness/summary?days=7
# Returns: mood_average, sleep_average, exercise_total, med_adherence_percent, etc.
```

### GET /api/user/medications
Get active medications - **No required fields**
```bash
curl http://localhost:5000/api/user/medications
# Returns: has_medications, medication list
```

### GET /api/homework/current
Get current homework - **No required fields**
```bash
curl http://localhost:5000/api/homework/current
# Returns: has_homework, has_weekly_goal, details
```

## ⏰ Time-Aware Logic

| Time | Morning (6-12) | Afternoon (12-17) | Evening (17-23) |
|------|---|---|---|
| Greeting | "Good morning! 🌅" | "Good afternoon! ☀️" | "Good evening! 🌙" |
| Sleep Q | ✅ Included | ❌ Skipped | ❌ Skipped |
| Hydration Q | "Have you had water yet?" | "How's water intake?" | "Total water today?" |
| Focus | Recovery from sleep | Movement & progress | Social connections |

## 📊 Database Tables

### wellness_logs (24 columns)
```sql
SELECT * FROM wellness_logs 
WHERE username = 'patient@example.com' 
ORDER BY timestamp DESC 
LIMIT 1;
```

### patient_medications (9 columns)
```sql
SELECT medication_name, dosage, frequency 
FROM patient_medications 
WHERE username = 'patient@example.com' AND is_active = TRUE;
```

## 🧠 AI Memory Integration

Wellness data automatically feeds into AI memory:
```
"Wellness rituals: 5 completed, avg mood 7.2/10, sleep quality 7.8/10, 
3 exercise sessions, 95% medication adherence"
```

AI uses for:
- Pattern detection (sleep ↔ mood correlation)
- Risk assessment (low adherence warning)
- Personalized recommendations
- Therapy context

## 🎮 Gamification Integration

Tracks 6 wellness streaks:
- `wellness_checkin` - Daily ritual completion
- `hydration` - Days with good/excellent hydration
- `exercise` - Days with any exercise
- `medication` - Days with medication adherence
- `sleep_quality` - Days with 7+ sleep quality
- `social_connection` - Days with good/strong social contact

## 🛠️ Developer Reference

### JavaScript State
```javascript
wellnessRitualState = {
  currentStep: 0,              // 0-9
  data: {},                    // Collected responses
  timeOfDay: 'morning',        // morning/afternoon/evening
  startTime: Date.now(),       // For session duration
  skipped: [],                 // Skipped step IDs
  steps: [...]                 // 10-step definition
}
```

### Key Functions
- `initializeWellnessRitual()` - Start ritual, check if logged today
- `showWellnessStep()` - Render current step
- `nextWellnessStep()` - Move to next step
- `submitWellnessRitual()` - Save data to server
- `renderMoodStep()` through `renderWrapUpStep()` - Step UI renderers

### Key SQL Queries
```sql
-- Check if logged today
SELECT COUNT(*) FROM wellness_logs 
WHERE username = %s AND DATE(timestamp) = DATE(NOW());

-- Get 7-day summary
SELECT AVG(mood), AVG(sleep_quality), COUNT(*) FROM wellness_logs
WHERE username = %s AND timestamp > NOW() - INTERVAL '7 days';

-- Medication adherence
SELECT COUNT(*) FILTER (WHERE medication_taken = TRUE) * 100.0 / COUNT(*) 
FROM wellness_logs
WHERE username = %s AND timestamp > NOW() - INTERVAL '7 days';
```

## 🧪 Testing Checklist

- [ ] Modal appears on Home tab load
- [ ] Time-appropriate greeting shows
- [ ] Complete all 10 steps without errors
- [ ] Can navigate backward with Previous button
- [ ] Can skip optional questions
- [ ] Data appears in PostgreSQL wellness_logs table
- [ ] Already-logged message shows on day 2
- [ ] AI memory updated with wellness data
- [ ] Mobile view is responsive
- [ ] Dark mode displays correctly

## ⚠️ Common Issues & Fixes

**Issue**: Modal doesn't show
- Check browser console for errors
- Verify `/api/wellness/today` returns JSON
- Check authentication is valid

**Issue**: Data not saving
- Check Network tab for POST errors
- Verify all required fields filled
- Check PostgreSQL connection

**Issue**: Sleep question shows at night
- Check `getTimeOfDay()` returns correct time
- Verify browser time is correct
- Check `shouldSkipWellnessStep()` logic

**Issue**: Medication question shouldn't show
- Check if patient has active medications in patient_medications table
- Consider using `/api/user/medications` endpoint before rendering

## 📈 Metrics to Monitor

**User Engagement**:
- Daily ritual completion rate (target: 80%+)
- Average session duration (target: 2-3 min)
- Step skip rate (target: <10%)

**Data Quality**:
- Missing data fields (target: <5%)
- Valid mood range (target: 100%)
- Medication adherence accuracy

**Performance**:
- API response times (target: <200ms)
- Modal initialization (target: <100ms)
- Database query times (target: <50ms)

## 📚 Related Documents

- `WELLNESS_RITUAL_IMPLEMENTATION_REPORT.md` - Full technical docs
- `WELLNESS_RITUAL_COMPLETE.md` - Implementation summary
- `IMPLEMENTATION_PROMPT_SECTION_1.md` - Original specifications
- `api.py` - Backend implementation
- `templates/index.html` - Frontend implementation

## 🚀 Next Steps

**Phase 2**: Clinician dashboard display
- Show wellness summaries in patient profiles
- Display 7/30-day trends
- Alert on negative patterns

**Phase 3**: Predictive analytics
- ML model for mood prediction
- Automated intervention suggestions

**Phase 4**: Mobile app
- Native iOS/Android
- Offline ritual support
- Push notifications

---

**Quick Start**: `python3 api.py` → Navigate to Home tab → Click wellness button

**Production Status**: ✅ Ready  
**Last Updated**: January 29, 2025
