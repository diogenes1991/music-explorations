"""Style codebook: quantized timbre from isolated notes.

Planned contents:
- Feature extraction from isolated notes: envelope shape + harmonic
  spectrum (+ vibrato features for viola).
- Clustering (k-means / VQ) over NSynth guitar notes + SOL viola notes,
  with a check that the clusters separate the instruments BEFORE any
  neural training. If clustering cannot separate them, the bridge will
  not either.
- Mapping from cluster id to the structured style token in internal.py.
"""
