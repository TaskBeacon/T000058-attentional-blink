from __future__ import annotations

from functools import partial
from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context
from src.utils import TrialPlan


def _response_trigger_map(settings: Any, prefix: str, keys: list[str]) -> dict[str, Any]:
    return {key: settings.triggers.get(f"{prefix}_{key}") for key in keys}


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """Run one preplanned Attentional Blink RSVP trial."""
    if not isinstance(condition, TrialPlan):
        raise TypeError("Attentional Blink trials require a preplanned TrialPlan.")
    plan = condition.to_dict()
    required = {
        "condition",
        "condition_id",
        "interval",
        "lag",
        "t2_present",
        "stream",
        "roles",
        "t1",
        "t2",
        "t1_index",
        "t2_index",
        "is_practice",
        "trial_index_in_block",
    }
    missing = required.difference(plan)
    if missing:
        raise ValueError(f"Attentional Blink plan missing fields: {sorted(missing)}")

    trial_id = next_trial_id()
    block_id_val = str(block_id or "block_0")
    block_idx_val = int(block_idx or 0)
    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)
    trial_data: dict[str, Any] = {
        "trial_id": int(trial_id),
        "block_id": block_id_val,
        "block_idx": block_idx_val,
        "trial_index_in_block": int(plan["trial_index_in_block"]),
        "condition": str(plan["condition"]),
        "condition_id": str(plan["condition_id"]),
        "interval": str(plan["interval"]),
        "lag": int(plan["lag"]),
        "t2_present": bool(plan["t2_present"]),
        "t1": str(plan["t1"]),
        "t2": str(plan["t2"]),
        "t1_index": int(plan["t1_index"]),
        "t2_index": int(plan["t2_index"]),
        "is_practice": bool(plan["is_practice"]),
        "stream": list(plan["stream"]),
        "roles": list(plan["roles"]),
    }

    fixation_duration = float(settings.fixation_duration)
    fixation = make_unit(unit_label="fixation").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        fixation,
        trial_id=trial_id,
        phase="fixation",
        deadline_s=fixation_duration,
        valid_keys=[],
        block_id=block_id_val,
        condition_id=plan["condition_id"],
        task_factors={"stage": "fixation", "condition": plan["condition"]},
        stim_id="fixation",
    )
    fixation.show(
        duration=fixation_duration,
        onset_trigger=settings.triggers.get("fixation_onset"),
    ).to_dict(trial_data)

    item_duration = float(settings.rsvp_item_duration)
    blank_duration = float(settings.rsvp_blank_duration)
    role_trigger = {
        "distractor": "rsvp_distractor_onset",
        "distractor_blank": "rsvp_distractor_onset",
        "t1": "t1_onset",
        "t2": "t2_onset",
        "t2_absent": "t2_absent_onset",
    }
    for item_index, (character, role) in enumerate(zip(plan["stream"], plan["roles"])):
        item_label = f"rsvp_item_{item_index + 1:02d}"
        item_stim = (
            stim_bank.get_and_format("rsvp_character", character=character)
            if character
            else stim_bank.get("blank")
        )
        item = make_unit(unit_label=item_label).add_stim(item_stim)
        set_trial_context(
            item,
            trial_id=trial_id,
            phase="rsvp_item",
            deadline_s=item_duration,
            valid_keys=[],
            block_id=block_id_val,
            condition_id=plan["condition_id"],
            task_factors={
                "stage": "rsvp_item",
                "condition": plan["condition"],
                "item_index": item_index,
                "item_role": role,
                "character": character,
            },
            stim_id="rsvp_character" if character else "blank",
        )
        item.show(
            duration=item_duration,
            onset_trigger=settings.triggers.get(role_trigger[role]),
        ).to_dict(trial_data)

        gap_label = f"rsvp_gap_{item_index + 1:02d}"
        gap = make_unit(unit_label=gap_label).add_stim(stim_bank.get("blank"))
        set_trial_context(
            gap,
            trial_id=trial_id,
            phase="rsvp_gap",
            deadline_s=blank_duration,
            valid_keys=[],
            block_id=block_id_val,
            condition_id=plan["condition_id"],
            task_factors={"stage": "rsvp_gap", "item_index": item_index},
            stim_id="blank",
        )
        gap.show(
            duration=blank_duration,
            onset_trigger=settings.triggers.get("rsvp_gap_onset"),
        ).to_dict(trial_data)

    retention_duration = float(settings.post_stream_delay)
    retention = make_unit(unit_label="post_stream_delay").add_stim(stim_bank.get("blank"))
    set_trial_context(
        retention,
        trial_id=trial_id,
        phase="post_stream_delay",
        deadline_s=retention_duration,
        valid_keys=[],
        block_id=block_id_val,
        condition_id=plan["condition_id"],
        task_factors={"stage": "post_stream_delay"},
        stim_id="blank",
    )
    retention.show(
        duration=retention_duration,
        onset_trigger=settings.triggers.get("retention_onset"),
    ).to_dict(trial_data)

    t1_keys = [str(key) for key in settings.t1_keys]
    t1_correct_key = str(plan["t1"])
    t1_report = make_unit(unit_label="t1_report")
    t1_report.add_stim(stim_bank.get("t1_report_prompt"))
    t1_report.add_stim(stim_bank.get("t1_report_options"))
    set_trial_context(
        t1_report,
        trial_id=trial_id,
        phase="t1_report",
        deadline_s=float(settings.report_window),
        valid_keys=t1_keys,
        block_id=block_id_val,
        condition_id=plan["condition_id"],
        task_factors={"stage": "t1_report", "correct_key": t1_correct_key},
        stim_id="t1_report_prompt",
    )
    t1_report.capture_response(
        keys=t1_keys,
        correct_keys=[t1_correct_key],
        duration=float(settings.report_window),
        onset_trigger=settings.triggers.get("t1_report_onset"),
        response_trigger=_response_trigger_map(settings, "t1_response", t1_keys),
        timeout_trigger=settings.triggers.get("t1_response_timeout"),
    ).to_dict(trial_data)
    t1_response = t1_report.get_state("response", None)
    t1_rt = t1_report.get_state("rt", None)
    t1_correct = bool(t1_response is not None and str(t1_response) == t1_correct_key)

    t2_keys = [str(key) for key in settings.t2_keys]
    t2_correct_key = str(plan["t2"]) if bool(plan["t2_present"]) else "0"
    t2_report = make_unit(unit_label="t2_report")
    t2_report.add_stim(stim_bank.get("t2_report_prompt"))
    t2_report.add_stim(stim_bank.get("t2_report_options"))
    set_trial_context(
        t2_report,
        trial_id=trial_id,
        phase="t2_report",
        deadline_s=float(settings.report_window),
        valid_keys=t2_keys,
        block_id=block_id_val,
        condition_id=plan["condition_id"],
        task_factors={
            "stage": "t2_report",
            "correct_key": t2_correct_key,
            "t2_present": bool(plan["t2_present"]),
        },
        stim_id="t2_report_prompt",
    )
    t2_report.capture_response(
        keys=t2_keys,
        correct_keys=[t2_correct_key],
        duration=float(settings.report_window),
        onset_trigger=settings.triggers.get("t2_report_onset"),
        response_trigger=_response_trigger_map(settings, "t2_response", t2_keys),
        timeout_trigger=settings.triggers.get("t2_response_timeout"),
    ).to_dict(trial_data)
    t2_response = t2_report.get_state("response", None)
    t2_rt = t2_report.get_state("rt", None)
    t2_correct = bool(t2_response is not None and str(t2_response) == t2_correct_key)

    trial_data.update(
        {
            "t1_response": str(t1_response) if t1_response is not None else "",
            "t1_rt": float(t1_rt) if isinstance(t1_rt, (int, float)) else None,
            "t1_correct": t1_correct,
            "t1_timed_out": t1_response is None,
            "t2_response": str(t2_response) if t2_response is not None else "",
            "t2_rt": float(t2_rt) if isinstance(t2_rt, (int, float)) else None,
            "t2_correct": t2_correct,
            "t2_timed_out": t2_response is None,
            "t2_correct_given_t1": bool(t2_correct) if t1_correct else None,
            "response_key": str(t2_response) if t2_response is not None else "",
            "response_rt": float(t2_rt) if isinstance(t2_rt, (int, float)) else None,
            "response_correct": bool(t1_correct and t2_correct),
        }
    )

    if bool(plan["is_practice"]):
        if t1_correct and t2_correct:
            feedback_stim_id = "practice_feedback_both_correct"
        elif t1_correct:
            feedback_stim_id = "practice_feedback_t1_only"
        elif t2_correct:
            feedback_stim_id = "practice_feedback_t2_only"
        else:
            feedback_stim_id = "practice_feedback_both_wrong"
        feedback = make_unit(unit_label="practice_feedback").add_stim(stim_bank.get(feedback_stim_id))
        set_trial_context(
            feedback,
            trial_id=trial_id,
            phase="practice_feedback",
            deadline_s=float(settings.practice_feedback_duration),
            valid_keys=[],
            block_id=block_id_val,
            condition_id=plan["condition_id"],
            task_factors={"stage": "practice_feedback", "t1_correct": t1_correct, "t2_correct": t2_correct},
            stim_id=feedback_stim_id,
        )
        feedback.show(
            duration=float(settings.practice_feedback_duration),
            onset_trigger=settings.triggers.get("practice_feedback_onset"),
        ).to_dict(trial_data)

    iti = make_unit(unit_label="iti").add_stim(stim_bank.get("blank"))
    set_trial_context(
        iti,
        trial_id=trial_id,
        phase="iti",
        deadline_s=float(settings.iti_duration),
        valid_keys=[],
        block_id=block_id_val,
        condition_id=plan["condition_id"],
        task_factors={"stage": "iti"},
        stim_id="blank",
    )
    iti.show(
        duration=float(settings.iti_duration),
        onset_trigger=settings.triggers.get("iti_onset"),
    ).to_dict(trial_data)
    return trial_data
