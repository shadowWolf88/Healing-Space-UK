# Daily Wellness Ritual - Complete Implementation Prompt

## Overview
Implement a comprehensive "Daily Wellness Ritual" feature that replaces the existing mood logging system with a conversational, branching 2-3 minute check-in. This captures 12+ wellness data points (mood, sleep, hydration, exercise, social contact, medication adherence, energy, capacity, homework progress, etc.) while feeling warm and non-clinical.

The ritual is time-aware (different questions for morning vs afternoon vs evening), AI-driven (uses conversational responses), and integrates with existing streak/badge systems.

---

## Database Schema

### New Table: wellness_logs
Create this table to store daily wellness ritual check-ins:

```sql
CREATE TABLE IF NOT EXISTS wellness_logs (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Mood Section
    mood INTEGER,  -- 1-10 scale
    mood_descriptor TEXT,  -- tired, anxious, calm, overwhelmed, etc.
    mood_context TEXT,  -- free text: "work stress, didn't sleep, argument with mum"
    
    -- Sleep Section
    sleep_quality INTEGER,  -- 1-10 rating of last night's sleep
    sleep_notes TEXT,  -- "up till 2am", "woke at 3am", "good 8 hrs"
    
    -- Hydration Section
    hydration_level TEXT,  -- low, medium, high
    total_hydration_cups INTEGER,  -- estimated cups of water today
    
    -- Exercise Section
    exercise_type TEXT,  -- walking, gym, yoga, none, etc.
    exercise_duration INTEGER,  -- minutes
    
    -- Social/Outdoor Section
    outdoor_time_minutes INTEGER,  -- minutes outside or fresh air
    social_contact TEXT,  -- text, call, in-person, none
    
    -- Medication Section
    medication_taken BOOLEAN,  -- if applicable
    medication_reason_if_missed TEXT,  -- why meds weren't taken
    
    -- Caffeine Tracking
    caffeine_intake_time TEXT,  -- time of last caffeine, if any
    
    -- Energy & Capacity
    energy_level INTEGER,  -- 1-10
    capacity_index INTEGER,  -- 1-10 ability to cope
    
    -- Weekly Goals/Homework
    weekly_goal_progress INTEGER,  -- 1-10 progress on patient's chosen focus
    homework_completed BOOLEAN,  -- did patient complete clinician homework
    homework_blockers TEXT,  -- why homework wasn't done
    
    -- AI Context
    emotional_narrative TEXT,  -- AI-captured elaboration on mood
    ai_reflection TEXT,  -- personalized insight from AI wrap-up
    
    -- Metadata
    time_of_day_category TEXT,  -- morning, afternoon, evening (for analysis)
    session_duration_seconds INTEGER  -- how long ritual took
);

CREATE INDEX idx_wellness_username_timestamp ON wellness_logs(username, timestamp DESC);
CREATE INDEX idx_wellness_date ON wellness_logs(DATE(timestamp));
```

### Optional: Update users table
If patient is on medications, you may want to add to users table:

```sql
-- Add to users table if not exists:
ALTER TABLE users ADD COLUMN IF NOT EXISTS has_medications BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS medication_reminders_enabled BOOLEAN DEFAULT TRUE;
```

### Optional: Medications table (if implementing medication tracking)
If you want a full medication management system:

```sql
CREATE TABLE IF NOT EXISTS patient_medications (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    medication_name TEXT NOT NULL,
    dosage TEXT,
    frequency TEXT,  -- once daily, twice daily, as needed, etc.
    time_of_day TEXT,  -- morning, evening, anytime
    prescribed_date DATE,
    notes TEXT,  -- "reduces anxiety better in morning", etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Frontend Implementation

### 1. HTML Structure

Add a new section in the Home tab (or create dedicated Wellness tab). Replace existing mood logging UI with this:

```html
<!-- In templates/index.html, create new section: -->
<div id="wellnessRitualSection" style="display: none;">
    <div class="wellness-container">
        <!-- Header with greeting -->
        <div class="wellness-header">
            <h2 id="wellnessGreeting">Good morning! 👋 How are you really doing today?</h2>
            <p class="wellness-subheader">Let's do a quick 2-3 min check-in</p>
        </div>

        <!-- Wellness ritual conversation interface -->
        <div id="wellnessConversation" class="wellness-conversation">
            <!-- AI messages and user responses will be injected here -->
        </div>

        <!-- Progress indicator -->
        <div class="wellness-progress">
            <div class="progress-bar" id="wellnessProgressBar" style="width: 0%;"></div>
            <p id="wellnessProgressText">Step 1 of 8</p>
        </div>

        <!-- Quick summary if already logged today -->
        <div id="alreadyLoggedToday" style="display: none;" class="wellness-already-logged">
            <p>✓ You've already logged today! Great job staying consistent.</p>
            <button onclick="viewWellnessSummary()" class="btn btn-secondary">View Today's Summary</button>
        </div>
    </div>
</div>

<!-- Wellness Ritual Modal (appears as main interaction) -->
<div id="wellnessRitualModal" class="modal" style="display: none;">
    <div class="modal-content wellness-modal">
        <div id="wellnessRitualContent"></div>
    </div>
