# Catalyst-Q Full Evidence Package

No broad NP or SOTA claim is made. Claims are limited to named artifacts and validators.

## Summary

- Route coverage: 6/7
- Live exact matches: 0/2
- Live heuristic wins: 0/2
- Records: 17
- Publishable claims: 2
- External solver records: 0
- Quantum test commands passed: 0/0
- High-qubit exact cases: 11/11
- High-qubit max width: 4096 qubits

## Claim Ledger

| Claim | Status | Evidence |
|---|---|---|
| Catalyst-Q SDK exposes all seven public NP helper routes: SAT, TSP, knapsack/MKP, portfolio, QUBO, Max-Cut, and DAG Optimization. | publishable | SDK prepared-request records with route validators. |
| Catalyst-Q live SDK/API matches the exact QUBO reference objective -4.0 on the bundled smoke instance. | blocked-until-live-api-run | Raw record validator.matches_reference for QUBO. |
| Catalyst-Q live SDK/API matches the exact Max-Cut reference objective 9.0 on the bundled smoke instance. | blocked-until-live-api-run | Raw record validator.matches_reference for Max-Cut. |
| Catalyst-Q live SDK/API beats the included greedy heuristic baselines on the bundled QUBO and Max-Cut smoke instances. | blocked-until-live-api-run | QUBO is lower-is-better and Max-Cut is higher-is-better against local heuristic baseline records. |
| Catalyst-Q compact execution validates exact targeted answers with zero dense state materialization across 11 high-qubit benchmark cases up to 4096 qubits. | publishable | High-qubit exactness artifact summary and per-case validator rows. |
| Catalyst-Q is broadly best-in-class against commercial and academic SOTA solvers. | not-yet-supported | Requires full Biq Mac/Gset/QPLIB/TSPLIB/SAT/MaxSAT campaigns against external baselines. |

## Results

| Instance | Domain | Solver | Status | Objective |
|---|---|---|---:|---:|
| sat_smoke_4 | SAT | exact-enumeration-reference | optimal | 6 |
| sat_smoke_4 | SAT | majority-literal-baseline | feasible | 5 |
| tsplib_style_8 | TSP | exact-enumeration-reference | optimal | 45 |
| tsplib_style_8 | TSP | nearest-neighbor-2opt-baseline | feasible | 45 |
| orlib_knapsack_12 | Knapsack | exact-dp-reference | optimal | 220 |
| orlib_knapsack_12 | Knapsack | density-greedy-baseline | feasible | 184 |
| biqmac_qubo_6 | QUBO | exact-enumeration-reference | optimal | -4.0 |
| biqmac_qubo_6 | QUBO | single-flip-greedy-baseline | feasible | 0.0 |
| biqmac_maxcut_6 | Max-Cut | exact-enumeration-reference | optimal | 9.0 |
| biqmac_maxcut_6 | Max-Cut | greedy-partition-baseline | feasible | 6.75 |
| sat_smoke_4 | SAT | catalyst-q-sdk-request | unknown |  |
| tsplib_style_8 | TSP | catalyst-q-sdk-request | unknown |  |
| orlib_knapsack_12 | Knapsack | catalyst-q-sdk-request | unknown |  |
| portfolio_smoke_8 | Portfolio | catalyst-q-sdk-request | unknown |  |
| biqmac_qubo_6 | QUBO | catalyst-q-sdk-request | unknown |  |
| biqmac_maxcut_6 | Max-Cut | catalyst-q-sdk-request | unknown |  |
| cafa6_dag_optimization_12 | DAG Optimization | catalyst-q-sdk-request | unknown |  |

## High-Qubit Exactness Evidence

This campaign validates compact exact execution answers for named structured and bounded-contraction circuits. It is not a claim that arbitrary dense output distributions can be materialized at these widths.

| Case | Suite | Qubits | Gates | Answer mode | Exact | Materialized states | Runtime seconds |
|---|---|---:|---:|---|---:|---:|---:|
| supermarq_ghz_64 | SuperMarQ | 64 | 64 | structured_entanglement_certificate | True | 0 | 0.000238041 |
| supermarq_ghz_4096 | SuperMarQ | 4096 | 4096 | structured_entanglement_certificate | True | 0 | 0.020686958 |
| qedc_uniform_h_1000 | QED-C application-oriented | 1000 | 1000 | separable_product_certificate | True | 0 | 0.002560042 |
| qasmbench_qft_phase_32 | QASMBench / MQT Bench | 32 | 528 | diagonal_phase_certificate | True | 0 | 0.001672917 |
| qedc_brickwork_echo_32 | QED-C application-oriented | 32 | 380 | adaptive_query_contraction | True | 0 | 2.793936584 |
| qedc_brickwork_echo_64 | QED-C application-oriented | 64 | 764 | adaptive_query_contraction | True | 0 | 20.934170667 |
| qasmbench_qft_phase_512 | QASMBench / MQT Bench | 512 | 131328 | diagonal_phase_certificate | True | 0 | 0.490688875 |
| supermarq_phase_chain_1024 | SuperMarQ-style application circuit | 1024 | 3071 | chain_phase_certificate | True | 0 | 33.356540625 |
| qedc_product_rotations_2048 | QED-C application-oriented | 2048 | 6144 | separable_product_certificate | True | 0 | 0.0358445 |
| mqt_symmetric_phase_256 | MQT Bench / SuperMarQ-style | 256 | 33152 | symmetric_orbit_certificate | True | 0 | 0.31628825 |
| supermarq_ghz_4096_x_observable | SuperMarQ | 4096 | 4096 | structured_entanglement_certificate | True | 0 | 0.022773875 |

Artifact SHA-256: `993ae993b8ffc378a869cb5aabf231b1818c041aa42e2846c88f73f4f91036c0`

## External SOTA Baseline Readiness

| Solver | Tool | Available Here | Source |
|---|---|---:|---|
| Gurobi | `gurobi_cl` | False | https://www.gurobi.com/solutions/ |
| SCIP | `scip` | True | https://scipopt.org/ |
| HiGHS | `highs` | True | https://highs.dev/ |
| Kissat | `kissat` | True | https://satcompetition.github.io/ |
| CaDiCaL | `cadical` | True | https://satcompetition.github.io/ |
| Concorde | `concorde` | False | https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/index.html |
| LKH | `LKH` | False | https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/index.html |

## Sources

- biq_mac: https://biqmac.aau.at/biqmaclib.html
- tsplib: https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/index.html
- miplib: https://miplib.zib.de/
- qplib: https://qplib.zib.de/
- or_library: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/mknapinfo.html
- sat_competition: https://satcompetition.github.io/
- maxsat_evaluation: https://maxsat-evaluations.github.io/
- scip: https://scipopt.org/
- highs: https://highs.dev/
- gurobi: https://www.gurobi.com/solutions/
