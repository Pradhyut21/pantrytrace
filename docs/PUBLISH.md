# Maintain and verify the public repository

Updated 20 October 2026. The user has authorized publishing the complete prepared project to the existing public repository:

**[https://github.com/Pradhyut21/pantrytrace](https://github.com/Pradhyut21/pantrytrace)**

The source and prepared assets were published on 20 October 2026. The public default branch is `main`, and the original preparation commits remain ancestors of it. A fresh clone from GitHub passed all 44 tests, fixture evaluation and the real local Meterless smoke check. See [verification details](VERIFICATION.md).

## Preserve provenance

The prepared history contains these commits:

| Commit | Existing preparation change |
| --- | --- |
| `c3786a5` | Declare PantryTrace pre-event prototype and research |
| `5c99df5` | Make Windows CLI JSON output UTF-8 |
| `af58b00` | Preserve pinned upstream source bytes on Windows |

Keep all three as ancestors of the published `main` branch. Add publication documentation/assets in a new commit with its actual date. Do not rebase away this history, force-push it away, backdate commits or imply that packaging is eligible-window implementation.

## Verify this owned remote

Run these checks against the prepared checkout when the source push is ready:

```powershell
git remote get-url origin
git status --short
git log --oneline --decorate -5
git merge-base --is-ancestor af58b00 main
git ls-remote --heads origin main
gh repo view Pradhyut21/pantrytrace --json url,visibility,defaultBranchRef
```

The remote should be the repository above, with published/default branch `main`. A nonzero ancestry result needs investigation, not a history rewrite. The `gh` command is optional; the branch can also be checked in GitHub's repository interface and with `git ls-remote --symref origin HEAD`.

After publication, maintain the normal `main` history with new commits and ordinary pushes. Use feature branches and pull requests for later changes; preserve the pre-event boundary in [PREEXISTING.md](../PREEXISTING.md).

## Verify a clean checkout and assets

Clone the real remote into a separate review folder after source publication, follow its README, and run the documented tests and fixture evaluation. Check the workbench plus links to [submission readiness](SUBMISSION_READINESS.md), [the 116-second walkthrough](media/pantrytrace-walkthrough.mp4), [the teaser](media/pantrytrace-brag.mp4) and [the pitch PDF](pitch/pantrytrace-pitch.pdf). Record the actual results in the release checklist.

The [preparation walkthrough on Google Drive](https://drive.google.com/file/d/1A3MebeBEs_cJHzJBYgj1wZ6Pcby7npV8/view?usp=drivesdk) has verified anyone-reader sharing metadata. Verify signed-out playback, and refresh the footage after actual sponsor execution. No YouTube or Vimeo publication is claimed. The form also offers video upload; final footage must show the final implementation and remain 1–4 minutes.

Suggested repository description: **Evidence-backed recall reconciliation for food banks: missing lots, conflicting intake records, transfer context and reviewable task drafts.**

Suggested topics: `food-banks`, `traceability`, `entity-resolution`, `agents`, `meterless`, `zetaris`, `hackathon`.

Public source publication does not establish final hackathon eligibility. Live Zetaris, Nemotron and Cursor proof remain pending; see [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md). No HackOS submission is performed by these maintenance instructions.
