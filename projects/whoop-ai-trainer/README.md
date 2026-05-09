# WHOOP AI Trainer

An AI fitness trainer that knows your body better than any human coach — because it reads your actual biometrics in real time.

Built on WHOOP's API + Anthropic Claude. Five specialist AI agents (strength coach, functional trainer, sports medicine doctor, dietitian, sleep coach) orchestrated by a master trainer into a single coherent daily plan.

---

## Why this beats a human trainer

| What a human trainer does | What this does |
|---|---|
| Guesses your recovery from how you look | Reads your HRV, RHR, SpO2, skin temp — numerically |
| Generic periodisation plans | Adjusts every session to today's recovery score |
| Nutrition advice based on your word | Calculates exact macros from actual calorie burn data |
| Sleep advice based on vibes | Analyses your sleep stages (deep, REM, light) per night |
| One speciality | Five specialists + synthesis in 90 seconds |
| Available 1 hour/week | Available any time |

---

## Architecture

```
MasterTrainerAgent (orchestrator)
├── DoctorAgent          → Health monitoring, HRV trends, anomaly detection
├── StrengthTrainerAgent → Periodisation, load management, session prescription
├── FunctionalTrainer   → Conditioning, mobility, movement quality
├── DietitianAgent       → Macros, meal timing, recovery nutrition
└── SleepCoachAgent      → Sleep stage analysis, tonight's targets
```

Each specialist is a Claude agent with:
- Domain-specific system prompt with clinical/coaching protocols
- Direct access to WHOOP API tools (recovery, sleep, workout, cycle, body)
- Agentic tool-use loop — it fetches what it needs, reasons, responds

The master trainer synthesises all five reports, resolves conflicts (health always wins), and delivers one coherent plan.

---

## Setup

### 1. Register a WHOOP app

1. Go to [developer.whoop.com](https://developer.whoop.com/)
2. Create a new application
3. Set redirect URI to `http://localhost:8484/callback`
4. Copy your Client ID and Client Secret

### 2. Get an Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Create an API key

### 3. Install

```bash
cd projects/whoop-ai-trainer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure

```bash
cp .env.example .env
# Edit .env with your WHOOP and Anthropic credentials
```

---

## Usage

### Daily Brief (full team report)

```bash
python -m src.main brief
```

Runs all 5 specialists + master synthesis. Takes ~60–90 seconds. Saves report locally.

Add `--verbose` to see each specialist's full report in addition to the synthesis.

### Ask a Question

```bash
python -m src.main ask "Should I do legs today given my HRV?"
python -m src.main ask "What should I eat before my run tonight?"
python -m src.main ask "How has my sleep been this week?"
```

### Interactive Chat

```bash
python -m src.main chat
```

Continuous Q&A session with the master trainer. Uses live WHOOP data.

### Single Specialist Report

```bash
python -m src.main specialist strength
python -m src.main specialist doctor
python -m src.main specialist dietitian
python -m src.main specialist sleep
python -m src.main specialist functional
```

### View History

```bash
python -m src.main history              # today's saved report
python -m src.main history --date 2025-05-08
python -m src.main history --specialist-key doctor  # just the doctor's section
```

---

## WHOOP Data Used

| Metric | Used by |
|---|---|
| Recovery score (0–100%) | All agents — primary readiness gate |
| HRV (RMSSD, ms) | Doctor, Strength, Sleep |
| Resting heart rate | Doctor, Strength |
| SpO2 | Doctor |
| Skin temperature | Doctor |
| Sleep stages (deep, REM, light) | Sleep Coach, Doctor, Dietitian |
| Sleep performance % | Sleep Coach, Master |
| Respiratory rate during sleep | Doctor, Sleep Coach |
| Workout strain (0–21) | Strength, Functional, Dietitian |
| Daily cycle strain | Dietitian, Master |
| Calorie burn | Dietitian |
| HR zones from workouts | Strength, Functional |
| Height, weight, max HR | Dietitian (macro calculations) |

---

## Extending

Add a new specialist in `src/agents/`:

```python
from .base import BaseAgent

class YogaCoachAgent(BaseAgent):
    name = "Yoga & Mindfulness Coach"
    system_prompt = "You are a..."

    def brief(self) -> str:
        return self.run("Fetch recovery data and provide today's yoga/mobility recommendation.")
```

Then register it in `master.py` alongside the existing specialists.
