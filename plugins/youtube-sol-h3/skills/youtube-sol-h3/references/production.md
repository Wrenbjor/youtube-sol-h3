# Production manifest, ComfyUI, and assembly

## Manifest contract

Copy the episode template into the production workspace and fill it. Its nulls/empty arrays deliberately do not form a complete episode. Copy scene/dialogue/reference templates into their corresponding arrays, then remove the three template keys from the completed plan.

Top level:

- `schema_version`: 1; `episode_id`, `title`, `show_bible_version`: explicit IDs/strings.
- `fps`: positive integer output frame rate, default 24; `target_frames`: complete runtime, default 7200.
- `intro`, `outro`: `asset_id`, `version`, `master_path`, `sha256`, `edit_frames`. During planning an absent master/hash can remain null, but reserved edit lengths must be present. Intro is exactly 30 seconds. Outro uses the configured length.
- `character_ids`: permanent cast IDs for this episode.
- `scenes`: chronological story scenes; bookends are separate reused assets. A requested cold open needs an explicit edit decision list that preserves all frame budgets.

Every scene:

- `scene_id`: unique, e.g. `E001-S003`; `sequence_id`: narrative grouping, not render unit.
- `view`: human-readable camera view; `camera`: framing and continuous movement; `single_camera_view`: true.
- `edit_frames`: frames kept in final cut, excluding handles; `generation_seconds`: render request length; `trim_in_frames`: source-frame offset at output fps after normalization. Record native frame count/fps separately when rendering.
- `characters`: present permanent IDs, including audible off-screen characters. `speaker_map`: prompt-local speaker ID to permanent ID, e.g. `{"S1":"mara","S2":"ivo"}`. Recompile local IDs if ordering changes; permanent IDs never change.
- `dialogue`: objects with unique `line_id`, `character_id`, `language`, `text`, `start_seconds`, `end_seconds`, `delivery`. Times are local to the selected edit window. Zero lines is valid for silent action; ambience can still exist.
- `actions`, `continuity_in`, `continuity_out`: observable states, including wardrobe/prop variants and eyelines.
- `input_mode`: `T2VA`, `I2VA`, `FL2VA`, `L2VA`, or `Ref2VA`.
- `references`: bindings with `label`, `asset_id`, `path`, `role`, and actual `workflow_input`. Paths/graph bindings may remain null during planning only; production must resolve them.
- `prompt`: compiled H3 text; `workflow_profile_id`: real profile ID, unresolved until configured.
- `output_file`: unique selected scene file, even for repeated framing; `takes`: accumulated provenance/evidence; `status`: initially `planned`.

Each take records seed, workflow hash, checkpoint/adapter hashes, reference versions, render request, `prompt_id`, source path, measured streams/duration, QA report, and selection status. QA belongs to that exact media hash; changing a take invalidates its old report.

`python scripts/validate_plan.py episode.json` checks budget, timing, IDs, one-shot labels, dialogue tags, and reference declarations. It does not connect to ComfyUI or validate media. Frame arithmetic assumes normalization to manifest fps. Its speech-rate warning is a planning heuristic, not a model limit or listening test.

## ComfyUI production profile

Prepare a versioned profile containing API base URL (no secret), API-format workflow path/hash, installed node/version information, actual H3 checkpoint/variant, attention/acceleration adapters, compatible identity/style adapters, input-node mappings, supported modes/duration/frame constraints, resolution, audio support, output nodes, seed settings, and hardware budget. Leave unresolved fields unset instead of inventing nodes.

Read the installed implementation and [official server API documentation](https://docs.comfy.org/development/comfyui-server/comms_routes) when integrating. Core discovery/submission routes include `GET /object_info`, `GET /system_stats`, `POST /prompt`, `GET /history/{prompt_id}`, `GET /queue`, and `/ws`. These belong to the self-hosted API; hosted services may differ.

Start from an exported **API-format** graph, not frontend layout JSON. Clone it per take; patch only inspected inputs. Check required node types/values against discovery. Bind assets through supported loaders/uploads; do not assume image uploads handle arbitrary video/audio assets.

Submit with `prompt` containing the graph and `client_id` identifying this run. Save returned `prompt_id` immediately. Queue acceptance is not completion. Match progress/errors and history to that ID, then retrieve documented output artifacts from the actual output nodes. A preview image is not final video.

On a submission timeout with unknown outcome, reconcile saved IDs and queue/history before resubmitting to avoid duplicates. Keep a ledger keyed by episode/scene/take plus workflow/reference hashes. Resume accepted takes and queued jobs. Do not clear another user's queue or globally interrupt unrelated renders to fix one scene.

Probe one difficult representative scene for identity, multiple voices, exact words, framing, and duration before batch rendering. Repair failing profile/prompt assumptions within budget rather than generating an entire episode against them.

## Shared intro and outro lifecycle

Create specifications during configuration; produce masters when requested. The 30-second intro can comprise, for example, three ten-second single-view clips plus externally added graphics. Its identity, channel promise, logo/music, and like/subscribe CTA should form an engaging opener. The ending CTA defaults to ten seconds and can accommodate an end-screen layout; duration is configurable.

Do not infer that a 30-second opener guarantees retention or monetization. Preserve requested length and make its content work within it. Track retention when channel data exists; revise the shared asset only when requested.

Inspect both assembled masters, verify CTA words and legible graphics, measure exact edit frames, and register asset IDs, versions, hashes, stream formats, transcript, and validation evidence. Episodes select files by version. Reuse originals; derive compatible encodes without treating conversion as regeneration. Bookend changes create new versions instead of overwriting accepted masters.

## FFmpeg edit plan

Build an explicit edit decision list: intro, selected story takes in order, outro, source in-points, frame lengths, subtitles, overlays, and deliberate audio transitions. Record requested cold-open placement explicitly. Do not assemble by file-name glob order.

Inspect media with ffprobe. Normalize mismatched fps, dimensions, pixel format, video/audio codecs, channel layout, and sample rate to the delivery profile. Trim with frame-aware selections and reset timestamps; preserve complete dialogue. Missing audio needs an intentional silent track when concatenation expects audio, not accidental loss of scene sound.

Use concat demuxing with stream copy only for compatible streams/timestamps; otherwise normalize/re-encode or use a concat filter. Use argument arrays or properly quoted list files. Consult [FFmpeg concat demuxer](https://ffmpeg.org/ffmpeg-formats.html#concat) and [concat filter](https://ffmpeg.org/ffmpeg-filters.html#concat) for the installed version rather than prescribing a universal command for unknown streams.

Hard picture cuts are default. Apply short ambience fades or a continuous licensed score where useful, keeping speech uncut. Overlapping transitions reduce runtime; include their overlap in final timing. Normalize loudness using measured audio, keeping music below speech. Do not time-stretch dialogue to conceal a planning error.

Create subtitles from **verified actual audio**, reconcile with intended script, and flag discrepancies; script alone is not evidence of spoken content. Add exact CTA text/logo graphics externally. Export master and subtitles, measure runtime/frames, and revalidate the final encode.

## Channel readiness

Write original episodes with distinct substance and payoff. Keep provenance for models, adapters, characters, voices, music, and graphics. Before release work, inspect current commercial-use terms and YouTube monetization/altered-content requirements from authoritative sources; do not promise revenue or eligibility from AI generation or CTAs alone. This is a release-stage check, not a reason to block episode planning.
