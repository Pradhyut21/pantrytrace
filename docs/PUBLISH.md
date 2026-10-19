# Publish this local repository

No remote repository has been created. The user chose local preparation.

1. Review `PREEXISTING.md`, remove private local files, and run the checks below.
2. Create an empty GitHub repository named `pantrytrace` under your account. Do not initialize a second README or license there.
3. If this folder already contains the prepared local commit, add your remote and push it. Otherwise initialize it and commit with your own configured Git identity.

```powershell
python -m unittest discover -s tests -v
python -m pantrytrace evaluate
git status
git remote add origin https://github.com/YOUR-ACCOUNT/pantrytrace.git
git push -u origin codex/pre-event-prototype
```

`YOUR-ACCOUNT` is an explicit placeholder. Replace it; no actual repository URL is claimed. If your starting branch differs, use the branch printed by `git branch --show-current`. Set the desired GitHub default branch after the first push, or use a normal pull request to merge the preparation snapshot.

Suggested repository description: **Evidence-backed recall reconciliation for food banks: missing lots, conflicting intake records, transfer context, and reviewable task drafts.**

Suggested topics: `food-banks`, `traceability`, `entity-resolution`, `agents`, `meterless`, `zetaris`, `hackathon`.

Keep the initial snapshot labeled as pre-event. Tag it `pre-event-2026-10-19` if desired. During the build window, use a new branch and publish a real before/after comparison. Do not change commit dates. Add the final demo URL and deck after validating their sharing permissions. For a private repository, grant judges the access required by HackOS before submission.
