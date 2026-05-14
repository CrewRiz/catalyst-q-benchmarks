# Catalyst-Q High-Qubit Exactness Evidence

This campaign validates compact exact execution answers for named structured and bounded-contraction circuits. It is not a claim that arbitrary dense output distributions can be materialized at these widths.

## Summary

- Cases: 11
- Exact cases: 11
- Zero-materialization cases: 11
- Maximum qubits: 4096
- Maximum gate count: 131328
- Maximum dense statevector memory: 10^1234.222982 bytes

## Cases

| ID | Suite | Qubits | Gates | Metric | Answer mode | Exact | Materialized states | Runtime seconds | Dense memory |
|---|---|---:|---:|---|---|---:|---:|---:|---:|
| supermarq_ghz_64 | SuperMarQ | 64 | 64 | probability | structured_entanglement_certificate | True | 0 | 0.000238041 | 2^68 bytes |
| supermarq_ghz_4096 | SuperMarQ | 4096 | 4096 | probability | structured_entanglement_certificate | True | 0 | 0.020686958 | 2^4100 bytes |
| qedc_uniform_h_1000 | QED-C application-oriented | 1000 | 1000 | probability | separable_product_certificate | True | 0 | 0.002560042 | 2^1004 bytes |
| qasmbench_qft_phase_32 | QASMBench / MQT Bench | 32 | 528 | probability | diagonal_phase_certificate | True | 0 | 0.001672917 | 2^36 bytes |
| qedc_brickwork_echo_32 | QED-C application-oriented | 32 | 380 | probability | adaptive_query_contraction | True | 0 | 2.793936584 | 2^36 bytes |
| qedc_brickwork_echo_64 | QED-C application-oriented | 64 | 764 | probability | adaptive_query_contraction | True | 0 | 20.934170667 | 2^68 bytes |
| qasmbench_qft_phase_512 | QASMBench / MQT Bench | 512 | 131328 | probability | diagonal_phase_certificate | True | 0 | 0.490688875 | 2^516 bytes |
| supermarq_phase_chain_1024 | SuperMarQ-style application circuit | 1024 | 3071 | amplitude | chain_phase_certificate | True | 0 | 33.356540625 | 2^1028 bytes |
| qedc_product_rotations_2048 | QED-C application-oriented | 2048 | 6144 | probability | separable_product_certificate | True | 0 | 0.0358445 | 2^2052 bytes |
| mqt_symmetric_phase_256 | MQT Bench / SuperMarQ-style | 256 | 33152 | amplitude | symmetric_orbit_certificate | True | 0 | 0.31628825 | 2^260 bytes |
| supermarq_ghz_4096_x_observable | SuperMarQ | 4096 | 4096 | observable | structured_entanglement_certificate | True | 0 | 0.022773875 | 2^4100 bytes |

## Sources

- qedc: https://quantumconsortium.org/publication/application-oriented-performance-benchmarks-for-quantum-computing/
- qedc_exploration: https://quantumconsortium.org/publication/quantum-algorithm-exploration-using-application-oriented-performance-benchmarks/
- supermarq: https://www.scholars.northwestern.edu/en/publications/supermarq-a-scalable-quantum-benchmark-suite
- qasmbench: https://github.com/pnnl/QASMBench
- mqt_bench: https://github.com/munich-quantum-toolkit/bench
