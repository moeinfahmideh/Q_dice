from __future__ import annotations
from pathlib import Path
import os
from table import load_lookup_table
from composer import Composer
from assembler import assemble

TABLE_CSV = Path("UE_lookup.csv")
MXL_DIR   = Path("MusicXML")
OUT_DIR   = Path("output")       
LOG_FILE  = OUT_DIR / "sequences.log"
BACKEND   = "aer_simulator"      

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        count = int(input("How many compositions would you like to generate? "))
        if count <= 0:
            raise ValueError
    except ValueError:
        print("Please enter a positive integer.")
        return

    table = load_lookup_table(TABLE_CSV)
    composer = Composer(table)

    with LOG_FILE.open("w") as log:
        for i in range(1, count + 1):
            seq = composer.generate()
            out_file = OUT_DIR / f"composition_{i}.mxl"
            assemble(seq, MXL_DIR, out_file)
            print(f"[{i}/{count}] Saved {out_file.relative_to(OUT_DIR)}")
            log.write(f"{i}: {seq}\n")

    print("\nDone!  All compositions are in", OUT_DIR.resolve())
    print("Sequences logged to", LOG_FILE.resolve())

if __name__ == "__main__":
    main()
