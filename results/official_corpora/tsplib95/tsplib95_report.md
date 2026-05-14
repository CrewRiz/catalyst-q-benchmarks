# TSPLIB95 Sequential Evidence Run

This is sequential benchmark evidence on a named official corpus. It is not a broad NP or SOTA proof.

## Corpus

- Source: http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/
- Available instances: 3
- Selected instances: 3

## Solver Summary

| Solver | Records | Valid records | Valid rate | Median runtime seconds | Total runtime seconds |
|---|---:|---:|---:|---:|---:|
| catalyst-q-sdk-request | 3 | 3 | 1.0 | 0.000388959 | 0.001488 |
| nearest-neighbor-2opt-baseline | 3 | 3 | 1.0 | 0.004397167 | 0.050414 |

## Result Rows

| Instance | Solver | Status | Objective | Runtime seconds | Valid |
|---|---|---:|---:|---:|---:|
| ulysses16.tsp | catalyst-q-sdk-request | unknown |  | 0.000735292 | True |
| ulysses16.tsp | nearest-neighbor-2opt-baseline | feasible | 83.0 | 0.001736375 | True |
| ulysses22.tsp | catalyst-q-sdk-request | unknown |  | 0.000363541 | True |
| ulysses22.tsp | nearest-neighbor-2opt-baseline | feasible | 84.0 | 0.004397167 | True |
| att48 | catalyst-q-sdk-request | unknown |  | 0.000388959 | True |
| att48 | nearest-neighbor-2opt-baseline | feasible | 34577.0 | 0.044280542 | True |
