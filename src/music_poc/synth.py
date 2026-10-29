"""Classic synth for test fixtures, mirroring Sound.py's model — fixed.

Sound.py's model, in brief: a note is a sine at its frequency times an
envelope; a chord is the mean of its notes' waveforms; a piece is its
events laid out sequentially. Two Sound.py bugs are NOT replicated here:

- Sound.py's "square" branch actually returned a sine. There is no
  square branch here at all.
- Sound.py's WAV writer (''.join(struct.pack(...))) only worked under
  Python 2. Rendering here uses numpy + the wave module (see audio.py).

Styles in v0:
- "guitar-pluck": sine * gaussian decay envelope, sigma = duration/2
  (Sound.py's dampfactor=2), i.e. fast attack, exponential decay.
- "viola-bow": sine with vibrato (5.5 Hz, phase modulation) times a
  sustain envelope: 0.1 s attack ramp, sustain, 0.1 s release ramp.
  Vibrato is part of the style token's meaning, not a pitch error.
- Any other style raises ValueError — silently falling back to a default
  timbre would make style-token tests meaningless.

Tempo mapping (v2 semantics, explicit): duration is in beats,
seconds = beats * 60 / tempo_bpm. Sound.py's blacknote/speed mapping is
not reused here; it was the least documented part of the original.
"""
from __future__ import annotations

import numpy as np

from .audio import write_wav
from .internal import Chord, Note, Piece


def _envelope(style: str, t: np.ndarray, duration_s: float) -> np.ndarray:
    if style == "guitar-pluck":
        sigma = duration_s / 2.0
        return np.exp(-((t / sigma) ** 2) / 2.0)
    if style == "viola-bow":
        attack = min(0.1, duration_s / 4.0)
        release = min(0.1, duration_s / 4.0)
        env = np.ones_like(t)
        attack_n = int(attack * len(t) / duration_s) if duration_s > 0 else 0
        release_n = int(release * len(t) / duration_s) if duration_s > 0 else 0
        if attack_n > 0:
            env[:attack_n] = np.linspace(0.0, 1.0, attack_n)
        if release_n > 0:
            env[-release_n:] = np.linspace(1.0, 0.0, release_n)
        return env
    raise ValueError(f"unknown style: {style!r}")


def note_waveform(note: Note, sr: int, tempo_bpm: float) -> np.ndarray:
    duration_s = float(note.duration) * 60.0 / tempo_bpm
    n = int(round(sr * duration_s))
    if n <= 0 or note.is_rest:
        return np.zeros(n)
    t = np.arange(n) / sr
    if note.style == "viola-bow":
        # Phase-modulated vibrato: 5.5 Hz, small depth, so the centre
        # pitch stays the note's frequency.
        phase = 2 * np.pi * note.frequency * t + 0.3 * np.sin(2 * np.pi * 5.5 * t)
        carrier = np.sin(phase)
    else:
        carrier = np.sin(2 * np.pi * note.frequency * t)
    return carrier * _envelope(note.style, t, duration_s)


def render_piece(piece: Piece) -> np.ndarray:
    parts = []
    for event in piece.events:
        if isinstance(event, Note):
            parts.append(note_waveform(event, piece.framerate, piece.tempo_bpm))
        elif isinstance(event, Chord):
            waves = [
                note_waveform(n, piece.framerate, piece.tempo_bpm)
                for n in event.notes
            ]
            parts.append(sum(waves) / len(waves))
        else:  # pragma: no cover - Piece only holds Note/Chord
            raise ValueError(f"unknown event: {event!r}")
    if not parts:
        return np.zeros(0)
    return np.concatenate(parts)


def render_piece_to_wav(piece: Piece, path: str) -> None:
    samples = render_piece(piece)
    # Normalize to a fixed peak so fixtures are comparable across styles.
    peak = np.max(np.abs(samples)) if len(samples) else 0.0
    if peak > 0:
        samples = samples * (0.8 / peak)
    write_wav(path, samples, piece.framerate)
