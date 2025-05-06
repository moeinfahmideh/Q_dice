from __future__ import annotations

from pathlib import Path
import sys
import time

from table import load_lookup_table
from composer import Composer
from assembler import assemble

TABLE_CSV = Path("UE_lookup.csv")
MXL_DIR   = Path("MusicXML")
OUT_DIR   = Path("output")
LOG_FILE  = OUT_DIR / "sequences.log"
COLS = list("ABCDEFGHIJKLMNOPQRSTUVWXY")  

def prompt_positive_int(msg: str) -> int:
    try:
        value = int(input(msg))
        if value <= 0:
            raise ValueError
    except ValueError:
        print("Please enter a positive integer.")
        sys.exit(1)
    return value


def prompt_row_sequence() -> list[int]:
    raw = input(
        "Enter 25 integers between 0‑10 separated by spaces/commas:> "
    )
    tokens = [tok.strip() for tok in raw.replace(",", " ").split()]
    if len(tokens) != 25:
        print("You must provide exactly 25 numbers.")
        sys.exit(1)

    rows: list[int] = []
    for tok in tokens:
        try:
            n = int(tok)
        except ValueError:
            print(f"'{tok}' is not an integer.")
            sys.exit(1)
        if 0 <= n <= 10:
            rows.append(n)
        elif 1 <= n <= 11:
            rows.append(n - 1)
        else:
            print("Each number must be between 0‑10 or 1‑11.")
            sys.exit(1)
    return rows


def rows_to_ue_sequence(rows: list[int], table) -> list[int]:
    if len(rows) != 25:
        raise ValueError("Need 25 row indices for columns A‑Y.")
    seq = [int(table.loc[row, col]) for col, row in zip(COLS, rows)]
    seq.append(188)
    return seq


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    table = load_lookup_table(TABLE_CSV)

    print("Choose mode: 1) Quantum‑dice compositions 2) Custom row indices (0‑10 / 1‑11)")
    mode = input("Enter 1 or 2: ").strip()

    if mode == "1":
        count = prompt_positive_int("How many compositions to generate? ")
        composer = Composer(table)
        with LOG_FILE.open("a") as log:
            for i in range(1, count + 1):
                seq = composer.generate()
                out_file = OUT_DIR / f"composition_{i}.mxl"
                assemble(seq, MXL_DIR, out_file)
                print(f"[{i}/{count}] Saved")
                print(seq)
                log.write(f"auto_{i}: {seq}")

    elif mode == "2":
        rows = prompt_row_sequence()
        seq = rows_to_ue_sequence(rows, table)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        out_file = OUT_DIR / f"composition_custom_{timestamp}.mxl"
        assemble(seq, MXL_DIR, out_file)
        with LOG_FILE.open("a") as log:
            log.write(f"custom_{timestamp}: {seq}")
        print("Saved", out_file.name)

    else:
        print("Invalid mode. Please run again and choose 1 or 2.")
        sys.exit(1)


if __name__ == "__main__":
    main()