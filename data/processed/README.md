# data/processed/ — model-ready data

Examples: 10-second chunks, mel-spectrogram features, internal
representations, and train/val/test splits (split by player/piece, never by
chunk — see `DATASETS.md`). Every file here must be traceable to a raw
dataset and a script in `scripts/`; if you cannot say which script made it,
it does not belong here.
