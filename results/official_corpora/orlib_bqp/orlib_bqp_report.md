# OR-Library BQP / QUBO Sequential Evidence Run

This is sequential benchmark evidence on a named official corpus. It is not a broad NP or SOTA proof.

## Corpus

- Source: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/
- Available instances: 5
- Selected instances: 5

## Solver Summary

| Solver | Records | Valid records | Valid rate | Median runtime seconds | Total runtime seconds |
|---|---:|---:|---:|---:|---:|
| catalyst-q-sdk-request | 5 | 5 | 1.0 | 0.000306292 | 0.001936 |
| single-flip-greedy-baseline | 5 | 5 | 1.0 | 0.090625833 | 0.492472 |

## Result Rows

| Instance | Solver | Status | Objective | Runtime seconds | Valid |
|---|---|---:|---:|---:|---:|
| bqp50_1 | catalyst-q-sdk-request | unknown |  | 0.000768584 | True |
| bqp50_1 | single-flip-greedy-baseline | feasible | -5124.0 | 0.086429542 | True |
| bqp50_2 | catalyst-q-sdk-request | unknown |  | 0.000303875 | True |
| bqp50_2 | single-flip-greedy-baseline | feasible | -2498.0 | 0.060591792 | True |
| bqp50_3 | catalyst-q-sdk-request | unknown |  | 0.000245084 | True |
| bqp50_3 | single-flip-greedy-baseline | feasible | -2702.0 | 0.159054541 | True |
| bqp50_4 | catalyst-q-sdk-request | unknown |  | 0.000312583 | True |
| bqp50_4 | single-flip-greedy-baseline | feasible | -2893.0 | 0.090625833 | True |
| bqp50_5 | catalyst-q-sdk-request | unknown |  | 0.000306292 | True |
| bqp50_5 | single-flip-greedy-baseline | feasible | -3617.0 | 0.095770667 | True |
