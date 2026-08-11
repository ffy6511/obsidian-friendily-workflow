# Templates

Write the **shortest** document that still supports adversarial review. Prefer checkboxes
and exact commands over prose. Skip sections that do not apply — do not leave empty stubs.

Heading names may be English or the Chinese equivalents recognized by the validator
(listed beside each required block).

---

## Active Spec (`specs/active/NN-<topic>-plan.md`)

**Required for implementation Specs:** Metadata, User Story, Acceptance, Phases overview.
Everything else is optional.

```markdown
# <Title>

## Metadata

| Field        | Value           |
| ------------ | --------------- |
| Created      | YYYY-MM-DD      |
| Status       | in-progress     |
| Completed    | pending         |
| Dependencies | none            |
| Decisions    | <links or none> |

## User Story

As a <role>, I can <action through the public entrypoint>, so that <observable result>.

## Acceptance

Adversarial: a reviewer runs only these items to pass/fail the Spec.

- [ ] **Success smoke:** `<exact command / API / UI path>` → `<observable result>`
- [ ] **Expected failure:** `<exact path>` → `<clear, non-destructive failure>`
- [ ] **Regression:** `<prior core smokes still pass; none only for greenfield MVP>`
- [ ] **Baseline:** starts from `<existing entrypoint + smoke; none for greenfield>`
- [ ] **Engineering gates:** format / lint / type / focused tests / project gate as applicable
- [ ] **Docs:** README / Architecture updated only if entrypoint or structure changed

## Scope

- Included: <minimum vertical behavior>
- Deferred: <named version / research / follow-up Spec — or "none">

## Phases

- [ ] Phase 0: <smallest useful step>
- [ ] Phase 1: <…>

## Phase 0: <name>

### Tasks

- [ ] …

### Files

- `path/…`

### Done when

- [ ] Focused validation for this Phase passes
- [ ] Phase committed (or message drafted if user forbade commit)
```

### Optional sections (add only when useful)

| Section           | When                                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------------- |
| Background        | Non-obvious problem / current behavior                                                               |
| Design            | Non-obvious control/data flow, schema, or interface delta — link Constitution first                  |
| Prerequisites     | External image/network/credential must be provisioned; name owner + verify command                   |
| User Acceptance   | Explicit human / external UAT gate                                                                   |
| Completion Check  | After executor smokes: default end subagent notes (verdict, findings, fixes) — not mid-flight Critic |
| Evaluation Record | Only if mid-flight `Independent review: required`                                                    |

### Writing rules

- One Spec = one vertical increment. Not “finish the database module.”
- User Story names a **real role**, **public action**, **observable result**.
- Acceptance uses **exact** commands/paths a stranger can run. No “works correctly.”
- Phases stay small; temporary public-path gaps are OK mid-Spec, not at completion.
- On execute: **one Phase → one commit facet** (`$staged-commit-message`); after all
  Phases/smokes, **default completion subagent** on Acceptance + in-scope code quality,
  then fix blocking feedback before `completed`.
- List repository-relative files. Map risky branches to a Phase checkbox or test.
- Greenfield Spec 00: skeleton gate + first public MVP journey in the same Spec.

---

## Roadmap (`specs/ROADMAP.md`)

Organize by version numbers, not “current / next / future” buckets.

```markdown
# <Project> Roadmap

## Version Index

- [ ] `v0.1` — <one-line user outcome>
- [ ] `v0.2` — <…>

## v0.1 — <name>

### Goal

<One sentence user/operator capability.>

### Key Deliverables

- [ ] <observable outcome, not a file list>

### Acceptance

- [ ] <new public success journey>
- [ ] <one expected failure>
- [ ] <prior journeys still pass when applicable>
- [ ] <engineering gates / docs sync when relevant>

### Follow-up TODO

- [ ] `v0.2`: <deferred adjacent work with a named owner>
```

Chinese aliases recognized: `目标` / `关键交付` / `验收标准` or `螺旋验收` / `后续 TODO`.

Rules:

- First greenfield version = skeleton + runnable MVP.
- Later versions deepen/widen/harden a **runnable** product — never “contracts → DB → CLI.”
- Mark version complete only when Version Index `[x]` and all required checkboxes are `[x]`.
- Every deferred item names exactly one destination (version, Research, or Spec).

Optional under a version: `Starting Runnable Baseline` / `Evolution Slice` when the spiral
jump needs an explicit baseline. Prefer Acceptance bullets when that is enough.

---

## Constitution (`specs/constitution/YYYY-MM-DD-<topic>.md`)

```markdown
# <Decision title>

## Metadata

| Field         | Value           |
| ------------- | --------------- |
| Decision date | YYYY-MM-DD      |
| Related specs | <links or none> |

## Decision

<Final choice in a few sentences.>

## Invariants

- <rules later Specs must preserve>

## Alternatives considered

- <option>: <why rejected>   <!-- optional but useful -->

## History

| Date       | Change  | Reason |
| ---------- | ------- | ------ |
| YYYY-MM-DD | Initial | …      |
```

No Phase lists, no temporary experiments. Update History when the decision changes.

---

## Research (`specs/research/YYYY-MM-DD-<topic>-research.md`)

```markdown
# <Title>

## Metadata

| Field   | Value      |
| ------- | ---------- |
| Created | YYYY-MM-DD |
| Status  | open       |

## Question

<What must be answered, and what “done” looks like.>

## Findings

- <evidence + interpretation>

## Recommendation

<Action + destination: Constitution / Roadmap version / Active Spec / drop.>

## Open Questions

- <remaining unknowns>
```

Research recommends; it does not silently become law.

---

## BLOCKED entry

Insert under the marker in `specs/BLOCKED.md`:

```markdown
## 2026-07-28T14:30:00+08:00 — <short title>

- Status: `resolved-autonomously`
- Spec / Phase: [Spec 01 Phase 0](active/01-example-plan.md)
- Blocker: <unexpected decision point>
- Decision: <chosen path>
- Rationale: <why safest in-scope option>
- Impact / follow-up: <effect; authority file updated if any>
```

---

## Archive marker

At top of archived body (or immediately after title):

```markdown
> Status: completed (YYYY-MM-DD)
> Archive reason: acceptance passed
```

Update every inbound link to the new `archive/` path in the same change.

---

## Shared writing rules

- Lead with the decision / story / result.
- Fenced code blocks for examples (not four-space indents — conflict with task lists).
- Repository-relative paths.
- Link existing authority; do not paste it.
- Prefer actors, inputs, outputs, failure modes over slogans.
- Match project language (中文项目写中文).
