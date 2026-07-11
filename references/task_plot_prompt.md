Use case: infographic-diagram
Asset type: TaskBeacon task flow diagram
Primary request: Create a clean, publication-ready task flow diagram as a timeline collection for the behavioral task described below.

Task: Attentional Blink Task
Construct: temporal attention / target consolidation
Rows/conditions:
- Short T2: a second digit follows the first digit after 336 ms.
- Long T2: a second digit follows the first digit after 672 ms.
- T2 absent: the planned second-target position is blank; the participant reports 0 when certain it was absent.

Timeline phases:
- Short T2: Fixation (1780 ms; no response; central +) -> RSVP (50 ms item + 34 ms blank; central letters with T1 digit, then T2 digit after 336 ms) -> Blank (1000 ms; empty gray screen) -> T1? (5 s max; first digit response) -> T2? (5 s max; second digit response) -> ITI (200 ms; empty screen)
- Long T2: Fixation (1780 ms; no response; central +) -> RSVP (50 ms item + 34 ms blank; central letters with T1 digit, then T2 digit after 672 ms) -> Blank (1000 ms; empty gray screen) -> T1? (5 s max; first digit response) -> T2? (5 s max; second digit response) -> ITI (200 ms; empty screen)
- T2 absent: Fixation (1780 ms; no response; central +) -> RSVP (50 ms item + 34 ms blank; central letters with T1 digit and blank T2 position) -> Blank (1000 ms; empty gray screen) -> T1? (5 s max; first digit response) -> T2? (5 s max; show 0 if absent) -> ITI (200 ms; empty screen)

Visual requirements:
- White background, landscape orientation, crisp dark text, restrained condition accent colors.
- One horizontal row per condition or representative trial type.
- Each row contains 3-7 participant-screen snapshots connected by a subtle arrow.
- Each screen snapshot shows the visible stimulus or feedback, not internal variable names.
- Use gray participant-screen boxes, thin black arrows, consistent row spacing, and subtle row separators.
- Place timing labels under each screen in compact text.
- Place condition labels at the left of each row.
- Use short labels only; avoid paragraphs inside the image.
- Make all text legible at normal document preview size.
- Leave a clean blank header band across the top 15-18% of the image. This band is reserved for a fixed title, `Construct: ...` subtitle, and TaskBeacon logo lockup that will be added after generation.

Accuracy constraints:
- Do not invent phases, stimuli, condition names, keys, rewards, or timings.
- Do not add people, lab equipment, decorative scenes, logos, or unrelated icons.
- Do not draw the task title, construct subtitle, any logo, watermark, brand mark, or `TaskBeacon` text inside the generated image.
- Draw only the timeline content below the blank header band.
- If a detail is unknown, omit it rather than guessing.
- Preserve these exact terms where used: Short T2, Long T2, T2 absent, +, T1?, T2?, 0 if absent, 1780 ms, 50 + 34 ms, 336 ms, 672 ms, 1000 ms, 5 s max, 200 ms

Style:
TaskBeacon scientific infographic style: clean vector-like raster image, organized spacing, gray screen boxes, restrained color accents, and a blank header-safe area.
