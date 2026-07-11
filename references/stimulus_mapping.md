# Stimulus Mapping

## Mapping Table

| Condition | Stage/Phase | Stimulus IDs | Participant-Facing Content | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Asset References | Notes |
|---|---|---|---|---|---|---|---|---|
| `all` | `fixation` | `fixation` | Central black `+` on gray for 1,780 ms. | `W1987937684` | Figure 1 and Methods specify fixation and colors. | `psychopy_builtin` | `config/*.yaml` | Centered text. |
| `all` | `rsvp_distractor` | `rsvp_character` | One uppercase distractor letter for 50 ms. | `W1987937684` | Methods specifies letter pool and duration. | `psychopy_builtin` | `src/utils.py`; `config/*.yaml` | Sampled without replacement. |
| `all` | `rsvp_optional_blank` | `blank` | Empty gray screen in place of an eligible distractor. | `W1987937684` | Methods specifies 20% optional blanks. | `psychopy_builtin` | `src/utils.py`; `config/*.yaml` | Protected positions follow cited exclusions. |
| `all` | `t1` | `rsvp_character` | First target digit from 2-9. | `W1987937684` | Figure 1 and Methods specify number targets among letters. | `psychopy_builtin` | `src/utils.py`; `config/*.yaml` | Distinct trigger. |
| `short_present` | `t2` | `rsvp_character` | Second target digit 336 ms after T1. | `W1987937684` | Figure 1 and Methods specify short interval. | `psychopy_builtin` | `src/utils.py`; `config/*.yaml` | Blink-window condition. |
| `long_present` | `t2` | `rsvp_character` | Second target digit 672 ms after T1. | `W1987937684` | Figure 1 and Methods specify long interval. | `psychopy_builtin` | `src/utils.py`; `config/*.yaml` | Long comparison. |
| `short_absent` | `t2_absent` | `blank` | Blank at the short-interval T2 position. | `W1987937684` | Methods replaces T2 with blank. | `psychopy_builtin` | `src/utils.py`; `config/*.yaml` | Label not displayed. |
| `long_absent` | `t2_absent` | `blank` | Blank at the long-interval T2 position. | `W1987937684` | Methods replaces T2 with blank. | `psychopy_builtin` | `src/utils.py`; `config/*.yaml` | Absence control. |
| `all` | `rsvp_gap` | `blank` | Gray blank for 34 ms after every RSVP item. | `W1987937684` | Methods specifies 34-ms gap. | `psychopy_builtin` | `config/*.yaml` | Maintains 84-ms cycle. |
| `all` | `t1_report` | `t1_report_prompt`, `t1_report_options` | Chinese prompt to report first digit using 2-9. | `W1987937684` | Methods specifies ordered keyboard report. | `psychopy_builtin` | `config/*.yaml` | Config-localized. |
| `all` | `t2_report` | `t2_report_prompt`, `t2_report_options` | Report T2 or press 0 when certain it was absent. | `W1987937684` | Methods specifies guessing versus zero. | `psychopy_builtin` | `config/*.yaml` | Timeout is distinct. |
| `practice` | `feedback` | `practice_feedback_*` | Brief correctness message for both reports. | `W1987937684` | Practice reported; feedback detail omitted. | `psychopy_builtin` | `config/*.yaml` | Inferred, practice-only. |
