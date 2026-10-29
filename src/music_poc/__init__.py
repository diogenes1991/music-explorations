"""Music PoC: audio <-> internal piece representation, guitar vs. viola.

Modules (all placeholders until internal v2 is frozen):
- internal: the fixed internal piece representation (notes/chords,
  Fraction durations, structured style token) + MIDI conversion.
- datasets: loaders for the free sets in data/raw/ (see DATASETS.md).
- audio: chunking (10 s), feature extraction, augmentation.
- style: style-codebook clustering from isolated notes.
- bridges: forward bridge (latent -> internal) and reverse bridge
  (internal -> latent), trained on a frozen latent space.
"""
