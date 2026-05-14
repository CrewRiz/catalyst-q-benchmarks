# Catalyst-Q Public Benchmark Harness

This report validates SDK request generation, billing estimates, and payload shape against public benchmark families.
It is not a formal complexity proof and does not disclose proprietary execution internals.

## Summary

- API execution mode: live-api
- Total cases: 17
- Quantum cases: 8
- Solver cases: 9
- Public suites covered: 15
- Successful API cases: 17
- Median API latency ms: 73.043
- Total compute units: 64515423390

## Cases

| ID | Suite | Family | Type | Size | Compute units | Payload bytes |
|---|---|---|---|---|---:|---:|
| qedc_bernstein_vazirani_8 | QED-C Application-Oriented Benchmarks | Bernstein-Vazirani | circuit | 8-bit hidden string | 285696 | 1778 |
| supermarq_ghz_16 | SupermarQ | GHZ | circuit | 16 qubits | 524288 | 2060 |
| supermarq_qaoa_ring_8 | SupermarQ | QAOA ring | circuit | 8 qubits, one layer | 393216 | 2781 |
| qasmbench_qft_5_qasm | QASMBench | QFT | qasm | 5 qubits | 112640 | 1430 |
| mqtbench_grover_6 | MQT Bench | Grover | circuit | 6 qubits | 282624 | 2107 |
| satlib_random_3sat_20 | SATLIB | Random 3-SAT | solver | 20 variables, 86 clauses | 1720 | 1737 |
| tsplib_euclidean_10 | TSPLIB | Euclidean TSP | solver | 10 cities | 100 | 1166 |
| orlib_mknap_12 | OR-Library Knapsack | 0/1 knapsack | solver | 12 items | 576 | 883 |
| orlib_portfolio_8 | OR-Library Portfolio | Cardinality-constrained portfolio | solver | 8 assets | 64 | 1432 |
| biqmac_qubo_6 | Biq Mac Library | Binary quadratic optimization | solver | 6 binary variables | 36 | 985 |
| biqmac_maxcut_6 | Biq Mac Library | Max-Cut | solver | 6 nodes, 9 weighted edges | 54 | 1049 |
| cafa6_dag_optimization_12 | Catalyst Biocomputation | DAG Optimization | solver | 12 nodes, 11 dependencies | 144 | 1494 |
| cafa6_full_adder_4 | Catalyst Arithmetic | Adder | circuit | 4 qubits | 36864 | 1197 |
| google_echo_8 | Catalyst Sampling | Loschmidt Echo | circuit | 8 qubits | 442368 | 2651 |
| sat_competition_100 | SAT Competition | Random 3-SAT | solver | 100 variables, 400 clauses | 40000 | 5732 |
| miplib_mknap_100 | MIPLIB 2017 | Integer Linear Programming | solver | 100 items, 5 constraints | 1303000 | 2427 |
| qasmbench_qft_500 | QASMBench Advantage | Quantum Fourier Transform | circuit | 500 qubits, 125,250 gates | 64512000000 | 8903542 |

## Sources

- qedc: https://quantumconsortium.org/publication/application-oriented-performance-benchmarks-for-quantum-computing/
- supermarq: https://www.scholars.northwestern.edu/en/publications/supermarq-a-scalable-quantum-benchmark-suite
- qasmbench: https://github.com/pnnl/QASMBench
- mqt_bench: https://github.com/munich-quantum-toolkit/bench
- satlib: https://www.cs.ubc.ca/~hoos/SATLIB/
- tsplib: https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/index.html
- orlib_knapsack: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/mknapinfo.html
- orlib_portfolio: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/portinfo.html
- biq_mac: https://biqmac.aau.at/biqmaclib.html
