# SATLIB uf20-91 Sequential Evidence Run

This is sequential benchmark evidence on a named official SATLIB corpus. It is not a broad NP or SOTA proof.

## Corpus

- Source: https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf20-91.tar.gz
- Download bytes: 323695
- Download SHA256: `be2835295e8500bb28f0314eba70bd0deaff1250b187260f7b6d0772bdf111a5`
- Available CNF instances: 1000
- Selected CNF instances: 3
- Temp corpus cache removed: True

## Solver Summary

| Solver | Records | Valid records | Valid rate | Median runtime seconds | Total runtime seconds |
|---|---:|---:|---:|---:|---:|
| cadical | 3 | 3 | 1.0 | 0.006333166 | 0.020309 |
| catalyst-q-sdk-live | 3 | 3 | 1.0 | 1.409471291 | 5.563996 |
| kissat | 3 | 3 | 1.0 | 0.008142375 | 0.024048 |

## First 20 Result Rows

| Instance | Solver | Status | Objective | Runtime seconds | Valid |
|---|---|---:|---:|---:|---:|
| uf20-01 | catalyst-q-sdk-live | optimal | 91 | 3.402670416 | True |
| uf20-01 | kissat | optimal | 91 | 0.006254667 | True |
| uf20-01 | cadical | optimal | 91 | 0.006202417 | True |
| uf20-010 | catalyst-q-sdk-live | optimal | 91 | 0.751854458 | True |
| uf20-010 | kissat | optimal | 91 | 0.009650459 | True |
| uf20-010 | cadical | optimal | 91 | 0.006333166 | True |
| uf20-0100 | catalyst-q-sdk-live | optimal | 91 | 1.409471291 | True |
| uf20-0100 | kissat | optimal | 91 | 0.008142375 | True |
| uf20-0100 | cadical | optimal | 91 | 0.007773834 | True |
