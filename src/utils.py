from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def ensure_outdir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def save_csv(df: pd.DataFrame, path: str | Path, index: bool = False) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)
    return path

def plot_bar(df: pd.DataFrame, x: str, y: str, title: str, out_path: str | Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df[x], df[y])
    ax.set_title(title)
    ax.set_xlabel(x.replace('_', ' ').title())
    ax.set_ylabel(y.replace('_', ' ').title())
    plt.xticks(rotation=30, ha='right')
    out_path = Path(out_path)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path

def plot_line(df: pd.DataFrame, x: str, y: str, title: str, out_path: str | Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df[x], df[y])
    ax.set_title(title)
    ax.set_xlabel(x.replace('_', ' ').title())
    ax.set_ylabel(y.replace('_', ' ').title())
    plt.xticks(rotation=45, ha='right')
    out_path = Path(out_path)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
