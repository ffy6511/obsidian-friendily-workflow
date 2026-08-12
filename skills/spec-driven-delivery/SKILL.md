---
name: spec-driven-delivery
description: >
  Spec-Driven Development for fast delivery: keep the product runnable, write short
  Specs with clear user stories and adversarial acceptance criteria, ship vertical
  increments. When implementing a Spec: commit each Phase during work (see
  staged-commit-message), keep mid-flight adversarial review off, and after the Spec
  work finishes run a completion subagent that checks acceptance + code quality and
  require fixes. Use when bootstrapping specs/, drafting or implementing an Active
  Spec, updating ROADMAP/ARCHITECTURE, auditing a specs workspace, completing or
  archiving a Spec, or validating workspace structure.
---

# Spec Driven Delivery

## Goal

Keep the product **runnable** while it evolves. Each Spec ships **one** user-verifiable
vertical increment from a known baseline — not a module layer, not a documentation dump.

## Core principles

These are non-negotiable. Everything else is optional scaffolding.

1. **Story + acceptance + approach.** Every implementation Spec needs (a) a concrete user
   story, (b) adversarial acceptance criteria, and (c) a **minimum implementation approach**
   (control flow, data flow, key interfaces, or short pseudocode for the changed path). Story
   and acceptance alone are not enough to implement. If Constitution / `docs/` / Architecture
   already spell the approach, **link the exact heading** and state only the local delta—do not
   paste essays.
2. **Vertical slice, not modules.** Roadmap and Specs are ordered by runnable user
   outcomes. Schema, adapters, and hardening live inside the thinnest slice that needs
   them.
3. **Spec = delivery unit.** Phases are small implementation steps. The Spec as a whole
   must end with the public path and affected prior smokes passing.
4. **Real entrypoint evidence.** Do not claim done from unit tests, test-only composition,
   or internal service calls. Use the real user-facing entrypoint and production wiring.
5. **Greenfield = skeleton + MVP together.** First Spec builds minimum maintainable
   project gate **and** one real public journey. No separate “foundation” Specs first.
6. **Short docs, link authority.** Prefer a tight Spec over essays. Stable decisions go
   to Constitution; structure to `ARCHITECTURE.md`; unresolved questions to Research.
7. **Phase boundary = commit boundary (default on execute).** When this skill drives
   Spec implementation, finish one Phase → commit that facet → next Phase. Do not pile
   the whole Spec into one end-of-epic commit.

## Workspace shape

```text
repository/
├── AGENTS.md
├── ARCHITECTURE.md
├── docs/                 # optional
└── specs/
    ├── AGENTS.md
    ├── BLOCKED.md        # required; create from assets/BLOCKED.md
    ├── ROADMAP.md        # optional but recommended
    ├── constitution/      # optional
    ├── research/         # optional
    ├── active/
    └── archive/          # optional until first archive
```

`specs/AGENTS.md` stays thin: authority order, local invariants, validation commands,
and a pointer to this skill. Templates and checklists live here, not in the project file.

## Artifact map

| Write…       | When…                                                | Owns                                                      |
| ------------ | ---------------------------------------------------- | --------------------------------------------------------- |
| Architecture | Structure / ownership / dependency direction changes | Current vs target layout, composition root, runnable path |
| Roadmap      | Version outcomes need tracking                       | Successive runnable user outcomes + acceptance checkboxes |
| Constitution | A long-lived decision or invariant changes           | Decision, invariants, short history                       |
| Research     | Something is still unknown                           | Question, evidence, recommendation — not silent authority |
| Active Spec  | Ready to implement one increment                     | User story, acceptance, approach, phases, evidence        |
| BLOCKED      | Unanticipated choice during execution                | Newest-first audit entry; does not override Specs         |
| Archive      | Spec completed or cancelled                          | Historical record with status marker                      |

Details and minimal templates: `references/templates.md`.  
Init / authority / lifecycle: `references/workspace.md`.

## Workflow

1. **Orient** — Read root → `ARCHITECTURE.md` → `specs/AGENTS.md` → relevant active Specs.
   Preserve unrelated git work; do not widen scope.
2. **Baseline** — Name the current public entrypoint, smoke, and observable result. Run it
   when possible. Restore a broken baseline before expanding.
3. **Classify** — Architecture / Roadmap / Constitution / Research / Active Spec / skip.
4. **Plan short** — For an Active Spec, write **User Story**, **Acceptance**, and
   **Approach** (or exact links + local delta) before Phases. One story, bounded scope,
   runnable acceptance, and enough implementation direction to code without inventing the design.
5. **Implement only when asked** — Small Phases; focused validation per Phase. Do not inflate
   a Phase into a mini-Spec. **Default: commit after each Phase** (see below). Mid-flight
   adversarial subagent review stays **off**.
6. **Executor complete** — Public success smoke, expected failure, affected prior smokes,
   project gates, Spec checkbox/status sync (do not archive as final until step 7 passes
   or findings are fixed).
7. **Completion check (default on)** — Spawn one read-only-leaning subagent to audit this
   Spec’s scope (acceptance + code quality). Fix required findings; re-check if material.
