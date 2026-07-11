# Task Logic Audit

## 1. Paradigm Intent

- Task: Attentional Blink Task.
- Primary construct: temporal attention and the limited-capacity consolidation of a second target.
- Manipulated factors: T1-T2 interval (short, 336 ms; long, 672 ms) and T2 presence (present; absent).
- Dependent measures: T1 accuracy, T2 accuracy conditional on correct T1 report, correct T2-absence reports, and the short-versus-long conditional T2 accuracy difference.
- Key citations: W1987937684 (primary protocol), W2098899462 (target awareness), and W2151876785 (lag-dependent temporal selection).

## 2. Block/Trial Workflow

### Block Structure

- Practice: 34 trials in the cited protocol. The implementation preserves this count in human mode and uses a reduced mechanism-complete count in QA/simulation profiles.
- Scored task: four blocks of 102 trials in human mode.
- Per-block composition: 48 short/T2-present, 18 long/T2-present, 18 short/T2-absent, and 18 long/T2-absent trials, matching the cited 192/72/72/72 totals.
- Randomization/counterbalancing: all four condition types are intermixed within each block using a deterministic block seed. Trial streams are generated before `run_trial()`.
- Condition weight policy: explicit counts are used instead of `task.condition_weights` because the 48:18:18:18 composition and item-level stream plans must be exact.
- Condition generation method: custom `generate_attentional_blink_conditions(...)` in `src/utils.py`.
- Why labels are insufficient: each trial requires a balanced condition, target identities sampled without replacement, a lag-specific stream length, a constrained T2 position, letters sampled without replacement, and controlled optional blank distractors.
- Generated condition shape: a hashable string-subclass `TrialPlan`. Its scalar value is the canonical condition label expected by BlockUnit/data export, while its payload contains `interval`, `lag`, `t2_present`, `t1`, `t2`, `stream`, target indexes, practice state, and `condition_id`.
- Runtime-generated trial values: none of the experimental factors or RSVP items are randomly generated inside `run_trial.py`.

### Trial State Machine

1. Fixation
   - Onset trigger: `fixation_onset`.
   - Stimuli shown: central black fixation cross on gray background.
   - Duration: 1,780 ms.
   - Valid keys: none.
   - Next state: RSVP stream.
2. RSVP item and inter-item blank loop
   - Onset triggers: distractor, T1, T2, or T2-absent event code according to the planned item role.
   - Stimuli shown: one central black letter or target digit for 50 ms, followed by a 34-ms blank. Planned blank distractors remain blank for the item interval.
   - Valid keys: none.
   - Next state: next item, then post-stream delay.
3. Post-stream delay
   - Onset trigger: `retention_onset`.
   - Stimuli shown: blank gray screen.
   - Duration: 1,000 ms.
   - Valid keys: none.
   - Next state: T1 report.
4. T1 report
   - Onset trigger: `t1_report_onset`.
   - Stimuli shown: Chinese prompt asking for the first number.
   - Valid keys: digits 2-9.
   - Timeout behavior: after the configured 5-s implementation window, record a missing response.
   - Next state: T2 report.
5. T2 report
   - Onset trigger: `t2_report_onset`.
   - Stimuli shown: Chinese prompt asking for the second number or 0 when certain no second number appeared.
   - Valid keys: 0 and digits 2-9.
   - Timeout behavior: after 5 s, record a missing response.
   - Next state: optional practice feedback or inter-trial blank.
6. Practice feedback (practice trials only)
   - Onset trigger: `practice_feedback_onset`.
   - Stimuli shown: correctness summary for T1 and T2.
   - Duration: 800 ms.
   - Next state: inter-trial blank.
7. Inter-trial blank
   - Onset trigger: `iti_onset`.
   - Stimuli shown: blank gray screen.
   - Duration: 200 ms.

## 3. Condition Semantics

- `short_present`: T2 is a digit and begins 336 ms after T1 (four 84-ms RSVP cycles), within the blink window.
- `long_present`: T2 is a digit and begins 672 ms after T1 (eight RSVP cycles), outside the principal blink window.
- `short_absent`: the planned T2 position after 336 ms is blank; participants should report 0 only when certain no second digit appeared.
- `long_absent`: the planned T2 position after 672 ms is blank.
- Participant-facing content: target digits 2-9 embedded among uppercase letter distractors. Internal condition labels are never shown.
- Text source: static prompts and instructions are defined in `config/*.yaml`; dynamic RSVP characters are inserted into a config-defined text stimulus template.
- Localization: Chinese participant-facing wording and SimHei font are entirely config-driven.

## 4. Response and Scoring Rules

- T1 response mapping: keyboard digits 2-9.
- T2 response mapping: keyboard digits 2-9; digit 0 denotes confident T2 absence.
- Response keys are defined in config.
- Missing-response policy: timeout is distinct from digit 0 and is scored incorrect.
- T1 correctness: reported digit equals planned T1.
- T2 correctness on present trials: reported digit equals planned T2.
- T2 correctness on absent trials: response is 0.
- Primary T2 measure: T2 correctness is included in conditional T2 accuracy only when T1 is correct.
- Blink magnitude: conditional T2 accuracy for long-present minus short-present trials.
- Reward/penalty updates: none.

## 5. Stimulus Layout Plan

- RSVP screen: one text stimulus centered at `(0, 0)`, black on gray, 0.8-degree-equivalent visual height; no concurrent labels.
- T1 report screen: prompt centered above fixation at `(0, 80)` and compact option reminder at `(0, -40)`; separate anchors and wrap widths prevent overlap.
- T2 report screen: prompt at `(0, 90)` and the `0 = no second number` instruction at `(0, -45)`; both use explicit positions, heights, and wrap widths.
- Practice feedback: two short lines centered with explicit line spacing in one textbox.
- QA review must confirm central alignment, readable digits/letters, and no prompt overlap at 1024x768.

## 6. Trigger Plan

- Experiment: onset 1, end 2.
- Block: onset 10, end 11.
- Fixation: 20.
- RSVP distractor/blank item: 30.
- T1: 31.
- T2 present: 32.
- T2 absent planned blank: 33.
- RSVP inter-item blank: 34.
- Post-stream retention: 40.
- T1 report: 50; digit responses 52-59; timeout 51.
- T2 report: 60; zero response 61; digit responses 62-69; timeout 70.
- Practice feedback: 80.
- ITI: 90.

## 7. Architecture Decisions (Auditability)

- `main.py`: one mode-aware runtime flow with an explicit practice phase followed by scored blocks.
- `utils.py`: yes; only deterministic, constrained RSVP condition generation and summary calculations.
- Custom controller: no.
- Custom generator justification: exact condition counts and complete RSVP item plans cannot be represented by scalar condition labels alone.
- Trial identity: PsyFlow `next_trial_id()`.
- Response/event/data ownership: StimUnit with `set_trial_context(...)` and `to_dict(...)`.
- Legacy compatibility logic: none.

## 8. Inference Log

- Decision: 5-s response window for each typed report.
  - Why: the primary paper specifies ordered keyboard entry but no deadline.
  - Rationale: a generous finite deadline preserves typed-report semantics while keeping QA/simulation bounded.
- Decision: practice-only 800-ms accuracy feedback.
  - Why: the paper reports 34 practice trials but does not describe feedback.
  - Rationale: feedback is restricted to practice and does not affect scored-trial procedure.
- Decision: deterministic per-block random seeds.
  - Why: the paper reports random selection/intermixing but not software seed policy.
  - Rationale: reproducibility requirement of TaskBeacon/PsyFlow.
