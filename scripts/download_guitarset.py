#!/usr/bin/env python3
"""Download GuitarSet (mic audio + annotations only) into data/raw/guitarset/.

Source: mirdata's GuitarSet remote definitions, Zenodo record 3371780.
Only two of the five remotes are fetched for PoC testing:
  - annotation.zip      (JAMS annotations for all 360 excerpts)
  - audio_mono-mic.zip  (single-channel reference-mic recordings)
The hex-pickup and pickup-mix zips are skipped for now; add them later
by extending REMOTES below if per-string audio is needed.

Downloads land unmodified in data/raw/guitarset/. Extraction for
testing happens in data/interim/, never by editing data/raw/.
Checksums are the md5 values published in the mirdata docs.
"""
import hashlib
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "data", "raw", "guitarset")

REMOTES = [
    (
        "annotation.zip",
        "https://zenodo.org/record/3371780/files/annotation.zip?download=1",
        "b39b78e63d3446f2e54ddb7a54df9b10",
    ),
    (
        "audio_mono-mic.zip",
        "https://zenodo.org/record/3371780/files/audio_mono-mic.zip?download=1",
        "275966d6610ac34999b58426beb119c3",
    ),
]


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(filename, url, checksum):
    path = os.path.join(DEST, filename)
    if os.path.exists(path) and md5_of(path) == checksum:
        print(f"  already present and checksum OK: {filename}")
        return path
    print(f"  downloading {filename} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "music-poc/0.1"})
    with urllib.request.urlopen(req) as resp, open(path, "wb") as out:
        downloaded = 0
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
            downloaded += len(chunk)
            if downloaded % (50 << 20) < (1 << 20):
                print(f"    ... {downloaded / (1 << 20):.0f} MB")
    got = md5_of(path)
    if got != checksum:
        print(f"  CHECKSUM MISMATCH for {filename}: got {got}, want {checksum}")
        sys.exit(1)
    print(f"  done, checksum OK: {filename} ({os.path.getsize(path)} bytes)")
    return path


def main():
    os.makedirs(DEST, exist_ok=True)
    for filename, url, checksum in REMOTES:
        download(filename, url, checksum)
    print("All GuitarSet test downloads complete.")


if __name__ == "__main__":
    main()
