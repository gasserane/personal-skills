import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import pytest  # noqa: E402

from helpers import build_env  # noqa: E402


@pytest.fixture
def env(tmp_path):
    return build_env(tmp_path)
