"""Verify pinned upstream and frozen media source bytes on every platform."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
vendor = ROOT / "vendor" / "meterless-hmem"
upstream = json.loads((vendor / "UPSTREAM.json").read_text(encoding="utf-8"))
checks = [(vendor / name, digest) for name, digest in upstream["sha256"].items()]
media = ROOT / "media-src"
media_count = 0
for line in (media / "SOURCE-MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
    if line and not line.startswith("#"):
        digest, name = line.split("  ", 1)
        checks.append((media / name, digest))
        media_count += 1

failures = [path.relative_to(ROOT).as_posix() for path, digest in checks
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest]
if failures:
    raise SystemExit("Provenance mismatch: " + ", ".join(failures))
print(json.dumps({"verified": True, "meterless_sources": len(upstream["sha256"]),
                  "frozen_media_sources": media_count}))