</div>
```

### 2. JavaScript - Initialization & Flow Control

```javascript
// Global state for wellness ritual
let wellnessRitualState = {
    currentStep: 0,
    data: {},
    steps: [
        'mood', 'mood_context', 'sleep', 'hydration', 
        'exercise', 'social', 'medication', 'energy', 
        'homework', 'wrap_up'
    ],
    userRole: null,  // for medication questions
    hasAlreadyLoggedToday: false
};

// Initialize wellness ritual
async function initWellnessRitual() {
    // Check if user already logged today
    const today = new Date().toLocaleDateString('en-GB');
    const lastLogDate = localStorage.getItem(`wellnessLastLog_${currentUser}`);
    
    if (lastLogDate === today) {
        wellnessRitualState.hasAlreadyLoggedToday = true;
        document.getElementById('alreadyLoggedToday').style.display = 'block';
        return;
    }
    
    // Get time-of-day to customize greeting
    const hour = new Date().getHours();
    let greeting = '';
    let timeCategory = '';
    
    if (hour >= 6 && hour < 12) {
        greeting = `Good morning! ☀️ How are you really doing today?`;
        timeCategory = 'morning';
    } else if (hour >= 12 && hour < 17) {
        greeting = `Hey there! ☀️ How's your afternoon going?`;
        timeCategory = 'afternoon';
    } else {
        greeting = `Good evening! 🌙 How are you winding down?`;
        timeCategory = 'evening';
    }
    
    document.getElementById('wellnessGreeting').textContent = greeting;
    wellnessRitualState.data.time_of_day_category = timeCategory;
    
    // Start first question
    startWellnessStep();
}

// Main flow: advance through wellness questions
function startWellnessStep() {
    wellnessRitualState.currentStep = 0;
    showWellnessStep(wellnessRitualState.steps[0]);
}

async function showWellnessStep(step) {
    const container = document.getElementById('wellnessRitualContent');
    const progressBar = document.getElementById('wellnessProgressBar');
    const progressText = document.getElementById('wellnessProgressText');
    
    const stepNumber = wellnessRitualState.currentStep + 1;
    const totalSteps = wellnessRitualState.steps.length;
    progressBar.style.width = ((stepNumber / totalSteps) * 100) + '%';
    progressText.textContent = `Step ${stepNumber} of ${totalSteps}`;
    
    let html = '';
    
    switch(step) {
        case 'mood':
            html = renderMoodStep();
            break;
        case 'mood_context':
            html = renderMoodContextStep();
            break;
        case 'sleep':
            html = renderSleepStep();
            break;
        case 'hydration':
            html = renderHydrationStep();
            break;
        case 'exercise':
            html = renderExerciseStep();
            break;
        case 'social':
            html = renderSocialStep();
            break;
        case 'medication':
            html = await renderMedicationStep();
            break;
        case 'energy':
            html = renderEnergyStep();
            break;
        case 'homework':
            html = await renderHomeworkStep();
            break;
        case 'wrap_up':
            html = renderWrapUpStep();
            break;
    }
    
    container.innerHTML = html;
}

