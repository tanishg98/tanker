"""WHOOP API v1 client — typed, paginated, with local cache."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

from .models import (
    BodyMeasurement,
    Cycle,
    Recovery,
    Sleep,
    UserProfile,
    WhoopSnapshot,
    Workout,
)

BASE_URL = "https://api.prod.whoop.com/developer/v1"
CACHE_DIR = Path.home() / ".cache" / "whoop_ai_trainer"

# Sport ID → human name mapping (partial — covers common sports)
SPORT_NAMES: dict[int, str] = {
    -1: "Activity",
    0: "Running",
    1: "Cycling",
    16: "Baseball",
    17: "Basketball",
    18: "Rowing",
    19: "Fencing",
    20: "Field Hockey",
    21: "Football",
    22: "Golf",
    24: "Ice Hockey",
    25: "Lacrosse",
    27: "Soccer",
    28: "Softball",
    29: "Squash",
    30: "Swimming",
    31: "Tennis",
    32: "Track & Field",
    33: "Volleyball",
    34: "Water Polo",
    35: "Wrestling",
    36: "Boxing",
    38: "Dance",
    39: "Pilates",
    42: "Skiing",
    43: "Hiking",
    44: "Yoga",
    45: "Weightlifting",
    47: "Cross Country Skiing",
    48: "Functional Fitness",
    49: "Duathlon",
    51: "Gymnastics",
    52: "Horseback Riding",
    53: "Kayaking",
    55: "Martial Arts",
    56: "Mountain Biking",
    57: "Powerlifting",
    59: "Rock Climbing",
    60: "Rowing",
    61: "Sailing",
    62: "Skating",
    63: "Snowboarding",
    64: "Softball",
    65: "Stairmaster",
    66: "Stand Up Paddleboarding",
    67: "Surfing",
    68: "Swimming",
    69: "Triathlon",
    70: "Walking",
    71: "Water Sports",
    72: "Wheelchair",
    73: "Obstacle Course Racing",
    74: "Indoor Cycling",
    75: "Jump Rope",
    76: "Australian Football",
    77: "Handball",
    78: "Kite Surfing",
    79: "Meditation",
    80: "Lap Swimming",
    81: "HIIT",
    82: "Pickleball",
    83: "Padel",
    84: "Racquetball",
    85: "Badminton",
    86: "Skateboarding",
    87: "Surfing",
    88: "Touch Football",
    89: "Ultimate",
    90: "Disc Golf",
    91: "Spikeball",
    92: "Wheelchair",
    93: "Cricket",
    94: "Rugby",
    95: "Table Tennis",
    96: "Esports",
}


def sport_name(sport_id: int) -> str:
    return SPORT_NAMES.get(sport_id, f"Sport {sport_id}")


class WhoopClient:
    def __init__(self, access_token: str):
        self._http = httpx.Client(
            base_url=BASE_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _get(self, path: str, params: dict | None = None) -> Any:
        resp = self._http.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    def _paginate(self, path: str, limit: int = 25, extra_params: dict | None = None) -> list[dict]:
        results = []
        params: dict = {"limit": limit, **(extra_params or {})}
        while True:
            data = self._get(path, params)
            results.extend(data.get("records", []))
            token = data.get("next_token")
            if not token:
                break
            params["nextToken"] = token
        return results

    # ── Profile & body ────────────────────────────────────────────────────────

    def get_profile(self) -> UserProfile:
        return UserProfile(**self._get("/user/profile/basic"))

    def get_body_measurement(self) -> BodyMeasurement:
        return BodyMeasurement(**self._get("/body/measurement"))

    # ── Sleep ─────────────────────────────────────────────────────────────────

    def get_sleeps(self, days: int = 7) -> list[Sleep]:
        start = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        raw = self._paginate("/activity/sleep", extra_params={"start": start})
        return [Sleep(**r) for r in raw]

    def get_latest_sleep(self) -> Sleep | None:
        sleeps = self.get_sleeps(days=2)
        return sleeps[0] if sleeps else None

    # ── Recovery ──────────────────────────────────────────────────────────────

    def get_recoveries(self, days: int = 7) -> list[Recovery]:
        start = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        raw = self._paginate("/recovery", extra_params={"start": start})
        return [Recovery(**r) for r in raw]

    def get_latest_recovery(self) -> Recovery | None:
        recoveries = self.get_recoveries(days=2)
        return recoveries[0] if recoveries else None

    # ── Workout ───────────────────────────────────────────────────────────────

    def get_workouts(self, days: int = 14) -> list[Workout]:
        start = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        raw = self._paginate("/activity/workout", extra_params={"start": start})
        return [Workout(**r) for r in raw]

    # ── Cycle ─────────────────────────────────────────────────────────────────

    def get_cycles(self, days: int = 7) -> list[Cycle]:
        start = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        raw = self._paginate("/cycle", extra_params={"start": start})
        return [Cycle(**r) for r in raw]

    def get_latest_cycle(self) -> Cycle | None:
        cycles = self.get_cycles(days=2)
        return cycles[0] if cycles else None

    # ── Snapshot ──────────────────────────────────────────────────────────────

    def build_snapshot(self) -> WhoopSnapshot:
        """Fetch all relevant data and return a single aggregate snapshot."""
        profile = self.get_profile()
        body = self.get_body_measurement()
        latest_recovery = self.get_latest_recovery()
        latest_sleep = self.get_latest_sleep()
        latest_cycle = self.get_latest_cycle()
        recent_workouts = self.get_workouts(days=14)
        recent_recoveries = self.get_recoveries(days=7)
        recent_sleeps = self.get_sleeps(days=7)

        snapshot = WhoopSnapshot(
            profile=profile,
            body=body,
            latest_recovery=latest_recovery,
            latest_sleep=latest_sleep,
            latest_cycle=latest_cycle,
            recent_workouts=recent_workouts,
            recent_recoveries=recent_recoveries,
            recent_sleeps=recent_sleeps,
        )

        # Cache snapshot to disk for offline / fast repeated access
        cache_path = CACHE_DIR / "snapshot.json"
        cache_path.write_text(snapshot.model_dump_json(indent=2))
        return snapshot

    def load_cached_snapshot(self) -> WhoopSnapshot | None:
        cache_path = CACHE_DIR / "snapshot.json"
        if cache_path.exists():
            return WhoopSnapshot(**json.loads(cache_path.read_text()))
        return None

    def close(self) -> None:
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
