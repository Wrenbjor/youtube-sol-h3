"""Validate this marketplace's local paths, versions, templates, and skill links."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main():
    claude = load(".claude-plugin/marketplace.json")
    codex = load(".agents/plugins/marketplace.json")
    assert claude["name"] == codex["name"]
    assert len(claude["plugins"]) == len(codex["plugins"]) == 1
    entry = claude["plugins"][0]
    entry2 = codex["plugins"][0]
    source = entry["source"]
    assert source.startswith("./") and ".." not in Path(source).parts
    assert entry2["source"] == {"source": "local", "path": source}
    assert entry2["policy"] == {"installation": "AVAILABLE", "authentication": "ON_USE"}
    assert entry2["category"]
    plugin = ROOT / source
    portable = load(f"{source}/plugin.json")
    claude_plugin = load(f"{source}/.claude-plugin/plugin.json")
    codex_plugin = load(f"{source}/.codex-plugin/plugin.json")
    manifests = [portable, claude_plugin, codex_plugin]
    assert {m["name"] for m in manifests} == {entry["name"], entry2["name"]}
    assert len({m["version"] for m in manifests}) == 1
    assert portable["version"] == entry["version"] == claude["metadata"]["version"]
    assert all(m["license"] == "MIT" for m in manifests)
    assert all(m["repository"] == "https://github.com/Wrenbjor/youtube-sol-h3" for m in manifests)
    assert codex_plugin["skills"] == "./skills/"
    assert portable["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    assert portable["extensions"]["com.openai"]["interface"] == codex_plugin["interface"]
    skills = list((plugin / "skills").glob("*/SKILL.md"))
    assert len(skills) == 1
    for skill in skills:
        text = skill.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        frontmatter = text.split("---", 2)[1]
        name = re.search(r"^name: (.+)$", frontmatter, re.M).group(1)
        description = re.search(r"^description: (.+)$", frontmatter, re.M).group(1)
        assert name == skill.parent.name == portable["name"]
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) and len(name) <= 64
        assert 0 < len(description) <= 1024
        assert f'version: "{portable["version"]}"' in frontmatter
        assert "license: MIT" in frontmatter
        assert "TODO" not in text
        for destination in re.findall(r"\]\(([^)]+)\)", text):
            if "://" not in destination and not destination.startswith("#"):
                assert (skill.parent / destination).exists(), destination
        for template in (skill.parent / "assets").glob("*.json"):
            json.loads(template.read_text(encoding="utf-8"))
        assert (skill.parent / "LICENSE").read_text() == (ROOT / "LICENSE").read_text()
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        assert path.suffix.lower() not in {".mp4", ".wav", ".safetensors"}, path
        assert not path.name.startswith(".env"), path
    print("PASS: marketplace paths, manifest versions, skill metadata/links, and JSON templates")
    print("This checks package structure, not host installation or rendered media.")


if __name__ == "__main__":
    main()
