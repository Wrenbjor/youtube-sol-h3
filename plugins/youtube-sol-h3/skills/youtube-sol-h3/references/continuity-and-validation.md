# Character packs, companion skills, and audiovisual validation

## Canonical continuity pack

Create one versioned show bible and registry. Separate canonical identity from episode-specific state:

| Pack | Required useful content |
| --- | --- |
| Character | Permanent ID, names, facial/body/species traits, proportions, palette, front/profile/three-quarter/full-body references, wardrobe variants, distinctive features, performance mannerisms |
| Voice | Permanent character binding, pitch/timbre/accent/rate, accepted clean sample when supported, pronunciation notes, usable rights |
| Theme/style | Palette, materials, lighting, framing habits, render style, prohibited style drift, approved references |
| Location | Layout, scale, entrances, anchor objects, light direction, reference viewpoints |
| Adapter | File/hash, type (identity/style/acceleration), intended architecture/variant, trigger tokens, tested strength range, compatibility evidence, license/source |

Companion skills hand back this contract plus files. Discover relevant existing skills before invoking them. Do not install/train an arbitrary LoRA as a side effect of planning. If training is requested, verify data rights/architecture compatibility and evaluate it in the actual render graph.

A still-image LoRA cannot be assumed compatible with H3 weights. It can help upstream with character sheets/keyframes; those images then guide a supported H3 reference workflow. A direct H3 identity/style LoRA needs its own compatible loader and test. An acceleration adapter does not replace identity conditioning.

For two characters in one view, bind distinct assets and spatial positions. Check identity blending, swapped wardrobes, and swapped voices. Test character/style/acceleration adapter interactions on the actual profile. Record successful combinations rather than guessing strengths or stacking many adapters.

Maintain a continuity ledger: positions, camera side/180-degree axis, eyelines, wardrobe, handedness, props, damage, lighting, time, voice, and action state. Keep original references as series anchors; a chain of drifting generated frames must not redefine canon.

## Validation method

Choose tools that actually accept the needed media/modalities. Prefer a capable audiovisual model that watches the clip with audio; supplement with timestamped transcription and technical probing. Use the source file and accepted references, not just its prompt. Do not spawn a separate agent unless delegation is independently authorized; independent review here means judging output evidence instead of trusting generation instructions.

For diagnosis, first obtain observed transcription/description without feeding expected dialogue as a suggested answer. Then compare observations with locked script and canonical references. Review full selected clips for performance and speech timing; compare beginning/middle/end and turn/reaction frames for identity, plus adjacent clips at every boundary.

A frames-only model supplies visual review only. Use the actual audio track with ASR/audio-capable review for speech. Frames/subtitles cannot prove dialogue is audible. ASR can mishear; uncertain mismatches need listening/review instead of blind acceptance or rejection.

### Scene evidence checklist

- **Speech:** locked lines present in order; no omitted/added words or changed meaning; correct audible speaker/voice; plausible pace; complete beginning/end; correct language/pronunciation. Ignore only punctuation/case differences that are not audible. Inspect names/numbers carefully.
- **Synchronization:** intended speaker's lips match speech; listeners do not mouth another character's words; off-screen voice distinguished; no unintended simultaneous turns.
- **Identity:** characters match canonical references throughout, stay distinct, and retain approved proportions/features/wardrobe. Intentional changes must be in the ledger.
- **Direction:** actions occur; objects remain coherent; no unplanned camera cut/viewpoint reset; movement fits one continuous view.
- **Continuity:** screen direction, eyelines, anchors, lighting, props, and action states fit neighboring scenes.
- **Technical:** media decodes, expected streams present, usable selected frames/duration, no corrupt/frozen sequence, clipped sound, severe artifacts, or unintended watermark.

Use `pass`, `fail`, or `needs_review` per check. Similarity scores support judgment only with a metric/threshold calibrated against accepted references/takes; never invent a universal consistency percentage. A different pose is not automatically identity drift.

### QA record

Store a structured report for each take and the final master:

```json
{
  "media_path": "scene-take.mp4",
  "media_sha256": "measured hash",
  "scene_id": "E001-S003",
  "reviewer": "actual tool/model and version",
  "modalities_checked": ["video", "audio"],
  "reference_versions": ["mara-v1", "workshop-v1"],
  "observed_transcript": [],
  "checks": {"dialogue": "needs_review", "identity": "needs_review"},
  "issues": [],
  "overall": "needs_review"
}
```

An issue includes timestamp, observed problem, expected state, evidence path, severity, confidence, and proposed repair. Missing evidence never becomes `pass`. Every applicable check must pass for overall pass; material defects fail; uncertain/unavailable checks need review.

## Repair choices

Change the smallest relevant input. For missing dialogue, shorten/split action load or increase supported length, preserving locked words. For speaker swaps, simplify turns and strengthen speaker/reference binding. For identity drift, repair references/keyframes or compatible adapters. For cuts, remove transitions/incompatible framing. For clipped audio, adjust the edit window or regenerate complete speech.

Preserve take history and accepted media. Respect scene/episode retry budgets. Dubbing creates a new lip-sync requirement; it is not an automatic pass. Revalidate replacements and neighboring cuts, then the rebuilt master.

## Final master review

Watch/listen from start to end. Verify story comprehension/pacing, every cut, all speech/subtitles, identity, audio balance, actual 300-second target (within declared frame/container tolerance), and both like/subscribe CTAs. Verify registered bookend versions were used. Scene passes do not prove assembly order, sound, subtitles, or bookends.

Save final evidence with the delivered encode's hash. If no suitable reviewer exists, deliver an explicit `needs_review` report naming the missing modality; do not claim final validation.