// Step 1: Mood Selection
function renderMoodStep() {
    return `
        <div class="wellness-step">
            <div class="ai-message">
                <p>How are you feeling right now?</p>
            </div>
            
            <div class="wellness-mood-selector">
                <div class="mood-scale">
                    ${[1,2,3,4,5,6,7,8,9,10].map(num => `
                        <button class="mood-btn" onclick="selectMood(${num})" title="Mood ${num}/10">
                            ${getMoodEmoji(num)}<br><span>${num}</span>
                        </button>
                    `).join('')}
                </div>
            </div>
            
            <div class="mood-descriptors">
                <p style="font-size: 0.9em; color: #999; margin: 20px 0 10px;">Pick a word that fits:</p>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    ${['Energized', 'Good', 'Okay', 'Tired', 'Stressed', 'Anxious', 'Sad', 'Overwhelmed', 'Numb', 'Calm'].map(desc => `
                        <button class="descriptor-btn" onclick="selectMoodDescriptor('${desc.toLowerCase()}')">
                            ${desc}
                        </button>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

function getMoodEmoji(num) {
    const emojis = ['😢', '😞', '😕', '😐', '😌', '😊', '😄', '😃', '🤩', '🥳'];
    return emojis[num - 1];
}

function selectMood(num) {
    wellnessRitualState.data.mood = num;
    document.querySelectorAll('.mood-btn').forEach(btn => btn.classList.remove('selected'));
    event.target.closest('.mood-btn').classList.add('selected');
}

function selectMoodDescriptor(descriptor) {
    wellnessRitualState.data.mood_descriptor = descriptor;
    document.querySelectorAll('.descriptor-btn').forEach(btn => btn.classList.remove('selected'));
    event.target.closest('.descriptor-btn').classList.add('selected');
    
    // Auto-advance to next step after 500ms
    setTimeout(() => advanceWellnessStep(), 500);
}

// Step 2: Mood Context (Why)
function renderMoodContextStep() {
    const descriptor = wellnessRitualState.data.mood_descriptor || 'feeling this way';
    const aiResponse = generateMoodContextQuestion(
        wellnessRitualState.data.mood,
        descriptor
    );
    
    return `
        <div class="wellness-step">
            <div class="ai-message">
                <p>${aiResponse}</p>
            </div>
            
            <div style="margin: 20px 0;">
                <textarea 
                    id="moodContextInput" 
                    rows="4" 
                    placeholder="What's been going on? (optional but helpful)"
                    style="width: 100%; padding: 12px; border-radius: 8px; border: 2px solid #e0e0e0;"
                ></textarea>
            </div>
            
            <button class="btn" onclick="captureMoodContext()">Continue</button>
            <button class="btn btn-secondary" onclick="skipMoodContext()">Skip</button>
        </div>
    `;
}

function generateMoodContextQuestion(moodNum, descriptor) {
    const questions = {
        low: "Sounds like you're having a tough time. What's been weighing on you?",
        mid: "What's contributing to how you're feeling right now?",
        high: "That's great! What's going well for you?"
    };
    
    let category = 'mid';
    if (moodNum <= 3) category = 'low';
    if (moodNum >= 8) category = 'high';
    
    return questions[category];
}

function captureMoodContext() {
    wellnessRitualState.data.mood_context = document.getElementById('moodContextInput').value;
    advanceWellnessStep();
}

function skipMoodContext() {
    wellnessRitualState.data.mood_context = null;
    advanceWellnessStep();
}

// Step 3: Sleep Quality (Morning) / Skip if afternoon/evening
function renderSleepStep() {
    if (wellnessRitualState.data.time_of_day_category !== 'morning') {
        // Skip sleep question in afternoon/evening, move to next
        advanceWellnessStep();
        return '';
    }
    
    return `
        <div class="wellness-step">
            <div class="ai-message">
                <p>How'd you sleep last night? (1 = terrible, 10 = amazing)</p>
            </div>
            
            <div class="mood-scale">
                ${[1,2,3,4,5,6,7,8,9,10].map(num => `
                    <button class="mood-btn" onclick="selectSleep(${num})">${num}</button>
                `).join('')}
            </div>
            
            <div style="margin: 20px 0;">
                <textarea 
                    id="sleepNotesInput" 
                    rows="3" 
                    placeholder="Any notes? (woke up, couldn't fall asleep, etc.)"
                    style="width: 100%; padding: 12px; border-radius: 8px; border: 2px solid #e0e0e0;"
                ></textarea>
            </div>
            
            <button class="btn" onclick="captureSleep()">Continue</button>
        </div>
    `;
}

function selectSleep(num) {
    wellnessRitualState.data.sleep_quality = num;
    document.querySelectorAll('.mood-scale .mood-btn').forEach(btn => btn.classList.remove('selected'));
    event.target.closest('.mood-btn').classList.add('selected');
}

function captureSleep() {
    wellnessRitualState.data.sleep_notes = document.getElementById('sleepNotesInput').value;
    advanceWellnessStep();
}

// Step 4: Hydration (Contextual)
function renderHydrationStep() {
    const timeCategory = wellnessRitualState.data.time_of_day_category;
    let aiMessage = '';
    
    if (timeCategory === 'morning') {
        aiMessage = "Have you had water yet today?";
    } else if (timeCategory === 'afternoon') {
        aiMessage = "You've made it to afternoon—how's your water intake looking?";
    } else {
        aiMessage = "How much water have you had today? (Easier to count in evening)";
    }
    
    return `
        <div class="wellness-step">
            <div class="ai-message">
                <p>${aiMessage}</p>
            </div>
            
            <div style="margin: 20px 0;">
                <p>Estimated cups of water:</p>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <button class="btn-small" onclick="adjustHydration(-1)">−</button>
                    <input 
                        type="number" 
                        id="hydrationCups" 
                        value="0" 
                        min="0" 
                        max="20"
                        style="width: 60px; text-align: center; padding: 10px; font-size: 18px;"
                    />
                    <button class="btn-small" onclick="adjustHydration(1)">+</button>
                    <span>cups</span>
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <p>Hydration level today:</p>
                <div style="display: flex; gap: 10px;">
                    ${['Low', 'Medium', 'High'].map(level => `
                        <button class="btn btn-secondary" onclick="selectHydrationLevel('${level.toLowerCase()}')">
                            ${level}
                        </button>
                    `).join('')}
                </div>
            </div>
            
            <button class="btn" onclick="captureHydration()">Continue</button>
        </div>
    `;
}

function adjustHydration(amount) {
    const input = document.getElementById('hydrationCups');
    input.value = Math.max(0, parseInt(input.value) + amount);
}

function selectHydrationLevel(level) {
    wellnessRitualState.data.hydration_level = level;
    document.querySelectorAll('[onclick*="selectHydrationLevel"]').forEach(btn => btn.classList.remove('selected'));
    event.target.classList.add('selected');
}

function captureHydration() {
    wellnessRitualState.data.total_hydration_cups = parseInt(document.getElementById('hydrationCups').value);
    advanceWellnessStep();
}

// Step 5: Exercise/Movement
function renderExerciseStep() {
    const timeCategory = wellnessRitualState.data.time_of_day_category;
    let aiMessage = "Any chance to move today yet? Even a quick walk counts.";
    
    if (timeCategory === 'evening') {
        aiMessage = "What kind of movement did you do today?";
    }
    
    return `
        <div class="wellness-step">
            <div class="ai-message">
                <p>${aiMessage}</p>
            </div>
            
            <div style="margin: 20px 0;">
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    ${['None', 'Walk', 'Gym', 'Yoga', 'Sports', 'Dance', 'Gardening', 'Other'].map(type => `
                        <button class="btn btn-secondary" onclick="selectExercise('${type.toLowerCase()}')">
                            ${type}
                        </button>
                    `).join('')}
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <p>Duration (minutes):</p>
                <input 
                    type="number" 
                    id="exerciseDuration" 
                    min="0" 
                    placeholder="0"
                    style="width: 100px; padding: 10px;"
                />
            </div>
            
            <button class="btn" onclick="captureExercise()">Continue</button>
        </div>
    `;
}

function selectExercise(type) {
    wellnessRitualState.data.exercise_type = type;
    document.querySelectorAll('[onclick*="selectExercise"]').forEach(btn => btn.classList.remove('selected'));
    event.target.classList.add('selected');
}

function captureExercise() {
    wellnessRitualState.data.exercise_duration = parseInt(document.getElementById('exerciseDuration').value) || 0;
    advanceWellnessStep();
}

// Step 6: Social & Outdoor Time
function renderSocialStep() {
    const timeCategory = wellnessRitualState.data.time_of_day_category;
    let aiMessage = "Any social time or fresh air today?";
    
    if (timeCategory === 'evening') {
        aiMessage = "Did you have any social time or outdoor time today? Even brief interactions count.";
    }
    
    return `
        <div class="wellness-step">
            <div class="ai-message">
                <p>${aiMessage}</p>
            </div>
            
            <div style="margin: 20px 0;">
                <p>Social contact:</p>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    ${['None', 'Text/DM', 'Call', 'In-person'].map(type => `
                        <button class="btn btn-secondary" onclick="selectSocialContact('${type.toLowerCase()}')">
                            ${type}
                        </button>
                    `).join('')}
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <p>Outdoor/fresh air time (minutes):</p>
                <input 
                    type="number" 
                    id="outdoorTime" 
                    min="0" 
                    placeholder="0"
                    style="width: 100px; padding: 10px;"
                />
            </div>
            
            <button class="btn" onclick="captureSocial()">Continue</button>
        </div>
    `;
}

function selectSocialContact(type) {
    wellnessRitualState.data.social_contact = type;
    document.querySelectorAll('[onclick*="selectSocialContact"]').forEach(btn => btn.classList.remove('selected'));
    event.target.classList.add('selected');
}

function captureSocial() {
    wellnessRitualState.data.outdoor_time_minutes = parseInt(document.getElementById('outdoorTime').value) || 0;
    advanceWellnessStep();
}

// Step 7: Medication (if applicable)
async function renderMedicationStep() {
    // Check if user has medications
    try {
        const response = await fetch(`/api/user/medications?username=${encodeURIComponent(currentUser)}`);
        const data = await response.json();
        
        if (!data.has_medications) {
            advanceWellnessStep();
            return '';
        }
        
        return `
            <div class="wellness-step">
                <div class="ai-message">
                    <p>Have you taken your meds today?</p>
                </div>
                
                <div style="margin: 20px 0;">
                    <div style="display: flex; gap: 10px;">
                        <button class="btn btn-success" onclick="setMedicationStatus(true)">Yes, took them</button>
                        <button class="btn btn-warning" onclick="setMedicationStatus(false)">Not yet</button>
                    </div>
                </div>
                
                <div id="medicationReasonContainer" style="display: none; margin: 20px 0;">
                    <p>Any reason?</p>
                    <textarea 
                        id="medicationReason" 
                        rows="3"
                        placeholder="Forgot, ran out, side effects, etc."
                        style="width: 100%; padding: 12px; border-radius: 8px; border: 2px solid #e0e0e0;"
                    ></textarea>
                </div>
                
                <button class="btn" onclick="captureMedication()">Continue</button>
            </div>
        `;
    } catch (error) {
        console.error('Error checking medications:', error);
        advanceWellnessStep();
        return '';
    }
}

function setMedicationStatus(taken) {
    wellnessRitualState.data.medication_taken = taken;
    const reasonContainer = document.getElementById('medicationReasonContainer');
    if (taken) {
        reasonContainer.style.display = 'none';
    } else {
        reasonContainer.style.display = 'block';
    }
}

function captureMedication() {
    if (!wellnessRitualState.data.medication_taken) {
        wellnessRitualState.data.medication_reason_if_missed = document.getElementById('medicationReason').value;
    }
    advanceWellnessStep();
}

// Step 8: Energy & Capacity
function renderEnergyStep() {
    return `
        <div class="wellness-step">
            <div class="ai-message">
                <p>On a scale of 1-10, what's your energy and ability to cope today?</p>
            </div>
            
            <div style="margin: 30px 0;">
                <p style="font-size: 0.9em; color: #999; margin-bottom: 10px;">Energy Level:</p>
                <div class="mood-scale">
                    ${[1,2,3,4,5,6,7,8,9,10].map(num => `
                        <button class="mood-btn" onclick="selectEnergyLevel(${num})">${num}</button>
                    `).join('')}
                </div>
            </div>
            
            <div style="margin: 30px 0;">
                <p style="font-size: 0.9em; color: #999; margin-bottom: 10px;">Capacity to Cope:</p>
                <div class="mood-scale">
                    ${[1,2,3,4,5,6,7,8,9,10].map(num => `
                        <button class="mood-btn" onclick="selectCapacity(${num})">${num}</button>
                    `).join('')}
                </div>
            </div>
            
            <button class="btn" onclick="captureEnergy()">Continue</button>
        </div>
    `;
}

function selectEnergyLevel(num) {
    wellnessRitualState.data.energy_level = num;
    document.querySelectorAll('.mood-scale .mood-btn').forEach(btn => btn.classList.remove('selected'));
    document.querySelectorAll('.mood-scale')[0].querySelectorAll('.mood-btn')[num-1].classList.add('selected');
}

function selectCapacity(num) {
    wellnessRitualState.data.capacity_index = num;
    document.querySelectorAll('.mood-scale .mood-btn').forEach(btn => btn.classList.remove('selected'));
    document.querySelectorAll('.mood-scale')[1].querySelectorAll('.mood-btn')[num-1].classList.add('selected');
}

function captureEnergy() {
    advanceWellnessStep();
}

// Step 9: Homework/Weekly Goals
async function renderHomeworkStep() {
    try {
        const response = await fetch(`/api/homework/current?username=${encodeURIComponent(currentUser)}`);
        const data = await response.json();
        
        if (!data.has_homework && !data.has_weekly_goal) {
            advanceWellnessStep();
            return '';
        }
        
        let html = '<div class="wellness-step">';
        
        if (data.has_weekly_goal) {
            html += `
                <div class="ai-message">
                    <p>You said you'd focus on <strong>${data.weekly_goal}</strong> this week. How's that going?</p>
                </div>
                
                <div style="margin: 20px 0;">
                    <div class="mood-scale">
                        ${[1,2,3,4,5,6,7,8,9,10].map(num => `
                            <button class="mood-btn" onclick="setWeeklyGoalProgress(${num})">${num}</button>
                        `).join('')}
                    </div>
                </div>
                
                <textarea 
                    id="goalNote"
                    rows="3"
                    placeholder="Any notes about your progress?"
                    style="width: 100%; padding: 12px; border-radius: 8px; border: 2px solid #e0e0e0; margin: 15px 0;"
                ></textarea>
            `;
        }
        
        if (data.has_homework) {
            html += `
                <div class="ai-message" style="margin-top: 20px;">
                    <p>${data.clinician_name || 'Your clinician'} gave you homework: <strong>${data.homework_title}</strong></p>
                </div>
                
                <div style="margin: 20px 0;">
                    <div style="display: flex; gap: 10px;">
                        <button class="btn btn-success" onclick="setHomeworkStatus(true)">Completed</button>
                        <button class="btn btn-warning" onclick="setHomeworkStatus(false)">Not yet</button>
                    </div>
                </div>
                
                <div id="homeworkBlockersContainer" style="display: none; margin: 20px 0;">
                    <p>What got in the way?</p>
                    <textarea 
                        id="homeworkBlockers"
                        rows="3"
                        placeholder="Too tired, forgot, felt overwhelmed, etc."
                        style="width: 100%; padding: 12px; border-radius: 8px; border: 2px solid #e0e0e0;"
                    ></textarea>
                </div>
            `;
        }
        
        html += '<button class="btn" onclick="captureHomework()">Continue</button>';
        html += '</div>';
        
        return html;
    } catch (error) {
        console.error('Error loading homework:', error);
        advanceWellnessStep();
        return '';
    }
}

function setWeeklyGoalProgress(num) {
    wellnessRitualState.data.weekly_goal_progress = num;
}

function setHomeworkStatus(completed) {
    wellnessRitualState.data.homework_completed = completed;
    const blockersContainer = document.getElementById('homeworkBlockersContainer');
    if (completed) {
        blockersContainer.style.display = 'none';
    } else {
        blockersContainer.style.display = 'block';
    }
}

function captureHomework() {
    wellnessRitualState.data.goal_note = document.getElementById('goalNote')?.value || '';
    if (!wellnessRitualState.data.homework_completed) {
        wellnessRitualState.data.homework_blockers = document.getElementById('homeworkBlockers')?.value || '';
    }
    advanceWellnessStep();
}

// Step 10: Wrap-up (AI Reflection)
function renderWrapUpStep() {
    const aiReflection = generateAIReflection(wellnessRitualState.data);
    wellnessRitualState.data.ai_reflection = aiReflection;
    
    return `
        <div class="wellness-step">
            <div class="ai-message celebratory">
                <p>${aiReflection}</p>
            </div>
            
            <div style="margin: 30px 0;">
                <button class="btn btn-success" onclick="submitWellnessRitual()">
                    Done! Save Check-in
                </button>
            </div>
        </div>
    `;
}

function generateAIReflection(data) {
    // Generate personalized closing message based on data captured
    let reflection = '';
    
    // Acknowledge what they shared
    const positives = [];
    const concerns = [];
    
    if (data.mood >= 7) positives.push('your mood is solid');
    if (data.sleep_quality >= 7) positives.push('you slept well');
    if (data.exercise_duration > 20) positives.push('you moved your body');
    if (data.social_contact !== 'none') positives.push('you stayed connected');
    if (data.medication_taken) positives.push('you took your meds on time');
    
    if (data.mood <= 3) concerns.push('your mood is low');
    if (data.sleep_quality <= 3) concerns.push('sleep is rough');
    if (data.exercise_type === 'none') concerns.push('movement could help');
    if (data.hydration_level === 'low') concerns.push('hydration matters');
    
    // Build message
    if (concerns.length > 0) {
        reflection = `I see ${concerns.join(' and ')}. That's real, and I'm glad you're checking in. `;
    }
    
    if (positives.length > 0) {
        reflection += `What's great is ${positives.join(', ')}. `;
    }
    
    reflection += `You showed up for yourself today. That's the win. 💙`;
    
    return reflection;
}

// Flow control
function advanceWellnessStep() {
    wellnessRitualState.currentStep++;
    if (wellnessRitualState.currentStep < wellnessRitualState.steps.length) {
        showWellnessStep(wellnessRitualState.steps[wellnessRitualState.currentStep]);
    }
}

// Submit to backend
async function submitWellnessRitual() {
    try {
        // Add metadata
        wellnessRitualState.data.session_duration_seconds = Math.floor(
            (new Date() - wellnessRitualState.startTime) / 1000
        );
        
        const response = await fetch('/api/wellness/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: currentUser,
                ...wellnessRitualState.data
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Save to localStorage that user logged today
            localStorage.setItem(`wellnessLastLog_${currentUser}`, new Date().toLocaleDateString('en-GB'));
            
            // Show success and update UI
            showWellnessSuccess();
            
            // Update streaks
            await updateWellnessStreaks();
            
            // Close modal
            document.getElementById('wellnessRitualModal').style.display = 'none';
        } else {
            alert('Error saving wellness check-in');
        }
    } catch (error) {
        console.error('Error submitting wellness ritual:', error);
        alert('Connection error');
    }
}

function showWellnessSuccess() {
    const container = document.getElementById('wellnessRitualContent');
    container.innerHTML = `
        <div style="text-align: center; padding: 40px;">
            <h2 style="color: #28a745; font-size: 2em; margin-bottom: 10px;">✓ Check-in Complete!</h2>
            <p style="font-size: 1.1em; color: #666; margin-bottom: 20px;">You're doing great staying consistent.</p>
            <button class="btn btn-success" onclick="closeWellnessRitual()">Close</button>
        </div>
    `;
}

function closeWellnessRitual() {
    document.getElementById('wellnessRitualModal').style.display = 'none';
}
```

---

## Backend Implementation

### 1. API Endpoints (api.py)

#### POST /api/wellness/log
```python
@app.route('/api/wellness/log', methods=['POST'])
def create_wellness_log():
    """Create a new daily wellness ritual log"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        # Insert wellness log
        cur.execute("""
            INSERT INTO wellness_logs (
                username, mood, mood_descriptor, mood_context,
                sleep_quality, sleep_notes, hydration_level, total_hydration_cups,
                exercise_type, exercise_duration, outdoor_time_minutes, social_contact,
                medication_taken, medication_reason_if_missed, caffeine_intake_time,
                energy_level, capacity_index, weekly_goal_progress,
                homework_completed, homework_blockers, emotional_narrative,
                ai_reflection, time_of_day_category, session_duration_seconds
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            username,
            data.get('mood'),
            data.get('mood_descriptor'),
            data.get('mood_context'),
            data.get('sleep_quality'),
            data.get('sleep_notes'),
            data.get('hydration_level'),
            data.get('total_hydration_cups'),
            data.get('exercise_type'),
            data.get('exercise_duration'),
            data.get('outdoor_time_minutes'),
            data.get('social_contact'),
            data.get('medication_taken'),
            data.get('medication_reason_if_missed'),
            data.get('caffeine_intake_time'),
            data.get('energy_level'),
            data.get('capacity_index'),
            data.get('weekly_goal_progress'),
            data.get('homework_completed'),
            data.get('homework_blockers'),
            data.get('emotional_narrative'),
            data.get('ai_reflection'),
            data.get('time_of_day_category'),
            data.get('session_duration_seconds')
        ))
        
        conn.commit()
        wellness_log_id = cur.lastrowid
        
        # Update AI memory with new wellness data
        update_ai_memory(username)
        
        # Log event for audit
        log_event(username, 'wellness', 'daily_ritual_completed', 
                  f"Mood: {data.get('mood')}/10, Energy: {data.get('energy_level')}/10")
        
        conn.close()
        
        return jsonify({
            'success': True,
            'wellness_log_id': wellness_log_id,
            'message': 'Wellness check-in saved'
        }), 201
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'wellness/log')


