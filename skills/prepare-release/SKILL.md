---
name: prepare-release
description: >
  Prepare a software package release: check/update project version, draft bilingual
  (zh then en) release notes from git history since the last package release, and only
  perform tag/publish/PR steps when the user explicitly asks to ship. Use when the user
  mentions release notes, changelog, 发版, 发布, release note, vX.Y.Z package version,
  GitHub Release, tag a release, or `$prepare-release`. Default is draft-only—never
  tag, push, or create GitHub releases unless the user says 直接发版 / ship / publish.
---

# Prepare Release

Default: **draft release notes only**.  
Ship (version commit / tag / GitHub Release / PR merge) only when the user explicitly asks.

Never invent commits or features. Prefer git history; open code only when a subject is unclear.

## Modes

| Mode | When | Deliverable |
| --- | --- | --- |
| **Draft** (default) | 写 release note / 准备发版 / review notes | Notes in chat (or user-named file); **no** tag/push/publish |
| **Ship** | User says 直接发版 / ship / publish / 打 tag 并发布 | After notes approved (or user skips review): version bump if needed → tag → remote actions only as user directed |

If unclear → **Draft only**.

## Version authority (do this first)

1. **Resolve target package version**
   - Prefer the version the user named (e.g. `v0.1.0` / `0.1.0`).
   - Else infer from conversation; if still missing, ask once.
   - Use `vX.Y.Z` for **Release/tag titles** and chat; version files omit the `v` prefix. Note **body** does not open with a version heading (title already has it).

2. **Find the package version source(s)** (first match that exists, update all that must stay in sync):
   - Prefer a single root `VERSION` (or hatch/dynamic version path) when the repo already uses one
   - Else: `pyproject.toml` / `Cargo.toml` / `package.json` / `src/**/__init__.py` `__version__`
   - Multi-package monorepos: if the user or repo treats packages as co-versioned (same release tag), bump **all** of those sources together—do not leave SDK/path deps drifting. Prefer one `VERSION` file (siblings may symlink to it) over hand-editing multiple numbers.

3. **Identify the last *package* release baseline**
   - Prefer GitHub Releases and tags that match the project’s release pattern (`v1.2.3`, `release-1.2.3`, etc.).
   - If several tag styles coexist, use the one that tracks published package versions—or ask once when ambiguous.
   - No prior package release → base notes on the initial commit (or a user-specified ref).

4. **Version gate (required before claiming “ready to ship”)**
   - If project version **≠** target: **declare it** first in the reply (paths + current → target). In Draft mode, do **not** edit version files unless the user asked to bump.
   - If already equal: state “version already at X.Y.Z”.
   - Ship mode: bump version files (and lockfiles if the project requires it) in a dedicated version commit before tagging, unless already correct.

## Baseline: “since last release”

Resolve the git range for notes:

```text
BASE = previous package release tag / GitHub Release / user-given ref
       else initial commit (first package release)
HEAD = current branch tip (usually the branch that will merge to the release branch)
```

Commands:

```bash
git tag -l --sort=-v:refname
git describe --tags --abbrev=0 2>/dev/null   # confirm it is a package release tag
git log --no-merges --pretty=format:'%h %s%n%b' BASE..HEAD
git log --no-merges --oneline BASE..HEAD
```

Optional when subjects are vague:

```bash
git show --stat <sha>
git log -p -1 <sha> -- <paths>   # narrow; do not dump whole trees
```

Include only **user-visible** or **operator-visible** change. Drop pure chore noise unless it affects install/run (deps, entrypoints, breaking CLI).

## Draft notes (always in Draft; also produce before Ship)

1. Read **all** commits in `BASE..HEAD` (subjects first; bodies next).
2. Cluster by intent → Conventional categories: `Feat` / `Fix` / `Refactor` / `Perf` / `Docs` / `Test` / `Build` / `CI` / `Chore` (omit empty categories).
3. **Match historical release-note voice (default when history exists)**  
   Load the latest prior package notes if any exist: GitHub Release body for the previous tag, `CHANGELOG*`, `RELEASE_NOTES*`, `docs/releases/*`, or repo-local `tmp/RELEASE_NOTES*` only when that is clearly the approved draft for this ship.  
   Align register, density, heading/bullet shape, and bilingual layout with that history. The format guide is a **fallback** when there is no prior package note (first release) or history is unusable.
