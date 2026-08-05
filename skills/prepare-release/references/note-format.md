# Release note format

Default when the repo already has package release notes: **copy that voice first** (density, bold lead phrases, bilingual layout, what they omit). This file is the fallback skeleton for a first release or when history is missing/unusable.

Two modules in order: **中文**, then **English**. Same facts; natural phrasing per language.

## Body vs Release title

- GitHub Release / tag **title** already carries the product + version (e.g. `BORA v0.1.0`).
- Note **body** must **not** repeat a top-level version heading (`# BORA v0.1.0`, `# v0.1.0`, etc.).
- Note **body** must **not** open with a language label (`## 中文`, `## Chinese`, …). Chinese starts at the first summary paragraph.

## Module skeleton

```markdown
<one Chinese summary paragraph — first line of the body, no heading above it>

### 新功能

- **<简洁短语>**: <一两句话介绍>. <可选：实现细节或其他补充>
- **<简洁短语>**: <一两句话介绍>.

### 修复

- **<简洁短语>**: <一两句话介绍>. <可选补充>

### 文档

- **<简洁短语>**: <一两句话介绍>.

## English

<one English summary paragraph — no extra title inside the paragraph>

### Feat

- **<short phrase>**: <one or two sentences>. <optional implementation or other detail>

### Fix

- **<short phrase>**: <one or two sentences>. <optional detail>
```

## Rules

### Opening (required)

- First non-empty line of the body = Chinese summary paragraph.
- No `#` / `##` version title, no `## 中文` before that paragraph.
- Version numbers may appear **inside** prose when useful; do not restate the release title as a heading.

### Summary paragraph

- Chinese: document open — **no** heading above it, **no** “概览” / “Overview” label.
- English: immediately under `## English` — still **no** extra title inside the paragraph.
- 2–5 sentences (or one dense paragraph): who this release is for, headline capabilities, and hard limits / non-goals if material.
- Do not bullet the summary.

### Language modules

- Chinese block first (summary + categories), then `## English` + English summary + categories.
- Only the English module uses a language heading (`## English`). Omit a Chinese language heading.

### Category headings

Use only categories that have items. **Chinese module uses Chinese headings; English module uses English headings**—do not put `Feat` / `Fix` under the Chinese block.

| Intent (cluster) | 中文标题 | English |
| --- | --- | --- |
| New capabilities | `新功能` | `Feat` |
| Bug fixes | `修复` | `Fix` |
| Behavior/API cleanup (user-visible) | `改进` | `Refactor` |
| Performance | `性能` | `Perf` |
| Documentation | `文档` | `Docs` |
| Tests (if operators/contributors care) | `测试` | `Test` |
| Install / packaging / tooling | `构建` / `CI` / `杂项` | `Build` / `CI` / `Chore` |
| Breaking change (when needed) | `破坏性变更` | `Breaking` |

Preferred order: 新功能 → 修复 → 改进 → 性能 → 文档 → 测试 → 构建 / CI / 杂项 (and the English row in the same order).

Omit empty categories. Keep the same category set on both sides when both languages ship.

### Bullet shape (required)

```text
- **<简洁短语>**: <一两句话的介绍>. <可选的实现细节或者其他补充>
```

| Part | Rule |
| --- | --- |
| 简洁短语 | Bold; noun/verb phrase, not a full sentence; no trailing colon inside the bold |
| 介绍 | 1–2 sentences after `: `; what changed and why it matters |
| 可选补充 | After the intro sentence(s); how it works, flag names, limits, migration — omit if empty |

Examples:

```markdown
- **ACP 统一入口**: coding-agent 后端改为 `executor: acp` + `options.entry`。父进程单一 JSON-RPC client；L1 镜像 build 期 bake-in 五 entry，禁止 invoke 时 `npm i`。
- **ACP unified inlet**: coding-agent backends use `executor: acp` plus `options.entry`. One parent JSON-RPC client; L1 image bakes five entries at build time—no invoke-time `npm i`.
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
