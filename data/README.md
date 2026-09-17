# Data

This directory documents the data used in the experiments reported in
*Coverage-Dependent Relational Learning for Multi-Station Earthquake
Magnitude Estimation*.

## Source dataset

The waveform data are derived from the Stanford Earthquake Dataset
(STEAD). The original STEAD waveform archive is not redistributed in
this repository.

Users should obtain STEAD from its official distribution source before
running the feature-extraction workflow.

## Regional selection

The study uses a Southern California subset of STEAD.

Both earthquake sources and recording stations are restricted to:

- latitude: 32.0°–37.0° N;
- longitude: 121.0°–114.5° W.

Only earthquake traces are considered.

After station-event construction, only events observed by at least two
distinct stations are retained for the principal experiments.

## Station-level features

Each station-event waveform is represented by 30 features: 10 features
computed independently for each of the E, N, and Z components.

The retained features are:

1. RMS amplitude;
2. peak amplitude;
3. crest factor;
4. spectral bandwidth;
5. spectral centroid;
6. spectral entropy;
7. zero-crossing rate;
8. early-to-late energy ratio;
9. relative energy in the 5–10 Hz band;
10. relative energy in the 20–50 Hz band.

The resulting analytical table contains:

- 307,392 station-event observations;
- 73,114 earthquake events;
- 314 infrastructure stations;
- 30 waveform-derived features;
- event-level station coverage ranging from 2 to 48 stations.

## Repository data organization

```text
data/
├── README.md
├── metadata/
│   └── full_stations.csv
└── sample/
```

`metadata/full_stations.csv` contains the station metadata used by the
graph-based experiments.

The full derived feature table (`features_socal_full.csv`) is not
versioned directly in this Git repository because of its size.

The feature-extraction workflow provided with this repository is
intended to reconstruct the analytical feature table from the source
STEAD data.

A small example dataset is provided under `sample/` for smoke testing
the data-loading and preprocessing pipeline. It is not intended to
reproduce the quantitative results reported in the manuscript.

## Building the analytical feature table

The full analytical feature table can be reconstructed from the
required STEAD CSV/HDF5 files using:

```bash
python src/build_stead_features.py \
    --data-dir /path/to/stead \
    --output-dir data/processed
```

The script applies the regional selection, extracts the station-level
waveform features, and generates `features_socal_full.csv`.

The source STEAD data are not redistributed by this repository.

## Reproducibility

The complete processing sequence is:

1. acquire the original STEAD data;
2. select earthquake traces within the study region;
3. extract the station-level waveform features;
4. construct station-event records;
5. retain events observed by at least two distinct stations;
6. run the set-learning and graph-learning experiments.

See `docs/REPRODUCIBILITY.md` for the computational environment,
cross-validation protocol, and model-evaluation procedure.