4. Write **two modules**: **中文 first**, then **English**. Same structure and coverage; do not leave one language thinner without reason.
5. **Body opening**: start with the Chinese summary paragraph—**no** `# Project vX.Y.Z` / version H1, **no** leading `## 中文`. After the Chinese categories, use `## English` then the English summary. Put the product+version only on the GitHub Release / tag title when shipping.
6. Format baseline: see [references/note-format.md](references/note-format.md)—defer to step 3 when history conflicts with the guide (except body-opening rules above, which always apply).

Output default: paste the full note in the reply for human review.  
Only write a file (e.g. `RELEASE_NOTES.md`, `CHANGELOG` fragment) if the user asks.

## Ship mode (explicit only)

When the user clearly asks to ship:

1. Confirm target version + base ref + remote actions (tag only? GitHub Release? PR `dev`→`main`?).
2. Ensure version files match target; commit if needed (prefer `$staged-commit-message` conventions).
3. Create annotated tag `vX.Y.Z` on the agreed commit **only if** user approved tagging.
4. Push / open PR **only** with explicit user approval for each externally visible step.
5. Publish GitHub Release with **custom body + auto “What’s Changed”** (see below)—default when creating or updating a Release.
6. Do **not** force-push, rewrite published tags, or delete releases without explicit order.

Stop and report if working tree is dirty with unrelated work, or if HEAD is not the intended release tip.

### GitHub auto notes (append “What’s Changed”)

GitHub can generate the PR-based trailer (What’s Changed / New Contributors / Full Changelog). **Default after the hand-written note is ready: always attach it to the end of the Release body.** Do not hand-write that trailer.

**Create** (custom body first, auto block appended by `gh`):

```bash
gh release create "vX.Y.Z" \
  --title "Product vX.Y.Z" \
  --notes-file path/to/body.md \
  --generate-notes \
  --verify-tag
```

`--notes` / `--notes-file` is **prepended** to the API-generated notes when combined with `--generate-notes`.

Optional: `--notes-start-tag vA.B.C` when the auto range should start after a specific previous package tag (not an unrelated milestone tag).

**Preview / edit existing Release** (compose yourself, then write):

```bash
# 1) Auto block only
gh api --method POST "repos/OWNER/REPO/releases/generate-notes" \
  -f tag_name="vX.Y.Z" \
  -f previous_tag_name="vA.B.C"   # optional
# → JSON field .body  (## What's Changed / New Contributors / Full Changelog)

# 2) Combine: custom_body + "\n\n" + generate-notes body
# 3) Create or update:
gh release create "vX.Y.Z" --title "…" --notes-file combined.md --verify-tag
gh release edit  "vX.Y.Z" --notes-file combined.md
```

Rules:

- Hand-written body stays free of version H1 and leading `## 中文` (see note-format).
- If the body **already** contains `## What's Changed`, do not append a second copy; regenerate and replace the trailer only when refreshing.
- After any substantive edit to the published note, **re-run generate-notes and re-attach** (or `release edit`) so the trailer stays present and current.
- Auto notes are PR-oriented; they do not replace the bilingual product summary—they sit **after** it.

## Quality rules

- Accuracy over marketing tone; no “completely rewritten” fluff.
- One bullet = one change cluster, not one file.
- Prefer product/operator language (what changed for users) over internal ticket or process noise; ids only as optional secondary detail.
- Do not overclaim readiness, security, or compatibility beyond what commits and project docs support.
- Match user’s language for the surrounding reply; notes themselves are always **zh then en**.
- No secrets, tokens, or host paths in notes.

## Tiny example (structure only)

Release title (outside body): `BORA v0.1.0`

```markdown
本版本首次打包公开入口……（正文第一段直接是中文 summary）

### Feat

- **配置锁定**: 提供 `bora lock` 生成可复现摘要。基于 Config Core 的 load_and_lock。
- **单次运行**: 提供 `bora run` 前台 Attempt 竖切。含独立 evaluator 与 fail-closed 离线路径。

### Fix

- **进程清理**: 修复 writer-stop 确认与 residual 进程组清理。避免 Attempt 结束后残留子进程。

## English

First packaged public surface… (one summary paragraph)

### Feat

- **Config lock**: Ship `bora lock` for a reproducible package digest. Backed by Config Core load_and_lock.
- **Single run**: Ship `bora run` for a foreground Attempt slice. Independent evaluator and offline fail-closed path.

### Fix

- **Process cleanup**: Fix writer-stop confirmation and residual process-group teardown. Prevents leftover children after an Attempt.
```
