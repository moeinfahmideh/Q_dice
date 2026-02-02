from __future__ import annotations

from pathlib import Path
from typing import Sequence
import copy as m21copy

from music21 import converter, stream, meter, tempo, instrument, clef, key

__all__ = ["assemble_midi"]


def _clone_part_template(source_part: stream.Part) -> stream.Part:
    new_part = stream.Part(id=source_part.id)

    for el in source_part.getElementsByClass(instrument.Instrument):
        new_part.append(m21copy.deepcopy(el))

    for el in source_part.getElementsByClass(clef.Clef):
        new_part.append(m21copy.deepcopy(el))

    for el in source_part.getElementsByClass(key.KeySignature):
        new_part.append(m21copy.deepcopy(el))

    return new_part


def assemble_midi(sequence: Sequence[int], midi_dir: str | Path, out_file: str | Path) -> None:
    midi_dir = Path(midi_dir)
    out_file = Path(out_file)

    if not midi_dir.is_dir():
        raise NotADirectoryError(midi_dir)

    if out_file.suffix.lower() != ".mid":
        out_file = out_file.with_suffix(".mid")

    if not sequence:
        raise ValueError("Sequence is empty.")

    first_path = midi_dir / f"mg_{sequence[0]}.mid"
    if not first_path.is_file():
        raise FileNotFoundError(first_path)

    first_piece = converter.parse(first_path)
    part_count = len(first_piece.parts)
    if part_count == 0:
        raise ValueError(f"Snippet '{first_path}' has no parts.")

    master_score = stream.Score(id="MasterScore")
    master_parts = [_clone_part_template(p) for p in first_piece.parts]

    ts_list = first_piece.recurse().getElementsByClass(meter.TimeSignature)
    ts = ts_list[0] if ts_list else meter.TimeSignature("3/4")
    for p in master_parts:
        p.append(m21copy.deepcopy(ts))

    mmb = first_piece.metronomeMarkBoundaries()
    mm = mmb[0][2] if mmb else tempo.MetronomeMark(number=120)
    master_score.insert(0, mm)

    master_score.append(master_parts)

    current_offset = 0.0
    for eid in sequence:
        snippet_path = midi_dir / f"mg_{eid}.mid"
        if not snippet_path.is_file():
            raise FileNotFoundError(snippet_path)

        piece = converter.parse(snippet_path)
        parts = piece.parts

        if len(parts) != part_count:
            raise ValueError(f"Snippet {eid} has {len(parts)} parts, expected {part_count}.")

        duration = 0.0
        for idx, part in enumerate(parts):
            dest_part = master_parts[idx]
            flat = part.flatten()

            start = flat.lowestOffset if flat.notesAndRests else 0.0

            for el in flat.notesAndRests:
                dest_part.insert(current_offset + (el.offset - start), m21copy.deepcopy(el))

            duration = max(duration, max(0.0, flat.highestTime - start))

        current_offset += duration

    master_score.write("midi", fp=str(out_file))
