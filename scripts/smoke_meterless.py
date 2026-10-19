"""Verify actual Meterless H-MEM locally, using disposable test memory."""
import importlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
package = "pantrytrace" if (root / "pantrytrace").is_dir() else "pantrytrace"
module = importlib.import_module(package + ".sponsors")
try:
    print(json.dumps(module.meterless_smoke(), indent=2))
except module.SponsorError as error:
    raise SystemExit(str(error)) from None
