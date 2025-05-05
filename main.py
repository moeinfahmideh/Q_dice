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


def prompt_positive_int(msg: str) -> int:
    try:
        value = int(input(msg))
        if value <= 0:
            raise ValueError
    except ValueError:
        print("Please enter a positive integer.")
        sys.exit(1)
    return value


def prompt_sequence() -> list[int]:
    raw = input(
        "Enter 25 integers between 1 and 188 (comma or space‑separated):\n> "
    )
    tokens = [tok.strip() for tok in raw.replace(",", " ").split()]
    if len(tokens) != 25:
        print("You must provide exactly 25 numbers.")
        sys.exit(1)
    try:
        nums = [int(tok) for tok in tokens]
    except ValueError:
        print("All entries must be integers.")
        sys.exit(1)
    if not all(1 <= n <= 188 for n in nums):
        print("Each number must be between 1 and 188.")
        sys.exit(1)
    return nums  


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    table = load_lookup_table(TABLE_CSV)

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
                print(f"[{i}/{count}] Saved {out_file.name}")
                log.write(f"auto_{i}: {seq}\n")

    elif mode == "2":
        seq = prompt_sequence()
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        out_file = OUT_DIR / f"composition_custom_{timestamp}.mxl"
        assemble(seq, MXL_DIR, out_file)
        with LOG_FILE.open("a") as log:
            log.write(f"custom_{timestamp}: {seq}\n")
        print("Saved", out_file.name)

    else:
        print("Invalid mode. Please run again and choose 1 or 2.")
        sys.exit(1)


if __name__ == "__main__":
    main()