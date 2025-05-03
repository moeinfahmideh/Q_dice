from __future__ import annotations
from pathlib import Path
from typing import Sequence
from music21 import converter, stream

__all__ = ["assemble"]

def assemble(sequence: Sequence[int], mxl_dir: str | Path, out_file: str | Path) -> None:
    mxl_dir = Path(mxl_dir)
    if not mxl_dir.is_dir():
        raise NotADirectoryError(mxl_dir)

    master_score = stream.Score()
    master_part = stream.Part(id="UE_Part")
    current_offset = 0.0  

    for eid in sequence:
        f = mxl_dir / f"mg_{eid}.mxl"
        if not f.is_file():
            raise FileNotFoundError(f)

        piece = converter.parse(f)
        flat = piece.flatten()
        duration_qL = flat.highestTime  

        for elem in flat.notesAndRests:
            master_part.insert(current_offset + elem.offset, elem)
        current_offset += duration_qL

    master_score.append(master_part)
    master_score.write("mxl", fp=str(out_file))