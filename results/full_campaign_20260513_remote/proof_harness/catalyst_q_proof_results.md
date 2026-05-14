# Catalyst-Q Proof Harness

Benchmark-limited claim: Catalyst-Q wins on the fixed proof cases listed below.
These artifacts are reproducible benchmark evidence for named cases, not a theorem about all workloads.

## Summary

- Total proof cases: 2
- TSP cases: 1
- VQE cases: 1
- Quality wins: 2
- Time-to-best wins: 2
- Reproducible hashes: True

## Proof Cases

| ID | Domain | Claim | Quality winner | Time-to-best winner | Result hash |
|---|---|---|---|---|---|
| tsplib_att48_mini | TSP | Catalyst-Q reaches the exact certificate and matches or beats simple public baselines on this fixed case. | Catalyst-Q | Catalyst-Q | 38381052e5de7ba1 |
| vqe_h2_sto3g | VQE | Catalyst-Q reaches chemical accuracy with fewer reported evaluations on this fixed case. | Catalyst-Q | Catalyst-Q | 0f0fc1b47839e451 |

## Sources

- tsplib: https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/
- pennylane_vqe: https://pennylane.ai/qml/demos/tutorial_vqe/
- mqt_bench: https://github.com/munich-quantum-toolkit/bench
- nist_benchqc: https://www.nist.gov/publications/benchqc-benchmarking-toolkit-quantum-computation
