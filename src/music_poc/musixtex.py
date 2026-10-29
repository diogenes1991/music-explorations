"""MusixTeX emitter, Python 3 port of Sound.py's create_latex/fill_latex.

What is preserved from Sound.py (so existing scores stay recognisable):
- The 60-letter pitch table, indexed by semitones above A1 = 55 Hz.
- Duration -> command mapping for whole/half/quarter/eighth/16th/32nd
  notes, and the separate rest-command mapping.
- Chord syntax: a \\zh / \\zq group for all but the last note, then a
  stemmed token for the last note.
- Two-staff layout split at 330 Hz, with \\hsk spacers on the other staff,
  and \\Notes ... | ... \\en groups per measure.
- Measure / line structure: 4/4 by default, 4 measures per line
  (\\zendextract / \\end{music} at line end, new \\begin{music} after).

What is deliberately changed (all are Sound.py bugs or silent failures):
- Durations are fractions.Fraction, not floats, and measure closing uses
  exact Fraction equality. An unsupported duration raises ValueError
  instead of leaving a note nameless and crashing later in fill_latex.
- Out-of-range pitches raise ValueError instead of IndexError (too high)
  or silently wrapping to the wrong pitch (too low, via negative indexing).
- A trailing partial measure raises ValueError instead of being silently
  dropped, and a trailing partial *line* is properly closed with
  \\zendextract / \\end{music} instead of being left unclosed (Sound.py
  only closed a block when it hit exactly cmpinline measures).
- The dead beamcounter logic is gone. The \\bar / \\Notes structure is
  emitted once per measure, explicitly.
- Title/composer are LaTeX-escaped. Sound.py interpolated them raw.
- No pdflatex is run here. Rendering a score is a separate step
  (pdflatex -> musixflx -> pdflatex, with return-code checking); this
  module only writes the .tex files, and returns their paths.
- Tempo: Sound.py wrote \\metron{\\qu}{60*blacknote} from its opaque
  blacknote/speed factor. Here the metronome mark is tempo_bpm directly
  (quarter notes per minute), which is what Piece.tempo_bpm means.

Chord staff assignment keeps Sound.py's behaviour (mean frequency of
the chord decides the staff) and is documented as a limitation in
docs/poc-scope.md — a chord straddling 330 Hz lands on one staff.
"""
from __future__ import annotations

import math
import os
from fractions import Fraction

from .internal import Chord, Note, Piece

NOTE_NAMES = [
    "A", "^A", "B", "C", "^C", "D", "^D", "E", "F", "^F", "G", "^G",
    "H", "^H", "I", "J", "^J", "K", "^K", "L", "M", "^M", "N", "^N",
    "a", "^a", "b", "c", "^c", "d", "^d", "e", "f", "^f", "g", "^g",
    "h", "^h", "i", "j", "^j", "k", "^k", "l", "m", "^m", "n", "^n",
    "o", "^o", "p", "q", "^q", "r", "^r", "s", "t", "^t", "u", "^u",
]

# duration (beats) -> (up-stem command, down-stem command)
PITCHED_COMMANDS = {
    Fraction(4): ("wh", "wh"),
    Fraction(2): ("hu", "hl"),
    Fraction(1): ("qu", "ql"),
    Fraction(1, 2): ("cu", "cl"),
    Fraction(1, 4): ("ccu", "ccl"),
    Fraction(1, 8): ("cccu", "cccl"),
}

REST_COMMANDS = {
    Fraction(4): "pausep",
    Fraction(2): "hp",
    Fraction(1): "qp",
    Fraction(1, 2): "ds",
    Fraction(1, 4): "qs",
    Fraction(1, 8): "hs",
}

STEM_FLIP_HZ = 523.25
STAFF_SPLIT_HZ = 330.0


def _pitch_letter(frequency: float) -> str:
    if frequency < 55.0 or frequency > 1661.22:
        raise ValueError(
            f"frequency {frequency} Hz outside MusixTeX range [55, 1661.22]"
        )
    index = int(round(12 * math.log(frequency / 55.0) / math.log(2)))
    if index < 0 or index >= len(NOTE_NAMES):
        raise ValueError(f"frequency {frequency} Hz maps outside pitch table")
    return NOTE_NAMES[index]


def _escape_latex(text: str) -> str:
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def note_token(note: Note) -> str:
    """MusixTeX token for a single note or rest (Sound.py note.__init__)."""
    if note.duration not in PITCHED_COMMANDS:
        raise ValueError(
            f"unsupported duration {note.duration} beats; "
            f"supported: {sorted(PITCHED_COMMANDS)}"
        )
    if note.is_rest:
        return "\\" + REST_COMMANDS[note.duration]
    up, down = PITCHED_COMMANDS[note.duration]
    command = up if note.frequency <= STEM_FLIP_HZ else down
    return "\\" + command + "{" + _pitch_letter(note.frequency) + "}"


def chord_token(chord: Chord) -> str:
    """MusixTeX token for a chord (Sound.py chord.__init__)."""
    if chord.duration not in PITCHED_COMMANDS:
        raise ValueError(
            f"unsupported chord duration {chord.duration} beats; "
            f"supported: {sorted(PITCHED_COMMANDS)}"
        )
    group = "zh" if chord.duration in (Fraction(4), Fraction(2)) else "zq"
    body = " ".join(_pitch_letter(n.frequency) for n in chord.notes[:-1])
    # Note: rests inside a chord are not supported by Sound.py's syntax
    # either; a rest frequency would raise in _pitch_letter, which is
    # the honest failure here, not a silent wrong token.
    if any(n.is_rest for n in chord.notes):
        raise ValueError("rests inside a chord are not supported")
    return "\\" + group + "{" + body + "} " + note_token(chord.notes[-1]) \
        if body else note_token(chord.notes[-1])


