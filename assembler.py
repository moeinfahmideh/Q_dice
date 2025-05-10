from __future__ import annotations
from pathlib import Path
from typing import Sequence
import copy as m21copy
from music21 import converter, stream, meter, tempo
from music21 import instrument

__all__ = ["assemble"]

def _clone_part_template(source_part: stream.Part) -> stream.Part:
    new_part = stream.Part(id=source_part.id)
    for el in source_part.getElementsByClass(instrument.Instrument):
        new_part.append(m21copy.deepcopy(el))
    return new_part

def assemble(sequence: Sequence[int], mxl_dir: str | Path, out_file: str | Path) -> None:
    mxl_dir = Path(mxl_dir)
    if not mxl_dir.is_dir():
        raise NotADirectoryError(mxl_dir)

    first_path = mxl_dir / f"mg_{sequence[0]}.mxl"
    first_piece = converter.parse(first_path)
    part_count = len(first_piece.parts)
    if part_count == 0:
        raise ValueError(f"Snippet '{first_path}' has no parts.")

    master_score = stream.Score(id="MasterScore")
    master_parts = [_clone_part_template(p) for p in first_piece.parts]
    for p in master_parts:
        p.append(meter.TimeSignature("3/4"))  # set meter once at start
    master_score.append(master_parts)

    tempo_mark = first_piece.metronomeMarkBoundaries()[0][2] if first_piece.metronomeMarkBoundaries() else tempo.MetronomeMark(number=120)
    master_score.insert(0, tempo_mark)

    current_offset = 0.0
    for eid in sequence:
        snippet_path = mxl_dir / f"mg_{eid}.mxl"
        piece = converter.parse(snippet_path)
        parts = piece.parts

        if len(parts) != part_count:
            raise ValueError(f"Snippet {eid} has {len(parts)} parts, expected {part_count}.")

        duration = 0.0
        for idx, part in enumerate(parts):
            dest_part = master_parts[idx]
            flat = part.flatten()
            for el in flat.notesAndRests:
                dest_part.insert(current_offset + el.offset, m21copy.deepcopy(el))
            duration = max(duration, flat.highestTime)

        current_offset += duration

    master_score.write("mxl", fp=str(out_file))
    master_score.write("midi", fp=str(out_file.with_suffix(".mid")))
