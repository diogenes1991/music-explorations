"""Dataset loaders — one loader per free set in data/raw/.

Each loader must: read only from data/raw/<set>/, never modify it;
enforce the split recorded in DATASETS.md (by player/piece, never by
chunk); and return data in the internal representation (see internal.py)
or in a documented intermediate form, never in a loader-specific format
that downstream code has to guess at.

Sets: guitarset, urmp, musicnet, solos (unlabelled only), nsynth,
tinysol, orchideasol, slakh (synthetic only).
"""
