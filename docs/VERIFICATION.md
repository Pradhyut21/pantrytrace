# Publication verification

Verified on **20 October 2026**. This records preparation checks, not final sponsor qualification.

## Reproducibility

A fresh clone of public `Pradhyut21/pantrytrace`, default branch `main`, was checked at `e3e687515d7c799c51b8f95b67f709d1a210051e`:

| Check | Observed result |
| --- | --- |
| `python -m unittest discover -s tests -v` | 44 passed, zero failures |
| `python -m pantrytrace evaluate` | 8/9 inventory-only baseline; 9/9 with retrieval, across nine authored development items |
| `npm ci` | Successful; zero vulnerabilities reported by npm at verification time |
| `python -m pantrytrace sponsor-smoke` | Real official local H-MEM remember, cross-process recall, audit and feedback; zero remote API calls |
| Documentation | All 85 relative Markdown links in that snapshot resolved with Git path case checked |
| Third-party provenance | All ten vendored TypeScript source hashes matched `UPSTREAM.json` |
| Rendered assets | Both videos and pitch PDF matched the original deliverable bytes |
| Bounded secret scan | No matches in the six checked credential patterns or private credential filenames; this is not an exhaustive security audit |
| Checkout state | Tracked worktree remained clean |

The first GitHub Actions run exposed a Windows test comparing an 8.3 temporary-folder alias with the same folder's resolved name. Commit `c596aa0f06a5974ee3c62ad4893ea9dcfa2c62a0` corrects the expected path; application behavior is unchanged. All 44 tests passed locally after the correction, and [the subsequent GitHub run passed all five jobs](https://github.com/Pradhyut21/pantrytrace/actions/runs/39461658042): Windows and Linux on Python 3.11/3.13, plus the official Meterless engine. The [Actions workflow](https://github.com/Pradhyut21/pantrytrace/actions/workflows/check.yml) records later runs.

After the editable video projects and final index were added, publication checks covered 108 relative Markdown links and all 49 preserved video-source hashes, with no broken targets or hash mismatches. The bounded scan of 97 text files also found no matches for the checked credential formats or private setup context.

`python scripts/verify_provenance.py` verifies the ten pinned Meterless source files and 49 frozen media files. CI runs it on both operating systems. Frozen media inputs retain their original newline bytes through Git attributes, so a checkout cannot silently invalidate their source manifest.

## Shareable deliverables

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `docs/media/pantrytrace-walkthrough.mp4` | 7,347,928 | `0b18e62f57ec293a6a886db06e71ff0757db0f69354482bc27cbd52b316e3aa9` |
| `docs/media/pantrytrace-brag.mp4` | 2,563,647 | `6dba06d0de49319a7ea37ea2ca36e5cb4acce837dc0afacbd5e87a0444975ac6` |
| `docs/pitch/pantrytrace-pitch.pdf` | 181,456 | `29b370c4f20d95b30a7135493e1c8d50216e72a25410041e61ce6c2e77df7b4d` |

The [Drive walkthrough](https://drive.google.com/file/d/1A3MebeBEs_cJHzJBYgj1wZ6Pcby7npV8/view?usp=drivesdk) is 116 seconds. Drive permission metadata was read back as `anyone` / `reader`, with search discovery disabled. Independent browser playback was not verified by the web-reading tool; the repository MP4 provides a second download path. Keep the [media attribution](media/MEDIA-CREDITS.md) when sharing.

Live Zetaris federation, NVIDIA Nemotron inference, actual Cursor development and held-out/operator validation remain pending. [Submission readiness](SUBMISSION_READINESS.md) tracks those requirements.
