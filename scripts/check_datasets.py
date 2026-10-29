#!/usr/bin/env python3
"""Report which datasets have arrived under data/raw/.

A dataset counts as 'present' only if its folder contains files other than
the tracked README.md / .gitkeep placeholders. This script never modifies
anything; it just tells you what is pending.

Usage: python scripts/check_datasets.py
Run from the music-poc/ directory (or anywhere; it resolves relative to
this file's parent).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")

DATASETS = [
    ("guitarset", "GuitarSet — guitar paired training/evaluation"),
    ("urmp", "URMP — viola stems from ensemble pieces"),
    ("musicnet", "MusicNet — viola-in-ensemble evaluation"),
    ("solos", "Solos — unlabelled viola pretraining only"),
    ("nsynth", "NSynth — isolated notes, guitar + string families"),
    ("tinysol", "TinySOL — viola isolated notes, ordinario"),
    ("orchideasol", "OrchideaSOL — viola isolated notes, incl. techniques"),
    ("slakh", "Slakh2100 — synthetic augmentation only (prefer BabySlakh)"),
]


def folder_stats(path):
    total_files = 0
    total_bytes = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for name in filenames:
            if name in ("README.md", ".gitkeep"):
                continue
            total_files += 1
            try:
                total_bytes += os.path.getsize(os.path.join(dirpath, name))
            except OSError:
                pass
    return total_files, total_bytes


def human(nbytes):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} PB"


def main():
    print(f"data/raw/ at {RAW}\n")
    pending = 0
    for folder, label in DATASETS:
        path = os.path.join(RAW, folder)
        if not os.path.isdir(path):
            print(f"  MISSING  {folder:<12} {label} (folder does not exist)")
            pending += 1
            continue
        nfiles, nbytes = folder_stats(path)
        if nfiles == 0:
            print(f"  PENDING  {folder:<12} {label}")
            pending += 1
        else:
            print(f"  PRESENT  {folder:<12} {label} — {nfiles} files, {human(nbytes)}")
    print(f"\n{pending} of {len(DATASETS)} datasets still pending.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
