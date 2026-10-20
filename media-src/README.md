# Editable video sources

These self-contained HyperFrames projects were prepared on **19–20 October 2026**, before the hackathon build window. They preserve the composition HTML, planning notes, recorded app footage, screenshots, fonts, music, sound effects and pinned local assets used for the current videos. They show a synthetic local prototype; they are **pre-event assets, not final eligible submission evidence**. See the [current readiness record](../docs/SUBMISSION_READINESS.md) and [pre-existing work disclosure](../PREEXISTING.md).

The sources were copied byte-for-byte from the preparation workspace's `outputs/video/brag/` and `outputs/video/walkthrough/` folders. Original planning notes are historical records of that preparation. Current sponsor status and submission requirements take precedence over their earlier wording.

| Project | Planning and composition | Prepared output |
| --- | --- | --- |
| Brag teaser | [Plan](brag/brag-plan.md), [brief](brag/composition-brief.md), [composition](brag/composition/index.html) | [24-second MP4](../docs/media/pantrytrace-brag.mp4), [poster](../docs/media/pantrytrace-brag.jpg); 1920×1080, 30 fps |
| Demo walkthrough | [Brief](walkthrough/composition/BRIEF.md), [storyboard](walkthrough/composition/STORYBOARD.md), [composition](walkthrough/composition/index.html) | [116-second MP4](../docs/media/pantrytrace-walkthrough.mp4), [poster](../docs/media/pantrytrace-walkthrough.jpg); 1920×1080, 24 fps |

Both videos have music and on-screen explanations, with no narration. All operational data shown is fictional. The bundled input capture MP4s are part of the editable walkthrough. Build caches, installed dependencies, temporary renders and agent instruction files are excluded. [SOURCE-MANIFEST.sha256](SOURCE-MANIFEST.sha256) records the SHA-256 digest of each of the 49 copied source files.

## Rerender

Install Node.js 22 or newer and FFmpeg, with `node`, `npx` and `ffmpeg` available on your path. The commands below use the projects' pinned **HyperFrames 0.8.176**. The first invocation downloads the CLI; the composition assets are already local. No application server or sponsor credentials are needed to replay the captured prototype footage.

Run each block from the repository root in PowerShell. Rendering overwrites the matching prepared MP4 and poster under `docs/media/`.

```powershell
Set-Location media-src/brag/composition
npx --yes hyperframes@0.8.176 check
npx --yes hyperframes@0.8.176 render --quality delivery --workers 1 --fps 30 --output ../../../docs/media/pantrytrace-brag.mp4
ffmpeg -y -ss 15.3 -i ../../../docs/media/pantrytrace-brag.mp4 -frames:v 1 -q:v 2 ../../../docs/media/pantrytrace-brag.jpg
Set-Location ../../..
```

```powershell
Set-Location media-src/walkthrough/composition
npx --yes hyperframes@0.8.176 check
npx --yes hyperframes@0.8.176 render --quality delivery --workers 1 --fps 24 --output ../../../docs/media/pantrytrace-walkthrough.mp4
ffmpeg -y -ss 25 -i ../../../docs/media/pantrytrace-walkthrough.mp4 -frames:v 1 -q:v 2 ../../../docs/media/pantrytrace-walkthrough.jpg
Set-Location ../../..
```

For an interactive preview, run `npx --yes hyperframes@0.8.176 preview` from the chosen composition directory.

The prepared deliveries also place their settled poster on frame zero for players that use the first frame as a thumbnail. To repeat that final packaging step after rendering, run this from the repository root:

```powershell
foreach ($videoName in @('pantrytrace-brag', 'pantrytrace-walkthrough')) {
    ffmpeg -y -i "docs/media/$videoName.mp4" -i "docs/media/$videoName.jpg" -filter_complex "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]" -map '[v]' -map '0:a?' -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -c:a copy -movflags +faststart "docs/media/$videoName.poster.mp4"
    if ($LASTEXITCODE -ne 0) { throw "Poster packaging failed for $videoName" }
    Move-Item -LiteralPath "docs/media/$videoName.poster.mp4" -Destination "docs/media/$videoName.mp4" -Force
}
```

Rendering can require substantial temporary disk space. Exact MP4 bytes can vary with encoder/runtime versions; the manifest verifies the preserved source files, not byte-identical encoded output.

## Credits and publication

Follow [MEDIA-CREDITS.md](../docs/media/MEDIA-CREDITS.md), including its [posting credit](../docs/media/MEDIA-CREDITS.md#posting-credit), when publishing either video. Third-party assets retain their own license terms. Font OFL notices remain beside the bundled font files in each composition. Music is “Happy Beats & Business Moves Vol. 12” by Sascha Ende, CC BY 4.0; it was trimmed and mixed with gain changes and fades.

Refresh the walkthrough with eligible-window implementation and verified sponsor evidence before treating it as a final competition deliverable.
