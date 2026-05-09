"""Pydantic models for all WHOOP API v1 data types."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    user_id: int
    email: str
    first_name: str
    last_name: str


class BodyMeasurement(BaseModel):
    height_meter: float
    weight_kilogram: float
    max_heart_rate: int


# ── Sleep ────────────────────────────────────────────────────────────────────

class SleepStageSummary(BaseModel):
    total_in_bed_time_milli: int
    total_awake_time_milli: int
    total_no_data_time_milli: int
    total_light_sleep_time_milli: int
    total_slow_wave_sleep_time_milli: int
    total_rem_sleep_time_milli: int
    sleep_cycle_count: int
    disturbance_count: int


class SleepNeeded(BaseModel):
    baseline_milli: int
    need_from_sleep_debt_milli: int
    need_from_recent_strain_milli: int
    need_from_recent_nap_milli: int


class SleepScore(BaseModel):
    stage_summary: SleepStageSummary
    sleep_needed: SleepNeeded
    respiratory_rate: Optional[float] = None
    sleep_performance_percentage: Optional[float] = None
    sleep_consistency_percentage: Optional[float] = None
    sleep_efficiency_percentage: Optional[float] = None


class Sleep(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    start: datetime
    end: datetime
    timezone_offset: str
    nap: bool
    score_state: str
    score: Optional[SleepScore] = None


# ── Recovery ─────────────────────────────────────────────────────────────────

class RecoveryScore(BaseModel):
    user_calibrating: bool
    recovery_score: float  # 0–100 %
    resting_heart_rate: float  # bpm
    hrv_rmssd_milli: float  # HRV in ms
    spo2_percentage: Optional[float] = None  # 4.0+ devices
    skin_temp_celsius: Optional[float] = None  # 4.0+ devices


class Recovery(BaseModel):
    cycle_id: int
    sleep_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    score_state: str
    score: Optional[RecoveryScore] = None


# ── Workout ───────────────────────────────────────────────────────────────────

class HeartRateZoneData(BaseModel):
    zone_zero_milli: Optional[int] = None
    zone_one_milli: Optional[int] = None
    zone_two_milli: Optional[int] = None
    zone_three_milli: Optional[int] = None
    zone_four_milli: Optional[int] = None
    zone_five_milli: Optional[int] = None


class WorkoutScore(BaseModel):
    strain: float  # 0–21
    average_heart_rate: int
    max_heart_rate: int
    kilojoule: float
    percent_recorded: float
    distance_meter: Optional[float] = None
    altitude_gain_meter: Optional[float] = None
    altitude_change_meter: Optional[float] = None
    zone_duration: Optional[HeartRateZoneData] = None


class Workout(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    start: datetime
    end: datetime
    timezone_offset: str
    sport_id: int
    score_state: str
    score: Optional[WorkoutScore] = None


# ── Cycle ─────────────────────────────────────────────────────────────────────

class CycleScore(BaseModel):
    strain: float  # 0–21
    kilojoule: float
    average_heart_rate: int
    max_heart_rate: int


class Cycle(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    start: datetime
    end: Optional[datetime] = None
    timezone_offset: str
    score_state: str
    score: Optional[CycleScore] = None


# ── Aggregated snapshot for agent consumption ────────────────────────────────

class WhoopSnapshot(BaseModel):
    """All relevant WHOOP data for a given day, ready for agent analysis."""
    profile: Optional[UserProfile] = None
    body: Optional[BodyMeasurement] = None
    latest_recovery: Optional[Recovery] = None
    latest_sleep: Optional[Sleep] = None
    latest_cycle: Optional[Cycle] = None
    recent_workouts: list[Workout] = Field(default_factory=list)
    recent_recoveries: list[Recovery] = Field(default_factory=list)
    recent_sleeps: list[Sleep] = Field(default_factory=list)
