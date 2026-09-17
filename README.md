# Coverage-Dependent Relational Learning for Multi-Station Earthquake Magnitude Estimation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22820001.svg)](https://doi.org/10.5281/zenodo.22820001)

This repository contains the code, experiment configurations, processed
results, and reproducibility material associated with the manuscript:

**Coverage-Dependent Relational Learning for Multi-Station Earthquake Magnitude Estimation**

The study investigates how event-level seismic station coverage affects
the relative utility of different inductive biases for multi-station
earthquake magnitude estimation.

The central question is not simply whether additional stations improve
prediction accuracy, but whether the appropriate aggregation mechanism
depends on how many stations observe an event.

## Overview

Multi-station earthquake observations naturally form
variable-cardinality sets because different earthquakes are recorded by
different numbers and configurations of seismic stations.

The primary experiments compare three aggregation strategies:

- **MeanPool-MLP** — mean aggregation of station-level features followed
  by a multilayer perceptron;
- **Deep Sets** — nonlinear station encoding followed by
  permutation-invariant aggregation;
- **Set Transformer** — self-attention among station representations
  before event-level aggregation.

Complementary graph-neural-network experiments evaluate:

- **Random-GATv2**
- **Geographic-GATv2**
- **FeatureSim-GATv2**
- **Geographic-GCN**

The graph experiments examine whether predefined infrastructure-level
connectivity provides additional predictive value when only a subset of
stations is active for each earthquake.

## Main finding

The usefulness of relational inductive bias is coverage-dependent rather
than universal.

Under the evaluation protocol used in the manuscript:

- sparse events (2–5 active stations) favor Deep Sets;
- intermediate events (6–10 stations) show no clear difference between
  Deep Sets and Set Transformer;
- dense events (11 or more stations) show an aggregate advantage for
  Set Transformer.

The purpose of the repository is to provide the computational material
needed to reproduce and inspect these results.

## Data

The experiments use earthquake observations derived from the
**Stanford Earthquake Dataset (STEAD)**.

The analysis is restricted to a Southern California regional subset:

- latitude: 32.0°–37.0° N;
- longitude: 121.0°–114.5° W;
- earthquake traces only;
- events observed by at least two distinct stations.

After preprocessing, the main experiment contains:

- 314 infrastructure stations;
- 73,114 eligible earthquake events;
- 307,392 station-event observations;
- 30 station-level waveform features;
- event coverage ranging from 2 to 48 stations.

The complete STEAD waveform archive is not redistributed in this
repository. Instructions for obtaining the original data and reproducing
the preprocessing workflow are provided in
`docs/REPRODUCIBILITY.md`.

A small example dataset is provided in `data/sample/` for smoke testing
the data-loading and preprocessing pipeline without downloading the
complete waveform archive. The sample is not intended to reproduce the
quantitative results reported in the manuscript.

## Repository structure

```text
.
├── README.md
├── LICENSE
├── requirements.txt
├── CITATION.cff
├── notebooks/
│   ├── 01_set_models_and_coverage.ipynb
│   └── 02_gnn_topology_comparison.ipynb
├── src/
│   └── STEAD preprocessing and feature-extraction code
├── data/
│   ├── README.md
│   ├── metadata/
│   │   └── full_stations.csv
│   └── sample/
│       └── features_socal_sample.csv
├── results/
│   └── Processed numerical results reported in the manuscript
├── figures/
│   └── Manuscript figures
└── docs/
    ├── USER_GUIDE.md
    └── REPRODUCIBILITY.md
```

## Installation

A Python environment containing the required dependencies can be created
from `requirements.txt`.

Example:

```bash
python -m venv .venv
```

Activate the environment and install the dependencies:

```bash
pip install -r requirements.txt
```

Exact package versions used for the reproducibility release are listed
in `requirements.txt`. Additional computational-environment information
is provided in `docs/REPRODUCIBILITY.md`.

## Reproducing the experiments

The reproducibility workflow consists of four main stages:

1. obtain and preprocess the STEAD earthquake data;
2. construct variable-cardinality event-level station sets;
3. train and evaluate the set-based and graph-based models using the
   predefined five-fold protocol;
4. reproduce the coverage-stratified statistical analyses, tables, and
   figures.

Detailed instructions are provided in:

```text
docs/REPRODUCIBILITY.md
```

The repository also includes processed result tables so that the
statistical analyses and manuscript figures can be inspected without
retraining all neural networks.

## Evaluation protocol

The main set-based experiments use five common event-level folds.
Feature standardization is performed independently within each fold.
Scaling parameters are estimated exclusively from the training
station-event observations and then applied to the corresponding
validation observations.

Model performance is evaluated using:

- mean absolute error (MAE);
- root mean squared error (RMSE);
- coefficient of determination (R²);
- paired event-level bootstrap confidence intervals.

Coverage-dependent performance is evaluated for:

- sparse coverage: 2–5 stations;
- intermediate coverage: 6–10 stations;
- dense coverage: 11 or more stations.

Alternative coverage partitions are also evaluated as a robustness
analysis.

## Reproducibility notes

All graph structures derived from station features are constructed using
training-fold data only.

In particular, **FeatureSim-GATv2** uses training-derived station feature
similarity. It does not use mutual information.

No test or validation observations are used to estimate feature scaling
parameters or training-derived graph topology.

Random seeds, model hyperparameters, and the computational environments
used in the reported experiments are documented in the experiment
notebooks and reproducibility documentation.

## Documentation

See:

- `docs/USER_GUIDE.md` for inputs, outputs, model options, and expected
  behavior;
- `docs/REPRODUCIBILITY.md` for the complete workflow used to reproduce
  the main results.

## License

The source code in this repository is released under the MIT License.
See `LICENSE` for details.

The STEAD dataset is distributed separately by its original providers
and is subject to its own terms and conditions.

## Citation

Citation metadata are provided in `CITATION.cff`.

The archived reproducibility release is available on Zenodo:

**DOI:** [10.5281/zenodo.22820001](https://doi.org/10.5281/zenodo.22820001)

## Status

Version **v1.0.1** is the archived reproducibility release associated
with the initial manuscript submission. The release is permanently
archived on Zenodo under DOI
[10.5281/zenodo.22820001](https://doi.org/10.5281/zenodo.22820001).