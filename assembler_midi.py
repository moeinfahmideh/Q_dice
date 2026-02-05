from __future__ import annotations

from pathlib import Path
from typing import Sequence, List, Tuple
import mido

__all__ = ["assemble_midi"]


def _track_to_absolute(track: mido.MidiTrack) -> List[Tuple[int, mido.Message]]:
    t = 0
    out: List[Tuple[int, mido.Message]] = []
    for msg in track:
        t += int(msg.time)
        out.append((t, msg))
    return out


def _events_to_delta(events: List[Tuple[int, mido.Message]]) -> mido.MidiTrack:
    events.sort(key=lambda x: x[0])
    tr = mido.MidiTrack()
    last = 0
    for t, msg in events:
        tr.append(msg.copy(time=int(t - last)))
        last = t
    return tr


def _strip_tempo_and_time_meta(track: mido.MidiTrack) -> mido.MidiTrack:
    filtered = mido.MidiTrack()
    for msg in track:
        if msg.is_meta and msg.type in {"set_tempo", "time_signature", "key_signature"}:
            continue
        filtered.append(msg)
    return filtered


def assemble_midi(sequence: Sequence[int], midi_dir: str | Path, out_file: str | Path) -> None:
    midi_dir = Path(midi_dir)
    out_file = Path(out_file)

    if not midi_dir.is_dir():
        raise NotADirectoryError(midi_dir)
    if not sequence:
        raise ValueError("Sequence is empty.")
    if out_file.suffix.lower() != ".mid":
        out_file = out_file.with_suffix(".mid")

    first_path = midi_dir / f"mg_{sequence[0]}.mid"
    if not first_path.is_file():
        raise FileNotFoundError(first_path)

    first_mid = mido.MidiFile(first_path)
    ticks_per_beat = first_mid.ticks_per_beat
    track_count = len(first_mid.tracks)

    out_mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    out_tracks_events: List[List[Tuple[int, mido.Message]]] = [[] for _ in range(track_count)]

    current_tick = 0

    for i, eid in enumerate(sequence):
        path = midi_dir / f"mg_{eid}.mid"
        if not path.is_file():
            raise FileNotFoundError(path)

        mid = mido.MidiFile(path)
        if mid.ticks_per_beat != ticks_per_beat:
            raise ValueError(
                f"ticks_per_beat mismatch in {path.name}: {mid.ticks_per_beat} != {ticks_per_beat}"
            )
        if len(mid.tracks) != track_count:
            raise ValueError(
                f"Track count mismatch in {path.name}: {len(mid.tracks)} != {track_count}"
            )

        track_end_ticks: List[int] = []
        abs_tracks: List[List[Tuple[int, mido.Message]]] = []

        for tr in mid.tracks:
            tr_use = tr if i == 0 else _strip_tempo_and_time_meta(tr)
            abs_ev = _track_to_absolute(tr_use)
            abs_tracks.append(abs_ev)
            track_end_ticks.append(abs_ev[-1][0] if abs_ev else 0)

        snippet_ticks = max(track_end_ticks) if track_end_ticks else 0

        for t_idx, abs_ev in enumerate(abs_tracks):
            for t, msg in abs_ev:
                out_tracks_events[t_idx].append((current_tick + t, msg))

        current_tick += snippet_ticks

    for ev in out_tracks_events:
        out_mid.tracks.append(_events_to_delta(ev))

    out_mid.save(str(out_file))
