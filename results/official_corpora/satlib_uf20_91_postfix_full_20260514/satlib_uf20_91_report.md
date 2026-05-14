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
| cadical | 1000 | 1000 | 1.0 | 0.009249604 | 8.845314 |
| catalyst-q-sdk-live | 1000 | 1000 | 1.0 | 0.54528125 | 748.303935 |
| kissat | 1000 | 1000 | 1.0 | 0.011456708 | 10.898355 |

## First 20 Result Rows

| Instance | Solver | Status | Objective | Runtime seconds | Valid |
|---|---|---:|---:|---:|---:|
| uf20-01 | catalyst-q-sdk-live | optimal | 91 | 3.298673666 | True |
| uf20-01 | kissat | optimal | 91 | 0.007278417 | True |
| uf20-01 | cadical | optimal | 91 | 0.005757416 | True |
| uf20-010 | catalyst-q-sdk-live | optimal | 91 | 1.6288745 | True |
| uf20-010 | kissat | optimal | 91 | 0.004330917 | True |
| uf20-010 | cadical | optimal | 91 | 0.004298458 | True |
| uf20-0100 | catalyst-q-sdk-live | optimal | 91 | 1.621106041 | True |
| uf20-0100 | kissat | optimal | 91 | 0.009260666 | True |
| uf20-0100 | cadical | optimal | 91 | 0.009296125 | True |
| uf20-01000 | catalyst-q-sdk-live | optimal | 91 | 2.067745791 | True |
| uf20-01000 | kissat | optimal | 91 | 0.0106405 | True |
| uf20-01000 | cadical | optimal | 91 | 0.009086958 | True |
| uf20-0101 | catalyst-q-sdk-live | optimal | 91 | 1.877441291 | True |
| uf20-0101 | kissat | optimal | 91 | 0.010379834 | True |
| uf20-0101 | cadical | optimal | 91 | 0.010798709 | True |
| uf20-0102 | catalyst-q-sdk-live | optimal | 91 | 1.50314975 | True |
| uf20-0102 | kissat | optimal | 91 | 0.013366542 | True |
| uf20-0102 | cadical | optimal | 91 | 0.01118725 | True |
| uf20-0103 | catalyst-q-sdk-live | optimal | 91 | 2.338602125 | True |
| uf20-0103 | kissat | optimal | 91 | 0.013577416 | True |
