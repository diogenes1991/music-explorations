# tests/

First test to write, before any model code: the round-trip test.

- Internal piece → score/audio (classic synth) → internal piece again
  must equal the original up to semitone quantization and style-token
  defaults. Without this oracle, refactoring the emitter or building the
  bridges is trading known bugs for unknown ones.

Later tests: style-codebook separation, chunk stitching (no double-counted
notes at chunk boundaries), and split integrity (no player/piece appears
in both train and test).
