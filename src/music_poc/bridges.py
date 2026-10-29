"""Forward and reverse bridges, on a frozen latent space.

- Forward bridge: encoder latent z -> internal piece.
- Reverse bridge: internal piece -> latent z_hat, rendered by the
  (frozen, then jointly fine-tuned) decoder into realistic audio.
- Training order (see docs/poc-scope.md): autoencoder first, freeze it,
  train both bridges, joint fine-tune only at the end. Training a bridge
  against a moving latent space is a bug, not a schedule.
"""
