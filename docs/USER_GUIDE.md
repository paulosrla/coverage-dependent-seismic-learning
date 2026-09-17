# User Guide

This document describes the inputs, outputs, model options, and expected
behavior of the computational workflow associated with the manuscript
*Coverage-Dependent Relational Learning for Multi-Station Earthquake
Magnitude Estimation*.

## Inputs

The workflow operates on station-event feature records derived from
earthquake waveforms in the Stanford Earthquake Dataset (STEAD).

Each station-event record contains:

- an event identifier;
- a station identifier;
- station-level waveform features;
- earthquake magnitude;
- metadata required for event construction.

## Event representation

Each earthquake is represented as a variable-cardinality, unordered set

\[
S_e = \{x_{e,1}, \ldots, x_{e,n_e}\},
\]

where \(n_e\) is the number of distinct stations observing event \(e\).

Only events observed by at least two distinct stations are included in
the main analysis.

## Models

The repository implements the following set-based models:

- MeanPool-MLP;
- Deep Sets;
- Set Transformer.

Complementary graph experiments include:

- Random-GATv2;
- Geographic-GATv2;
- FeatureSim-GATv2;
- Geographic-GCN.

FeatureSim-GATv2 uses a training-derived feature-similarity graph and
should not be interpreted as a mutual-information graph.

## Outputs

The workflow produces:

- fold-level predictions;
- overall MAE, RMSE, and R²;
- coverage-stratified performance metrics;
- paired bootstrap comparisons;
- coverage-boundary robustness analyses;
- manuscript figures.

Detailed execution commands and configuration options are provided in
the reproducibility documentation.