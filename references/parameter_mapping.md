# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `fixation_duration` | `timing.fixation_duration` | `1.780 s` | `W1987937684` | Methods and Figure 1: each trial begins with a 1,780-ms fixation cross. | `direct` | Preserved in human mode. |
| `rsvp_item_duration` | `timing.rsvp_item_duration` | `0.050 s` | `W1987937684` | Methods: each letter is presented for 50 ms. | `direct` | Applies to letters, digits, and planned blank items. |
| `rsvp_blank_duration` | `timing.rsvp_blank_duration` | `0.034 s` | `W1987937684` | Methods: each item is followed by a 34-ms blank. | `direct` | Produces an 84-ms RSVP cycle. |
| `short_interval` | `condition short_present/short_absent` | `336 ms; lag 4` | `W1987937684` | Methods: short T1-T2 temporal distance is 336 ms. | `direct` | Four 84-ms cycles. |
| `long_interval` | `condition long_present/long_absent` | `672 ms; lag 8` | `W1987937684` | Methods: long T1-T2 temporal distance is 672 ms. | `direct` | Eight 84-ms cycles. |
| `stream_length` | `src/utils.py CONDITION_SPECS` | `15 short; 19 long` | `W1987937684` | Figure 1 and Methods: rapid streams contain 15 or 19 items. | `adapted` | Paired with interval to keep target placement comparable. |
| `target_pool` | `src/utils.py TARGET_DIGITS` | `2-9 without replacement` | `W1987937684` | Methods: target numbers are randomly drawn without replacement from 2-9. | `direct` | T1 and T2 differ on present trials. |
| `distractor_pool` | `src/utils.py DISTRACTOR_LETTERS` | `A-Z except B, I, O, Q, S` | `W1987937684` | Methods specifies excluded letters. | `direct` | Sampled without replacement per stream. |
| `optional_blanks` | `src/utils.py _build_stream` | `20% eligible distractors` | `W1987937684` | Methods: distractors may be empty with 20% probability, with stated exclusions. | `direct` | Target-adjacent and final items are protected. |
| `post_stream_delay` | `timing.post_stream_delay` | `1.000 s` | `W1987937684` | Methods: reports begin 1,000 ms after the stream. | `direct` | Blank retention interval. |
| `report_keys` | `task.t1_keys`, `task.t2_keys` | `T1: 2-9; T2: 0,2-9` | `W1987937684` | Methods: type numbers in order; zero denotes certainty that T2 was absent. | `direct` | Timeout remains distinct from zero. |
| `report_window` | `timing.report_window` | `5.000 s each` | `W1987937684` | Paper specifies ordered keyboard entry but no deadline. | `inferred` | Generous finite window for bounded runtime. |
| `condition_counts` | `task.condition_counts` | `48/18/18/18 per block` | `W1987937684` | Methods reports totals 192/72/72/72 over four blocks. | `direct` | Exact per-block division. |
| `practice_trials` | `task.practice_condition_counts` | `34` | `W1987937684` | Procedure reports 34 practice trials. | `direct` | QA/sim shorten while retaining all conditions. |
| `iti_duration` | `timing.iti_duration` | `0.200 s` | `W1987937684` | Methods: new trial begins 200 ms after the second response. | `direct` | Blank interval. |
| `conditional_t2_accuracy` | `src/utils.py summarize_block` | `T2 accuracy when T1 correct` | `W1987937684`, `W2151876785` | Behavioral analyses condition T2 accuracy on correct T1 report. | `direct` | Primary outcome. |
| `trigger_codes` | `triggers.map` | `1-90 phase-specific` | `W2098899462` | Target-locked processing motivates distinct T1/T2 markers; exact codes are unreported. | `inferred` | TaskBeacon-specific codes. |