8. **Close** — Archive / Roadmap / inbound links when acceptance and completion check are
   satisfied. Run the workspace validator if structure or Spec shape changed.

## Active Spec minimum

Every implementation Spec must cover **what**, **how we'll know**, and **how we'll build**:

```text
User Story:  As a <role>, I can <action via public entrypoint>, so that <observable result>.
Acceptance:  exact success smoke · exact expected failure · affected regressions · evidence
Approach:    control/data flow, key types/interfaces, or short pseudocode for the changed path
             — OR exact links to Constitution/docs/Architecture that already define that path
             + a local delta (what this Spec alone adds or changes)
Scope:       included vertical minimum · deferred with a named owner (version / research / Spec)
```

- **Acceptance (adversarial):** a reviewer runs only Acceptance items to pass/fail the Spec.
- **Approach (implementable):** an executor can implement without inventing core control flow,
  data shape, or composition. Prefer diagrams/pseudocode over long prose. Prefer **link + delta**
  when a decision doc already has detail; never leave Approach empty.

Prefer the lean template in `references/templates.md`. Skip Decision Summary tables,
six-column prerequisite audits, and mid-flight Evaluation Records unless the project or
user asks.

## Execution defaults

### Phase commits (default **on** when implementing)

When this skill is used to **execute** an Active Spec (not mere planning):

1. Implement **one Phase** (one intentional facet: e.g. domain, adapter, CLI, tests for that
   slice).
2. Run focused validation for that Phase.
3. Stage **only** that Phase’s paths — never blind `git add .`.
4. Write a Conventional Commit message from the staged diff + recent log style, following
   `$staged-commit-message` (phase-during-work): `type(scope): subject` + short body bullets.
5. `git commit` locally. Do **not** amend / rebase / push unless the user asks.
6. Then start the next Phase on a clean tree (unrelated dirt left intentional).

Do **not** implement all Phases first and invent retrospective commits at the end. If the
user says “don’t commit” / draft-only, draft messages at each Phase boundary instead of
committing. Spec / docs updates that belong with a Phase go in that Phase’s commit (or an
immediate `docs` commit after it).

### Mid-flight adversarial review (default **off**)

Do **not** spawn independent Critic / adversarial subagents between Phases unless the user
or repository explicitly requires it (`Independent review: required`, or a direct ask).

### Completion check subagent (default **on** after Spec work)

After the Executor believes the Spec’s Phases and acceptance smokes are done — and **before**
treating the Spec as fully closed — **default: start one subagent** scoped to this Spec:

| Focus        | What to verify                                                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Acceptance   | Each Acceptance checkbox: success smoke, expected failure, regressions, gates — with evidence in-scope                                     |
| Code quality | Diff / paths owned by this Spec: correctness, tests, obvious bugs, unsafe shortcuts, missing error paths, docs drift vs claimed entrypoint |
| Scope        | Stay inside this Spec’s story and files; do not expand into unrelated refactors                                                            |

Subagent output: short pass / fail, checklist against Acceptance items, ranked findings
(blocking vs follow-up). **Executor must act on feedback:**

- **Blocking** (acceptance fail, broken smoke, security/data-loss, clear defect in-scope) →
  fix, re-run affected smokes, phase-commit the fix if non-trivial, re-run the check if the
  change was material.
- **Non-blocking polish** → fix now if cheap; else record a named follow-up (version /
  Research / Spec) and do not claim it done.
- Cap at **two** fix rounds unless the user asks for more. Then summarize residual risks.

Skip the completion subagent only if the user says so, or the change is docs-only with no
code/acceptance path. Mid-flight review remaining off does **not** cancel this end check.

### Other execution defaults

- Prefer completing an authorized Spec. On an unanticipated **safe, reversible, in-scope**
  choice: pick the safest path, prepend a short `BLOCKED.md` entry, continue.
- Pause only for missing authority, material irreversible risk, or product/security
  semantic change.
- Missing production mechanism (image, network, credential binding with no owner) → Research
  or amend the Spec; do not claim implementation-ready.
- Multiple Active Specs may coexist when each has its own acceptance and dependencies.

## Validation

```bash
PY="${PY:-python3}"
SKILL_DIR="<path-to-installed-spec-driven-delivery>"
"$PY" "$SKILL_DIR/scripts/validate_specs_workspace.py" <repository-or-specs-path>
```

`--strict` treats warnings as failure (use for init / CI). `--json` for machine output.

The validator is a **structure** check, not a substitute for running smokes and project gates.

## Guardrails

- Repository-relative paths only in tracked docs.
- Never mark Spec `completed` / version done with open required acceptance checkboxes.
- Do not declare Spec execution finished while default completion-check findings that
  block acceptance remain open (unless the user waived the check).
- Never present planned architecture as current code.
- Do not invent module-completion Roadmaps (contracts → DB → runtime → CLI).
- Deferred work needs one named owner; no orphan “later” piles.
- `docs/` is reference, not decision authority — bind lasting rules in Constitution.
- Match the user's language when writing project docs.
- No force-push, history rewrite, or remote publish unless the user explicitly asks.
