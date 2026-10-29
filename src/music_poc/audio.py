"""Audio interfaces: load WAV, chunk into fixed-length pieces.

These are the interfaces the unit tests exercise. They are deliberately
small and dependency-light (numpy + stdlib wave only):

- load_wav(path) -> (samples as float array in [-1, 1], sample rate)
- chunk_samples(samples, sr, chunk_seconds) -> list of arrays; the last
  chunk may be shorter than chunk_seconds and is kept, not dropped or
  padded — dropping it would silently lose the tail of a piece.
- chunk_wav_file(input_path, output_dir, chunk_seconds) -> output paths
"""
from __future__ import annotations

import os
import wave

import numpy as np


def load_wav(path: str):
    with wave.open(path, "rb") as w:
        n_channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        sr = w.getframerate()
        raw = w.readframes(w.getnframes())
    if sampwidth == 2:
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    elif sampwidth == 4:
        samples = np.frombuffer(raw, dtype=np.int32).astype(np.float64) / 2147483648.0
    else:
        raise ValueError(f"unsupported sample width: {sampwidth} bytes")
    if n_channels > 1:
        samples = samples.reshape(-1, n_channels).mean(axis=1)
    return samples, sr


def write_wav(path: str, samples: np.ndarray, sr: int) -> None:
    clipped = np.clip(samples, -1.0, 1.0)
    ints = (clipped * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(ints.tobytes())


def chunk_samples(samples: np.ndarray, sr: int, chunk_seconds: float):
    if chunk_seconds <= 0:
        raise ValueError("chunk_seconds must be positive")
    chunk_len = int(round(sr * chunk_seconds))
    if chunk_len <= 0:
        raise ValueError("chunk too short for this sample rate")
    chunks = []
    for start in range(0, len(samples), chunk_len):
        chunks.append(samples[start : start + chunk_len])
    return chunks


def chunk_wav_file(input_path: str, output_dir: str, chunk_seconds: float):
    samples, sr = load_wav(input_path)
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(input_path))[0]
    paths = []
    for i, chunk in enumerate(chunk_samples(samples, sr, chunk_seconds)):
        out = os.path.join(output_dir, f"{base}_chunk{i:03d}.wav")
        write_wav(out, chunk, sr)
        paths.append(out)
    return paths
