#!/usr/bin/env python3
"""Build the Southern California STEAD station-event feature table.

This script reproduces the feature-building stages used in the associated
study. It expects STEAD CSV/HDF5 chunk pairs named ``chunkN.csv`` and
``chunkN.hdf5`` in the input directory.

Example
-------
python src/build_stead_features.py --data-dir /path/to/stead --output-dir data/processed
"""

from __future__ import annotations

import argparse
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from scipy import stats


FS = 100.0
CHUNKS = (2, 3, 4, 5, 6)
CHANNELS = ("E", "N", "Z")
LAT_MIN, LAT_MAX = 32.0, 37.0
LON_MIN, LON_MAX = -121.0, -114.5

NUMERIC_COLUMNS = (
    "source_magnitude",
    "source_depth_km",
    "source_distance_km",
    "p_arrival_sample",
    "s_arrival_sample",
    "source_latitude",
    "source_longitude",
    "receiver_latitude",
    "receiver_longitude",
    "back_azimuth_deg",
    "p_travel_sec",
)


def extract_features_single_channel(x: np.ndarray) -> dict[str, float]:
    """Compute the per-channel features used in the original workflow."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)

    rms = np.sqrt(np.mean(x**2))
    peak = np.max(np.abs(x))
    crest_factor = peak / rms if rms > 0 else 0.0
    kurtosis = stats.kurtosis(x, fisher=True)
    skewness = stats.skew(x)
    zcr = np.sum(np.diff(np.sign(x)) != 0) / (n - 1)

    third = n // 3
    e1 = np.mean(x[:third] ** 2)
    e3 = np.mean(x[2 * third :] ** 2)
    energy_ratio = e1 / e3 if e3 > 0 else 0.0

    freqs = np.fft.rfftfreq(n, d=1.0 / FS)
    psd = np.abs(np.fft.rfft(x)) ** 2
    psd_sum = np.sum(psd)

    if psd_sum > 0:
        psd_norm = psd / psd_sum
        centroid = np.sum(freqs * psd_norm)
        bandwidth = np.sqrt(np.sum(((freqs - centroid) ** 2) * psd_norm))
        dominant = freqs[np.argmax(psd[1:]) + 1]
        psd_pos = psd_norm[psd_norm > 0]
        entropy = -np.sum(psd_pos * np.log2(psd_pos))
    else:
        centroid = bandwidth = dominant = entropy = 0.0

    bands = {
        "0.5_5Hz": (0.5, 5),
        "5_10Hz": (5, 10),
        "10_20Hz": (10, 20),
        "20_50Hz": (20, 50),
    }
    band_energy = {}
    for name, (flo, fhi) in bands.items():
        mask = (freqs >= flo) & (freqs < fhi)
        band_energy[f"band_{name}"] = (
            np.sum(psd[mask]) / psd_sum if psd_sum > 0 else 0.0
        )

    return {
        "rms": rms,
        "peak": peak,
        "crest_factor": crest_factor,
        "kurtosis": kurtosis,
        "skewness": skewness,
        "zcr": zcr,
        "energy_ratio_early_late": energy_ratio,
        "spectral_centroid": centroid,
        "spectral_bandwidth": bandwidth,
        "dominant_freq": dominant,
        "spectral_entropy": entropy,
        **band_energy,
    }


def enrich_chunk(data_dir: Path, chunk_id: int, force: bool = False) -> Path:
    """Add HDF5 SNR and coda metadata to one STEAD CSV chunk."""
    csv_path = data_dir / f"chunk{chunk_id}.csv"
    hdf5_path = data_dir / f"chunk{chunk_id}.hdf5"
    enriched_path = data_dir / f"chunk{chunk_id}_enriched.csv"

    if enriched_path.exists() and not force:
        print(f"chunk{chunk_id}: enriched CSV exists; skipping")
        return enriched_path

    if not csv_path.exists() or not hdf5_path.exists():
        raise FileNotFoundError(
            f"Missing input pair for chunk{chunk_id}: {csv_path} / {hdf5_path}"
        )

    print(f"chunk{chunk_id}: enriching metadata")
    df = pd.read_csv(csv_path, low_memory=False)

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    snr_e, snr_n, snr_z, coda_end = [], [], [], []

    with h5py.File(hdf5_path, "r") as h5:
        for i, trace_name in enumerate(df["trace_name"]):
            ds = h5["data"].get(str(trace_name))
            if ds is None:
                snr_e.append(np.nan)
                snr_n.append(np.nan)
                snr_z.append(np.nan)
                coda_end.append(np.nan)
            else:
                snr = np.array(ds.attrs.get("snr_db", [np.nan] * 3)).flatten()
                snr_e.append(snr[0] if len(snr) >= 1 else np.nan)
                snr_n.append(snr[1] if len(snr) >= 2 else np.nan)
                snr_z.append(snr[2] if len(snr) >= 3 else np.nan)

                ce = ds.attrs.get("coda_end_sample", np.nan)
                coda_end.append(float(np.array(ce).flatten()[0]))

            if (i + 1) % 50000 == 0:
                print(f"  {i + 1:,} / {len(df):,}")

    df["snr_E"] = snr_e
    df["snr_N"] = snr_n
    df["snr_Z"] = snr_z
    df["snr_mean"] = df[["snr_E", "snr_N", "snr_Z"]].mean(axis=1)
    df["coda_end_sample"] = coda_end

    if "snr_db" in df.columns:
        df.drop(columns=["snr_db"], inplace=True)

    df.to_csv(enriched_path, index=False)
    print(f"  saved {enriched_path} ({len(df):,} traces)")
    return enriched_path


def extract_chunk_features(
    data_dir: Path, output_dir: Path, chunk_id: int, force: bool = False
) -> Path:
    """Filter one chunk to the study region and extract waveform features."""
    feature_path = output_dir / f"features_socal_chunk{chunk_id}.csv"

    if feature_path.exists() and not force:
        print(f"chunk{chunk_id}: feature table exists; skipping")
        return feature_path

    enriched_path = data_dir / f"chunk{chunk_id}_enriched.csv"
    hdf5_path = data_dir / f"chunk{chunk_id}.hdf5"

    df = pd.read_csv(enriched_path, low_memory=False)

    mask = (
        df["receiver_latitude"].between(LAT_MIN, LAT_MAX)
        & df["receiver_longitude"].between(LON_MIN, LON_MAX)
        & df["source_latitude"].between(LAT_MIN, LAT_MAX)
        & df["source_longitude"].between(LON_MIN, LON_MAX)
        & (df["trace_category"] == "earthquake_local")
    )
    df_socal = df.loc[mask].copy()
    print(f"chunk{chunk_id}: SoCal traces {len(df_socal):,} / {len(df):,}")

    if df_socal.empty:
        pd.DataFrame().to_csv(feature_path, index=False)
        return feature_path

    records = []
    trace_names = df_socal["trace_name"].values

    with h5py.File(hdf5_path, "r") as h5:
        for i, trace_name in enumerate(trace_names):
            ds = h5["data"].get(str(trace_name))
            if ds is None:
                continue

            data = np.array(ds)
            if data.ndim != 2 or data.shape[1] < 3:
                raise ValueError(
                    f"Unexpected waveform shape for {trace_name}: {data.shape}"
                )

            row = {"trace_name": trace_name}

            for channel_index, channel_name in enumerate(CHANNELS):
                features = extract_features_single_channel(data[:, channel_index])
                for feature_name, value in features.items():
                    row[f"{feature_name}_{channel_name}"] = value

            rms_h = np.sqrt(
                np.mean(data[:, 0] ** 2) + np.mean(data[:, 1] ** 2)
            )
            rms_z = np.sqrt(np.mean(data[:, 2] ** 2))
            row["zh_ratio"] = rms_z / rms_h if rms_h > 0 else 0.0
            row["corr_EN"] = np.corrcoef(data[:, 0], data[:, 1])[0, 1]
            row["corr_EZ"] = np.corrcoef(data[:, 0], data[:, 2])[0, 1]
            row["corr_NZ"] = np.corrcoef(data[:, 1], data[:, 2])[0, 1]

            records.append(row)

            if (i + 1) % 10000 == 0:
                print(f"  {i + 1:,} / {len(trace_names):,}")

    df_features = pd.DataFrame(records)
    df_merged = df_socal.merge(df_features, on="trace_name", how="inner")
    df_merged.to_csv(feature_path, index=False)
    print(f"  saved {feature_path} ({len(df_merged):,} traces)")
    return feature_path


def concatenate_chunks(output_dir: Path, force: bool = False) -> Path:
    """Concatenate per-chunk feature tables into features_socal_full.csv."""
    full_path = output_dir / "features_socal_full.csv"

    if full_path.exists() and not force:
        print(f"Full feature table exists: {full_path}")
        return full_path

    frames = []
    for chunk_id in CHUNKS:
        feature_path = output_dir / f"features_socal_chunk{chunk_id}.csv"
        frame = pd.read_csv(feature_path, low_memory=False)
        if len(frame) > 0:
            frame["chunk"] = chunk_id
            frames.append(frame)
            print(f"chunk{chunk_id}: {len(frame):,} traces")

    if not frames:
        raise RuntimeError("No non-empty per-chunk feature tables were found.")

    full = pd.concat(frames, ignore_index=True)
    full.to_csv(full_path, index=False)

    print(f"Saved: {full_path}")
    print(
        "Full dataset: "
        f"{len(full):,} traces, "
        f"{full['source_id'].nunique():,} events, "
        f"{full['receiver_code'].nunique():,} receiver codes"
    )
    return full_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Southern California STEAD feature table."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Directory containing chunk2..chunk6 CSV/HDF5 pairs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for per-chunk and concatenated feature tables.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recompute outputs even when files already exist.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_dir = args.data_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for chunk_id in CHUNKS:
        enrich_chunk(data_dir, chunk_id, force=args.force)

    for chunk_id in CHUNKS:
        extract_chunk_features(
            data_dir, output_dir, chunk_id, force=args.force
        )

    concatenate_chunks(output_dir, force=args.force)


if __name__ == "__main__":
    main()
