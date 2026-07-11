# CHANGELOG

## [0.1.0] - 2026-07-11

### Added

- Literature-aligned digit-target Attentional Blink RSVP task.
- Exact 50-ms item, 34-ms gap, 336-ms short, and 672-ms long timing.
- T2-present and T2-absent conditions with conditional T2 scoring.
- Deterministic item-level planning, QA, scripted simulation, and lag-sensitive sampler simulation.
- Evidence mappings, trigger plan, and TAPS v0.2.0 metadata.

### Changed

- Replaced the generic scaffold with a literature-derived RSVP state machine.

### Fixed

- Ensured custom trial plans are immutable and compatible with BlockUnit logging.
- Preserved scalar condition labels in CSV export while carrying the complete preplanned RSVP payload.
