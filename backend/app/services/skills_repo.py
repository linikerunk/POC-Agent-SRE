"""Loads SRE "skills" (known failure patterns + runbooks) from the local
clone of the skill-repo (https://github.com/linikerunk/skill-repo).

Each skill is a Markdown file with YAML front matter — see
skills-repo/README.md for the schema.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from app.config import settings


@dataclass
class Skill:
    id: str
    name: str
    triggers: list[str]
    severity: str
    root_cause: str
    recommended_actions: list[str]
    body: str


def _parse_skill_file(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"Skill file {path} is missing YAML front matter")
    _, frontmatter, body = text.split("---", 2)
    meta = yaml.safe_load(frontmatter) or {}
    return Skill(
        id=meta.get("id", path.stem),
        name=meta.get("name", path.stem),
        triggers=[t.lower() for t in meta.get("triggers", [])],
        severity=meta.get("severity", "low"),
        root_cause=meta.get("root_cause", ""),
        recommended_actions=meta.get("recommended_actions", []),
        body=body.strip(),
    )


def load_skills() -> list[Skill]:
    skills_dir = Path(settings.skills_repo_path) / "skills"
    if not skills_dir.exists():
        return []
    return [_parse_skill_file(p) for p in sorted(skills_dir.glob("*.md"))]


def match_skills(text: str) -> list[Skill]:
    """Skills whose triggers appear in the given text (case-insensitive)."""
    lowered = text.lower()
    return [s for s in load_skills() if any(t in lowered for t in s.triggers)]


def render_context(skills: list[Skill] | None = None) -> str:
    skills = load_skills() if skills is None else skills
    if not skills:
        return "No skills available in the skill repo."

    blocks = []
    for s in skills:
        actions = "\n".join(f"  - {a}" for a in s.recommended_actions) or "  (none listed)"
        blocks.append(
            f"### {s.name} (id: {s.id}, severity: {s.severity})\n"
            f"Triggers: {', '.join(s.triggers)}\n"
            f"Root cause: {s.root_cause}\n"
            f"Recommended actions:\n{actions}\n\n"
            f"{s.body}"
        )
    return "\n\n---\n\n".join(blocks)
