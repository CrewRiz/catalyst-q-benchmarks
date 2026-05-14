# DIMACS / G-Set Max-Cut Sequential Evidence Run

This is sequential benchmark evidence on a named official corpus. It is not a broad NP or SOTA proof.

## Corpus

- Source: https://web.stanford.edu/~yyye/yyye/Gset/
- Available instances: 3
- Selected instances: 3

## Solver Summary

| Solver | Records | Valid records | Valid rate | Median runtime seconds | Total runtime seconds |
|---|---:|---:|---:|---:|---:|
| catalyst-q-sdk-request | 3 | 3 | 1.0 | 0.0043785 | 0.015409 |
| greedy-partition-baseline | 3 | 3 | 1.0 | 1.536893292 | 4.661162 |

## Result Rows

| Instance | Solver | Status | Objective | Runtime seconds | Valid |
|---|---|---:|---:|---:|---:|
| G1 | catalyst-q-sdk-request | unknown |  | 0.0043785 | True |
| G1 | greedy-partition-baseline | feasible | 10137.0 | 1.5973665 | True |
| G2 | catalyst-q-sdk-request | unknown |  | 0.006949708 | True |
| G2 | greedy-partition-baseline | feasible | 10146.0 | 1.536893292 | True |
| G3 | catalyst-q-sdk-request | unknown |  | 0.004080541 | True |
| G3 | greedy-partition-baseline | feasible | 10026.0 | 1.526902542 | True |
