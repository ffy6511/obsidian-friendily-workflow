# Workspace

## Authority

```text
Constitution          stable decisions / invariants
  → docs/ (optional)  product specs & contracts (reference only)
  → ARCHITECTURE.md   structure, ownership, dependency direction
  → ROADMAP.md        version outcomes
  → Active Spec       one implementable increment
  → code + smoke evidence
```

Research feeds Constitution / Roadmap / Spec after the question is resolved.  
`BLOCKED.md` is an audit log under the chain — it never overrides higher authority.  
Archive is history only.

When sources disagree: stop, fix the highest-authority source first, then sync downstream
in one coherent change.

## Required paths

Initialized workspace:

```text
AGENTS.md
ARCHITECTURE.md
specs/AGENTS.md
specs/BLOCKED.md    # from assets/BLOCKED.md
specs/active/
```

Root `AGENTS.md` and `specs/AGENTS.md` each need a repository-relative Markdown link to
`ARCHITECTURE.md` / `../ARCHITECTURE.md`.

Optional: `specs/ROADMAP.md`, `constitution/`, `research/`, `archive/`, root `docs/`.

## ARCHITECTURE.md (short)

Keep it a map, not a PRD or Phase list. Minimum sections (EN or 中文 equivalents):

```markdown
# <Project> Architecture

## Document Status

## System Overview

## Runnable System Path

## Source Layout

## Dependency Direction

## Change Ownership
```

| Section              | Content                                                               |
| -------------------- | --------------------------------------------------------------------- |
| Document Status      | Implemented vs planned; evidence level                                |
| System Overview      | Major parts and validated-output flow                                 |
| Runnable System Path | Public entrypoint → composition root → observable result + smoke link |
| Source Layout        | Current tree; target only if clearly marked                           |
| Dependency Direction | Allowed / forbidden edges; composition root                           |
| Change Ownership     | What kind of change updates Architecture / Constitution / Spec        |

Mark current vs target explicitly. Never claim “implemented” from Specs or fixtures alone.

## specs/AGENTS.md (thin)

Keep only:

1. Directory map + authority order
2. Required reading sequence
3. Project-specific invariants / forbidden actions
4. Naming + lifecycle status words
5. Sync surfaces + validation commands
6. Pointer to `$spec-driven-delivery`

Do not paste templates or long SDD essays here.

## Lifecycle

```text
Research:    open → concluded → superseded / archive
Active Spec: in-progress → completed / archive
                        ↘ cancelled / archive
Roadmap:     [ ] → [x] when deliverables + acceptance all pass
```

Optional status `review` only while an **explicit** human / external gate remains open
after implementation smokes already pass.

Complete sequence (implementation Specs): all Phases done with **per-Phase commits** →
acceptance smokes pass → **default completion subagent** (acceptance + in-scope code
quality) → fix blocking findings → set `completed` + date → `archive/` → fix inbound
links. Mid-flight adversarial subagents stay off unless explicitly required.

Archive marker:

```markdown
> Status: completed (YYYY-MM-DD)
> Archive reason: <short reason>
```

(or `cancelled`)

## BLOCKED.md

Newest-first execution exceptions only. Create from `assets/BLOCKED.md`. Insert each entry
immediately under `<!-- BLOCKED_ENTRIES_START -->`.

Statuses: `resolved-autonomously` | `awaiting-user` | `resolved-by-user`.

Do not log routine TODOs, expected failures, or secret values. If a decision changes a
Spec/Constitution/Architecture/Roadmap claim, update that artifact in the same change.

## Init checklist

1. Read existing instructions, layout, ADRs before inventing parallel trees.
2. Create/normalize `ARCHITECTURE.md` (current vs target, runnable path).
3. Ensure root + `specs/AGENTS.md` link to Architecture.
4. Create `specs/AGENTS.md`, `specs/BLOCKED.md`, `specs/active/`.
5. Add `ROADMAP.md` only if version tracking is useful; first version = MVP.
6. Optional Constitution / Research only when ownership is real.
7. Run validator `--strict` + project gates.

Init is **planning**. Implement the first public journey only when requested.

## Optional `docs/`

Create only when the project has stable PRD / API contracts / DESIGN deeper than
Architecture. Rules:

1. Structural truth stays in `ARCHITECTURE.md`.
2. Binding long-term rules are mirrored into Constitution.
3. Specs link exact headings; they do not copy pages.

## Sync (minimum)

| Change                                 | Also update                                                  |
| -------------------------------------- | ------------------------------------------------------------ |
| Ownership / dependency / runnable path | Architecture, README if entrypoint changes                   |
| Stable product/tech boundary           | Constitution, then docs if present                           |
| Version outcome                        | Roadmap checkboxes                                           |
| Spec complete / cancel                 | Status, archive path, inbound links, Roadmap if criteria met |
| User-visible behavior                  | README / docs / site as the project uses them                |