#### GET /api/wellness/today
```python
@app.route('/api/wellness/today', methods=['GET'])
def get_today_wellness_log():
    """Get today's wellness log if it exists"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        
        today = datetime.now().date()
        
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        row = cur.execute("""
            SELECT * FROM wellness_logs
            WHERE username = %s AND DATE(timestamp) = %s
            LIMIT 1
        """, (username, today)).fetchone()
        
        conn.close()
        
        if row:
            result = dict(zip([c[0] for c in cur.description], row))
            return jsonify({
                'exists': True,
                'log': result
            }), 200
        else:
            return jsonify({
                'exists': False
            }), 200
            
    except Exception as e:
        return handle_exception(e, request.endpoint or 'wellness/today')


#### GET /api/wellness/summary
```python
@app.route('/api/wellness/summary', methods=['GET'])
def get_wellness_summary():
    """Get wellness summary for dashboard (last 7/30 days)"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        
        period = request.args.get('period', '7')  # 7 or 30 days
        days = int(period)
        
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        logs = cur.execute("""
            SELECT mood, sleep_quality, energy_level, exercise_duration,
                   medication_taken, hydration_level, timestamp
            FROM wellness_logs
            WHERE username = %s 
            AND timestamp >= NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
        """, (username, days)).fetchall()
        
        conn.close()
        
        if not logs:
            return jsonify({
                'summary': {},
                'period_days': days
            }), 200
        
        # Calculate summary statistics
        moods = [log[0] for log in logs if log[0]]
        sleeps = [log[1] for log in logs if log[1]]
        energies = [log[2] for log in logs if log[2]]
        exercise_durations = [log[3] for log in logs if log[3]]
        med_taken = sum(1 for log in logs if log[4])
        hydration_count = {level: 0 for level in ['low', 'medium', 'high']}
        for log in logs:
            if log[5]:
                hydration_count[log[5]] += 1
        
        summary = {
            'logs_count': len(logs),
            'mood_avg': sum(moods) / len(moods) if moods else 0,
            'mood_trend': 'up' if len(moods) > 1 and moods[0] > moods[-1] else 'down',
            'sleep_avg': sum(sleeps) / len(sleeps) if sleeps else 0,
            'energy_avg': sum(energies) / len(energies) if energies else 0,
            'exercise_total_mins': sum(exercise_durations),
            'med_adherence_percent': (med_taken / len(logs) * 100) if logs else 0,
            'hydration_distribution': hydration_count,
            'period_days': days
        }
        
        return jsonify({'summary': summary}), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'wellness/summary')
```

#### GET /api/user/medications
```python
@app.route('/api/user/medications', methods=['GET'])
def get_user_medications():
    """Check if user has medications and get details"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        # Check if user has medications
        meds = cur.execute("""
            SELECT medication_name, dosage, frequency, time_of_day
            FROM patient_medications
            WHERE username = %s AND is_active = TRUE
        """, (username,)).fetchall()
        
        conn.close()
        
        return jsonify({
            'has_medications': len(meds) > 0,
            'medications': [
                {
                    'name': m[0],
                    'dosage': m[1],
                    'frequency': m[2],
                    'time_of_day': m[3]
                } for m in meds
            ] if meds else []
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'user/medications')
```

#### GET /api/homework/current
```python
@app.route('/api/homework/current', methods=['GET'])
def get_current_homework():
    """Get current homework and weekly goal"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        # Get current homework (due today or later)
        homework = cur.execute("""
            SELECT id, title, description FROM homework
            WHERE patient_username = %s
            AND due_date >= DATE(NOW())
            ORDER BY due_date ASC
            LIMIT 1
        """, (username,)).fetchone()
        
        # Get current weekly focus
        this_week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        weekly_focus = cur.execute("""
            SELECT focus_type, focus_custom_text FROM weekly_focus
            WHERE username = %s
            AND week_start_date = %s
        """, (username, this_week_start.date())).fetchone()
        
        conn.close()
        
        return jsonify({
            'has_homework': bool(homework),
            'homework_title': homework[1] if homework else None,
            'homework_id': homework[0] if homework else None,
            'has_weekly_goal': bool(weekly_focus),
            'weekly_goal': weekly_focus[0] or weekly_focus[1] if weekly_focus else None
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'homework/current')
```

### 2. Integration with Existing Systems

#### Update AI Memory
Modify `update_ai_memory()` function to include wellness data:

```python
def update_ai_memory(username):
    """Update AI's memory with latest wellness patterns"""
    try:
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        # Get last 14 days of wellness logs
        wellness_logs = cur.execute("""
            SELECT mood, sleep_quality, exercise_duration, energy_level,
                   medication_taken, hydration_level
            FROM wellness_logs
            WHERE username = %s
            AND timestamp >= NOW() - INTERVAL '14 days'
            ORDER BY timestamp DESC
        """, (username,)).fetchall()
        
        if not wellness_logs:
            return
        
        # Analyze patterns
        avg_mood = sum(log[0] for log in wellness_logs if log[0]) / len([l for l in wellness_logs if l[0]])
        avg_sleep = sum(log[1] for log in wellness_logs if log[1]) / len([l for l in wellness_logs if l[1]])
        total_exercise = sum(log[2] for log in wellness_logs if log[2])
        avg_energy = sum(log[3] for log in wellness_logs if log[3]) / len([l for l in wellness_logs if l[3]])
        med_adherence = sum(1 for log in wellness_logs if log[4]) / len(wellness_logs)
        
        memory = f"""
        Recent wellness patterns (14-day window):
        - Average mood: {avg_mood:.1f}/10
        - Average sleep quality: {avg_sleep:.1f}/10
        - Total exercise minutes: {total_exercise}
        - Average energy: {avg_energy:.1f}/10
        - Medication adherence: {med_adherence*100:.0f}%
        
        Observations:
        - Patient shows {' consistent' if avg_mood > 6 else ' variable'} mood
        - {'Sleep is a strength' if avg_sleep > 7 else 'Sleep needs support'}
        - {'Good exercise compliance' if total_exercise > 60 else 'Exercise is a barrier'}
        - {'High medication adherence' if med_adherence > 0.9 else 'Medication adherence needs work'}
        """
        
        cur.execute("""
            UPDATE ai_memory SET memory_summary = %s, last_updated = NOW()
            WHERE username = %s
        """, (memory, username))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error updating AI memory: {e}")
```

#### Update Streak Tracking
Add wellness streak updates to streak system:

```python
def update_wellness_streaks(username):
    """Update wellness habit streaks after daily ritual"""
    try:
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        # Check if user logged today
        today = datetime.now().date()
        logged_today = cur.execute("""
            SELECT 1 FROM wellness_logs
            WHERE username = %s AND DATE(timestamp) = %s
        """, (username, today)).fetchone()
        
        if logged_today:
            # Increment wellness check-in streak
            update_habit_streak(username, 'wellness_checkin', 1)
            
            # Get today's log to check other streaks
            log = cur.execute("""
                SELECT hydration_level, exercise_duration, medication_taken,
                       sleep_quality, social_contact
                FROM wellness_logs
                WHERE username = %s AND DATE(timestamp) = %s
            """, (username, today)).fetchone()
            
            if log:
                if log[0]:  # hydration logged
                    update_habit_streak(username, 'hydration', 1)
                if log[1] and log[1] > 0:  # exercise done
                    update_habit_streak(username, 'exercise', 1)
                if log[2]:  # meds taken
                    update_habit_streak(username, 'medication', 1)
                if log[3] and log[3] >= 7:  # 7+ hours sleep
                    update_habit_streak(username, 'sleep_quality', 1)
                if log[4] != 'none':  # social contact
                    update_habit_streak(username, 'social_connection', 1)
        
        conn.close()
        
    except Exception as e:
        print(f"Error updating wellness streaks: {e}")
```

### 3. CSS Styling

Add to templates/index.html `<style>` section:

```css
/* Wellness Ritual Styling */
.wellness-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
}

