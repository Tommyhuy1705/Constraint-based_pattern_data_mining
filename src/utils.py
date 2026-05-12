from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence


def ensure_package(import_name: str, pip_name: Optional[str] = None) -> None:
    """Ensure a package is available, installing via pip if needed."""
    pip_name = pip_name or import_name
    if importlib.util.find_spec(import_name) is None:
        bundled_packages = (
            Path.home()
            / ".cache"
            / "codex-runtimes"
            / "codex-primary-runtime"
            / "dependencies"
            / "python"
        )
        if bundled_packages.exists() and str(bundled_packages) not in sys.path:
            sys.path.insert(0, str(bundled_packages))

    if importlib.util.find_spec(import_name) is None:
        print(f"Missing package '{import_name}'. Installing '{pip_name}'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])


def parse_support_ratios(value: str, default_ratios: Sequence[float]) -> List[float]:
    """Parse flexible support ratios like '5%,4%,3%' or '0.05,0.04'."""
    if not value:
        return list(default_ratios)
    ratios: List[float] = []
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        if token.endswith("%"):
            ratios.append(float(token[:-1]) / 100)
        else:
            number = float(token)
            ratios.append(number / 100 if number > 1 else number)
    return ratios


def find_artifact(filename: str, output_dir: Path, project_root: Path, in_colab: bool) -> Path:
    """Find an artifact file under output_dir, project_root, or /content."""
    direct_candidates = [output_dir / filename, project_root / filename]
    search_roots = [project_root]
    if in_colab:
        search_roots.append(Path("/content"))

    seen = set()
    for path in direct_candidates:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            if resolved.exists():
                return resolved

    for root in search_roots:
        if not root.exists():
            continue
        for path in root.glob(f"**/{filename}"):
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                if resolved.exists():
                    return resolved

    return output_dir / filename