def _event_token(event) -> str:
    if isinstance(event, Note):
        return note_token(event)
    if isinstance(event, Chord):
        return chord_token(event)
    raise ValueError(f"unknown event: {event!r}")


def _event_staff_frequency(event) -> float:
    if isinstance(event, Note):
        return event.frequency
    if isinstance(event, Chord):
        return sum(n.frequency for n in event.notes) / len(event.notes)
    raise ValueError(f"unknown event: {event!r}")


def render_music_tex(piece: Piece, meter=(4, 4), measures_per_line=4) -> str:
    """Body of music.tex for a piece (Sound.py fill_latex, fixed)."""
    tempo_num, tempo_den = meter
    measure_beats = Fraction(4 * tempo_num, tempo_den)
    metric = f"{tempo_num}{tempo_den}"
    lines = []
    lines.append("\\begin{music}")
    lines.append("\\generalmeter{\\meterfrac" + metric + "}")
    lines.append("\\nostartrule")
    lines.append("\\setstaffs1{2}")
    lines.append("\\setclef1{\\bass}")
    bar_no = 0
    lines.append(f"\\startbarno={bar_no}")
    lines.append("\\startextract")

    low, high = "", ""  # fkey (<=330 Hz), gkey (>330 Hz) in Sound.py terms
    measure_pos = Fraction(0)
    line_measures = 0
    block_open = True

    def close_measure():
        nonlocal low, high, measure_pos, line_measures, bar_no
        lines.append("\\bar")
        lines.append("\\Notes" + low + "|" + high + "\\en")
        low, high = "", ""
        measure_pos = Fraction(0)
        line_measures += 1
        bar_no += 1

    def close_line(final: bool):
        nonlocal line_measures, block_open
        lines.append("\\zendextract")
        lines.append("\\end{music}")
        block_open = False
        line_measures = 0
        if not final:
            lines.append("")
            lines.append("\\begin{music}")
            lines.append("\\generalmeter{\\meterfrac" + metric + "}")
            lines.append(f"\\startbarno={bar_no}")
            lines.append("\\setstaffs1{2}")
            lines.append("\\setclef1{\\bass}")
            lines.append("\\startextract")
            block_open = True

    for i, event in enumerate(piece.events):
        token = _event_token(event)
        if _event_staff_frequency(event) > STAFF_SPLIT_HZ:
            high += token + " "
            low += "\\hsk "
        else:
            low += token + " "
            high += "\\hsk "
        measure_pos += event.duration
        if measure_pos > measure_beats:
            raise ValueError(
                f"measure overflow at event {i}: position {measure_pos} "
                f"exceeds measure length {measure_beats}"
            )
        if measure_pos == measure_beats:
            close_measure()
            if line_measures == measures_per_line and i != len(piece.events) - 1:
                close_line(final=False)
    if measure_pos != 0:
        raise ValueError(
            f"trailing partial measure of {measure_pos} beats "
            f"(measure length {measure_beats}); pad with rests or trim"
        )
    if block_open:
        close_line(final=True)
    return "\n".join(lines) + "\n"


def render_document_tex(piece: Piece, composer: str = "Author") -> str:
    """Wrapper .tex file (Sound.py create_latex)."""
    title = _escape_latex(piece.title)
    author = _escape_latex(composer)
    return (
        "\\documentclass[a4paper]{article}\n"
        "\\usepackage[english]{babel}\n"
        "\\usepackage{graphicx}\n"
        "\\usepackage{musixtex}\n"
        "\\usepackage{calligra}\n"
        "\\addtolength{\\oddsidemargin}{-.875in}\n"
        "\\addtolength{\\evensidemargin}{-.875in}\n"
        "\\addtolength{\\textwidth}{1.70in}\n"
        "\\addtolength{\\topmargin}{-.875in}\n"
        "\\addtolength{\\textheight}{1.50in}\n"
        "\\pagenumbering{gobble}\n"
        f"\\title{{{title}}}\n"
        f"\\author{{{author}}}\n"
        "\\begin{document}\n"
        "\\maketitle\n"
        "\\centering\n"
        f"\\metron{{\\qu}}{{{piece.tempo_bpm:g}}}\n"
        "\\input{music.tex}\n"
        "\\end{document}\n"
    )


def write_score(piece: Piece, output_dir: str, composer: str = "Author"):
    """Write <title>.tex and music.tex; return (document_path, music_path).

    Does NOT run pdflatex. Use pdflatex -> musixflx -> pdflatex separately,
    with return-code checking (see docs/poc-scope.md / README).
    """
    os.makedirs(output_dir, exist_ok=True)
    safe_title = "".join(c if c.isalnum() or c in "._-" else "_" for c in piece.title)
    doc_path = os.path.join(output_dir, safe_title + ".tex")
    music_path = os.path.join(output_dir, "music.tex")
    with open(doc_path, "w") as f:
        f.write(render_document_tex(piece, composer))
    with open(music_path, "w") as f:
        f.write(render_music_tex(piece))
    return doc_path, music_path
