# SATLIB uf20-91 Sequential Evidence Run

This is sequential benchmark evidence on a named official SATLIB corpus. It is not a broad NP or SOTA proof.

## Corpus

- Source: https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf20-91.tar.gz
- Download bytes: 323695
- Download SHA256: `be2835295e8500bb28f0314eba70bd0deaff1250b187260f7b6d0772bdf111a5`
- Available CNF instances: 1000
- Selected CNF instances: 1
- Temp corpus cache removed: True

## Solver Summary

| Solver | Records | Valid records | Valid rate | Median runtime seconds | Total runtime seconds |
|---|---:|---:|---:|---:|---:|
| cadical | 1 | 1 | 1.0 | 0.005807042 | 0.005807 |
| catalyst-q-sdk-live | 1 | 1 | 1.0 | 0.390092709 | 0.390093 |
| kissat | 1 | 1 | 1.0 | 0.004579875 | 0.00458 |

## First 20 Result Rows

| Instance | Solver | Status | Objective | Runtime seconds | Valid |
|---|---|---:|---:|---:|---:|
| uf20-0102 | catalyst-q-sdk-live | optimal | 91 | 0.390092709 | True |
| uf20-0102 | kissat | optimal | 91 | 0.004579875 | True |
| uf20-0102 | cadical | optimal | 91 | 0.005807042 | True |
