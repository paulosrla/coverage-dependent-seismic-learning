# Coverage-Dependent Relational Learning for Multi-Station Earthquake Magnitude Estimation

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
the preprocessing workflow will be provided in
`docs/REPRODUCIBILITY.md`.

A small example dataset will be provided in `data/sample/` so that the
code and model interfaces can be tested without downloading the complete
waveform archive.

## Repository structure

```text
.
├── README.md
├── LICENSE
├── requirements.txt
├── CITATION.cff
├── notebooks/
│   └── Reproducible experiment notebooks
├── src/
│   └── Reusable preprocessing, model, and evaluation code
├── configs/
│   └── Experiment configurations
├── data/
│   └── sample/
│       └── Small example data for testing
├── results/
│   └── Processed numerical results reported in the manuscript
├── figures/
│   └── Reproducible manuscript figures
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

Exact package versions used for the reproducibility release will be
listed in `requirements.txt`.

## Reproducing the experiments

The reproducibility workflow consists of four main stages:

1. obtain and preprocess the STEAD earthquake data;
2. construct variable-cardinality event-level station sets;
3. train and evaluate the set-based and graph-based models using the
   predefined five-fold protocol;
4. reproduce the coverage-stratified statistical analyses, tables, and
   figures.

Detailed instructions will be provided in:

```text
docs/REPRODUCIBILITY.md
```

The repository will also include processed result tables so that the
statistical analyses and manuscript figures can be reproduced without
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

Random seeds and model hyperparameters used in the reported experiments
will be included in the configuration files.

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

Citation information for the associated manuscript will be provided in
`CITATION.cff`.

## Status

This repository is being prepared as the reproducibility archive for the
associated manuscript. The public release submitted with the manuscript
will contain the complete documented workflow required to reproduce the
main reported results.
