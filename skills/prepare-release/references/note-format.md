# Release note format

Default when the repo already has package release notes: **copy that voice first** (density, bold lead phrases, bilingual layout, what they omit). This file is the fallback skeleton for a first release or when history is missing/unusable.

Two modules in order: **English**, then **中文**. Same facts; natural phrasing per language.

## Body vs Release title

- GitHub Release / tag **title** already carries the product + version (e.g. `BORA v0.1.0`).
- Note **body** must **not** repeat a top-level version heading (`# BORA v0.1.0`, `# v0.1.0`, etc.).
- Note **body** must **not** open with a language label (`## English`, `## 中文`, `## Chinese`, …). English starts at the first summary paragraph.

## Module skeleton

```markdown
<one English summary paragraph — first line of the body, no heading above it>

### Feat

- **<short phrase>**: <one or two sentences>. <optional implementation or other detail>
- **<short phrase>**: <one or two sentences>.

### Fix

- **<short phrase>**: <one or two sentences>. <optional detail>

### Docs

- **<short phrase>**: <one or two sentences>.

## 中文

<one Chinese summary paragraph — no extra title inside the paragraph>

### 新功能

- **<简洁短语>**: <一两句话介绍>. <可选：实现细节或其他补充>
- **<简洁短语>**: <一两句话介绍>.

### 修复

- **<简洁短语>**: <一两句话介绍>. <可选补充>
```

## Rules

### Opening (required)

- First non-empty line of the body = English summary paragraph.
- No `#` / `##` version title, no `## English` before that paragraph.
- Version numbers may appear **inside** prose when useful; do not restate the release title as a heading.

### Summary paragraph

- English: document open — **no** heading above it, **no** “Overview” label.
- Chinese: immediately under `## 中文` — still **no** extra title inside the paragraph.
- 2–5 sentences (or one dense paragraph): who this release is for, headline capabilities, and hard limits / non-goals if material.
- Do not bullet the summary.

### Language modules

- English block first (summary + categories), then `## 中文` + Chinese summary + categories.
- Only the Chinese module uses a language heading (`## 中文`). Omit an English language heading.

### Category headings

Use only categories that have items. **Chinese module uses Chinese headings; English module uses English headings**—do not put `Feat` / `Fix` under the Chinese block.

| Intent (cluster) | English | 中文标题 |
| --- | --- | --- |
| New capabilities | `Feat` | `新功能` |
| Bug fixes | `Fix` | `修复` |
| Behavior/API cleanup (user-visible) | `Refactor` | `改进` |
| Performance | `Perf` | `性能` |
| Documentation | `Docs` | `文档` |
| Tests (if operators/contributors care) | `Test` | `测试` |
| Install / packaging / tooling | `Build` / `CI` / `Chore` | `构建` / `CI` / `杂项` |
| Breaking change (when needed) | `Breaking` | `破坏性变更` |

Preferred order: Feat → Fix → Refactor → Perf → Docs → Test → Build / CI / Chore (and the Chinese row in the same order).

Omit empty categories. Keep the same category set on both sides when both languages ship.

### Bullet shape (required)

```text
- **<short phrase>**: <one or two sentences>. <optional detail>
```

| Part | Rule |
| --- | --- |
| short phrase | Bold; noun/verb phrase, not a full sentence; no trailing colon inside the bold |
| intro | 1–2 sentences after `: `; what changed and why it matters |
| optional detail | After the intro sentence(s); how it works, flag names, limits, migration — omit if empty |

Examples:

```markdown
- **ACP unified inlet**: coding-agent backends use `executor: acp` plus `options.entry`. One parent JSON-RPC client; L1 image bakes five entries at build time—no invoke-time `npm i`.
- **ACP 统一入口**: coding-agent 后端改为 `executor: acp` + `options.entry`。父进程单一 JSON-RPC client；L1 镜像 build 期 bake-in 五 entry，禁止 invoke 时 `npm i`。
```

### What to exclude

- Pure internal renames with no user/operator effect (unless API break).
- Process / checklist noise that does not change the product (reviews, status flips, chore-only housekeeping).
- Duplicate bullets that restate the same feature from multiple commits—merge them.
- Ticket or milestone labels as the primary story (optional secondary detail only).
- Redundant body titles that duplicate the GitHub Release / tag title.

### Length

- Prefer ≤12 bullets per language for a minor release; major first releases may be longer but still merge related commits.
- Split mega-bullets rather than writing paragraphs under one bold phrase.
