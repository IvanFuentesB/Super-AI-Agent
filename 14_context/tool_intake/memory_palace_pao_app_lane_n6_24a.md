# Memory Palace / PAO App Lane (N+6.24A)

Milestone: N+6.24A
Date: 2026-06-06
Status: future product lane, planning only. Tier-1-**last** (build last, after the
operator stack is solid). Nothing here is built, installed, or wired. Capture from
camera/LiDAR/devices is gated behind privacy + consent milestones and is NOT enabled.

## The idea (operator product concept)

A **memory palace** learning app built on the **PAO** (Person-Action-Object) mnemonic
system, where the "palaces" are real or generated 3D environments:

- **Environments from anywhere:** a place described in text, a real place captured by
  **camera / LiDAR / depth scan**, a movie/scene, or a fully generated environment.
- **Infinite expansion:** palaces can grow and link, so memory space is effectively
  unbounded; rooms/wings are added as the learner needs more loci.
- **Object placement:** the learner places vivid objects/scenes at loci (the classic
  method of loci); the app tracks positions and associations.
- **PAO system:** structured Person-Action-Object encodings (for numbers, cards, decks,
  vocabulary, facts) mapped onto loci for fast, durable recall.
- **Study / revise / learn loop:** spaced revision, self-testing walks through the palace,
  and progress tracking.

## Why tier-1-last

- It is a **product**, not operator infrastructure. It should be built only after the core
  supervised agent stack (launcher, approval bridge, overnight loop) is proven.
- It has the **heaviest capability surface** in the whole backlog (3D capture, on-device
  sensors, generated environments), so it carries the most privacy/consent risk.
- It is high value but not on the critical path to safe agent launching.

## Capability surface (all gated, none enabled)

| Capability | Status | Gate needed |
|------------|--------|-------------|
| Text-described environments | planning | content lane |
| Camera / LiDAR / depth capture | **gated, NOT enabled** | privacy + on-device consent milestone |
| Movie/scene-derived environments | planning | licensing/rights review |
| Generated environments | planning | generation-asset lane |
| Object/loci placement + PAO encoding | planning | app data model milestone |
| Study/revise/test loop | planning | learning-loop milestone |

## Hard rules for this lane

- No camera/LiDAR/microphone/device access is requested or enabled by this note.
- No personal scans, images, faces, or location data are captured, stored, or committed.
- No real local paths, usernames, or private images appear in any committed file.
- No third-party media is downloaded or processed; movie/scene use needs a rights review.
- This is a **future** lane: it does not affect the current operator stack and is not on
  the swarm-launcher critical path.

## Smallest safe first step (when it is eventually picked up)

A purely local, text-only prototype: define the PAO data model and a single
text-described palace with a few loci, no sensors, no media, no accounts - then expand
only behind the gates above. Recorded here so the idea is captured without pulling any
capability forward.
