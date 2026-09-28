"""Thin command-line driver over ``ane_package.deliverable_doctor``.

Every step is one call into the package, where it is tested
(``tests/test_deliverable_doctor.py`` in the work folder). This file only finds
the package and hands over the arguments. Run with no arguments for the list
of subcommands.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# --- generated from ane_package.officeops.bootstrap.BOOTSTRAP_SNIPPET ---------
# This script runs from the personal-skills clone, outside the work folder, so
# it has to find ane_package before it can import it.


def _bootstrap_ane_package() -> None:
    """Put the work folder on sys.path so ane_package imports from anywhere.

    Generated from ane_package.officeops.bootstrap.BOOTSTRAP_SNIPPET.
    Do not edit here; edit the canonical copy and regenerate.
    """
    try:
        import ane_package  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    candidates = []
    env_root = os.environ.get("WORK_FOLDER_ROOT")
    if env_root:
        candidates.append(Path(env_root))
    candidates.extend(Path(__file__).resolve().parents)

    for candidate in candidates:
        if (candidate / "ane_package" / "reporting" / "brand.py").is_file():
            sys.path.insert(0, str(candidate))
            return

    raise ModuleNotFoundError(
        "ane_package not found. Set WORK_FOLDER_ROOT to the work folder, or run "
        "this script from inside it."
    )


_bootstrap_ane_package()
# --- end generated bootstrap ---------------------------------------------------

from ane_package.deliverable_doctor.__main__ import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
