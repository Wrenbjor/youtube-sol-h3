# YouTube SOL-H3 Episodes

An open Agent Skill for turning episode ideas into five-minute YouTube shows using **SOL-H3 / MiniMax H3**, **ComfyUI**, and **FFmpeg**.

A capable reasoning model writes and directs the episode. H3 generates the individual audiovisual clips. The skill connects planning, character continuity, rendering instructions, editing, and review.

**One scene means one camera view and one generated video file.** A two-shot → close-up of A → close-up of B → returning two-shot is four scenes. Shot transitions happen in FFmpeg so each render can use its own framing and character references.

## What it provides

- Episode writing and timed shot manifests, with multiple characters, actions, exact dialogue, speaker bindings, and continuous camera direction.
- A reusable 30-second intro and closing like-and-subscribe CTA, generated once when production is configured and reused by version.
- Character, voice, location, and theme packs, with contracts for companion character/style LoRA workflows.
- H3 prompt compilation based on the official base and full-reference formats.
- ComfyUI API production guidance using an inspected workflow export and real node/input bindings.
- FFmpeg editing guidance and separate checks for rendered scenes and the complete master.
- A dependency-free Python plan validator and 16 offline regression tests.

Default timing: **30 seconds intro + 260 seconds story + 10 seconds outro = 300 seconds**. The outro is configurable; the five-minute total includes both bookends.

## Install

### Agent Skills CLI

List the available skill without installing:

```sh
npx skills add Wrenbjor/youtube-sol-h3 --list
```

Install the skill for your agent:

```sh
npx skills add Wrenbjor/youtube-sol-h3 --skill youtube-sol-h3
```

The repository follows the [Agent Skills specification](https://agentskills.io/specification). Installation options are documented in the [Skills CLI](https://github.com/vercel-labs/skills).

### Claude Code marketplace

```sh
claude plugin marketplace add Wrenbjor/youtube-sol-h3
claude plugin install youtube-sol-h3@wrenbjor-video-skills
```

In a Claude Code session, invoke `/youtube-sol-h3:youtube-sol-h3` or request the workflow in natural language. See the [marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces).

### Codex marketplace

```sh
codex plugin marketplace add Wrenbjor/youtube-sol-h3 --ref main
```

Use the desktop Plugins Directory to choose **Wrenbjor Video Skills** and install **YouTube SOL-H3 Episodes**. The package includes a portable Agent Plugins manifest and a Codex compatibility manifest; see [official packaging guidance](https://developers.openai.com/plugins/build/plugins).

### Manual skill installation

Copy `plugins/youtube-sol-h3/skills/youtube-sol-h3` into your agent's skills directory. Keep its supporting files together. For Codex, invoke `$youtube-sol-h3` after the skill is loaded.

## Start with a plan

```text
Use youtube-sol-h3 in Plan mode. Draft a five-minute episode for my show,
using the existing show bible and character packs. Make each camera view a
separate scene with exact dialogue and an H3 prompt. Reserve the shared
30-second intro and 10-second outro. Do not render yet.
```

The workflow supports **Configure**, **Plan**, **Produce**, and **Repair**. Production needs your actual ComfyUI endpoint, API-format workflow, H3 model/profile, canonical references, and audiovisual review tools. Missing production details can remain unconfigured while writing the plan.

Copy the channel and episode templates from the skill's `assets/` directory into a separate production workspace. Keep personal media, model weights, production credentials, and episode outputs outside this repository.

## Validate

From the repository root:

```sh
python scripts/validate_package.py
python plugins/youtube-sol-h3/skills/youtube-sol-h3/scripts/test_validate_plan.py
python plugins/youtube-sol-h3/skills/youtube-sol-h3/scripts/validate_plan.py /path/to/episode.json
```

The plan checker catches inconsistent frame budgets, duplicate scene/output IDs, multi-shot labels, dialogue timing problems, changed dialogue, and undeclared asset references. It does **not** watch rendered video. Actual speech, lip synchronization, identity, continuity, and assembled quality require audiovisual review.

## Package layout

```text
.agents/plugins/marketplace.json       Codex marketplace catalog
.claude-plugin/marketplace.json        Claude Code marketplace catalog
plugins/youtube-sol-h3/
  plugin.json                         Portable Agent Plugins manifest
  .claude-plugin/plugin.json           Claude Code manifest
  .codex-plugin/plugin.json            Codex compatibility manifest
  skills/youtube-sol-h3/
    SKILL.md                          Portable skill instructions
    agents/openai.yaml                Optional Codex skill UI metadata
    assets/                           Channel and episode templates
    references/                       Prompt, production, continuity, QA
    scripts/                          Plan validator and offline tests
scripts/validate_package.py            Distribution checks
```

## Status and scope

Version **1.0.1** packages the instructions, templates, validators, and marketplace metadata. It is not a bundled ComfyUI installation, H3 checkpoint, character LoRA, trained voice, or autonomous video-rendering service. Rendering and audiovisual acceptance have not been exercised against a configured production system.

Publishing the repository makes it publicly accessible and installable. It does not imply acceptance into Anthropic's or OpenAI's curated directories, or immediate indexing by third-party skill catalogs.

The skill's H3 references link to [NVIDIA SOL-H3](https://nvlabs.github.io/Sana/Sol-Engine/Sol-H3/) and [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3). Model weights, adapters, music, and generated assets have their own terms. This repository's MIT license covers its skill and supporting code.

## Contributing

Report issues with the affected mode, a minimal anonymized plan or manifest, and expected versus observed behavior. Do not include credentials or private production assets. Run package checks and offline tests before proposing changes. Keep the skill portable and preserve one camera view per render.
