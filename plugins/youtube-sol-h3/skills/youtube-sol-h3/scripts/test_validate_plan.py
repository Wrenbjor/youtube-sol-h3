"""Offline regression checks for the structural validator; no media or API jobs."""

import copy
import unittest

from validate_plan import validate


def fixture():
    # 26 ten-second views + 30-second intro + 10-second outro = 300 seconds.
    plan = {
        "schema_version": 1, "episode_id": "fixture", "title": "Validation fixture",
        "show_bible_version": "v1", "fps": 24, "target_frames": 7200,
        "intro": {"edit_frames": 720}, "outro": {"edit_frames": 240},
        "character_ids": ["a", "b"], "scenes": [],
    }
    views = ["two-shot", "close-up A", "close-up B", "two-shot"]
    for index in range(26):
        plan["scenes"].append({
            "scene_id": f"s{index}", "sequence_id": "q1",
            "view": views[index % 4], "camera": "static",
            "single_camera_view": True, "edit_frames": 240,
            "generation_seconds": 10, "trim_in_frames": 0,
            "characters": ["a", "b"], "speaker_map": {"S1": "a", "S2": "b"},
            "input_mode": "T2VA", "references": [], "output_file": f"s{index}.mp4",
            "dialogue": [
                {"line_id": f"l{index}a", "character_id": "a", "language": "English",
                 "text": "Are you ready?", "start_seconds": 1, "end_seconds": 3},
                {"line_id": f"l{index}b", "character_id": "b", "language": "English",
                 "text": "I am ready.", "start_seconds": 4, "end_seconds": 6},
            ],
            "prompt": "integrated_multimodal_description: [Shot 1] A (S1) says: "
                      "<d>[English] Are you ready?</d> B (S2) replies: "
                      "<d>[English] I am ready.</d>\n"
                      "overall_soundscape: Quiet room.\nnon_diegetic_music: N/A",
        })
    return plan


class PlanValidationTests(unittest.TestCase):
    def setUp(self):
        self.plan = fixture()
        self.scene = self.plan["scenes"][0]

    def assert_failure(self, fragment):
        errors, _ = validate(self.plan)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_full_runtime_and_four_independent_views(self):
        self.assertEqual(validate(self.plan), ([], []))
        self.assertEqual(len({s["output_file"] for s in self.plan["scenes"][:4]}), 4)

    def test_multishot_generation_is_rejected(self):
        self.scene["prompt"] += "\n[Shot 2] Reverse angle."
        self.assert_failure("exactly one")

    def test_changed_words_are_rejected(self):
        self.scene["prompt"] = self.scene["prompt"].replace("I am ready.", "I was ready.")
        self.assert_failure("locked lines")

    def test_late_speech_is_rejected(self):
        self.scene["dialogue"][1]["end_seconds"] = 11
        self.assert_failure("past selected edit")

    def test_runtime_overrun_is_rejected(self):
        self.plan["outro"]["edit_frames"] += 24
        self.assert_failure("target is")

    def test_shared_intro_length_is_enforced(self):
        self.plan["intro"]["edit_frames"] = 696
        self.assert_failure("exactly 30")

    def test_duplicate_output_is_rejected(self):
        self.plan["scenes"][1]["output_file"] = self.scene["output_file"]
        self.assert_failure("duplicate output_file")

    def test_unknown_character_is_rejected(self):
        self.scene["characters"].append("c")
        self.assert_failure("absent from episode cast")

    def test_unknown_prompt_speaker_is_rejected(self):
        self.scene["prompt"] = self.scene["prompt"].replace("(S2)", "(S3)")
        self.assert_failure("speaker IDs")

    def test_trim_cannot_exceed_generation(self):
        self.scene["trim_in_frames"] = 48
        self.assert_failure("cannot cover")

    def test_unbound_reference_is_rejected(self):
        self.scene["prompt"] += " <Picture 1>"
        self.assert_failure("without supplied")

    def test_first_frame_mode_requires_image(self):
        self.scene["input_mode"] = "I2VA"
        self.assert_failure("requires reference")

    def test_malformed_inputs_return_errors(self):
        for bad in ([], {"fps": None}, {"fps": True}, {"fps": 24, "target_frames": 7200, "scenes": [None]}):
            self.assertTrue(validate(bad)[0])
        self.scene["input_mode"] = []
        self.assert_failure("invalid input_mode")

    def test_ref2va_format_with_bound_image(self):
        self.scene["input_mode"] = "Ref2VA"
        self.scene["references"] = [{"label": "<Picture 1>", "asset_id": "cast-v1"}]
        body = self.scene["prompt"].replace("integrated_multimodal_description:", "detailed_description:")
        self.scene["prompt"] = (
            "subject_definitions: <Subject 1> is A from <Picture 1>.\n"
            "summary: [reference generation] Two people speak.\n"
            "retention_analysis: <Subject 1>: fully_preserved.\n" + body
        )
        self.assertEqual(validate(self.plan)[0], [])

    def test_speech_load_is_warning_not_audio_verification(self):
        self.scene["dialogue"][0]["end_seconds"] = 1.2
        errors, warnings = validate(self.plan)
        self.assertEqual(errors, [])
        self.assertTrue(any("pacing" in warning for warning in warnings))

    def test_fixture_does_not_mutate_during_validation(self):
        saved = copy.deepcopy(self.plan)
        validate(self.plan)
        self.assertEqual(saved, self.plan)


if __name__ == "__main__":
    unittest.main()
