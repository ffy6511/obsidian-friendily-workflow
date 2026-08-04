---
name: obsidian-public-sync
description: Sync selected notes from a private Obsidian vault into a public Quartz repository while preserving vault-relative paths and resolving Obsidian wikilink dependencies. Use when the user asks to sync, publish, copy, migrate, or update one or more notes or folders in the public site, especially requests such as “同步到公开仓库” or “发布这篇笔记”.
---

# Obsidian Public Sync

## User Preferences (`preferences.toml`)

Local roots live in preferences — never hardcode machine paths in this skill.

| File | Role | Git |
| --- | --- | --- |
| `preferences.example.toml` | Documented template | tracked |
| `preferences.toml` | Real local paths | **gitignored** |

### First-time setup

When `preferences.toml` is missing or `initialized` is `false`:

1. `cp preferences.example.toml preferences.toml`
2. Set `source_root` (private vault) and `public_root` (Quartz repo)
3. Optionally set `content_subdir` (default `content`)
4. Set `initialized = true`

After setup, read preferences silently. CLI `--source-root` / `--public-root` / `--content-subdir` always override the file (tests / one-off relocation).

## Contract

### Paths

- Resolve vault and public roots from `preferences.toml` (or CLI overrides).
- Sync into `<public_root>/<content_subdir>/` (default `content/`).
- Do not ask for paths on every run once initialized.

### Sync rules

- Copy only the user-named file or folder plus its resolved dependency closure. Preserve paths relative to the source vault so Quartz can resolve the same links.
- Follow local Obsidian wikilinks and embeds transitively by default, including `[[note]]`, `[[path/note|label]]`, `![[note]]`, Canvas files, and local attachments. Follow local Markdown links too.
- If the user explicitly says that wikilinked notes do not need to be copied, pass `--no-wikilinks`. Still copy directly referenced local assets so the selected page can render.
- Do not copy the whole vault, `.obsidian/`, `.agents/`, or unrelated backlinks. Do not delete public files, commit, push, or deploy unless the user asks.
- Before writing, report if the selected closure includes notes whose frontmatter declares `visibility: private` or `public.include: false`. A sync request authorizes the named note and its requested dependency closure, but the user should see this inventory.

## Workflow

### 1. Preferences + inspect scope

1. Ensure preferences are initialized (see above).
2. Resolve every user-supplied path relative to the source vault. Reject paths outside it.
3. Inspect the target repository status and the named source files before modifying anything.
4. Locate the skill directory and run the script in dry-run mode:

```bash
PY="${PY:-python3}"
SKILL_DIR="<installed obsidian-public-sync skill directory>"
"$PY" "$SKILL_DIR/scripts/sync_public.py" \
  --source <vault-relative-path> \
  --dry-run
```

Use `--no-wikilinks` only when the user explicitly opts out of linked-note synchronization. Use `--allow-homepage-overwrite` only when the user explicitly wants a source `index.md` to replace the public homepage.

### 2. Sync the dependency closure

After reviewing the dry-run inventory, run the same command without `--dry-run`.

```bash
"$PY" "$SKILL_DIR/scripts/sync_public.py" \
  --source <vault-relative-path>
```

The script copies each file to the matching path under the public content directory, reports unresolved local references, and never deletes destination files. Treat unresolved references as an audit task: copy the missing source if it is meant to be public, rewrite the source link only when the user asks, or leave an intentional external/non-public reference documented in the handoff.

### 3. Validate the public site

Run the Quartz build from the public repository path in preferences after every sync:

```bash
cd <public_root from preferences.toml>
npx quartz plugin install --from-config
npx quartz build
```

Check that the copied note, each copied attachment, and any copied Canvas page appear in the site output. Inspect the generated page or the build output when the source contains Obsidian links, embeds, attachments, Canvas, callouts, Mermaid, or non-ASCII filenames.

### 4. Hand off

Report the source roots, copied dependency files, skipped wikilinks, unresolved references, and build result. State separately whether Git commit, push, or Vercel deployment remains pending.

## Exceptions

- For a directory request, copy the entire requested directory and then resolve outward references from its Markdown and Canvas files.
- Preserve Markdown and frontmatter without converting links to HTML. Quartz is configured for Obsidian-flavored Markdown.
- Keep public-site-only files such as `content/index.md`, `quartz.config.yaml`, and deployment configuration untouched unless the user explicitly targets them.
- Use `--strict` when the user requires an all-resolved closure; it exits nonzero if any local reference cannot be resolved.
