# Attentional Blink Task

| Field | Value |
|---|---|
| Name | Attentional Blink Task |
| Version | v0.1.0 |
| Repository | https://github.com/TaskBeacon/T000058-attentional-blink |
| Date Updated | 2026-07-11 |
| PsyFlow Version | 0.1.0 |
| PsychoPy Version | 2025.1.1 |
| Modality | Behavior |
| Language | Chinese |
| Primary construct | Temporal attention |

## 1. Task Overview

This task measures the reduced ability to report a second target presented shortly after a first target in a rapid serial visual presentation (RSVP). Participants view uppercase letters containing one or two digit targets, then report the targets in order. The primary outcome is T2 accuracy conditional on correct T1 report, compared between 336-ms and 672-ms intervals.

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

| Step | Description |
|---|---|
| Instructions | Explain targets, ordered report, and the T2-absent zero response. |
| Practice | Run 34 practice trials with brief feedback in human mode. |
| Scored blocks | Run four intermixed 102-trial blocks with exact counts. |
| Block summary | Show T1 and conditional T2 accuracy. |
| Save | Export one reduced row per RSVP trial. |

### Trial-Level Flow

| Phase | Duration | Visible content / response |
|---|---:|---|
| Fixation | 1,780 ms | Central `+`. |
| RSVP item | 50 ms | One letter, digit, or planned blank. |
| Inter-item blank | 34 ms | Gray blank. |
| Post-stream delay | 1,000 ms | Gray blank. |
| T1 report | 5 s max | Press 2-9. |
| T2 report | 5 s max | Press 2-9, or 0 for confident absence. |
| ITI | 200 ms | Gray blank. |

### Controller Logic

No adaptive controller is used. `src/utils.py` deterministically preplans exact condition counts, target identities, constrained positions, letter streams, and optional blank distractors before trials begin.

### Other Logic

T2 accuracy is conditionalized on correct T1 report. Blink magnitude is long-present conditional T2 accuracy minus short-present conditional T2 accuracy.

## 3. Configuration Summary

### a. Subject Info

| Field | Meaning |
|---|---|
| `subject_id` | Three-digit participant identifier. |

### b. Window Settings

| Parameter | Value |
|---|---|
| Resolution | 1024 x 768 |
| Units | visual degrees |
| Background | gray |

### c. Stimuli

| Element | Implementation |
|---|---|
| Distractors | Uppercase letters excluding B, I, O, Q, S. |
| Targets | Distinct digits from 2-9. |
| Optional blanks | 20% of eligible distractor positions. |
| Prompts | Config-defined Chinese text using SimHei. |

### d. Timing

| Parameter | Value |
|---|---:|
| Fixation | 1.780 s |
| Item / blank | 0.050 / 0.034 s |
| Short / long interval | 0.336 / 0.672 s |
| Post-stream delay | 1.000 s |
| ITI | 0.200 s |

### Triggers

Separate codes mark fixation, distractors, T1, T2, T2-absent positions, reports, responses, timeouts, practice feedback, and ITI. See `config/config.yaml`.

### Adaptive Controller

None.

## 4. Methods (for academic publication)

Participants completed a digit-target attentional-blink task adapted from Slagter et al. (2007). Each trial began with a 1,780-ms fixation, followed by a 15- or 19-item RSVP stream. Items appeared for 50 ms with a 34-ms blank between items. One or two digits from 2-9 were embedded among uppercase letter distractors. T2 occurred either 336 ms or 672 ms after T1, or was replaced by a blank on T2-absent trials. One second after the stream, participants reported T1 and then T2; zero indicated confident T2 absence. T2 accuracy was analyzed conditional on correct T1 report.

## Running

```powershell
python main.py
python main.py qa --config config/config_qa.yaml
python main.py sim --config config/config_scripted_sim.yaml
python main.py sim --config config/config_sampler_sim.yaml
```
