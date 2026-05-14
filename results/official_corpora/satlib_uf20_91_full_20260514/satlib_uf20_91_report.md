# SATLIB uf20-91 Sequential Evidence Run

This is sequential benchmark evidence on a named official SATLIB corpus. It is not a broad NP or SOTA proof.

## Corpus

- Source: https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf20-91.tar.gz
- Download bytes: 323695
- Download SHA256: `be2835295e8500bb28f0314eba70bd0deaff1250b187260f7b6d0772bdf111a5`
- Available CNF instances: 1000
- Selected CNF instances: 1000
- Temp corpus cache removed: True

## Solver Summary

| Solver | Records | Valid records | Valid rate | Median runtime seconds | Total runtime seconds |
|---|---:|---:|---:|---:|---:|
| cadical | 1000 | 1000 | 1.0 | 0.007983896 | 8.127082 |
| catalyst-q-sdk-live | 1000 | 799 | 0.799 | 0.840183563 | 1481.134243 |
| kissat | 1000 | 1000 | 1.0 | 0.009750708 | 10.048748 |

## First 20 Result Rows

| Instance | Solver | Status | Objective | Runtime seconds | Valid |
|---|---|---:|---:|---:|---:|
| uf20-01 | catalyst-q-sdk-live | optimal | 91 | 0.799928375 | True |
| uf20-01 | kissat | optimal | 91 | 0.007664 | True |
| uf20-01 | cadical | optimal | 91 | 0.00577025 | True |
| uf20-010 | catalyst-q-sdk-live | optimal | 91 | 0.997450042 | True |
| uf20-010 | kissat | optimal | 91 | 0.008879333 | True |
| uf20-010 | cadical | optimal | 91 | 0.008111625 | True |
| uf20-0100 | catalyst-q-sdk-live | optimal | 91 | 0.572848209 | True |
| uf20-0100 | kissat | optimal | 91 | 0.008938292 | True |
| uf20-0100 | cadical | optimal | 91 | 0.008019917 | True |
| uf20-01000 | catalyst-q-sdk-live | optimal | 91 | 1.347348792 | True |
| uf20-01000 | kissat | optimal | 91 | 0.009327667 | True |
| uf20-01000 | cadical | optimal | 91 | 0.009541834 | True |
| uf20-0101 | catalyst-q-sdk-live | optimal | 91 | 0.594279125 | True |
| uf20-0101 | kissat | optimal | 91 | 0.005907458 | True |
| uf20-0101 | cadical | optimal | 91 | 0.005873917 | True |
| uf20-0102 | catalyst-q-sdk-live | feasible | 90 | 2.560675083 | False |
| uf20-0102 | kissat | optimal | 91 | 0.005236292 | True |
| uf20-0102 | cadical | optimal | 91 | 0.004818917 | True |
| uf20-0103 | catalyst-q-sdk-live | optimal | 91 | 1.1469835 | True |
| uf20-0103 | kissat | optimal | 91 | 0.01149 | True |
