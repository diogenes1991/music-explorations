#!/usr/bin/env python3
"""Generate synthetic test fixtures: WAV + internal-rep JSON per fixture.

Fixtures (all at 120 bpm unless noted, so 1 beat = 0.5 s):
- melody_guitar: 8 single notes, guitar-pluck style.
- melody_viola: the SAME 8 notes, viola-bow style — the style-contrast
  pair. Same pitch sequence, different timbre token.
- chords_guitar: 4 two-note chords, guitar-pluck style.
- piece_10s: exactly 20 quarter notes = 10.0 s at 120 bpm, for chunking tests.
- melody_with_rests: single notes + rests (frequency 0), guitar-pluck.

Output: tests/fixtures/<name>.wav and tests/fixtures/<name>.json.
The JSON is Piece.to_dict() output, so a test can load the WAV and the
internal rep independently and check they agree.
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from music_poc.internal import Chord, Note, Piece
from music_poc.synth import render_piece_to_wav

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(ROOT, "tests", "fixtures")

MELODY = [
    (440.00, Fraction(1)),   # A4
    (523.25, Fraction(1)),   # C5
    (659.25, Fraction(1)),   # E5
    (392.00, Fraction(1)),   # G4
    (440.00, Fraction(1, 2)),
    (523.25, Fraction(1, 2)),
    (659.25, Fraction(1)),
    (440.00, Fraction(2)),
]


def melody_piece(style: str) -> Piece:
    return Piece(
        events=[Note(f, d, style) for f, d in MELODY],
        tempo_bpm=120.0,
        title=f"melody_{style}",
    )


def main():
    os.makedirs(FIXTURES, exist_ok=True)
    pieces = {
        "melody_guitar": melody_piece("guitar-pluck"),
        "melody_viola": melody_piece("viola-bow"),
        "chords_guitar": Piece(
            events=[
                Chord([Note(440.00, Fraction(2), "guitar-pluck"),
                       Note(554.37, Fraction(2), "guitar-pluck")]),
                Chord([Note(392.00, Fraction(2), "guitar-pluck"),
                       Note(523.25, Fraction(2), "guitar-pluck")]),
                Chord([Note(329.63, Fraction(2), "guitar-pluck"),
                       Note(440.00, Fraction(2), "guitar-pluck")]),
                Chord([Note(440.00, Fraction(2), "guitar-pluck"),
                       Note(659.25, Fraction(2), "guitar-pluck")]),
            ],
            tempo_bpm=120.0,
            title="chords_guitar",
        ),
        "piece_10s": Piece(
            events=[Note(440.00, Fraction(1), "guitar-pluck")] * 20,
            tempo_bpm=120.0,
            title="piece_10s",
        ),
        "melody_with_rests": Piece(
            events=[
                Note(440.00, Fraction(1), "guitar-pluck"),
                Note(0.0, Fraction(1), "guitar-pluck"),
                Note(523.25, Fraction(1), "guitar-pluck"),
                Note(0.0, Fraction(1, 2), "guitar-pluck"),
                Note(659.25, Fraction(1, 2), "guitar-pluck"),
            ],
            tempo_bpm=120.0,
            title="melody_with_rests",
        ),
    }
    for name, piece in pieces.items():
        wav = os.path.join(FIXTURES, f"{name}.wav")
        js = os.path.join(FIXTURES, f"{name}.json")
        render_piece_to_wav(piece, wav)
        with open(js, "w") as f:
            json.dump(piece.to_dict(), f, indent=2)
        print(f"{name}: {piece.total_seconds:.2f} s, {len(piece.events)} events -> {wav}")
    print(f"Fixtures in {FIXTURES}")


if __name__ == "__main__":
    main()
