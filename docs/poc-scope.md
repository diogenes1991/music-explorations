# PoC scope — solo guitar vs. viola timbre contrast

## System

- Forward: audio (10 s chunks) → encoder → latent z → bridge →
  internal piece (notes/chords, durations, style token).
- Reverse: internal piece → reverse bridge → z → decoder → realistic audio.
- The encoder is trained on real music, not on our synth output. The bridges
  are trained on synthetic paired data (known internal → audio) plus whatever
  real paired data exists, with augmentation across timbres.

## Frozen PoC definition (v0)

- Solo only. Classical (nylon) guitar, not steel-string. Viola, arco only —
  pizzicato viola is a v1 hard case (it sounds plucked, like guitar).
- Standard tuning, A440. Pitch range restricted to the guitar/viola overlap,
  so the same pitch can appear in both timbres.
- Monophonic melodies first. Guitar chords and viola double stops are v1.
- 10 s chunks for training; evaluation on full pieces, with stitching
  handled explicitly (notes cut at chunk boundaries must not double-count).

## Style token (v0)

- Piece/track level: instrument (guitar / viola).
- Note level: envelope code (decay vs. sustain) and, for viola, vibrato
  presence/depth. A static sine × envelope token cannot represent vibrato;
  if viola renders as an organ, the vibrato code is missing, not the decoder.
- The token is a conditioning code for the neural decoder, and a literal
  waveform recipe (generalized gaussian × harmonic series) only in the
  classic synth. Do not confuse the two roles.

## Order of work

1. Freeze internal v2 (structured style token, Fraction durations,
   deterministic MIDI ↔ internal conversion).
2. Style codebook from isolated notes (NSynth guitar + SOL viola) — check
   clusters separate the instruments before any neural training.
3. Synthetic paired data (own synth + soundfont renderings + augmentation).
4. Encoder pretraining on unlabelled solo guitar/viola recordings.
5. Forward bridge, then reverse bridge, on a frozen latent space; joint
   fine-tuning only at the end.
6. Evaluation: instrument classification per chunk, note pitch/onset F1
   (viola pitch measured to vibrato centre), style-token accuracy, and
   round-trip internal → rendered → transcribed.

## Known limitations (do not pretend away)

- Guitar notes ring over into following notes; the internal rep is a
  sequence of non-overlapping notes. v0 restricts to melodies with enough
  space; note-off vs. decay is a v1 problem.
- Viola paired data is the bottleneck (see DATASETS.md). Evaluation quality
  on viola will cap below guitar until that gap is closed.
- Paid data is out of scope for now (free sets only, 2026-10-29).
