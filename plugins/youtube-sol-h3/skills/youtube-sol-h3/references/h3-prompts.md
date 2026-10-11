# H3 prompt compilation

## Evidence and capability binding

Checked on 2026-10-11. SOL-H3 is NVIDIA's accelerated MiniMax-H3 inference stack, not a separate narrative instruction language. Published speed profiles are hardware-specific; do not promise those timings for another system.

Sources:

- [NVIDIA SOL-H3 project](https://nvlabs.github.io/Sana/Sol-Engine/Sol-H3/)
- [MiniMax H3 model card](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- [Official base-mode prompt format](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/base-en.txt)
- [Official full-reference prompt format](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/ref-en.txt)

Before compiling production prompts, read the applicable official guide and compare it with the installed workflow. Pin its revision/URL in the production profile. If unavailable, label the local examples as a starting point requiring a probe; do not claim verified compatibility.

The published H3 base range is 4–15 seconds, with 24 fps and native stereo audio. Use actual workflow limits, including discrete frame constraints, rather than assuming every duration is available. Ref2VA has documented limits of nine images, three videos, and three audio clips, with at most twelve files combined; video/audio references also have duration restrictions. Check the model card and installed nodes before binding assets. A 30-second intro is assembled from multiple supported clips.

## Compilation contract

Base modes use, in order: `integrated_multimodal_description`, `overall_soundscape`, `non_diegetic_music`. Keyframe modes place the official alignment instruction first. Ref2VA uses: `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music`.

Identify each vocal source with a prompt-local `(S1)`, `(S2)`, etc. following the official numbering rules; map it to a permanent character ID outside the prompt. Preserve dialogue inside `<d>[Language] ...</d>`; keep action and delivery outside it. Reference labels must map to supplied files. A label alone supplies no image or voice.

## Decisions specific to this show workflow

Compile each local timeline into ONE `[Shot 1]`, even when official examples show multi-shot generation. Do not insert `[Shot 2]`, cut instructions, `<scenetrans>`, or deliberate speech cutoff. Cross-scene audio transitions belong to the external edit plan.

Each view needs its own canonical references. A previous scene's last frame can help continuous action, but is not automatically the right first frame for a reverse-angle close-up. Create a composition appropriate to the new viewpoint while keeping the original character pack as the identity anchor.

Use explicit blocking: who is left/right, who holds a prop, where they look, who speaks, and what the listener does. Describe the intended camera path naturally. Avoid two incompatible perspectives within one continuous scene.

Production IDs, paths, QA criteria, seeds, and node settings belong in the manifest/API graph. A seed is reproducibility metadata, not a character ID.

## Original one-shot example (text mode)

This is a format illustration, not a channel episode or tested render. For eight seconds:

```text
integrated_multimodal_description: [Shot 1] Stylized 3D animation. A static medium two-shot shows Mara on the left in her navy work jacket and Ivo on the right in his rust vest, facing each other across a brass workbench. Warm light falls from the left; the circular blue lamp remains centered behind them. From 0 to 3 seconds, Mara, with a low measured English voice (S1), sets the sealed silver box on the bench and says: <d>[English] You said it was empty.</d> Ivo watches the box with his mouth closed. From 3 to 7 seconds, Ivo, with a light dry English voice (S2), raises one eyebrow and replies: <d>[English] It was. Then it started knocking.</d> Mara listens with her mouth closed. During the final second they both look down as the closed box taps once. The same uninterrupted camera view lasts throughout.

overall_soundscape: Quiet workshop ventilation. The box touches the wooden bench with a soft thud, followed at the end by one metallic tap from inside.

non_diegetic_music: N/A
```

For Ref2VA, bind real canonical assets in the six-section format. Retention analysis expresses intent; inspecting the output establishes whether it was retained.

## Audio decisions

Default to native dialogue, sound effects, and restrained ambience. Set non-diegetic music to `N/A` when scoring continuously in FFmpeg so clips do not generate mismatched music restarts. Add exact logos, CTA typography, and subtitles during editing when reliable legibility matters.

Prefer complete lines within each clip. If a line must span a camera cut, render a complete approved audio performance, define where its audio continues across independently generated picture files, and verify lips in both views. Do not silently substitute a different voice system or dub visibly speaking characters without checking synchronization.
