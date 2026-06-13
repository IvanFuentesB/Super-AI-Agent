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
_NODE_EXCLUSIVE_WRITE_SCRIPT = (
    "const fs=require('fs'),p=require('path');"
    "const dest=process.argv[1],data=Buffer.from(process.argv[2],'base64');"
    "fs.mkdirSync(p.dirname(dest),{recursive:true});"
    "try{fs.writeFileSync(dest,data,{flag:'wx'});process.exit(0)}"
    "catch(e){if(e&&e.code==='EEXIST')process.exit(17);throw e}"
)
_NODE_REMOVE_SCRIPT = (
    "const fs=require('fs'),dest=process.argv[1];"
    "try{fs.unlinkSync(dest)}catch(e){if(!e||e.code!=='ENOENT')throw e}"
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


def write_text_exclusive(path: Path, content: str) -> bool:
    """Create fixed data only if the destination does not already exist."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        return True
    except FileExistsError:
        return False
    except OSError:
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        result = subprocess.run(
            ["node", "-e", _NODE_EXCLUSIVE_WRITE_SCRIPT, str(path), encoded],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode == 17:
            return False
        if result.returncode != 0:
            raise OSError(
                f"safe exclusive data write failed for {path.name}: "
                f"{result.stderr.strip()}"
            )
        return True


def remove_file(path: Path) -> None:
    """Remove one validated runtime file, with a fixed data-path fallback."""
    try:
        path.unlink(missing_ok=True)
        return
    except OSError:
        result = subprocess.run(
            ["node", "-e", _NODE_REMOVE_SCRIPT, str(path)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            raise OSError(
                f"safe data-file removal failed for {path.name}: "
                f"{result.stderr.strip()}"
            )
