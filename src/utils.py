from __future__ import annotations

import random
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any


DISTRACTOR_LETTERS = tuple(letter for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if letter not in "BIOQS")
TARGET_DIGITS = tuple(str(value) for value in range(2, 10))
CONDITION_SPECS = {
    "short_present": {"interval": "short", "lag": 4, "t2_present": True, "stream_length": 15},
    "long_present": {"interval": "long", "lag": 8, "t2_present": True, "stream_length": 19},
    "short_absent": {"interval": "short", "lag": 4, "t2_present": False, "stream_length": 15},
    "long_absent": {"interval": "long", "lag": 8, "t2_present": False, "stream_length": 19},
}


class TrialPlan(str):
    """Hashable scalar condition label carrying an immutable trial payload."""

    def __new__(cls, *, condition: str, **payload: Any):
        instance = super().__new__(cls, condition)
        instance.condition = condition
        instance._payload = MappingProxyType({"condition": condition, **payload})
        return instance

    def to_dict(self) -> dict[str, Any]:
        return dict(self._payload)


def _normalized_counts(counts: Mapping[str, Any]) -> dict[str, int]:
    normalized = {name: int(counts.get(name, 0)) for name in CONDITION_SPECS}
    if any(value < 0 for value in normalized.values()):
        raise ValueError("Condition counts must be non-negative.")
    if sum(normalized.values()) <= 0:
        raise ValueError("At least one Attentional Blink condition is required.")
    return normalized


def _build_stream(rng: random.Random, spec: Mapping[str, Any]) -> dict[str, Any]:
    stream_length = int(spec["stream_length"])
    lag = int(spec["lag"])
    t2_index = stream_length - rng.choice((3, 4, 5))
    t1_index = t2_index - lag
    if t1_index < 1:
        raise ValueError("Invalid target positions for RSVP stream.")

    targets = rng.sample(TARGET_DIGITS, 2)
    t1 = targets[0]
    t2 = targets[1] if bool(spec["t2_present"]) else ""

    distractor_count = stream_length - 2
    letters = rng.sample(DISTRACTOR_LETTERS, distractor_count)
    stream: list[str] = []
    letter_index = 0
    for item_index in range(stream_length):
        if item_index == t1_index:
            stream.append(t1)
        elif item_index == t2_index:
            stream.append(t2)
        else:
            stream.append(letters[letter_index])
            letter_index += 1

    protected = {
        t1_index - 1,
        t1_index,
        t1_index + 1,
        t2_index - 1,
        t2_index,
        t2_index + 1,
        stream_length - 1,
    }
    for item_index, value in enumerate(stream):
        if item_index not in protected and value and rng.random() < 0.20:
            stream[item_index] = ""

    roles = ["distractor_blank" if value == "" else "distractor" for value in stream]
    roles[t1_index] = "t1"
    roles[t2_index] = "t2" if bool(spec["t2_present"]) else "t2_absent"
    return {
        "stream": tuple(stream),
        "roles": tuple(roles),
        "t1": t1,
        "t2": t2,
        "t1_index": t1_index,
        "t2_index": t2_index,
    }


def generate_attentional_blink_conditions(
    *,
    block_idx: int,
    condition_counts: Mapping[str, Any],
    seed: int,
    is_practice: bool = False,
) -> list[TrialPlan]:
    """Build a deterministic, fully planned RSVP block."""
    counts = _normalized_counts(condition_counts)
    rng = random.Random(int(seed) + int(block_idx) * 1009 + (500_000 if is_practice else 0))
    labels = [label for label, count in counts.items() for _ in range(count)]
    rng.shuffle(labels)

    plans: list[TrialPlan] = []
    for trial_index, label in enumerate(labels):
        spec = CONDITION_SPECS[label]
        stream_plan = _build_stream(rng, spec)
        condition_id = f"{'practice' if is_practice else f'block_{block_idx}'}_{trial_index + 1:03d}_{label}"
        plans.append(
            TrialPlan(
                condition=label,
                condition_id=condition_id,
                interval=str(spec["interval"]),
                lag=int(spec["lag"]),
                t2_present=bool(spec["t2_present"]),
                is_practice=bool(is_practice),
                trial_index_in_block=trial_index,
                **stream_plan,
            )
        )
    return plans


def summarize_block(trials: list[dict[str, Any]]) -> dict[str, float]:
    scored = [trial for trial in trials if not bool(trial.get("is_practice", False))]
    if not scored:
        return {"t1_accuracy": 0.0, "conditional_t2_accuracy": 0.0, "blink_magnitude": 0.0}

    t1_accuracy = sum(bool(trial.get("t1_correct", False)) for trial in scored) / len(scored)
    conditional = [trial for trial in scored if bool(trial.get("t1_correct", False))]
    conditional_t2_accuracy = (
        sum(bool(trial.get("t2_correct", False)) for trial in conditional) / len(conditional)
        if conditional
        else 0.0
    )
    short_present = [
        trial for trial in conditional if trial.get("condition") == "short_present"
    ]
    long_present = [
        trial for trial in conditional if trial.get("condition") == "long_present"
    ]
    short_accuracy = (
        sum(bool(trial.get("t2_correct", False)) for trial in short_present) / len(short_present)
        if short_present
        else 0.0
    )
    long_accuracy = (
        sum(bool(trial.get("t2_correct", False)) for trial in long_present) / len(long_present)
        if long_present
        else 0.0
    )
    return {
        "t1_accuracy": t1_accuracy,
        "conditional_t2_accuracy": conditional_t2_accuracy,
        "blink_magnitude": long_accuracy - short_accuracy,
    }
