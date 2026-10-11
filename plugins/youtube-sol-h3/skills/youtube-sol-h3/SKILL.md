---
name: youtube-sol-h3
description: Plan and produce five-minute YouTube episodes as individual SOL-H3 camera shots through ComfyUI, with reusable intro/outro CTAs, character and style continuity, FFmpeg assembly, and audiovisual validation. Use for this episodic production workflow or its production packages.
license: MIT
compatibility: Planning requires file access. The plan validator needs Python 3.10 or later. Production additionally needs a configured ComfyUI H3 workflow, FFmpeg/ffprobe, and audiovisual review tools.
metadata:
  author: Wrenbjor
  version: "1.0.0"
  repository: "https://github.com/Wrenbjor/youtube-sol-h3"
---

# YouTube SOL-H3 Episodes

Act as a showrunner and technical director. Use the capable reasoning model running this skill to write the story, resolve continuity, and compile render instructions. SOL-H3 generates individual audiovisual clips; it does not write or assemble the episode. If a separately configured writer model exists, use its documented interface; do not invent model IDs or switch models implicitly.

## Scope and modes

Respect the requested stage:

- **Configure:** establish the channel/show bible, character packs, production profile, and reusable-asset specifications.
- **Plan:** deliver the episode script, shot manifest, exact dialogue, H3 prompts, edit plan, and validation checklist. No rendering is implied by planning.
- **Produce:** render through the configured ComfyUI API, validate takes, assemble the master, then validate the finished episode.
- **Repair:** use observed failures to replace only affected takes and repeat relevant validation.

When asked to create or edit this skill, change the skill resources without running production. Publishing is a separate action and requires a request to publish.

## Production invariants

1. **One scene = one uninterrupted camera view = one rendered video file.** A narrative sequence may contain many scenes. A two-shot, A close-up, B close-up, and returning two-shot are four scenes and four independently generated files. Never request their cuts inside one H3 generation.
2. Continuous camera movement is allowed within that view. A cut, reverse angle, montage, or discontinuous viewpoint starts another scene. Returning to the same framing still gets a new scene ID.
3. Compile each H3 prompt with exactly one `[Shot 1]`. Episode scene IDs and H3 shot labels are different namespaces. FFmpeg performs the cuts between files.
4. Default final runtime is **300 seconds including intro and outro**. The intro is exactly **30 seconds**. Default outro is **10 seconds**, configurable because the user has not fixed its length. At 24 fps: intro 720 frames + story 6240 frames + outro 240 frames = 7200 frames. Never silently make a five-minute story plus bookends.
5. Both bookends explicitly ask viewers to **like and subscribe**. Generate and validate each master once, then reuse its versioned media file across episodes. Never regenerate them as routine episode scenes.
6. Character identity, wardrobe, voice, setting, and theme come from versioned canonical packs. Repeating a seed or an adjective is not evidence of consistency. Character/style LoRAs are distinct from acceleration/distillation LoRAs.
7. A rendered or assembled file is not validated until its visible content and actual audio have been inspected. Missing audiovisual tools mean unverified output, not a pass.

## Establish inputs without stalling

Find existing show configuration, character/reference packs, accepted bookends, workflow export, and production profile first. Copy [assets/channel-config.template.json](assets/channel-config.template.json) into the show's writable production folder when no configuration exists. Its nulls represent unconfigured facts; fill them from evidence or ask only for information needed at the current stage.

Keep the skill folder reusable: store channel-specific media, bibles, credentials, and episodes in the show's production folder. Keep credentials outside manifests.

For planning, mark unknown channel name, premise, target audience, genre, visual style, cast, language, or ending duration as proposed choices rather than inventing established canon. For rendering, a working API workflow and its actual checkpoint/reference capabilities are required. Unknown rendering details need not block story development.

## Write and compile an episode

1. Read the show bible and previous episode's canon ledger. Define the hook, conflict or question, escalation, payoff, and specific contribution to the channel's promise. Avoid filling runtime with repetition.
2. Reserve the bookends before allocating story time. Default order is intro → story → outro. If a cold open is requested, explicitly allocate it within the story budget and preserve the complete 30-second intro.
3. Write dialogue before compiling prompts. Lock each line's ID, exact words, language, character, delivery, and intended local time interval. Estimate whether natural speech plus pauses and actions fits; shorten or split an overloaded scene instead of requiring unnatural speech speed.
4. Break narrative sequences into camera views. Choose framing, continuous camera path, blocking, eyelines, screen direction, action progression, and continuity-in/out for each. Several characters can act and speak in the same scene. Prefer sequential turns where they improve attribution; do not impose a single-character limit.
5. Compile per-scene H3 prompts using [references/h3-prompts.md](references/h3-prompts.md). Bind real references to actual workflow inputs. Store mappings between episode character IDs and prompt-local speaker IDs.
6. Build `episode.json` from [assets/episode-plan.template.json](assets/episode-plan.template.json). Read its contract in [references/production.md](references/production.md). Keep an ordered shot table for the human alongside the machine-readable manifest.
7. Run `python scripts/validate_plan.py <episode.json>` from this skill folder. Resolve structural failures before handing off the plan. This does not assess story quality, spoken performance, or media.

Use source media duration and frame counts as evidence during production. Generate enough frames for the selected edit window and intentional handles; never assume requested clip duration equals encoded duration. Record generation and selected edit windows separately.

## Produce and verify

Read [references/production.md](references/production.md) before rendering or editing. Discover the installed ComfyUI graph and node schema; adapt a real API-format workflow rather than constructing imaginary SOL-H3 nodes. Render a representative multi-character dialogue shot before committing to the batch.

Read [references/continuity-and-validation.md](references/continuity-and-validation.md) before building character packs or judging media. Use available companion skills for character sheets, compatible character/style LoRAs, reference preparation, and audiovisual review only when their capabilities fit. If none are available, follow the pack contract directly and record the gap. Never pretend a companion skill, LoRA, voice lock, or validator is installed.

Validate every selected scene and the final assembled master. Repair missing/changed speech, wrong speakers, identity drift, wardrobe errors, unintended cuts, clipped lines, or material continuity failures. Preserve accepted takes. Default retry limit: initial take plus two repairs per scene, subject to the total budget. When exhausted, return concrete failure evidence and options instead of retrying indefinitely.

Finish with requested deliverables and their status: planned, rendered, scene-validated, assembled, final-validated, or needs review. Include master/subtitle paths when produced, selected take IDs, unresolved defects, actual runtime, and next necessary action. Never describe planning checks as a rendered-video test.
