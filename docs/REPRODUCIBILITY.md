# Reproducibility Guide

This document describes the computational workflow associated with
*Coverage-Dependent Relational Learning for Multi-Station Earthquake
Magnitude Estimation*.

## Workflow

The analysis consists of:

1. STEAD data acquisition;
2. regional and event filtering;
3. station-level waveform feature extraction;
4. variable-cardinality event construction;
5. five-fold model evaluation;
6. coverage-stratified analysis;
7. paired bootstrap analysis;
8. manuscript figure generation.

## Dataset selection

The experiments use earthquake observations from STEAD restricted to
Southern California. Both recording stations and earthquake sources
are restricted to:

- latitude: 32.0°–37.0° N;
- longitude: 121.0°–114.5° W.

Only earthquake traces are considered, and the main analysis retains
events observed by at least two distinct stations.

## Final analysis dataset

The principal analysis contains:

- 73,114 earthquake events;
- 307,392 station-event observations;
- 314 infrastructure stations;
- 30 waveform-derived features per station observation;
- event-level station coverage ranging from 2 to 48 stations.

## Cross-validation

The principal set-based models are evaluated using the same five
event-level folds.

Feature standardization is performed independently within each fold.
Scaling parameters are estimated exclusively from training
station-event observations and subsequently applied to the
corresponding validation observations.

## Graph experiments

The complementary graph experiments use three connectivity definitions:

- geographic proximity;
- training-derived station feature similarity;
- random connectivity as a topology control.

The feature-similarity topology is constructed independently within
each fold using training data only.

## Coverage analysis

Performance is evaluated for three principal event-level coverage
regimes:

- sparse: 2–5 active stations;
- intermediate: 6–10 active stations;
- dense: 11 or more active stations.

Alternative coverage boundaries are evaluated as a robustness analysis.

## Statistical analysis

Paired event-level bootstrap resampling is used to estimate confidence
intervals for differences in MAE between models.

## Computational environment

The experiments were executed in a Linux x86-64 environment with the
following principal software versions:

- Python 3.13.15
- NumPy 2.1.3
- pandas 2.2.3
- SciPy 1.16.3
- scikit-learn 1.6.1
- Matplotlib 3.10.0
- PyTorch 2.11.0+cu128
- PyTorch Geometric 2.8.0.post1
- NetworkX 3.6.1
- CUDA runtime 12.8

GPU-accelerated experiments were executed on an NVIDIA Tesla T4.

The principal set-learning experiments use PyTorch directly. PyTorch
Geometric is additionally required for the complementary GATv2 and GCN
experiments.

## Reproduction instructions

Exact execution commands, configuration files, random seeds, and
expected output files are provided with the finalized computational
pipeline.