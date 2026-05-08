"""Unit test for smoke-test.py logic, runnable in isolation without an installed venv."""
import sys
from pathlib import Path
import pytest

# Add parent dir to path so we can import smoke_test
sys.path.insert(0, str(Path(__file__).parent))


def test_smoke_test_module_importable():
    """smoke-test.py imports cleanly when its dependencies are available."""
    pytest.importorskip("faster_whisper")
    import importlib.util
    spec = importlib.util.spec_from_file_location("smoke_test", Path(__file__).parent / "smoke-test.py")
    assert spec is not None, "smoke-test.py not found"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "run_smoke_test"), "smoke_test must expose run_smoke_test()"


def test_smoke_test_returns_dict_with_expected_keys():
    """run_smoke_test() returns a dict with the contract keys."""
    pytest.importorskip("faster_whisper")
    import importlib.util
    spec = importlib.util.spec_from_file_location("smoke_test", Path(__file__).parent / "smoke-test.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fixture = Path(__file__).parent / "test-fixtures" / "silence-5sec.wav"
    if not fixture.exists():
        pytest.skip("test fixture not yet generated; run Generate-TestFixture.ps1 first")
    result = module.run_smoke_test(str(fixture))
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"ok", "model_loaded", "transcription_attempted", "duration_seconds", "errors"}
