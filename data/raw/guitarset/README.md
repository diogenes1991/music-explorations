# GuitarSet — PRESENT (downloaded 2026-10-29, checksums verified)

- Purpose: guitar paired training + evaluation (the anchor set).
- What it is: 360 acoustic-guitar excerpts, ~30 s each, ~3 h total, 6 players,
  hexaphonic pickup + reference mic; string/fret note annotations, pitch
  contours, chords, beats, tempo. Comping + soloing, 5 styles, 3 progressions,
  2 tempi.
- Files here (unmodified downloads): annotation.zip (39,132,574 bytes) and
  audio_mono-mic.zip (656,927,981 bytes), both md5-verified against mirdata's
  published checksums. Hex-pickup zips were deliberately NOT fetched for this
  test — add them later if per-string audio is needed.
- Extracted copy: `data/interim/guitarset/` (360 JAMS + 360 mic WAVs).
  Example tested: 00_BN1-129-Eb_solo — 22.32 s, 44,100 Hz, tempo 129 bpm,
  71 note_midi notes, chunks into 10 / 10 / 2.32 s.
- Caveat: improvisation over lead sheets, not classical-guitar repertoire.
