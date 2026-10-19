"""Install the pinned local TypeScript runner; no sponsor credentials required."""
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
npm = shutil.which("npm")
if not npm or not shutil.which("node"):
    raise SystemExit("Install Node.js (with npm), then run this script again.")
result = subprocess.run([npm, "ci", "--no-audit", "--no-fund"], cwd=root, check=False)
if result.returncode:
    raise SystemExit(result.returncode)
print("Pinned tsx runtime installed. Run python scripts/smoke_meterless.py to verify the official local engine.")
