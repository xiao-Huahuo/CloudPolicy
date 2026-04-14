# KMP Micro-Lesson Remotion Video Design

Date: 2026-04-14
Status: Approved in conversation, written spec drafted for user review
Audience: Middle-school students
Duration target: 60 seconds
Format target: 1920x1080, 30 fps

## Goal

Create a competition-ready, one-minute micro-lesson video in the repository root using Remotion. The video explains the core intuition of the KMP string-matching algorithm to middle-school students.

The first version must optimize for clarity and presentation quality, not for full algorithmic completeness. The video should make students understand one idea clearly:

KMP is faster because after a mismatch, it avoids repeating comparisons that are already known to be unnecessary.

## Scope

### In scope

- A standalone Remotion project created under the repository root
- One renderable composition for a one-minute KMP micro-lesson
- A visual style that feels computational, data-driven, and presentation-ready
- A subtitle system with a typing effect
- Background music support
- Code-generated visuals for the main scenes and algorithm animation
- Editable script and timing data separated from core components
- One rendered output video file if the environment supports rendering

### Out of scope for version 1

- Full proof or formal derivation of the KMP algorithm
- Detailed construction of the `next` array
- Voice-over narration
- Multiple aspect ratios
- Multiple language versions
- Heavy external asset pipelines or 3D scenes

## Audience and Teaching Strategy

The video is for middle-school students, so the explanation must stay intuitive and visual.

The content should teach the core idea, not the full theory:

- Show that naive matching wastes work by restarting comparisons after a mismatch
- Ask the viewer why already-compared parts must be compared again
- Show KMP as a smarter strategy that uses known information to jump
- End with a short, memorable summary sentence

The tone should be lively and approachable, but not childish.

## Creative Direction

### Chosen direction

The visual direction is "algorithm laboratory mission mode".

This means the video should look like a science-fiction data lab or transparent control console, not a classroom blackboard and not a pure code terminal. It should still be friendly enough for students, but clearly computer-themed.

### Visual characteristics

- Dark lab background with subtle grid, particles, scan lines, and data pulses
- HUD-style panels and translucent interface cards
- Strong focus on string arrays, pointers, highlights, and jump trajectories
- Blue-cyan as the main color family, with orange-red used for mismatch warnings and emphasis
- Smooth motion with deliberate camera pushes, panel reveals, and pointer movement
- Enough decorative motion to feel competition-ready, but never so much that it obscures the explanation

### Educational style

- Semi-cartoon presentation rather than realistic UI
- Data-rich and technical rather than playful amusement-park aesthetics
- Every visual effect must support teaching focus, timing, or emphasis

## Narrative Structure

The video should feel like one guided mission with a clear escalation from a simple problem to a smart solution.

### Story spine

1. A search task is initialized on the main laboratory screen
2. Naive matching begins and seems reasonable
3. A mismatch reveals wasted repeated work
4. The system escalates into KMP mode
5. KMP demonstrates a smart jump instead of restarting
6. The video closes with a concise takeaway

## Scene Plan

### Scene 1: Mission startup (0s - 6s)

Purpose:
- Establish the computational lab setting
- Introduce the task of fast string matching

Visuals:
- Main laboratory display powers on
- Data grid and HUD panels animate into place
- Title and mission prompt appear with a typing effect

Subtitle intent:
- "Task: Find the target pattern in a long string quickly."

### Scene 2: Naive matching begins (6s - 16s)

Purpose:
- Show how ordinary matching compares characters one by one

Visuals:
- Main string and pattern string appear as aligned cells
- `i` and `j` pointers move through successful matches
- The motion is calm and readable

Subtitle intent:
- "At first, character-by-character matching looks fine."

### Scene 3: Mismatch and waste (16s - 23s)

Purpose:
- Make the waste of repeated work visible and emotionally obvious

Visuals:
- A mismatch triggers a warning state
- The pattern resets and overlapping characters are rechecked
- Red accents and repeated highlight motion emphasize inefficiency

Subtitle intent:
- "But once a mismatch appears, the ordinary method starts over."

### Scene 4: Question the waste (23s - 31s)

Purpose:
- Create the key teaching question before showing KMP

Visuals:
- Camera or layout focus tightens around the repeated-comparison region
- Previously matched sections are highlighted as "already known"
- The repeated area is visually marked as unnecessary work

Subtitle intent:
- "If we already know part of the result, why compare it again?"

### Scene 5: KMP mode activation (31s - 40s)

Purpose:
- Create a clear transition from old method to new method

Visuals:
- The interface upgrades into KMP mode
- Helper guides, jump lines, and intelligence overlays appear
- Music energy lifts slightly

