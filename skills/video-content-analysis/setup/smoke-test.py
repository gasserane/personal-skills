"""Post-install smoke test for video-content-analysis skill.

Loads the smallest practical Whisper model, transcribes the 5-second silence WAV,
and reports success or specific failure modes. Exit code 0 = ready; non-zero = problem.
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path
from typing import Any


def run_smoke_test(audio_path: str, model_size: str = "tiny") -> dict[str, Any]:
    """Run the smoke test end-to-end.

    Returns a result dict; does not raise on most failures so the caller can
    decide how to surface them. The 'ok' key is True only when every stage
    completed without error.
    """
    result: dict[str, Any] = {
        "ok": False,
        "model_loaded": False,
        "transcription_attempted": False,
        "duration_seconds": None,
        "errors": [],
    }

    audio = Path(audio_path)
    if not audio.exists():
        result["errors"].append(f"audio file not found: {audio_path}")
        return result

    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        result["errors"].append(f"faster_whisper import failed: {e}")
        return result

    t0 = time.time()
    try:
        # 'tiny' model is ~75MB. Sufficient for a smoke test and avoids forcing
        # the 3GB large-v3 download up front.
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        result["model_loaded"] = True
    except Exception as e:
        result["errors"].append(f"model load failed: {e}")
        return result

    try:
        segments, info = model.transcribe(str(audio), language="en")
        result["transcription_attempted"] = True
        # Force iteration so transcription actually runs (faster-whisper is lazy)
        _ = list(segments)
    except Exception as e:
        result["errors"].append(f"transcription failed: {e}")
        return result

    result["duration_seconds"] = round(time.time() - t0, 2)
    result["ok"] = True
    return result


EXIT_OK = 0
EXIT_FIXTURE_MISSING = 2
EXIT_IMPORT_FAILED = 3
EXIT_MODEL_LOAD_FAILED = 4
EXIT_TRANSCRIPTION_FAILED = 5


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test for video-content-analysis install.")
    parser.add_argument("--audio", default=str(Path(__file__).parent / "test-fixtures" / "silence-5sec.wav"))
    parser.add_argument("--model", default="tiny")
    args = parser.parse_args()

    print(f"Smoke test starting (audio: {args.audio}, model: {args.model})...")
    result = run_smoke_test(args.audio, args.model)
    print(f"Result: {result}")
    if result["ok"]:
        return EXIT_OK
    if any("audio file not found" in e for e in result["errors"]):
        return EXIT_FIXTURE_MISSING
    if any("faster_whisper import failed" in e for e in result["errors"]):
        return EXIT_IMPORT_FAILED
    if any("model load failed" in e for e in result["errors"]):
        return EXIT_MODEL_LOAD_FAILED
    if any("transcription failed" in e for e in result["errors"]):
        return EXIT_TRANSCRIPTION_FAILED
    return 1


if __name__ == "__main__":
    sys.exit(main())
