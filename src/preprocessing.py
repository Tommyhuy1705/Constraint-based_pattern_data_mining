from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Set

from .utils import ensure_package


DEFAULT_SUPPORTED_EXTENSIONS: Set[str] = {".csv", ".xlsx", ".xls"}


def infer_csv_separator(dataset_path: Path) -> str:
    """Infer the CSV separator from the first line."""
    with dataset_path.open("r", encoding="utf-8-sig", errors="ignore") as f:
        first_line = f.readline()
    candidates = [";", ",", "\t", "|"]
    return max(candidates, key=lambda sep: first_line.count(sep))


def read_preview_columns(dataset_path: Path):
    """Read a few rows to detect available columns."""
    import pandas as pd

    suffix = dataset_path.suffix.lower()
    if suffix == ".csv":
        sep = infer_csv_separator(dataset_path)
        preview = pd.read_csv(dataset_path, sep=sep, nrows=5, dtype="string")
    elif suffix in {".xlsx", ".xls"}:
        ensure_package("openpyxl")
        preview = pd.read_excel(dataset_path, nrows=5, dtype="string")
    else:
        return []
    return list(preview.columns)


def looks_like_target_dataset(dataset_path: Path, required_columns: Sequence[str]) -> bool:
    """Check whether a dataset contains the required columns."""
    try:
        columns = read_preview_columns(dataset_path)
    except Exception:
        return False
    return set(required_columns).issubset(set(columns))


def candidate_dataset_files(
    project_root: Path,
    output_dir: Path,
    dataset_path_override: str,
    in_colab: bool,
    supported_extensions: Optional[Set[str]] = None,
):
    """Yield candidate dataset files under the project root."""
    if dataset_path_override:
        yield Path(dataset_path_override).expanduser()

    search_roots = [project_root]
    if in_colab:
        search_roots.append(Path("/content"))

    seen = set()
    candidates = []
    extensions = supported_extensions or DEFAULT_SUPPORTED_EXTENSIONS
    for root in search_roots:
        if not root.exists():
            continue
        for suffix in extensions:
            candidates.extend(root.glob(f"*{suffix}"))
            candidates.extend(root.glob(f"*/*{suffix}"))
            candidates.extend(root.glob(f"**/*{suffix}"))

    def sort_key(path: Path):
        suffix_rank = 0 if path.suffix.lower() == ".csv" else 1
        return (suffix_rank, len(path.parts), path.name.lower())

    for path in sorted(candidates, key=sort_key):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if output_dir in resolved.parents:
            continue
        yield resolved


def find_dataset(
    project_root: Path,
    required_columns: Sequence[str],
    output_dir: Path,
    dataset_path_override: str = "",
    in_colab: bool = False,
    supported_extensions: Optional[Set[str]] = None,
) -> Path:
    """Find a dataset by extension and required columns."""
    extensions = supported_extensions or DEFAULT_SUPPORTED_EXTENSIONS
    for path in candidate_dataset_files(
        project_root,
        output_dir,
        dataset_path_override,
        in_colab,
        extensions,
    ):
        if path.exists() and path.suffix.lower() in extensions and looks_like_target_dataset(path, required_columns):
            return path

    if in_colab:
        from google.colab import files  # type: ignore

        print("Dataset not found. Please upload a CSV or Excel file with the required columns.")
        uploaded = files.upload()
        for filename in uploaded.keys():
            uploaded_path = Path("/content") / filename
            if (
                uploaded_path.suffix.lower() in extensions
                and looks_like_target_dataset(uploaded_path, required_columns)
            ):
                return uploaded_path

    raise FileNotFoundError(
        "No valid dataset found. Place a CSV/Excel file with columns "
        f"{list(required_columns)} in the project root or set MARKET_BASKET_DATASET_PATH."
    )


def read_market_basket_dataset(dataset_path: Path):
    """Read a Market Basket dataset from CSV or Excel."""
    import pandas as pd

    suffix = dataset_path.suffix.lower()
    if suffix == ".csv":
        sep = infer_csv_separator(dataset_path)
        df = pd.read_csv(dataset_path, sep=sep, dtype="string")
    elif suffix in {".xlsx", ".xls"}:
        ensure_package("openpyxl")
        df = pd.read_excel(dataset_path, dtype="string")
    else:
        raise ValueError(f"Unsupported dataset format: {dataset_path.suffix}")

    return df
