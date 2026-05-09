"""Claude tool definitions that let agents pull WHOOP data on demand."""
from __future__ import annotations

import json
from typing import Any

from ..whoop.client import WhoopClient, sport_name
from ..whoop.models import WhoopSnapshot

# ── Tool schemas ──────────────────────────────────────────────────────────────

TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "get_recovery_data",
        "description": (
            "Retrieve the user's latest WHOOP recovery score and metrics. "
            "Returns recovery percentage (0-100), HRV (RMSSD in ms), resting heart rate, "
            "and optionally SpO2 and skin temperature. Use this to assess readiness for training."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of past days to retrieve recovery data for (1-30). Default 7.",
                    "default": 7,
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_sleep_data",
        "description": (
            "Retrieve WHOOP sleep analysis including duration, stages (light, REM, deep/SWS), "
            "sleep performance percentage, efficiency, respiratory rate, and sleep need. "
            "Use this to assess sleep quality and recovery."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of past days to retrieve sleep data for (1-14). Default 7.",
                    "default": 7,
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_workout_data",
        "description": (
            "Retrieve recent workout sessions from WHOOP. Returns sport type, strain score (0-21), "
            "duration, average/max HR, calories, heart rate zones, and distance if applicable. "
            "Use this to understand training load and recent activity."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of past days to retrieve workouts for (1-30). Default 14.",
                    "default": 14,
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_cycle_data",
        "description": (
            "Retrieve WHOOP physiological cycle data including total daily strain, "
            "daily calorie burn, and average/max heart rate for the full day. "
            "Use this for overall daily load assessment."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of past days of cycle data to retrieve (1-14). Default 7.",
                    "default": 7,
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_body_and_profile",
        "description": (
            "Retrieve the user's physical measurements (height, weight, max heart rate) "
            "and profile (name, email). Use this for personalised nutrition and training calculations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_full_snapshot",
        "description": (
            "Retrieve a comprehensive snapshot of all WHOOP data including today's recovery, "
            "last night's sleep, recent workouts, recent cycles, and body measurements. "
            "Use this for a full picture assessment rather than querying individual endpoints."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


# ── Tool executor ─────────────────────────────────────────────────────────────

class WhoopToolExecutor:
    """Executes tool calls from Claude agents against the live WHOOP API or cached snapshot."""

    def __init__(self, client: WhoopClient, snapshot: WhoopSnapshot | None = None):
        self._client = client
        self._snapshot = snapshot

    def execute(self, tool_name: str, tool_input: dict) -> str:
        """Dispatch a tool call and return a JSON string result."""
        handlers = {
            "get_recovery_data": self._recovery,
            "get_sleep_data": self._sleep,
            "get_workout_data": self._workout,
            "get_cycle_data": self._cycle,
            "get_body_and_profile": self._body_profile,
            "get_full_snapshot": self._full_snapshot,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
        return handler(tool_input)

    def _recovery(self, inp: dict) -> str:
        days = inp.get("days", 7)
        recoveries = self._client.get_recoveries(days=days)
        result = []
        for r in recoveries:
            entry: dict[str, Any] = {
                "date": r.created_at.date().isoformat(),
                "score_state": r.score_state,
            }
            if r.score:
                entry.update({
                    "recovery_score": r.score.recovery_score,
                    "resting_heart_rate_bpm": r.score.resting_heart_rate,
                    "hrv_rmssd_ms": r.score.hrv_rmssd_milli,
                })
                if r.score.spo2_percentage:
                    entry["spo2_percent"] = r.score.spo2_percentage
                if r.score.skin_temp_celsius:
                    entry["skin_temp_celsius"] = r.score.skin_temp_celsius
            result.append(entry)
        return json.dumps({"recovery_records": result, "count": len(result)}, indent=2)

    def _sleep(self, inp: dict) -> str:
        days = inp.get("days", 7)
        sleeps = self._client.get_sleeps(days=days)
        result = []
        for s in sleeps:
            if s.nap:
                continue  # skip naps unless main sleep
            duration_hr = 0.0
            if s.score and s.score.stage_summary:
                duration_hr = round(s.score.stage_summary.total_in_bed_time_milli / 3_600_000, 2)
            entry: dict[str, Any] = {
                "date": s.start.date().isoformat(),
                "start": s.start.isoformat(),
                "end": s.end.isoformat(),
                "total_in_bed_hours": duration_hr,
                "score_state": s.score_state,
            }
            if s.score:
                ss = s.score.stage_summary
                entry.update({
                    "performance_percent": s.score.sleep_performance_percentage,
                    "efficiency_percent": s.score.sleep_efficiency_percentage,
                    "consistency_percent": s.score.sleep_consistency_percentage,
                    "respiratory_rate": s.score.respiratory_rate,
                    "light_sleep_hours": round(ss.total_light_sleep_time_milli / 3_600_000, 2),
                    "rem_sleep_hours": round(ss.total_rem_sleep_time_milli / 3_600_000, 2),
                    "deep_sleep_hours": round(ss.total_slow_wave_sleep_time_milli / 3_600_000, 2),
                    "awake_hours": round(ss.total_awake_time_milli / 3_600_000, 2),
                    "disturbances": ss.disturbance_count,
                    "sleep_cycles": ss.sleep_cycle_count,
                })
                if s.score.sleep_needed:
                    sn = s.score.sleep_needed
                    entry["sleep_needed_hours"] = round(sn.baseline_milli / 3_600_000, 2)
            result.append(entry)
        return json.dumps({"sleep_records": result, "count": len(result)}, indent=2)

    def _workout(self, inp: dict) -> str:
        days = inp.get("days", 14)
        workouts = self._client.get_workouts(days=days)
        result = []
        for w in workouts:
            duration_min = (w.end - w.start).seconds // 60
            entry: dict[str, Any] = {
                "date": w.start.date().isoformat(),
                "sport": sport_name(w.sport_id),
                "duration_minutes": duration_min,
                "score_state": w.score_state,
            }
            if w.score:
                entry.update({
                    "strain": w.score.strain,
                    "avg_heart_rate_bpm": w.score.average_heart_rate,
                    "max_heart_rate_bpm": w.score.max_heart_rate,
                    "calories_kcal": round(w.score.kilojoule / 4.184, 1),
                })
                if w.score.distance_meter:
                    entry["distance_km"] = round(w.score.distance_meter / 1000, 2)
                if w.score.zone_duration:
                    z = w.score.zone_duration
                    def ms_to_min(v): return round(v / 60_000, 1) if v else 0
                    entry["hr_zones_minutes"] = {
                        "zone_1_easy": ms_to_min(z.zone_one_milli),
                        "zone_2_fat_burn": ms_to_min(z.zone_two_milli),
                        "zone_3_aerobic": ms_to_min(z.zone_three_milli),
                        "zone_4_threshold": ms_to_min(z.zone_four_milli),
                        "zone_5_max": ms_to_min(z.zone_five_milli),
                    }
            result.append(entry)
        return json.dumps({"workouts": result, "count": len(result)}, indent=2)

    def _cycle(self, inp: dict) -> str:
        days = inp.get("days", 7)
        cycles = self._client.get_cycles(days=days)
        result = []
        for c in cycles:
            entry: dict[str, Any] = {
                "date": c.start.date().isoformat(),
                "score_state": c.score_state,
            }
            if c.score:
                entry.update({
                    "day_strain": c.score.strain,
                    "calories_kcal": round(c.score.kilojoule / 4.184, 1),
                    "avg_heart_rate_bpm": c.score.average_heart_rate,
                    "max_heart_rate_bpm": c.score.max_heart_rate,
                })
            result.append(entry)
        return json.dumps({"cycles": result, "count": len(result)}, indent=2)

    def _body_profile(self, _inp: dict) -> str:
        profile = self._client.get_profile()
        body = self._client.get_body_measurement()
        return json.dumps({
            "name": f"{profile.first_name} {profile.last_name}",
            "email": profile.email,
            "height_cm": round(body.height_meter * 100, 1),
            "weight_kg": body.weight_kilogram,
            "max_heart_rate_bpm": body.max_heart_rate,
        }, indent=2)

    def _full_snapshot(self, _inp: dict) -> str:
        snap = self._client.build_snapshot()
        # Return a condensed but complete view
        out: dict[str, Any] = {}

        if snap.profile:
            out["athlete"] = {
                "name": f"{snap.profile.first_name} {snap.profile.last_name}",
            }
        if snap.body:
            out["body"] = {
                "height_cm": round(snap.body.height_meter * 100, 1),
                "weight_kg": snap.body.weight_kilogram,
                "max_hr": snap.body.max_heart_rate,
            }
        if snap.latest_recovery and snap.latest_recovery.score:
            s = snap.latest_recovery.score
            out["today_recovery"] = {
                "score": s.recovery_score,
                "hrv_ms": s.hrv_rmssd_milli,
                "rhr_bpm": s.resting_heart_rate,
                "spo2": s.spo2_percentage,
            }
        if snap.latest_sleep and snap.latest_sleep.score:
            sl = snap.latest_sleep.score
            ss = sl.stage_summary
            out["last_sleep"] = {
                "performance": sl.sleep_performance_percentage,
                "efficiency": sl.sleep_efficiency_percentage,
                "deep_h": round(ss.total_slow_wave_sleep_time_milli / 3_600_000, 2),
                "rem_h": round(ss.total_rem_sleep_time_milli / 3_600_000, 2),
                "light_h": round(ss.total_light_sleep_time_milli / 3_600_000, 2),
                "respiratory_rate": sl.respiratory_rate,
            }
        if snap.latest_cycle and snap.latest_cycle.score:
            c = snap.latest_cycle.score
            out["today_strain"] = {
                "strain": c.strain,
                "calories": round(c.kilojoule / 4.184, 1),
            }
        out["recent_workouts"] = [
            {
                "date": w.start.date().isoformat(),
                "sport": sport_name(w.sport_id),
                "strain": w.score.strain if w.score else None,
                "duration_min": (w.end - w.start).seconds // 60,
            }
            for w in snap.recent_workouts[:5]
        ]
        hrv_trend = [
            r.score.hrv_rmssd_milli
            for r in snap.recent_recoveries
            if r.score
        ]
        if hrv_trend:
            out["hrv_7day_trend"] = hrv_trend
            out["hrv_7day_avg"] = round(sum(hrv_trend) / len(hrv_trend), 1)

        return json.dumps(out, indent=2)
