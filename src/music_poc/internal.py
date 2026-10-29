"""Internal piece representation, v2 (minimal, testable core).

This is a deliberate break from Sound.py in three places, all documented
so the old behaviour is not silently reintroduced:

- Durations are fractions.Fraction (in beats; 1 = one quarter note),
  not floats. Sound.py compared float lengths with ==, which only worked
  for dyadic durations and silently left notes nameless otherwise.
- A chord's notes must all share a duration; violation raises ValueError
  instead of printing an error and calling exit(), as Sound.py did.
- Style is a structured token string, not a waveform branch name:
  "guitar-pluck" (fast attack, exponential decay) and "viola-bow"
  (slow attack, sustain, vibrato) in v0. The token is a conditioning code
  for a neural decoder and a literal envelope recipe only in the classic
  synth (see synth.py) — those are two roles for one token, not one
  implementation.

A rest is a Note with frequency 0.0.

Original code (reference only, not copied here):
diogenes1991/Small_Projects, Sound/Sound.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Union


@dataclass(frozen=True)
class Note:
    frequency: float  # Hz; 0.0 means rest
    duration: Fraction  # beats; 1 = quarter note
    style: str = "guitar-pluck"

    def __post_init__(self):
        if self.duration <= 0:
            raise ValueError(f"note duration must be positive, got {self.duration}")
        if self.frequency < 0:
            raise ValueError(f"frequency must be >= 0, got {self.frequency}")

    @property
    def is_rest(self) -> bool:
        return self.frequency == 0.0

    def to_dict(self) -> dict:
        return {
            "type": "note",
            "frequency": self.frequency,
            "duration": str(self.duration),
            "style": self.style,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Note":
        return cls(
            frequency=float(d["frequency"]),
            duration=Fraction(d["duration"]),
            style=d.get("style", "guitar-pluck"),
        )


@dataclass(frozen=True)
class Chord:
    notes: List[Note]

    def __post_init__(self):
        if not self.notes:
            raise ValueError("chord must contain at least one note")
        durations = {n.duration for n in self.notes}
        if len(durations) != 1:
            raise ValueError(
                f"all chord notes must share a duration, got {durations}"
            )

    @property
    def duration(self) -> Fraction:
        return self.notes[0].duration

    def to_dict(self) -> dict:
        return {"type": "chord", "notes": [n.to_dict() for n in self.notes]}

    @classmethod
    def from_dict(cls, d: dict) -> "Chord":
        return cls(notes=[Note.from_dict(n) for n in d["notes"]])


Event = Union[Note, Chord]


@dataclass
class Piece:
    events: List[Event] = field(default_factory=list)
    tempo_bpm: float = 120.0
    framerate: int = 44100
    title: str = "test-piece"

    @property
    def total_beats(self) -> Fraction:
        total = Fraction(0)
        for e in self.events:
            total += e.duration
        return total

    @property
    def total_seconds(self) -> float:
        return float(self.total_beats) * 60.0 / self.tempo_bpm

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "tempo_bpm": self.tempo_bpm,
            "framerate": self.framerate,
            "events": [
                e.to_dict() if isinstance(e, Note) else e.to_dict()
                for e in self.events
            ],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Piece":
        events: List[Event] = []
        for e in d["events"]:
            if e["type"] == "note":
                events.append(Note.from_dict(e))
            elif e["type"] == "chord":
                events.append(Chord.from_dict(e))
            else:
                raise ValueError(f"unknown event type: {e['type']}")
        return cls(
            events=events,
            tempo_bpm=float(d["tempo_bpm"]),
            framerate=int(d["framerate"]),
            title=d["title"],
        )
