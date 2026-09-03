"""Small I/O and plotting helpers shared by create_db.py and analyze_sales.py."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
import pandas as pd


def ensure_outdir(path: str | Path) -> Path:
    """Create ``path`` (and parents) if needed and return it as a Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_csv(df: pd.DataFrame, path: str | Path, index: bool = False) -> Path:
    """Write ``df`` to ``path`` as CSV, creating parent directories as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)
    return path


def _plot(
    kind: Literal["bar", "line"],
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    out_path: str | Path,
    *,
    tick_rotation: int,
) -> Path:
    """Shared chart rendering for ``plot_bar``/``plot_line``: set up the figure,
    draw ``y`` vs ``x`` as ``kind``, apply common styling, and save as PNG."""
    fig, ax = plt.subplots(figsize=(8, 5))
    if kind == "bar":
        ax.bar(df[x], df[y])
    else:
        ax.plot(df[x], df[y])
    ax.set_title(title)
    ax.set_xlabel(x.replace("_", " ").title())
    ax.set_ylabel(y.replace("_", " ").title())
    plt.xticks(rotation=tick_rotation, ha="right")
    out_path = Path(out_path)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_bar(df: pd.DataFrame, x: str, y: str, title: str, out_path: str | Path) -> Path:
    """Render a bar chart of ``y`` vs ``x`` and save it as a PNG to ``out_path``."""
    return _plot("bar", df, x, y, title, out_path, tick_rotation=30)


def plot_line(df: pd.DataFrame, x: str, y: str, title: str, out_path: str | Path) -> Path:
    """Render a line chart of ``y`` vs ``x`` and save it as a PNG to ``out_path``."""
    return _plot("line", df, x, y, title, out_path, tick_rotation=45)
