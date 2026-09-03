from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils import ensure_outdir, plot_bar, plot_line, save_csv


def test_ensure_outdir_creates_nested_dirs(tmp_path: Path) -> None:
    target = tmp_path / "a" / "b" / "c"
    result = ensure_outdir(target)
    assert result == target
    assert target.is_dir()


def test_save_csv_round_trips(tmp_path: Path, sample_df: pd.DataFrame) -> None:
    out = save_csv(sample_df, tmp_path / "nested" / "out.csv")
    assert out.is_file()
    reloaded = pd.read_csv(out)
    assert len(reloaded) == len(sample_df)
    assert list(reloaded.columns) == list(sample_df.columns)


def test_plot_bar_writes_png(tmp_path: Path, sample_df: pd.DataFrame) -> None:
    by_region = sample_df.groupby("region", as_index=False)[["revenue"]].sum()
    out = plot_bar(by_region, "region", "revenue", "Revenue by Region", tmp_path / "bar.png")
    assert out.is_file()
    assert out.stat().st_size > 0


def test_plot_line_writes_png(tmp_path: Path, sample_df: pd.DataFrame) -> None:
    out = plot_line(sample_df, "order_id", "revenue", "Revenue by Order", tmp_path / "line.png")
    assert out.is_file()
    assert out.stat().st_size > 0