.wellness-header {
    text-align: center;
    margin-bottom: 30px;
}

.wellness-header h2 {
    font-size: 1.8em;
    margin-bottom: 10px;
    color: #2c3e50;
}

.wellness-subheader {
    color: #7f8c8d;
    font-size: 0.95em;
}

.wellness-conversation {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}

.wellness-step {
    animation: fadeIn 0.3s ease-in;
}

.ai-message {
    background: #ecf0f1;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 20px;
    border-left: 4px solid #3498db;
}

.ai-message p {
    margin: 0;
    font-size: 1em;
    line-height: 1.5;
    color: #2c3e50;
}

.ai-message.celebratory {
    background: #d5f4e6;
    border-left-color: #27ae60;
}

.mood-scale {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin: 20px 0;
    flex-wrap: wrap;
}

.mood-btn {
    flex: 0 1 calc(10% - 8px);
    min-width: 40px;
    padding: 10px 5px;
    text-align: center;
    border: 2px solid #e0e0e0;
    background: white;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.8em;
}

.mood-btn:hover {
    border-color: #3498db;
    background: #ebf5fb;
}

.mood-btn.selected {
    background: #3498db;
    color: white;
    border-color: #3498db;
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.mood-descriptors {
    margin: 20px 0;
}

.descriptor-btn {
    padding: 8px 16px;
    border: 2px solid #e0e0e0;
    background: white;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9em;
}

.descriptor-btn:hover {
    border-color: #3498db;
}

.descriptor-btn.selected {
    background: #3498db;
    color: white;
    border-color: #3498db;
}

.wellness-progress {
    background: white;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 20px;
}

.progress-bar {
    background: #3498db;
    height: 4px;
    border-radius: 2px;
    transition: width 0.3s ease;
    margin-bottom: 10px;
}

.wellness-already-logged {
    background: #d5f4e6;
    border-left: 4px solid #27ae60;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
}

.wellness-modal {
    max-width: 500px !important;
    width: 90% !important;
    max-height: 90vh;
    overflow-y: auto;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.btn-small {
    padding: 8px 12px;
    border: 1px solid #e0e0e0;
    background: white;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9em;
    transition: all 0.2s;
}

.btn-small:hover {
    background: #f5f5f5;
}

.btn-success {
    background: #27ae60;
    color: white;
    border: none;
}

.btn-success:hover {
    background: #229954;
}

.btn-warning {
    background: #f39c12;
    color: white;
    border: none;
}

.btn-warning:hover {
    background: #e67e22;
}
```

---

## Integration Checklist

- [ ] Create wellness_logs table in database
- [ ] Add medication-related endpoints
- [ ] Implement wellness ritual frontend (HTML + JS)
- [ ] Add backend API endpoints (POST/GET wellness data)
- [ ] Update AI memory function to include wellness patterns
- [ ] Add streak tracking for wellness habits
- [ ] Add CSS styling
- [ ] Test time-aware question logic
- [ ] Test data submission and database storage
- [ ] Update clinician dashboard to show wellness summaries
- [ ] Add wellness metrics to patient profile
- [ ] Create migration path from old mood logs to new wellness logs
- [ ] Test with real user flow

---

## Notes for Implementation

1. **Time-aware Logic**: Use `datetime.now().hour` to determine morning (6-12), afternoon (12-17), evening (17-23)
2. **Data Persistence**: Save wellness data to database immediately, not localStorage
3. **User Experience**: Show 300-400ms fade transitions between steps for smoothness
4. **Error Handling**: Gracefully skip medication/homework questions if data doesn't exist
5. **Clinician View**: Build summary dashboard showing rolling 7-day and 30-day trends
6. **Mobile**: Ensure touch-friendly button sizes (minimum 44px height)
7. **Accessibility**: Use semantic HTML, ARIA labels for complex interactions
8. **Performance**: Lazy-load meditation/homework data only when needed

