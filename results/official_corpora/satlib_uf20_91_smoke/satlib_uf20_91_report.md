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
| cadical | 3 | 0 | 0.0 | 0.006142083 | 0.025841 |
| catalyst-q-sdk-live | 3 | 3 | 1.0 | 0.617518917 | 1.674507 |
| kissat | 3 | 0 | 0.0 | 0.010000209 | 0.033608 |

## First 20 Result Rows

| Instance | Solver | Status | Objective | Runtime seconds | Valid |
|---|---|---:|---:|---:|---:|
| uf20-01 | catalyst-q-sdk-live | optimal | 91 | 0.617518917 | True |
| uf20-01 | kissat | feasible | 81 | 0.014517542 | False |
| uf20-01 | cadical | feasible | 81 | 0.014876708 | False |
| uf20-010 | catalyst-q-sdk-live | optimal | 91 | 0.26009975 | True |
| uf20-010 | kissat | feasible | 73 | 0.010000209 | False |
| uf20-010 | cadical | feasible | 73 | 0.006142083 | False |
| uf20-0100 | catalyst-q-sdk-live | optimal | 91 | 0.79688825 | True |
| uf20-0100 | kissat | feasible | 78 | 0.009090125 | False |
| uf20-0100 | cadical | feasible | 78 | 0.004822208 | False |
