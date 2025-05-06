from __future__ import annotations

from pathlib import Path
from typing import Sequence

from music21 import converter, stream

__all__ = ["assemble"]

def assemble(sequence: Sequence[int], mxl_dir: str | Path, out_file: str | Path) -> None:
    mxl_dir = Path(mxl_dir)
    if not mxl_dir.is_dir():
        raise NotADirectoryError(mxl_dir)

    score = stream.Score()
    part = stream.Part(id="UE_Part")
    offset = 0.0

    for eid in sequence:
        f = mxl_dir / f"mg_{eid}.mxl"
        if not f.is_file():
            raise FileNotFoundError(f)
        piece = converter.parse(f)
        flat = piece.flatten()
        for elem in flat.notesAndRests:
            part.insert(offset + elem.offset, elem)
        offset += flat.highestTime

    score.append(part)

    score.write("mxl", fp=str(out_file))
    midi_path = out_file.with_suffix(".mid")
    score.write("midi", fp=str(midi_path))