"""Fixed data-only text writer for repo-local Agent OS artifacts."""

from __future__ import annotations

import base64
import subprocess
from pathlib import Path


_NODE_WRITE_SCRIPT = (
    "const fs=require('fs'),p=require('path');"
    "const dest=process.argv[1],data=Buffer.from(process.argv[2],'base64');"
    "fs.mkdirSync(p.dirname(dest),{recursive:true});"
    "fs.writeFileSync(dest,data);"
)


def write_text(path: Path, content: str) -> None:
    """Write fixed data after the caller has validated the destination path."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return
    except OSError:
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        result = subprocess.run(
            ["node", "-e", _NODE_WRITE_SCRIPT, str(path), encoded],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            raise OSError(
                f"safe data-only write fallback failed for {path.name}: "
                f"{result.stderr.strip()}"
            )
