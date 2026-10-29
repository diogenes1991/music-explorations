# Dataset inventory — free/public sets only

Decision (2026-10-29): the PoC uses free/public sets. Paid routes were
surveyed and set aside: FullSOL (Ircam Premium) buys more viola isolated
notes only; commercial sample libraries are production licenses, not ML
training rights, and several now explicitly forbid AI training; cleared
catalogs and dataset vendors sell clearance/metadata, not note-level
solo-instrument labels; commissioning would close the viola gap but is a
different project (hire musicians, own the recordings). Revisit only by an
explicit decision, with a new folder and a new entry here.

## The asymmetry to plan around

Guitar paired data is strong. Viola paired data is the bottleneck: there is
no dedicated solo-viola transcription set in the public map. Viola coverage
comes from ensemble stems (URMP), ensemble labels (MusicNet), unlabelled
solo recordings (Solos), and isolated notes (TinySOL/OrchideaSOL).

## Inventory

| Folder | Set | What it is | PoC use | License / access note | Status |
|---|---|---|---|---|---|
| `data/raw/guitarset/` | GuitarSet | 360 acoustic-guitar excerpts, ~30 s each, ~3 h, 6 players, hexaphonic pickup + reference mic; string/fret note annotations, pitch contours, chords, beats, tempo | Guitar paired training + evaluation (anchor set) | Public research set; Zenodo record 3371780 | **Present 2026-10-29**: annotation.zip (39,132,574 bytes, md5 verified) + audio_mono-mic.zip (656,927,981 bytes, md5 verified); 360 JAMS + 360 mic WAVs extracted to `data/interim/guitarset/`; example excerpt 00_BN1-129-Eb_solo tested: 22.32 s, 44,100 Hz, tempo 129 bpm, 71 note_midi notes across strings, chunks cleanly into 10/10/2.32 s |
| `data/raw/urmp/` | URMP | 44 ensemble pieces, each part recorded in isolation then mixed; audio, video, MIDI per track | Viola stems (extract viola-only tracks); viola evaluation | Public research set; check license on download | Pending |
| `data/raw/musicnet/` | MusicNet | 330 freely-licensed classical recordings, ~34 h, 1M+ note labels (time, pitch, instrument) | Viola-in-ensemble evaluation; NOT solo training data | Freely licensed recordings; check license on download | Pending |
| `data/raw/solos/` | Solos | 755 YouTube audition recordings; 55 viola recordings, mean 5:31 | Unlabelled viola audio for encoder pretraining ONLY (no note labels) | YouTube-sourced: availability fragile, terms unclear — pretraining use only, never as labelled data | Pending |
| `data/raw/nsynth/` | NSynth | 305,979 isolated notes, 4 s, 16 kHz, 1,006 sample-library instruments; families incl. guitar (35,423) and string (20,594) | Style-codebook clustering at family level; guitar isolated notes | Public; check license on download. Samples, not performances — no phrasing/vibrato variation | Pending |
| `data/raw/tinysol/` | TinySOL | 2,478 isolated notes, 44.1 kHz mono, 14 instruments incl. viola, ordinario only | Viola isolated notes for style codebook | Free for non-commercial use | Pending |
| `data/raw/orchideasol/` | OrchideaSOL | 13,265 isolated notes, 44.1 kHz mono, 14 instruments incl. viola, incl. mutes + extended techniques | Viola isolated notes, incl. technique variation | Free for non-commercial use after Ircam Forum subscription | Pending |
| `data/raw/slakh/` | Slakh2100 | 2,100 synthesized tracks, 145 h, MIDI rendered with sample instruments, stems + MIDI | Synthetic paired augmentation ONLY, not real evaluation. Heavy: 105 GB download (~500 GB unzipped) — prefer BabySlakh for prototyping | Public; check license on download | Pending |

## Notes per set

- **SOL has no guitar.** TinySOL/OrchideaSOL's 14 instruments include violin,
  viola and cello, but not guitar. The style codebook therefore mixes regimes:
  viola notes from SOL, guitar notes from NSynth. Compare their clusters with
  that caveat in mind.
- **NSynth "string" is a family, not viola.** Do not treat NSynth string
  samples as viola samples. Viola-specific isolated notes come from SOL.
- **Slakh is synthesized.** Its guitar/strings stems are useful augmentation
  for the bridge, but a model evaluated only on Slakh has not been evaluated
  on real performances. Keep real and synthetic evaluation separate, always.
- **Splits must be by player/piece, never by chunk.** A 10 s chunk from a
  performance in training must never have a sibling chunk in test, or the
  evaluation is measuring memorization of a recording, not transcription.

## On arrival checklist (per set)

1. Drop the download, unmodified, into `data/raw/<set>/`.
2. Read its license file; if it conflicts with the note above, stop and flag it.
3. Record in this file: version/date downloaded, file count, total size, and
   the split you will use.
4. Run `python scripts/check_datasets.py` and confirm the set shows up.
5. Do not start training on it until steps 1–4 are done.
