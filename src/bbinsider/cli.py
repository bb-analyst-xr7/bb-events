from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    # Load root-level main.py so users can run from repo root without refactor.
    module = _load_module(Path.cwd() / "main.py", "_bbinsider_main")
    module.main()


def shotchart() -> None:
    # Load root-level event.py so users can run from repo root without refactor.
    module = _load_module(Path.cwd() / "event.py", "_bbinsider_event")
    module.shotchart_main()


def buzzerbeaters() -> None:
    # Load root-level buzzerbeaters.py so users can run from repo root without refactor.
    module = _load_module(Path.cwd() / "buzzerbeaters.py", "_bbinsider_buzzerbeaters")
    module.main()


def normalize_buzzerbeater_periods() -> None:
    # Load root-level normalize_buzzerbeater_periods.py from repo root.
    module = _load_module(
        Path.cwd() / "normalize_buzzerbeater_periods.py",
        "_bbinsider_normalize_buzzerbeater_periods",
    )
    module.main()


def team_info() -> None:
    # Load root-level team_info.py from repo root.
    module = _load_module(Path.cwd() / "team_info.py", "_bbinsider_team_info")
    module.main()


def team_buzzerbeaters() -> None:
    # Load root-level team_buzzerbeaters.py from repo root.
    module = _load_module(
        Path.cwd() / "team_buzzerbeaters.py",
        "_bbinsider_team_buzzerbeaters",
    )
    module.main()


def debug_ot_buzzers() -> None:
    # Load root-level debug_ot_buzzers.py from repo root.
    module = _load_module(Path.cwd() / "debug_ot_buzzers.py", "_bbinsider_debug_ot_buzzers")
    module.main()
