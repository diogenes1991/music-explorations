"""Tests for the Python 3 MusixTeX emitter (src/music_poc/musixtex.py).

Reference values are computed from Sound.py's own rules, not from the
emitter itself: A4 = 440 Hz -> semitone index 36 -> letter 'h';
440 Hz <= 523.25 Hz, so a quarter note is \\qu{h}.
"""
import json
import os
import sys
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from music_poc.internal import Chord, Note, Piece
from music_poc.musixtex import (
    chord_token,
    note_token,
    render_document_tex,
    render_music_tex,
    write_score,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(ROOT, "tests", "fixtures")


def load_piece(name):
    with open(os.path.join(FIXTURES, f"{name}.json")) as f:
        return Piece.from_dict(json.load(f))


class TestTokens(unittest.TestCase):
    def test_a4_quarter_is_qu_h(self):
        self.assertEqual(note_token(Note(440.0, Fraction(1), "guitar-pluck")),
                         "\\qu{h}")

    def test_high_note_uses_down_stem(self):
        # 659.25 Hz (E5) > 523.25 Hz, so down stem, and semitone index
        # 36 (A4) + 7 = 43 -> letter 'l'.
        self.assertEqual(note_token(Note(659.25, Fraction(1), "guitar-pluck")),
                         "\\ql{l}")
        from music_poc.musixtex import _pitch_letter
        self.assertEqual(_pitch_letter(659.25), "l")

    def test_rest_tokens(self):
        self.assertEqual(note_token(Note(0.0, Fraction(1), "guitar-pluck")),
                         "\\qp")
        self.assertEqual(note_token(Note(0.0, Fraction(4), "guitar-pluck")),
                         "\\pausep")

    def test_unsupported_duration_raises(self):
        with self.assertRaises(ValueError):
            note_token(Note(440.0, Fraction(1, 3), "guitar-pluck"))

    def test_out_of_range_pitch_raises(self):
        with self.assertRaises(ValueError):
            note_token(Note(30.0, Fraction(1), "guitar-pluck"))
        with self.assertRaises(ValueError):
            note_token(Note(2000.0, Fraction(1), "guitar-pluck"))

    def test_chord_token_is_group_plus_last_note(self):
        chord = Chord([Note(440.0, Fraction(1), "guitar-pluck"),
                       Note(554.37, Fraction(1), "guitar-pluck")])
        token = chord_token(chord)
        self.assertTrue(token.startswith("\\zq{h"))
        # Last note 554.37 Hz > 523.25 Hz, so down stem: \ql{^j}
        self.assertIn("\\ql{^j}", token)


class TestScoreRendering(unittest.TestCase):
    def test_melody_fixture_renders_two_closed_measures(self):
        piece = load_piece("melody_guitar")
        tex = render_music_tex(piece)
        self.assertIn("\\begin{music}", tex)
        self.assertIn("\\generalmeter{\\meterfrac44}", tex)
        self.assertEqual(tex.count("\\en\n"), 2)  # 8 beats = 2 measures of 4
        self.assertTrue(tex.rstrip().endswith("\\end{music}"))
        self.assertIn("\\qu{h}", tex)  # A4 quarter notes

    def test_staff_split_uses_hsk_spacers(self):
        # Low note (A4, 440 Hz > 330 Hz) goes to the high staff in
        # Sound.py's convention (freq > split -> gkey), low staff gets \hsk.
        piece = Piece(events=[Note(440.0, Fraction(4), "guitar-pluck")])
        tex = render_music_tex(piece)
        self.assertIn("\\hsk", tex)

    def test_trailing_partial_measure_raises_not_dropped(self):
        piece = Piece(events=[Note(440.0, Fraction(1), "guitar-pluck")])
        with self.assertRaises(ValueError):
            render_music_tex(piece)

    def test_measure_overflow_raises(self):
        piece = Piece(events=[Note(440.0, Fraction(4), "guitar-pluck"),
                              Note(440.0, Fraction(1), "guitar-pluck")])
        with self.assertRaises(ValueError):
            render_music_tex(piece)

    def test_document_tex_escapes_title_and_has_metronome(self):
        piece = load_piece("melody_guitar")
        doc = render_document_tex(piece, composer="A & B")
        self.assertIn("\\usepackage{musixtex}", doc)
        self.assertIn("\\metron{\\qu}{120}", doc)
        self.assertIn("A \\& B", doc)
        self.assertIn("\\input{music.tex}", doc)

    def test_write_score_writes_both_files(self):
        import tempfile
        piece = load_piece("melody_guitar")
        with tempfile.TemporaryDirectory() as tmp:
            doc_path, music_path = write_score(piece, tmp)
            self.assertTrue(os.path.exists(doc_path))
            self.assertTrue(os.path.exists(music_path))
            with open(music_path) as f:
                self.assertIn("\\begin{music}", f.read())


if __name__ == "__main__":
    unittest.main()
