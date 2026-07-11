from contextlib import nullcontext
from functools import partial
from pathlib import Path
from typing import Any

import pandas as pd
from psychopy import core

from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskRunOptions,
    TaskSettings,
    context_from_config,
    count_down,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    runtime_context,
)

from src import generate_attentional_blink_conditions, run_trial, summarize_block

MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _execute_block(
    *,
    block_id: str,
    block_idx: int,
    conditions: list[Any],
    settings: TaskSettings,
    win: Any,
    kb: Any,
    stim_bank: StimBank,
    trigger_runtime: Any,
    sink: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    block = (
        BlockUnit(
            block_id=block_id,
            block_idx=block_idx,
            settings=settings,
            window=win,
            keyboard=kb,
        )
        .add_condition(conditions)
        .on_start(lambda _: trigger_runtime.send(settings.triggers.get("block_onset")))
        .on_end(lambda _: trigger_runtime.send(settings.triggers.get("block_end")))
        .run_trial(
            partial(
                run_trial,
                stim_bank=stim_bank,
                trigger_runtime=trigger_runtime,
                block_id=block_id,
                block_idx=block_idx,
            )
        )
        .to_dict(sink)
    )
    return list(block.get_all_data())


def run(options: TaskRunOptions) -> None:
    task_root = Path(__file__).resolve().parent
    cfg = load_config(str(options.config_path))
    task_cfg = dict(cfg["task_config"])

    output_dir: Path | None = None
    runtime_scope = nullcontext()
    runtime_ctx = None
    if options.mode in ("qa", "sim"):
        runtime_ctx = context_from_config(task_dir=task_root, config=cfg, mode=options.mode)
        output_dir = runtime_ctx.output_dir
        runtime_scope = runtime_context(runtime_ctx)

    with runtime_scope:
        if options.mode == "qa":
            subject_data = {"subject_id": "qa"}
        elif options.mode == "sim":
            participant_id = "sim"
            if runtime_ctx is not None and runtime_ctx.session is not None:
                participant_id = str(runtime_ctx.session.participant_id or "sim")
            subject_data = {"subject_id": participant_id}
        else:
            subject_data = SubInfo(cfg["subform_config"]).collect()

        settings = TaskSettings.from_dict(task_cfg)
        if options.mode in ("qa", "sim") and output_dir is not None:
            settings.save_path = str(output_dir)
        settings.add_subinfo(subject_data)
        if options.mode == "qa" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "qa_trace.csv")
            settings.log_file = str(output_dir / "qa_psychopy.log")
            settings.json_file = str(output_dir / "qa_settings.json")

        settings.triggers = cfg["trigger_config"]
        trigger_runtime = (
            initialize_triggers(mock=True)
            if options.mode in ("qa", "sim")
            else initialize_triggers(cfg)
        )
        win, kb = initialize_exp(settings)
        stim_bank = StimBank(win, cfg["stim_config"])
        if options.mode == "human":
            stim_bank = stim_bank.convert_to_voice("instruction_text")
        stim_bank = stim_bank.preload_all()
        settings.save_to_json()

        trigger_runtime.send(settings.triggers.get("exp_onset"))
        instruction = StimUnit("instruction", win, kb, runtime=trigger_runtime).add_stim(
            stim_bank.get("instruction_text")
        )
        if options.mode == "human":
            instruction.add_stim(stim_bank.get("instruction_text_voice"))
        instruction.wait_and_continue()

        seed = int(task_cfg.get("random_seed", 2026))
        practice_counts = dict(task_cfg.get("practice_condition_counts") or {})
        if sum(int(value) for value in practice_counts.values()) > 0:
            StimUnit("practice_intro", win, kb, runtime=trigger_runtime).add_stim(
                stim_bank.get("practice_intro")
            ).wait_and_continue()
            practice_conditions = generate_attentional_blink_conditions(
                block_idx=0,
                condition_counts=practice_counts,
                seed=seed,
                is_practice=True,
            )
            practice_data: list[dict[str, Any]] = []
            _execute_block(
                block_id="practice",
                block_idx=-1,
                conditions=practice_conditions,
                settings=settings,
                win=win,
                kb=kb,
                stim_bank=stim_bank,
                trigger_runtime=trigger_runtime,
                sink=practice_data,
            )

        all_data: list[dict[str, Any]] = []
        condition_counts = dict(task_cfg["condition_counts"])
        for block_idx in range(int(settings.total_blocks)):
            if options.mode == "human":
                count_down(win, 3, color="black")
            planned_conditions = generate_attentional_blink_conditions(
                block_idx=block_idx,
                condition_counts=condition_counts,
                seed=seed,
                is_practice=False,
            )
            block_trials = _execute_block(
                block_id=f"block_{block_idx}",
                block_idx=block_idx,
                conditions=planned_conditions,
                settings=settings,
                win=win,
                kb=kb,
                stim_bank=stim_bank,
                trigger_runtime=trigger_runtime,
                sink=all_data,
            )
            summary = summarize_block(block_trials)
            if block_idx < int(settings.total_blocks) - 1:
                StimUnit("block_summary", win, kb, runtime=trigger_runtime).add_stim(
                    stim_bank.get_and_format(
                        "block_break",
                        block_num=block_idx + 1,
                        total_blocks=settings.total_blocks,
                        t1_accuracy=summary["t1_accuracy"],
                        conditional_t2_accuracy=summary["conditional_t2_accuracy"],
                    )
                ).wait_and_continue()

        overall = summarize_block(all_data)
        StimUnit("good_bye", win, kb, runtime=trigger_runtime).add_stim(
            stim_bank.get_and_format(
                "good_bye",
                t1_accuracy=overall["t1_accuracy"],
                conditional_t2_accuracy=overall["conditional_t2_accuracy"],
                blink_magnitude=overall["blink_magnitude"],
            )
        ).wait_and_continue(terminate=True)
        trigger_runtime.send(settings.triggers.get("exp_end"))

        pd.DataFrame(all_data).to_csv(settings.res_file, index=False)
        trigger_runtime.close()
        core.quit()


def main() -> None:
    task_root = Path(__file__).resolve().parent
    options = parse_task_run_options(
        task_root=task_root,
        description="Run the Attentional Blink task in human, QA, or simulation mode.",
        default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
        modes=MODES,
    )
    run(options)


if __name__ == "__main__":
    main()
