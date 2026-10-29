# Music PoC — solo guitar vs. viola timbre contrast

Audio → piece transcription, plus the reverse bridge (internal piece → realistic audio).

## The idea, in one paragraph

An encoder is trained on real music (not on our own synth output) in ~10-second
chunks. A forward bridge maps the encoder's latent representation to our fixed
internal piece representation (notes/chords, durations, and a `style` token that
carries quantized timbre: envelope × harmonic content, e.g. guitar vs. viola).
A reverse bridge maps internal → latent → decoder, so the same internal piece
can be rendered in realistic timbre. This repo is the PoC for that system,
scoped to one clean contrast: solo classical guitar vs. solo viola (arco only).

## Decision log

- PoC genre: solo guitar vs. viola timbre contrast (chosen 2026-10-29).
- Datasets: **free/public sets only** (leaning confirmed 2026-10-29). Paid sets
  (sample libraries, cleared catalogs, dataset vendors, commissioned recordings)
  are out of scope for now — see `DATASETS.md` for why they were set aside.
- Original code: `diogenes1991/Small_Projects`, file `Sound/Sound.py`
  (~1,220 lines). It synthesizes a WAV and emits a MusixTeX score. It is NOT
  copied here. The internal representation v2 (structured `style` token,
  `Fraction` durations, deterministic MIDI ↔ internal conversion) will live in
  `src/music_poc/` and must be frozen before any neural training.

## Layout

```
music-poc/
  README.md            this file
  DATASETS.md          dataset inventory: what each set is for, license, status
  .gitignore           raw audio is NEVER committed
  data/
    raw/               datasets exactly as downloaded, one folder per set
                       (see data/raw/<set>/README.md in each folder)
    interim/           extracted / re-organized, but not yet model-ready
    processed/         model-ready: 10s chunks, internal reps, splits
  src/music_poc/       code: internal rep (Fraction durations, style tokens),
                       audio load/chunk, classic synth (Python 3, mirrors
                       Sound.py's model, documented divergences), MusixTeX
                       emitter (Python 3 port of Sound.py's create_latex /
                       fill_latex, with the silent failures made explicit)
  scripts/             runnable helpers (see scripts/check_datasets.py,
                       scripts/synthesize_test_fixtures.py)
  tests/               tests: 21 passing (2026-10-29) — interface tests on
                       synthetic fixtures + MusixTeX token/score tests
  docs/                PoC scope notes
```

## Rules for `data/`

1. A dataset goes in `data/raw/<set>/` and nowhere else on arrival. Do not
   rename, re-encode, or mix sets on import — re-organization happens in
   `data/interim/` and `data/processed/`, with a script, so the raw copy stays
   a faithful reference.
2. Raw audio (`.wav`, `.flac`, `.mp3`, …) is never committed to git
   (see `.gitignore`). Only the per-dataset READMEs and `.gitkeep` files are
   tracked in `data/raw/`.
3. Nothing in `data/raw/` is training data yet. A set becomes usable only
   after it is registered in `DATASETS.md` with its license checked and its
   split (train/val/test, split by player/piece, never by chunk) recorded.
4. Paid/commissioned data does not belong here unless the free-sets decision
   is explicitly revisited. If that happens, add a new folder and a new
   `DATASETS.md` entry — do not silently mix paid audio into a free folder.

## Status

GuitarSet: **present** (downloaded 2026-10-29, md5-verified, extracted to
`data/interim/guitarset/`, one excerpt tested end-to-end). All other
datasets: **not yet downloaded**. Run `python scripts/check_datasets.py`
to see what has arrived and what is still pending.
