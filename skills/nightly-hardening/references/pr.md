# Draft PR against the source branch

Push from the **worktree**, not the primary checkout.

```bash
git push -u "$UPSTREAM" "$BRANCH"
gh pr create --repo OWNER/REPO --draft --base "$BASE" --head "$BRANCH" \
  --title "<title>" \
  --body-file -
```

`--base` is the **source branch** (`canary`, `main`, …), not a hardcoded `main`.

Do not merge. Do not `--fill` if that ignores the repo's template.

## Match this repo

Before writing the body, load:

1. `.github/PULL_REQUEST_TEMPLATE*` if present — keep required headings.
2. A few recent PRs into the **same base**:

```bash
gh pr list --repo OWNER/REPO --base "$BASE" --state all --limit 8 \
  --json number,title,body,isDraft
```

Match title language, Conventional Commit density, heading names, and whether they use `Closes #N`. Do not copy another PR's issue numbers or test claims.

If history is mixed, prefer the latest non-trivial PR into `$BASE`. Fallback shape below is only when the repo has no template and no useful history.

## Title

Usually `type(scope): subject` if recent PRs look like that. One line, no trailing period. Language = the PRs, not the chat.

## Body fallback

```markdown
## Summary
<what changed, one short paragraph>

## Approach
<the knob / files / default = omit means old behavior>

## Test plan
- [ ] <local CI-equivalent actually run>
- [ ] <slice or acceptance item>

Closes #<N>
```

- `Closes #N` only for issues this PR fully delivers. Bundle of related issues: list them; close only those that are actually done.
- Oral / autonomous work with no issue: omit `Closes`.
- No secrets, no host-absolute paths, no "as we discussed".
- Do not claim CI jobs that were skipped or not run. Skipped live Agent/Docker jobs are not acceptance.

## Reply to the user

After the PR exists, the originating chat gets (user's language):

1. PR URL (draft).
2. Base → branch, worktree path.
3. What landed, by slice (not a file laundry list).
4. Checks actually run, and what was **not** verified.
5. Deferred follow-ups.

Do not paste the full PR body again unless they asked. Do not delete the worktree.
