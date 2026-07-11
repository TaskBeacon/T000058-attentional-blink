from __future__ import annotations

import random as _py_random
from dataclasses import dataclass
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    """Lag-sensitive responder for the Attentional Blink task."""

    continue_key: str = "space"
    continue_rt_s: float = 0.25
    t1_accuracy: float = 0.90
    short_t2_accuracy: float = 0.55
    long_t2_accuracy: float = 0.85
    absent_accuracy: float = 0.80
    timeout_rate: float = 0.02
    rt_mean_s: float = 0.65
    rt_sd_s: float = 0.12
    rt_min_s: float = 0.15

    def __post_init__(self) -> None:
        self._rng: Any = None

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _random(self) -> float:
        if hasattr(self._rng, "random"):
            return float(self._rng.random())
        return float(_py_random.random())

    def _normal(self) -> float:
        if hasattr(self._rng, "normal"):
            return float(self._rng.normal(self.rt_mean_s, self.rt_sd_s))
        if hasattr(self._rng, "gauss"):
            return float(self._rng.gauss(self.rt_mean_s, self.rt_sd_s))
        return self.rt_mean_s

    @staticmethod
    def _task_factors(obs: Observation) -> dict[str, Any]:
        factors = dict(getattr(obs, "task_factors", {}) or {})
        if not factors and isinstance(getattr(obs, "extras", None), dict):
            factors = dict(obs.extras.get("task_factors", {}) or {})
        return factors

    def act(self, obs: Observation) -> Action:
        valid_keys = [str(key) for key in list(obs.valid_keys or [])]
        if not valid_keys:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "no_valid_keys"})

        factors = self._task_factors(obs)
        stage = str(factors.get("stage", getattr(obs, "phase", ""))).lower()
        if any(token in stage for token in ("instruction", "intro", "summary", "good_bye")):
            key = self.continue_key if self.continue_key in valid_keys else valid_keys[0]
            return Action(key=key, rt_s=self.continue_rt_s, meta={"source": "task_sampler", "stage": stage})

        if self._random() < self.timeout_rate:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "stage": stage, "outcome": "timeout"})

        correct_key = str(factors.get("correct_key", ""))
        if stage == "t1_report":
            accuracy = self.t1_accuracy
        elif stage == "t2_report" and correct_key == "0":
            accuracy = self.absent_accuracy
        elif stage == "t2_report" and str(factors.get("t2_present", "")).lower() != "false":
            condition_id = str(getattr(obs, "condition_id", ""))
            accuracy = self.short_t2_accuracy if "short" in condition_id else self.long_t2_accuracy
        else:
            accuracy = 0.75

        if correct_key in valid_keys and self._random() < accuracy:
            key = correct_key
            outcome = "hit"
        else:
            alternatives = [key for key in valid_keys if key != correct_key]
            key = alternatives[int(self._random() * len(alternatives)) % len(alternatives)] if alternatives else valid_keys[0]
            outcome = "miss"
        return Action(
            key=key,
            rt_s=max(self.rt_min_s, self._normal()),
            meta={"source": "task_sampler", "stage": stage, "outcome": outcome, "correct_key": correct_key},
        )
