#!/usr/bin/env python3
"""Validate a lean SDD specs workspace (stdlib only).

Checks structure, relative links, and the minimum adversarial surface:
user story + acceptance on Active Specs; goal + acceptance on Roadmap versions.
Heavy Decision Summary / prerequisite-audit bureaucracy is intentionally not required.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote

VERSION_HEADING = re.compile(r"^##\s+v(\d+\.\d+)\b", re.MULTILINE)
VERSION_INDEX = re.compile(r"^- \[([ xX])\]\s+`v(\d+\.\d+)`\s+—\s+.+$", re.MULTILINE)
ACTIVE_NAME = re.compile(r"^\d{2}-.+-plan\.md$")
DATED_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-.+\.md$")
RESEARCH_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-.+-research\.md$")
ARCHIVE_STATUS = re.compile(
    r"^>\s*Status:\s*(completed|cancelled)\s*\((\d{4}-\d{2}-\d{2})\)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
ARCHIVE_REASON = re.compile(r"^>\s*Archive reason:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
BLOCKED_ENTRY_MARKER = "<!-- BLOCKED_ENTRIES_START -->"
BLOCKED_ENTRY_TITLE = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?"
    r"(?:Z|[+-]\d{2}:\d{2}))\s+—\s+(?P<title>\S.*)"
)
BLOCKED_STATUS_VALUES = {
    "resolved-autonomously",
    "awaiting-user",
    "resolved-by-user",
}
BLOCKED_FIELD_ALIASES = {
    "status": {"status", "状态"},
    "spec_phase": {
        "spec / phase",
        "spec/phase",
        "所属 spec / phase",
        "所属 spec/phase",
    },
    "blocker": {"blocker", "阻塞原因"},
    "decision": {"decision", "决策"},
    "rationale": {"rationale", "决策理由"},
    "impact": {
        "impact / follow-up",
        "impact/follow-up",
        "影响 / 后续",
        "影响/后续",
    },
}
STATUS_ROW = re.compile(
    r"^\|[ \t]*(?:\*\*)?(?:状态|Status)(?:\*\*)?[ \t]*\|[ \t]*([^|\r\n]+?)[ \t]*\|[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
COMPLETED_ROW = re.compile(
    r"^\|[ \t]*(?:\*\*)?(?:完成日期|Completed)(?:\*\*)?[ \t]*\|[ \t]*([^|\r\n]+?)[ \t]*\|[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
TASK_ITEM = re.compile(
    r"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+\[([ xX])\](?:[ \t]+(.*))?$",
    re.MULTILINE,
)

GOAL_HEADINGS = ("目标", "Goal")
DELIVERABLE_HEADINGS = ("关键交付", "Key Deliverables")
ACCEPTANCE_HEADINGS = (
    "验收标准",
    "Acceptance",
    "Acceptance Criteria",
    "螺旋验收",
    "Spiral Acceptance",
    "可运行验收",
    "Runnable Acceptance",
)
USER_STORY_HEADINGS = ("用户故事", "User Story")
PHASES_HEADINGS = ("实施阶段", "Phases", "Implementation Phases")
METADATA_HEADINGS = ("元数据", "Metadata")
ARCH_STATUS_HEADINGS = ("文档状态", "Document Status")
ARCH_OVERVIEW_HEADINGS = ("系统概览", "System Overview")
ARCH_RUNNABLE_HEADINGS = ("可运行系统路径", "Runnable System Path")
ARCH_SOURCE_HEADINGS = (
    "源码布局",
    "Source Layout",
    "当前源码布局",
    "Current Source Layout",
    "目标源码布局",
    "Target Source Layout",
)
ARCH_DEPENDENCY_HEADINGS = ("依赖方向", "Dependency Direction")
ARCH_OWNERSHIP_HEADINGS = ("变更归属", "Change Ownership")

# Optional legacy Increment Contract: if present, require user story + acceptance inside it.
INCREMENT_CONTRACT_HEADINGS = ("增量契约", "Increment Contract")


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    path: str
    message: str


class Validator:
    def __init__(self, specs: Path) -> None:
        self.specs = specs
        self.issues: list[Issue] = []

    def error(self, code: str, path: Path, message: str) -> None:
        self.issues.append(Issue("error", code, self._display(path), message))

    def warn(self, code: str, path: Path, message: str) -> None:
        self.issues.append(Issue("warning", code, self._display(path), message))

    def _display(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.specs.parent))
        except ValueError:
            return str(path)

    def run(self) -> list[Issue]:
        self._check_repository_architecture()
        self._check_shape()
        self._check_blocked_log()
        self._check_roadmap()
        self._check_named_directories()
        self._check_active_specs()
        self._check_archived_artifacts()
        self._check_links()
        return self.issues

    # --- repository / shape -------------------------------------------------

    def _check_repository_architecture(self) -> None:
        repository = self.specs.parent
        architecture = repository / "ARCHITECTURE.md"
        root_agents = repository / "AGENTS.md"
        specs_agents = self.specs / "AGENTS.md"

        if not architecture.is_file():
            self.error(
                "missing_architecture",
                architecture,
                "root ARCHITECTURE.md is required for initialized workspaces",
            )
            return

        text = architecture.read_text(encoding="utf-8")
        structure = strip_fenced_code(text)
        h1 = re.findall(r"^#\s+\S.*$", structure, re.MULTILINE)
        if len(h1) != 1:
            self.error("architecture_title", architecture, "expected exactly one non-empty H1")

        for headings, code in [
            (ARCH_STATUS_HEADINGS, "status"),
            (ARCH_OVERVIEW_HEADINGS, "overview"),
            (ARCH_RUNNABLE_HEADINGS, "runnable_path"),
            (ARCH_SOURCE_HEADINGS, "source_layout"),
            (ARCH_DEPENDENCY_HEADINGS, "dependency_direction"),
            (ARCH_OWNERSHIP_HEADINGS, "change_ownership"),
        ]:
            if not has_h2(structure, headings):
                self.error(
                    f"architecture_{code}",
                    architecture,
                    f"missing expected section: {headings[0]}",
                )

        if root_agents.is_file():
            if not has_md_link_to(root_agents.read_text(encoding="utf-8"), "ARCHITECTURE.md"):
                self.error(
                    "root_agents_architecture_link",
                    root_agents,
                    "root AGENTS.md must include a repository-relative Markdown link to ARCHITECTURE.md",
                )
        else:
            self.warn("missing_root_agents", root_agents, "root AGENTS.md is missing")

        if specs_agents.is_file():
            if not has_md_link_to(specs_agents.read_text(encoding="utf-8"), "../ARCHITECTURE.md"):
                self.error(
                    "specs_agents_architecture_link",
                    specs_agents,
                    "specs/AGENTS.md must include a repository-relative Markdown link to ../ARCHITECTURE.md",
                )

    def _check_shape(self) -> None:
        agents = self.specs / "AGENTS.md"
        blocked = self.specs / "BLOCKED.md"
        active = self.specs / "active"
        roadmap = self.specs / "ROADMAP.md"
        archive = self.specs / "archive"

        if not agents.is_file():
            self.error("missing_required_path", agents, "required AGENTS.md file is missing")
        if not blocked.is_file():
            self.error("missing_required_path", blocked, "required BLOCKED.md file is missing")
        if not active.is_dir():
            self.error("missing_required_path", active, "required active directory is missing")
        if roadmap.exists() and not roadmap.is_file():
            self.error("invalid_optional_path", roadmap, "ROADMAP.md must be a file when present")
        for name in ("constitution", "research"):
            path = self.specs / name
            if path.exists() and not path.is_dir():
                self.error(
                    "invalid_optional_path",
                    path,
                    f"{name} must be a directory when present",
                )
        if archive.exists() and not archive.is_dir():
            self.error("invalid_optional_path", archive, "archive must be a directory when present")

    # --- BLOCKED ------------------------------------------------------------

    def _check_blocked_log(self) -> None:
        path = self.specs / "BLOCKED.md"
        if not path.is_file():
            return
        text = path.read_text(encoding="utf-8")
        structure = strip_fenced_code(text)
        h1 = re.findall(r"^#\s+\S.*$", structure, re.MULTILINE)
        if len(h1) != 1:
            self.error("blocked_title", path, "expected exactly one non-empty H1 title")
        if text.count(BLOCKED_ENTRY_MARKER) != 1:
            self.error(
                "blocked_marker",
                path,
                "BLOCKED.md must contain exactly one insertion marker",
            )
            return
        marker_at = text.index(BLOCKED_ENTRY_MARKER)
        body = text[marker_at + len(BLOCKED_ENTRY_MARKER) :]
        # Entries may only appear after the marker.
        before = text[:marker_at]
        if re.search(r"^##\s+\d{4}-\d{2}-\d{2}T", before, re.MULTILINE):
            self.error(
                "blocked_entry_placement",
                path,
                "decision entries must appear below the insertion marker",
            )

        entries = split_h2_sections(body)
        timestamps: list[str] = []
        for entry_number, (heading, entry_body) in enumerate(entries, start=1):
            title_match = BLOCKED_ENTRY_TITLE.fullmatch(heading.strip())
            if title_match is None:
                self.error(
                    "blocked_entry_heading",
                    path,
                    (
                        f"entry {entry_number} heading must use a timezone-aware ISO 8601 "
                        "timestamp and title"
                    ),
                )
                continue
            timestamps.append(title_match.group("timestamp"))
            if not _has_timezone(title_match.group("timestamp")):
                self.error(
                    "blocked_entry_timezone",
                    path,
                    f"entry {entry_number} timestamp must include a timezone",
                )
            self._check_blocked_entry(path, entry_number, entry_body)

        if timestamps != sorted(timestamps, reverse=True):
            # Only warn: clock skew / same-second edits shouldn't hard-fail lean flow.
            self.warn(
                "blocked_entry_order",
                path,
                "decision entries should be ordered newest-first",
            )

    def _check_blocked_entry(self, path: Path, entry_number: int, body: str) -> None:
        fields: dict[str, str] = {}
        for line in body.splitlines():
            match = re.match(r"^-\s+([^:]+):\s*(.+?)\s*$", line)
            if not match:
                continue
            label = normalize_scalar(match.group(1))
            key = next(
                (
                    candidate
                    for candidate, aliases in BLOCKED_FIELD_ALIASES.items()
                    if label in aliases
                ),
                None,
            )
            if key is None or key in fields:
                continue
            fields[key] = match.group(2).strip()

        missing = sorted(set(BLOCKED_FIELD_ALIASES) - set(fields))
        if missing:
            self.error(
                "blocked_entry_fields",
                path,
                (
                    f"entry {entry_number} missing fields: "
                    + ", ".join(missing)
                ),
            )
            return

        status = normalize_scalar(fields["status"]).strip("`")
        if status not in BLOCKED_STATUS_VALUES:
            self.error(
                "blocked_entry_status",
                path,
                f"entry {entry_number} status must be one of {sorted(BLOCKED_STATUS_VALUES)}",
            )

        if is_placeholder(fields["blocker"]) or is_placeholder(fields["decision"]):
            self.error(
                "blocked_entry_empty",
                path,
                f"entry {entry_number} field blocker/decision must be concrete",
            )

        if not re.search(r"\[[^\]]+\]\([^)]+\)", fields["spec_phase"]):
            self.warn(
                "blocked_entry_spec_link",
                path,
                f"entry {entry_number} Spec / Phase should link to an active or archived plan",
            )

    # --- roadmap ------------------------------------------------------------

    def _check_roadmap(self) -> None:
        path = self.specs / "ROADMAP.md"
        if not path.is_file():
            return
        text = path.read_text(encoding="utf-8")
        structure = strip_fenced_code(text)
        h1 = re.findall(r"^#\s+\S.*$", structure, re.MULTILINE)
        if len(h1) != 1:
            self.error("roadmap_title", path, "expected exactly one non-empty H1 title")
        if find_h2_section(structure, ("版本索引", "Version Index")) is None:
            self.error("roadmap_index", path, "missing Version Index section")

        index = [
            (match.group(2), match.group(1))
            for match in VERSION_INDEX.finditer(structure)
        ]
        headings = [match.group(1) for match in VERSION_HEADING.finditer(structure)]
        if not index:
            self.error("roadmap_index_entries", path, "Version Index has no recognized checkbox entries")
        if [version for version, _ in index] != headings:
            self.error(
                "roadmap_index_mismatch",
                path,
                "Version Index and version headings must match in the same order",
            )
        if headings != sorted(headings, key=version_key):
            self.error("roadmap_version_order", path, "version headings must increase numerically")
        if len(headings) != len(set(headings)):
            self.error("roadmap_duplicate_version", path, "version headings must be unique")

        bodies = {
            match.group(1): find_version_body(structure, match.group(1))
            for match in VERSION_HEADING.finditer(structure)
        }
        for version, mark in index:
            body = bodies.get(version, "")
            completed = mark.lower() == "x"
            self._check_version_section(path, version, body, completed)

    def _check_version_section(
        self, path: Path, version: str, body: str, completed: bool
    ) -> None:
        if find_subsection(body, GOAL_HEADINGS) is None:
            self.error("roadmap_goal", path, f"v{version} is missing Goal")
        acceptance = find_subsection(body, ACCEPTANCE_HEADINGS)
        if acceptance is None:
            self.error("roadmap_acceptance", path, f"v{version} is missing Acceptance")
        else:
            boxes = [m.group(1) for m in TASK_ITEM.finditer(acceptance)]
            if not boxes:
                self.error(
                    "roadmap_acceptance_checkbox",
                    path,
                    f"v{version} Acceptance needs checkboxes",
                )
            elif completed and any(mark.lower() != "x" for mark in boxes):
                self.error(
                    "roadmap_completed_open",
                    path,
                    f"v{version} is marked complete but Acceptance still has open checkboxes",
                )

        deliverables = find_subsection(body, DELIVERABLE_HEADINGS)
        if deliverables is not None:
            boxes = [m.group(1) for m in TASK_ITEM.finditer(deliverables)]
            if not boxes:
                self.warn(
                    "roadmap_deliverables_checkbox",
                    path,
                    f"v{version} Key Deliverables should use checkboxes",
                )
            elif completed and any(mark.lower() != "x" for mark in boxes):
                self.error(
                    "roadmap_completed_open",
                    path,
                    f"v{version} is marked complete but Key Deliverables still has open checkboxes",
                )

        goal = find_subsection(body, GOAL_HEADINGS)
        if goal is not None and not re.search(r"\S", goal.strip()):
            self.error("roadmap_goal_empty", path, f"v{version} goal is empty")

    # --- naming -------------------------------------------------------------

    def _check_named_directories(self) -> None:
        constitution = self.specs / "constitution"
        if constitution.is_dir():
            for path in sorted(constitution.glob("*.md")):
                if not DATED_NAME.match(path.name):
                    self.warn("constitution_name", path, "expected YYYY-MM-DD-<topic>.md")
        research = self.specs / "research"
        if research.is_dir():
            for path in sorted(research.glob("*.md")):
                if not RESEARCH_NAME.match(path.name):
                    self.warn("research_name", path, "expected YYYY-MM-DD-<topic>-research.md")

    # --- active specs -------------------------------------------------------

    def _check_active_specs(self) -> None:
        active = self.specs / "active"
        if not active.is_dir():
            return
        for path in sorted(active.glob("*.md")):
            if not ACTIVE_NAME.match(path.name):
                self.warn("active_name", path, "expected NN-<topic>-plan.md")
            text = path.read_text(encoding="utf-8")
            structure = strip_fenced_code(text)

            if not has_h2(structure, METADATA_HEADINGS):
                self.warn("active_metadata", path, "missing recommended section: Metadata")
            if not has_h2(structure, PHASES_HEADINGS) and not re.search(
                r"^##\s+Phase\s+\d+", structure, re.MULTILINE
            ):
                self.warn("active_phases", path, "missing recommended Phases overview")

            # Prefer top-level User Story + Acceptance (lean). Fall back to Increment Contract.
            user_story = find_h2_section(structure, USER_STORY_HEADINGS)
            acceptance = find_h2_section(structure, ACCEPTANCE_HEADINGS)
            increment = find_h2_section(structure, INCREMENT_CONTRACT_HEADINGS)

            if user_story is None and increment is not None:
                user_story = find_subsection(increment, USER_STORY_HEADINGS)
            if acceptance is None and increment is not None:
                acceptance = find_subsection(increment, ACCEPTANCE_HEADINGS)

            if user_story is None:
                self.error(
                    "active_user_story",
                    path,
                    "Active Spec is missing User Story (top-level or under Increment Contract)",
                )
            elif not re.search(r"\S", user_story.strip()):
                self.error("active_user_story_empty", path, "User Story is empty")
            elif not _looks_like_user_story(user_story):
                self.warn(
                    "active_user_story_shape",
                    path,
                    "User Story should name a role, action, and observable result",
                )

            if acceptance is None:
                self.error(
                    "active_acceptance",
                    path,
                    "Active Spec is missing Acceptance (top-level or under Increment Contract)",
                )
            else:
                boxes = list(TASK_ITEM.finditer(acceptance))
                if not boxes:
                    self.error(
                        "active_acceptance_checkbox",
                        path,
                        "Acceptance needs checkboxes a reviewer can try to fail",
                    )
                else:
                    # Soft check: success / failure language encourages adversarial criteria.
                    joined = acceptance.lower()
                    if not any(
                        token in joined
                        for token in (
                            "success",
                            "smoke",
                            "失败",
                            "failure",
                            "回归",
                            "regression",
                            "验收",
                        )
                    ):
                        self.warn(
                            "active_acceptance_adversarial",
                            path,
                            "Acceptance should include success smoke and expected failure",
                        )

            self._check_spec_lifecycle(path, text, in_active=True)

    def _check_spec_lifecycle(self, path: Path, text: str, *, in_active: bool) -> None:
        status_match = STATUS_ROW.search(text)
        completed_match = COMPLETED_ROW.search(text)
        status = normalize_scalar(status_match.group(1)) if status_match else ""
        completed = normalize_scalar(completed_match.group(1)) if completed_match else ""

        if in_active and status in {"completed", "cancelled", "已完成", "已取消"}:
            self.warn(
                "active_terminal_status",
                path,
                "terminal status in active/; move to archive/ after recording completion",
            )
        if status in {"completed", "已完成"} and completed in {"", "pending", "待定"}:
            self.warn(
                "completed_without_date",
                path,
                "completed status should record a completion date",
            )

    # --- archive ------------------------------------------------------------

    def _check_archived_artifacts(self) -> None:
        archive = self.specs / "archive"
        if not archive.is_dir():
            return
        for path in sorted(archive.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            if ARCHIVE_STATUS.search(text) is None:
                self.error(
                    "archive_status",
                    path,
                    "archived artifact needs > Status: completed|cancelled (YYYY-MM-DD)",
                )
            if ARCHIVE_REASON.search(text) is None:
                self.warn(
                    "archive_reason",
                    path,
                    "archived artifact should include > Archive reason: …",
                )

    # --- links --------------------------------------------------------------

    def _check_links(self) -> None:
        repository = self.specs.parent
        roots = [self.specs]
        for extra in (repository / "AGENTS.md", repository / "ARCHITECTURE.md"):
            if extra.is_file():
                roots.append(extra)

        md_files: list[Path] = []
        for root in roots:
            if root.is_file():
                md_files.append(root)
            elif root.is_dir():
                md_files.extend(sorted(root.rglob("*.md")))

        link_re = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
        for path in md_files:
            text = path.read_text(encoding="utf-8")
            for match in link_re.finditer(strip_fenced_code(text)):
                target = match.group(1).strip()
                if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                if " " in target and not target.startswith("<"):
                    # title-bearing links: take URL part
                    target = target.split()[0]
                target = unquote(target.strip("<>"))
                href, _, fragment = target.partition("#")
                if not href:
                    continue
                if href.startswith("/"):
                    self.warn(
                        "absolute_link",
                        path,
                        f"prefer repository-relative links: {href}",
                    )
                    continue
                resolved = (path.parent / href).resolve()
                try:
                    resolved.relative_to(repository.resolve())
                except ValueError:
                    self.warn("link_outside_repo", path, f"link leaves repository: {href}")
                    continue
                if not resolved.exists():
                    self.error("broken_link", path, f"broken relative link: {href}")
                    continue
                if fragment and resolved.is_file() and resolved.suffix.lower() == ".md":
                    anchors = markdown_heading_anchors(resolved.read_text(encoding="utf-8"))
                    if slugify_fragment(fragment) not in anchors:
                        self.warn(
                            "broken_heading_fragment",
                            path,
                            f"missing heading fragment: {target}",
                        )


# --- helpers ----------------------------------------------------------------

def strip_fenced_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def has_h2(text: str, names: tuple[str, ...]) -> bool:
    return find_h2_section(text, names) is not None


def find_h2_section(text: str, names: tuple[str, ...]) -> str | None:
    start = find_h2_heading_start(text, names)
    if start is None:
        return None
    match = re.match(r"^##\s+.+$", text[start:], re.MULTILINE)
    if match is None:
        return None
    body_start = start + match.end()
    next_heading = re.search(r"^##\s+", text[body_start:], re.MULTILINE)
    end = body_start + next_heading.start() if next_heading else len(text)
    return text[body_start:end]


def find_h2_heading_start(text: str, names: tuple[str, ...]) -> int | None:
    for name in names:
        match = re.search(rf"^##\s+{re.escape(name)}\s*$", text, re.MULTILINE | re.IGNORECASE)
        if match is not None:
            return match.start()
    return None


def find_subsection(text: str, names: tuple[str, ...]) -> str | None:
    for name in names:
        match = re.search(rf"^###\s+{re.escape(name)}\s*$", text, re.MULTILINE | re.IGNORECASE)
        if match is None:
            continue
        body_start = match.end()
        next_heading = re.search(r"^###\s+", text[body_start:], re.MULTILINE)
        end = body_start + next_heading.start() if next_heading else len(text)
        return text[body_start:end]
    return None


def find_version_body(text: str, version: str) -> str:
    match = re.search(rf"^##\s+v{re.escape(version)}\b.*$", text, re.MULTILINE)
    if match is None:
        return ""
    body_start = match.end()
    next_heading = re.search(r"^##\s+", text[body_start:], re.MULTILINE)
    end = body_start + next_heading.start() if next_heading else len(text)
    return text[body_start:end]


def split_h2_sections(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group(1), text[start:end]))
    return sections


def version_key(version: str) -> tuple[int, int]:
    major, minor = version.split(".")
    return int(major), int(minor)


def normalize_scalar(value: str) -> str:
    text = value.strip()
    text = re.sub(r"^[`'\"]+|[`'\"]+$", "", text)
    return re.sub(r"\s+", " ", text).casefold()


def is_placeholder(value: str) -> bool:
    text = normalize_scalar(value)
    if not text:
        return True
    return text in {"tbd", "todo", "…", "...", "<...>", "pending", "待定", "无"}


def _has_timezone(timestamp: str) -> bool:
    return bool(re.search(r"(Z|[+-]\d{2}:\d{2})$", timestamp))


def _looks_like_user_story(body: str) -> bool:
    text = body.strip()
    # EN: As a … I can/want … so that …
    if re.search(r"as a\b", text, re.IGNORECASE) and re.search(
        r"\b(i can|i want|so that)\b", text, re.IGNORECASE
    ):
        return True
    # ZH common patterns
    if re.search(r"(作为|作为一名|我希望|以便|从而)", text):
        return True
    # Fallback: non-trivial multi-word statement
    return len(re.findall(r"\S+", text)) >= 6


def has_md_link_to(text: str, target_suffix: str) -> bool:
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        href = match.group(1).strip().split()[0].strip("<>")
        href = unquote(href.partition("#")[0])
        if href == target_suffix or href.endswith("/" + target_suffix.lstrip("./")):
            return True
        if Path(href).name == Path(target_suffix).name and target_suffix in href:
            return True
    return False


def markdown_heading_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    for raw_heading in re.findall(
        r"^#{1,6}[ \t]+(.+?)\s*#*\s*$", strip_fenced_code(text), re.MULTILINE
    ):
        plain = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", raw_heading)
        plain = re.sub(r"[`*_~]", "", plain).strip()
        anchors.add(slugify_fragment(plain))
    return anchors


def slugify_fragment(text: str) -> str:
    value = unquote(text).strip().strip("#").casefold()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^\w\- \u4e00-\u9fff]", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "-", value)
    return value


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        type=Path,
        help="Repository root or specs/ directory",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON",
    )
    return parser.parse_args(argv)


def resolve_specs(path: Path) -> Path:
    path = path.resolve()
    if path.name == "specs" and path.is_dir():
        return path
    specs = path / "specs"
    if specs.is_dir():
        return specs
    if path.is_dir() and (path / "AGENTS.md").is_file():
        # Allow validating a bare specs directory that was passed indirectly.
        return path
    raise SystemExit(f"could not find specs/ under {path}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        specs = resolve_specs(args.path)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 2

    issues = Validator(specs).run()
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]

    if args.json:
        print(
            json.dumps(
                {
                    "specs": str(specs),
                    "ok": not errors and not (args.strict and warnings),
                    "errors": [asdict(i) for i in errors],
                    "warnings": [asdict(i) for i in warnings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for issue in issues:
            print(f"{issue.severity.upper()}: {issue.path}: {issue.message} [{issue.code}]")
        print(
            f"summary: {len(errors)} error(s), {len(warnings)} warning(s) — specs={specs}"
        )

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
