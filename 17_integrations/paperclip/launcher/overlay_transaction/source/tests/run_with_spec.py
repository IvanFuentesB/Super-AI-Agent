"""Test entry point: run the helper CLI against a fixture Spec. Never used with the accepted package; the
production CLI (paperclip_overlay.py) has no way to replace its accepted Spec."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paperclip_overlay as h  # noqa: E402

spec_data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
spec_data["outputs"] = tuple(spec_data["outputs"])
spec_data["allowed_tracked_changes"] = frozenset(spec_data["allowed_tracked_changes"])
sys.exit(h.main(sys.argv[2:], h.Spec(**spec_data)))
