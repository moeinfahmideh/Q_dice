from __future__ import annotations
from pathlib import Path
import pandas as pd

__all__ = ["load_lookup_table"]

def load_lookup_table(csv_path: str | Path) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(csv_path)
    df = pd.read_csv(path, index_col=0)
    if list(df.columns) != list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        raise ValueError("CSV must have columns A–Z in order.")
    if list(df.index) != list(range(11)):
        raise ValueError("CSV must have rows 0–10.")
    return df