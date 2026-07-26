---
name: obsidian-public-sync
description: Sync selected notes from this private Obsidian vault into the sibling public Quartz repository while preserving vault-relative paths and resolving Obsidian wikilink dependencies. Use when the user asks to sync, publish, copy, migrate, or update one or more notes or folders in the public site, especially requests such as “同步到公开仓库” or “发布这篇笔记”.
---

# Obsidian Public Sync

## Contract

### Fixed paths

- Use `~/Developer/ob-notes` as the source vault.
- Use `~/Developer/ob-notes-public` as the public Quartz repository and sync into its `content/` directory.
- Derive both paths automatically from this project-level skill. Do not ask the user for either path and do not pass `--source-root` or `--public-root` during normal use. Keep those flags for isolated tests or an explicit future relocation only.

### Sync rules

- Copy only the user-named file or folder plus its resolved dependency closure. Preserve paths relative to the source vault so Quartz can resolve the same links.
- Follow local Obsidian wikilinks and embeds transitively by default, including `[[note]]`, `[[path/note|label]]`, `![[note]]`, Canvas files, and local attachments. Follow local Markdown links too.
- If the user explicitly says that wikilinked notes do not need to be copied, pass `--no-wikilinks`. Still copy directly referenced local assets so the selected page can render.
- Do not copy the whole vault, `.obsidian/`, `.agents/`, or unrelated backlinks. Do not delete public files, commit, push, or deploy unless the user asks.
- Before writing, report if the selected closure includes notes whose frontmatter declares `visibility: private` or `public.include: false`. A sync request authorizes the named note and its requested dependency closure, but the user should see this inventory.

## Workflow

### 1. Inspect scope

1. Resolve every user-supplied path relative to the source vault. Reject paths outside it.
2. Inspect the target repository status and the named source files before modifying anything.
3. Locate the skill directory and run the script in dry-run mode:

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

The script copies each file to the matching path below `content/`, reports unresolved local references, and never deletes destination files. Treat unresolved references as an audit task: copy the missing source if it is meant to be public, rewrite the source link only when the user asks, or leave an intentional external/non-public reference documented in the handoff.

### 3. Validate the public site

Run the Quartz build from the public repository after every sync:

```bash
cd ../ob-notes-public
npx quartz plugin install --from-config
npx quartz build
```

Check that the copied note, each copied attachment, and any copied Canvas page appear in `public/`. Inspect the generated page or the build output when the source contains Obsidian links, embeds, attachments, Canvas, callouts, Mermaid, or non-ASCII filenames.

### 4. Hand off

Report the source roots, copied dependency files, skipped wikilinks, unresolved references, and build result. State separately whether Git commit, push, or Vercel deployment remains pending.

## Exceptions

- For a directory request, copy the entire requested directory and then resolve outward references from its Markdown and Canvas files.
- Preserve Markdown and frontmatter without converting links to HTML. Quartz is configured for Obsidian-flavored Markdown.
- Keep public-site-only files such as `content/index.md`, `quartz.config.yaml`, and deployment configuration untouched unless the user explicitly targets them.
- Use `--strict` when the user requires an all-resolved closure; it exits nonzero if any local reference cannot be resolved.