Subtitle intent:
- "KMP uses what we already know."

### Scene 6: Smart jump demonstration (40s - 52s)

Purpose:
- Deliver the one concept the audience must remember

Visuals:
- The same type of mismatch happens again
- The main string does not rewind
- The pattern shifts directly to a better position
- A jump trajectory and a stable main-string pointer make the idea unmistakable

Subtitle intent:
- "After a mismatch, KMP skips comparisons that no longer need to be repeated."

### Scene 7: Closing takeaway (52s - 60s)

Purpose:
- End with a short memory-friendly definition

Visuals:
- A clean final composition with the core sentence centered on the main display
- Remaining UI calms down for a strong closing frame

Subtitle intent:
- "KMP is fast because it does less repeated work."

## Timing and Motion Rules

- Default frame rate is 30 fps
- Animations should favor easing and spring-like smoothness, not abrupt cuts
- Important instructional beats should have extra visual hold time
- New information should enter in layers rather than all at once
- Typing subtitles should stay readable and should not force the user to race the text
- Transitions should feel polished and modern, but not flashy for their own sake

## Subtitle Design

Subtitles are required and should not be baked directly into scene components.

### Requirements

- Use a data-driven subtitle track
- Display subtitles with a typing-style reveal
- Support emphasis styling for key words or phrases
- Keep line lengths readable at 1080p
- Match subtitle timing to scene beats rather than constant-speed text only

### Styling

- Subtitle container should fit the laboratory HUD aesthetic
- Cursor blink or terminal-style reveal is allowed
- The effect should feel digital, not retro typewriter

## Music Strategy

Version 1 uses background music only, with no narration.

### Requirements

- Music should be light electronic or technology-themed
- It must support the rhythm of the edit without overpowering the instructional content
- The composition should remain functional if the track is swapped later
- Audio hookup should be modular, so a future replacement track does not require scene rewrites

If a suitable local track is unavailable in the current workspace, the code structure must still support easy later insertion. In that case, version 1 may ship with the music layer disabled, but the audio slot and timing hooks must still exist in the project structure.

## Visual System Components

The composition should be built from reusable scene and UI primitives rather than one giant monolithic component.

### Expected building blocks

- Lab background
- HUD card and panel primitives
- String cell row component
- Pointer indicator component for `i` and `j`
- Match and mismatch highlight overlays
- Jump path or trajectory effect
- Typing subtitle component
- Title and mission intro components
- Scene timeline data or script data

## Data Model

The project should separate content from animation logic as much as practical.

### Recommended data files

- Script or subtitle lines with start and end timing
- Scene-level configuration values
- Demo string content for the naive and KMP comparison
- Theme constants for colors, spacing, and motion values

This separation is required so the video can later be extended into a longer 3-minute teaching version without rewriting core animation components.

## Repository Placement

The Remotion project must live under the repository root in a dedicated `kmp-remotion` directory. It must not be mixed into the existing `web` or `app` code.

Rendered outputs should go into a dedicated `kmp-renders` directory at the repository root.

## Testing and Verification

The implementation must be verifiable in stages.

### Minimum verification expectations

- Project dependencies install successfully
- Remotion Studio starts
- The KMP composition registers correctly
- At least one still or frame render succeeds for visual sanity checking
- A full video render must be attempted; if the environment blocks it, the blocker must be recorded explicitly and a still or frame render must still be produced

### Quality checks

- Subtitle timing is readable
- Key KMP jump moment is visually unambiguous
- Music, if present, does not overwhelm the scene
- Layout remains clean at 1080p

## Risks and Constraints

### Main risks

- One minute is short, so over-explaining can ruin pacing
- Too much UI decoration can distract from the core algorithm idea
- Too much simplification can make the result feel empty or generic
- Missing local audio assets may reduce polish unless handled modularly

### Responses

- Keep the teaching target limited to the core intuition only
- Use a small number of recurring visual motifs
- Build audio as an optional but supported layer
- Prefer code-generated graphics over brittle external assets

## Success Criteria

Version 1 is successful if it achieves all of the following:

- The result looks like a finished competition micro-lesson rather than a prototype
- A middle-school student can explain the main KMP idea after watching once
- The video feels computational and data-driven
- The subtitle typing effect reads cleanly and supports the pacing
- The project is easy to extend later with more scenes, more algorithm detail, or narration

## Implementation Notes for Next Phase

The next phase should produce a concrete implementation plan covering:

- Project scaffolding
- Remotion composition registration
- Asset and audio handling
- Scene component breakdown
- Subtitle data format
- Render and verification workflow

No implementation should start until the written spec is reviewed and accepted.


