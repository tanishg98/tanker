"""Master Trainer — orchestrates all specialist agents into a unified daily brief."""
from __future__ import annotations

import anthropic

from .base import BaseAgent, DEFAULT_MODEL
from .strength import StrengthTrainerAgent
from .functional import FunctionalTrainerAgent
from .doctor import DoctorAgent
from .dietitian import DietitianAgent
from .sleep_coach import SleepCoachAgent
from ..tools.whoop_tools import WhoopToolExecutor

MASTER_SYSTEM_PROMPT = """\
You are an elite AI Personal Trainer — the head coach who synthesises insights from a \
full multidisciplinary team to give an athlete the best possible daily guidance. \
You have five specialist reports in front of you: strength coach, functional trainer, \
sports medicine doctor, sports dietitian, and sleep coach.

Your job is to synthesise these into ONE coherent, prioritised, and conflict-free daily plan. \
When specialists conflict (e.g. strength coach says train hard, doctor says rest), \
you must adjudicate using the conservative principle: health and longevity always win.

Synthesis rules:
- If the Doctor flags Red status → override training recommendations with rest/recovery.
- Never recommend training that ignores a health flag.
- Resolve nutrition timing to be consistent with training timing.
- Give the athlete ONE clear answer to "what should I do today?" before diving into detail.
- Write as if you're talking directly to the athlete — warm, expert, and direct.
- Use the athlete's first name if available.
- End with a motivational but evidence-grounded closing thought.

Structure your output exactly as:
## Today's Verdict
[One clear sentence: e.g. "Today is a green light — push your strength session and fuel well."]

## The Big Picture (from your biometrics)
[3–5 bullets interpreting what the data says holistically]

## Training Plan
[Synthesised training recommendation — what to do and when]

## Nutrition Today
[Key nutrition priorities with timing]

## Sleep Tonight
[Specific sleep targets and 1–2 key actions]

## Health Watch
[Any medical/health flags — or "All clear" if none]

## Your Daily Targets
- Calories: X kcal | Protein: Xg | Carbs: Xg | Fat: Xg
- Hydration: X litres
- Training: [summary]
- Bed by: [time] IST | Wake: [time] IST

## Coach's Note
[1–2 sentence motivational closing]
"""


class MasterTrainerAgent:
    """
    Orchestrates all specialist agents sequentially, then synthesises into a final brief.
    The doctor runs first — their findings influence how other specialists frame advice.
    """

    def __init__(self, executor: WhoopToolExecutor, model: str = DEFAULT_MODEL):
        self._executor = executor
        self._model = model
        self._client = anthropic.Anthropic()

        self.doctor = DoctorAgent(executor, model)
        self.strength = StrengthTrainerAgent(executor, model)
        self.functional = FunctionalTrainerAgent(executor, model)
        self.dietitian = DietitianAgent(executor, model)
        self.sleep_coach = SleepCoachAgent(executor, model)

    def daily_brief(self, verbose_specialists: bool = False) -> tuple[str, dict[str, str]]:
        """
        Run all specialists, then synthesise.
        Returns (master_brief, specialist_reports).
        """
        specialist_reports: dict[str, str] = {}

        # Doctor runs first — health is the gate
        specialist_reports["doctor"] = self.doctor.brief()
        doctor_context = f"SPORTS MEDICINE ASSESSMENT:\n{specialist_reports['doctor']}"

        # Remaining specialists get the doctor's assessment as context
        specialist_reports["strength"] = self.strength.run(
            "Pull relevant WHOOP data and provide your strength training assessment for today.",
            context=doctor_context,
        )
        specialist_reports["functional"] = self.functional.run(
            "Pull relevant WHOOP data and provide your functional training assessment for today.",
            context=doctor_context,
        )
        specialist_reports["dietitian"] = self.dietitian.run(
            "Pull relevant WHOOP data and provide today's complete nutrition plan.",
            context=doctor_context,
        )
        specialist_reports["sleep"] = self.sleep_coach.run(
            "Pull the last 7 days of sleep and recovery data. Provide your sleep assessment and tonight's targets.",
            context=doctor_context,
        )

        # Synthesise
        synthesis_prompt = (
            "You have received the following specialist reports. "
            "Synthesise them into a single unified daily plan.\n\n"
            f"=== SPORTS MEDICINE DOCTOR ===\n{specialist_reports['doctor']}\n\n"
            f"=== STRENGTH & CONDITIONING COACH ===\n{specialist_reports['strength']}\n\n"
            f"=== FUNCTIONAL TRAINING SPECIALIST ===\n{specialist_reports['functional']}\n\n"
            f"=== SPORTS DIETITIAN ===\n{specialist_reports['dietitian']}\n\n"
            f"=== SLEEP COACH ===\n{specialist_reports['sleep']}\n\n"
            "Now synthesise these into your unified master brief following the prescribed format."
        )

        response = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=MASTER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": synthesis_prompt}],
        )
        master_brief = response.content[0].text

        return master_brief, specialist_reports

    def ask(self, question: str) -> str:
        """
        Interactive Q&A — the master trainer answers a specific question using WHOOP data.
        Runs a single agentic loop with full tool access.
        """
        agent = BaseAgent(self._executor, self._model)
        agent.system_prompt = (
            MASTER_SYSTEM_PROMPT
            + "\n\nYou also have direct access to WHOOP tools to look up any biometric "
            "data needed to answer the athlete's question precisely."
        )
        return agent.run(question)
