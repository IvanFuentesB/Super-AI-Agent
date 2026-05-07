"""
Continuous screen capture sidecar for Ghoti Active Mode.

Capture method: PIL ImageGrab (Windows).
If PIL is unavailable, exits with code 2 and a clear error message.

Usage:
    python -m super_ai_agent.screen_capture_sidecar <output_dir> <state_json_path> [fps]

Runs until it receives SIGTERM / KeyboardInterrupt or the stop file appears.
Stop file: <output_dir>/.stop
"""

import json
import os
import pathlib
import sys
import time

STOP_FILENAME = ".stop"


def _fail(msg, code=2):
    print(f"screen_capture_sidecar: {msg}", file=sys.stderr)
    sys.exit(code)


def _try_import_imagegrab():
    try:
        from PIL import ImageGrab  # noqa: PLC0415
        return ImageGrab
    except ImportError:
        return None


def _write_state(state_path: pathlib.Path, patch: dict, current: dict | None = None):
    base = current or {}
    if state_path.exists():
        try:
            base = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    merged = {**base, **patch, "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    return merged


def main():
    if len(sys.argv) < 3:
        _fail("usage: screen_capture_sidecar <output_dir> <state_json_path> [fps]")

    output_dir = pathlib.Path(sys.argv[1])
    state_path = pathlib.Path(sys.argv[2])
    fps = float(sys.argv[3]) if len(sys.argv) >= 4 else 1.0
    interval = 1.0 / max(fps, 0.1)

    ImageGrab = _try_import_imagegrab()
    if ImageGrab is None:
        _write_state(state_path, {
            "capturing": False,
            "error": "PIL ImageGrab not available. Install Pillow.",
            "capture_method": "none",
        })
        _fail("PIL ImageGrab not available. Install Pillow.", code=2)

    output_dir.mkdir(parents=True, exist_ok=True)
    stop_file = output_dir / STOP_FILENAME
    # Remove any stale stop file from a prior run
    if stop_file.exists():
        stop_file.unlink()

    frame_count = 0
    latest_path = str(output_dir / "latest.png")

    _write_state(state_path, {
        "capturing": True,
        "capture_method": "PIL_ImageGrab",
        "fps_target": fps,
        "frame_count": 0,
        "latest_frame_path": None,
        "latest_frame_utc": None,
        "error": None,
    })

    print(f"screen_capture_sidecar: started fps={fps} dir={output_dir}", flush=True)

    try:
        while True:
            if stop_file.exists():
                print("screen_capture_sidecar: stop file detected, exiting.", flush=True)
                break

            t0 = time.monotonic()
            try:
                img = ImageGrab.grab()
                frame_path = output_dir / f"frame-{frame_count:06d}.png"
                img.save(str(frame_path))
                img.save(latest_path)
                frame_count += 1
                now_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                _write_state(state_path, {
                    "capturing": True,
                    "capture_method": "PIL_ImageGrab",
                    "fps_target": fps,
                    "frame_count": frame_count,
                    "latest_frame_path": latest_path,
                    "latest_frame_utc": now_utc,
                    "error": None,
                })
            except Exception as exc:
                _write_state(state_path, {"error": str(exc)})
                print(f"screen_capture_sidecar: capture error: {exc}", file=sys.stderr, flush=True)

            elapsed = time.monotonic() - t0
            sleep_for = max(0.0, interval - elapsed)
            time.sleep(sleep_for)
    except KeyboardInterrupt:
        pass
    finally:
        _write_state(state_path, {
            "capturing": False,
            "frame_count": frame_count,
            "error": None,
        })
        print(f"screen_capture_sidecar: stopped. frames={frame_count}", flush=True)


if __name__ == "__main__":
    main()
