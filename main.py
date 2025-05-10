from __future__ import annotations
from pathlib import Path
import sys, time
from table import load_lookup_table
from composer import Composer
from assembler import assemble

TABLE_CSV = Path("UE_lookup.csv")
MXL_DIR   = Path("MusicXML")
OUT_DIR   = Path("output")
LOG_FILE  = OUT_DIR / "sequences.log"

def prompt_positive_int(msg: str) -> int:
    try:
        n = int(input(msg))
        if n <= 0:
            raise ValueError
    except ValueError:
        print("Please enter a positive integer.")
        sys.exit(1)
    return n


def prompt_rows() -> list[int]:
    raw = input(
        "Enter 25 integers between 1 and 11 (row indices for A–Y):\n> "
    )
    tokens = [tok.strip() for tok in raw.replace(",", " ").split()]
    if len(tokens) != 25:
        print("You must provide exactly 25 numbers.")
        sys.exit(1)
    try:
        rows = [int(tok) for tok in tokens]
    except ValueError:
        print("All entries must be integers.")
        sys.exit(1)
    if not all(1 <= r <= 11 for r in rows):
        print("Each number must be between 1 and 11.")
        sys.exit(1)
    return rows

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    table = load_lookup_table(TABLE_CSV)
    cols = list("ABCDEFGHIJKLMNOPQRSTUVWXY")

    print("Choose mode:\n  1) Quantum‑dice compositions\n  2) Custom sequence")
    mode = input("Enter 1 or 2: ").strip()

    if mode == "1":
        count = prompt_positive_int("How many compositions to generate? ")
        composer = Composer(table)
        with LOG_FILE.open("a") as log:
            for i in range(1, count + 1):
                seq = composer.generate()
                out_file = OUT_DIR / f"composition_{i}.mxl"
                assemble(seq, MXL_DIR, out_file)
                print(f"[{i}/{count}] Saved {out_file.stem}.mxl & .mid")
                log.write(f"auto_{i}: {seq}\n")

    elif mode == "2":
        rows = prompt_rows()           
        seq  = [int(table.loc[r - 1, c]) for r, c in zip(rows, cols)]
        seq.append(188)

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        out_file  = OUT_DIR / f"composition_custom_{timestamp}.mxl"
        assemble(seq, MXL_DIR, out_file)

        with LOG_FILE.open("a") as log:
            log.write(f"custom_{timestamp}: {seq}\n")
        print(f"Saved {out_file.stem}.mxl & .mid")

    else:
        print("Invalid mode. Please run again and choose 1 or 2.")
        sys.exit(1)


if __name__ == "__main__":
    main()
