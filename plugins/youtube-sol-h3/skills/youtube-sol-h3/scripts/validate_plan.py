"""Check episode planning invariants without rendering or inspecting media."""

import argparse
import json
import math
import re
from pathlib import Path


BASE_FIELDS = ("integrated_multimodal_description", "overall_soundscape", "non_diegetic_music")
REF_FIELDS = ("subject_definitions", "summary", "retention_analysis", "detailed_description",
              "overall_soundscape", "non_diegetic_music")
MODES = {"T2VA", "I2VA", "FL2VA", "L2VA", "Ref2VA"}


def integer(value, minimum=1):
    return type(value) is int and value >= minimum


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def string(value):
    return isinstance(value, str) and bool(value.strip())


def validate(plan):
    errors, warnings = [], []

    def fail(where, message):
        errors.append(f"{where}: {message}")

    def unique_strings(values, where):
        if not isinstance(values, list) or any(not string(v) for v in values):
            fail(where, "must be an array of nonempty strings")
            return set()
        if len(values) != len(set(values)):
            fail(where, "duplicate IDs")
        return set(values)

    if not isinstance(plan, dict):
        return ["plan: must be a JSON object"], warnings
    if type(plan.get("schema_version")) is not int or plan["schema_version"] != 1:
        fail("schema_version", "must be 1")
    for key in ("episode_id", "title", "show_bible_version"):
        if not string(plan.get(key)):
            fail(key, "must be a nonempty string")
    fps, target = plan.get("fps"), plan.get("target_frames")
    if not integer(fps) or not integer(target):
        fail("runtime", "fps and target_frames must be positive integers")
        return errors, warnings
    if target != 300 * fps:
        warnings.append("runtime: target differs from the default five-minute episode")
    cast = unique_strings(plan.get("character_ids"), "character_ids")
    total = 0
    for key in ("intro", "outro"):
        asset = plan.get(key)
        if not isinstance(asset, dict) or not integer(asset.get("edit_frames")):
            fail(key, "requires positive integer edit_frames")
            continue
        total += asset["edit_frames"]
        if key == "intro" and asset["edit_frames"] != 30 * fps:
            fail(key, "must reserve exactly 30 seconds")
    scenes = plan.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        fail("scenes", "requires at least one story scene")
        return errors, warnings
    for key in ("scene_template", "dialogue_template", "reference_template"):
        if key in plan:
            fail(key, "remove template seeds from a completed episode plan")
    seen_scenes, seen_files, seen_lines = set(), set(), set()
    for index, scene in enumerate(scenes):
        where = f"scenes[{index}]"
        if not isinstance(scene, dict):
            fail(where, "must be an object")
            continue
        for key, seen in (("scene_id", seen_scenes), ("output_file", seen_files)):
            value = scene.get(key)
            if not string(value):
                fail(where, f"{key} must be a nonempty string")
            elif value in seen:
                fail(where, f"duplicate {key}: {value}")
            else:
                seen.add(value)
        for key in ("sequence_id", "view", "camera"):
            if not string(scene.get(key)):
                fail(where, f"requires {key}")
        if scene.get("single_camera_view") is not True:
            fail(where, "single_camera_view must be true")
        frames, generated, trim = (scene.get("edit_frames"), scene.get("generation_seconds"),
                                   scene.get("trim_in_frames", 0))
        duration = None
        if not integer(frames):
            fail(where, "edit_frames must be a positive integer")
        else:
            total += frames
            duration = frames / fps
        if not number(generated) or generated <= 0:
            fail(where, "generation_seconds must be positive and finite")
        elif not 4 <= generated <= 15:
            warnings.append(f"{where}: generation length outside published H3 base range; verify profile")
        if not integer(trim, 0):
            fail(where, "trim_in_frames must be a nonnegative integer")
        elif duration is not None and number(generated) and (trim + frames) / fps > generated + 1 / fps:
            fail(where, "generation request cannot cover trim plus selected edit window")
        characters = unique_strings(scene.get("characters"), f"{where}.characters")
        if not characters <= cast:
            fail(where, "characters includes IDs absent from episode cast")
        speakers = scene.get("speaker_map")
        if not isinstance(speakers, dict):
            fail(where, "speaker_map must be an object")
            speakers = {}
        elif any(not re.fullmatch(r"S[1-9]\d*", key) or not string(value) or value not in characters
                 for key, value in speakers.items()):
            fail(where, "speaker_map must bind S-number IDs to characters in this scene")
        mode = scene.get("input_mode")
        if not string(mode) or mode not in MODES:
            fail(where, "invalid input_mode")
        prompt = scene.get("prompt")
        if not string(prompt):
            fail(where, "requires compiled prompt")
            prompt = ""
        shots = re.findall(r"\[Shot\s+(\d+)\]", prompt, re.I)
        if shots != ["1"]:
            fail(where, "prompt must contain exactly one [Shot 1] and no other shot labels")
        if "<scenetrans>" in prompt or "<cutoff>" in prompt:
            fail(where, "cross-shot/cutoff dialogue tags do not belong in single-view generation")
        required = REF_FIELDS if mode == "Ref2VA" else BASE_FIELDS
        fields = re.findall(r"^([a-z_]+):", prompt, re.M)
        if fields != list(required):
            fail(where, f"prompt sections must occur exactly once in order: {', '.join(required)}")
        references = scene.get("references")
        if not isinstance(references, list):
            fail(where, "references must be an array")
            references = []
        labels = set()
        for ref in references:
            if not isinstance(ref, dict) or not string(ref.get("label")) or not string(ref.get("asset_id")):
                fail(where, "reference needs label and asset_id")
                continue
            if not re.fullmatch(r"<(?:Picture|Video|Audio) [1-9]\d*>", ref["label"]):
                fail(where, "asset reference label must be <Picture N>, <Video N>, or <Audio N>")
            if ref["label"] in labels:
                fail(where, "duplicate reference label")
            labels.add(ref["label"])
        used_labels = set(re.findall(r"<(?:Picture|Video|Audio) [1-9]\d*>", prompt))
        if not used_labels <= labels:
            fail(where, "prompt contains reference labels without supplied asset declarations")
        image_labels = {label for label in labels if label.startswith("<Picture")}
        needed_images = 2 if mode == "FL2VA" else 1 if mode == "I2VA" or mode == "L2VA" else 0
        if len(image_labels) < needed_images or (mode == "Ref2VA" and not labels):
            fail(where, "input mode requires reference asset declarations")
        dialogue = scene.get("dialogue")
        if not isinstance(dialogue, list):
            fail(where, "dialogue must be an array")
            dialogue = []
        expected, last_start = [], -1
        for line in dialogue:
            if not isinstance(line, dict):
                fail(where, "dialogue entry must be an object")
                continue
            lid, character = line.get("line_id"), line.get("character_id")
            if not string(lid) or lid in seen_lines:
                fail(where, "dialogue line IDs must be nonempty and unique across episode")
            else:
                seen_lines.add(lid)
            if not string(character) or character not in characters or character not in speakers.values():
                fail(where, "dialogue character must be present and bound to a speaker")
            text, language = line.get("text"), line.get("language")
            if not string(text) or not string(language):
                fail(where, "dialogue requires exact text and language")
            else:
                expected.append((language, text))
            start, end = line.get("start_seconds"), line.get("end_seconds")
            if not number(start) or not number(end) or start < 0 or end <= start:
                fail(where, "dialogue interval must be finite, nonnegative, and nonempty")
                continue
            if duration is not None and end > duration + 1e-6:
                fail(where, "dialogue extends past selected edit window")
            if start < last_start:
                fail(where, "dialogue entries must be chronological")
            last_start = start
            if string(text) and language == "English" and len(text.split()) / (end - start) * 60 > 210:
                warnings.append(f"{where}/{lid}: more than 210 English words/minute; review natural pacing")
        actual = re.findall(r"<d>\[([^\]]+)\]\s?(.*?)</d>", prompt, re.S)
        if actual != expected:
            fail(where, "prompt dialogue differs from locked lines in words, language, count, or order")
        prompt_speakers = set()
        for group in re.findall(r"\((S\d+(?:,S\d+)*)\)", prompt):
            prompt_speakers.update(group.split(","))
        if prompt_speakers != set(speakers):
            fail(where, "prompt speaker IDs and speaker_map do not match")
    if total != target:
        fail("runtime", f"bookends plus story total {total} frames; target is {target}")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8-sig"))
        errors, warnings = validate(plan)
    except (OSError, ValueError) as exc:
        print(f"FAIL: cannot read plan: {exc}")
        return 2
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"FAIL: {error}")
    if not errors:
        print("PASS: planning invariants checked; audiovisual output remains unverified.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
