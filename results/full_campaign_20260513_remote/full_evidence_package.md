# Catalyst-Q Full Evidence Package

No broad NP or SOTA claim is made. Claims are limited to named artifacts and validators.

## Summary

- Route coverage: 6/6
- Live exact matches: 2/2
- Live heuristic wins: 2/2
- Records: 20
- Publishable claims: 4
- External solver records: 4
- Quantum test commands passed: 2/2

## Claim Ledger

| Claim | Status | Evidence |
|---|---|---|
| Catalyst-Q SDK exposes all six public NP helper routes: SAT, TSP, knapsack, portfolio, QUBO, and Max-Cut. | publishable | SDK prepared-request records with route validators. |
| Catalyst-Q live SDK/API matches the exact QUBO reference objective -4.0 on the bundled smoke instance. | publishable | Raw record validator.matches_reference for QUBO. |
| Catalyst-Q live SDK/API matches the exact Max-Cut reference objective 9.0 on the bundled smoke instance. | publishable | Raw record validator.matches_reference for Max-Cut. |
| Catalyst-Q live SDK/API beats the included greedy heuristic baselines on the bundled QUBO and Max-Cut smoke instances. | publishable | QUBO is lower-is-better and Max-Cut is higher-is-better against local heuristic baseline records. |
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
| biqmac_qubo_6 | QUBO | catalyst-q-sdk-live | optimal | -4.0 |
| biqmac_maxcut_6 | Max-Cut | catalyst-q-sdk-live | optimal | 9.0 |
| sat_smoke_4 | SAT | kissat | optimal | 6 |
| sat_smoke_4 | SAT | cadical | optimal | 6 |
| orlib_knapsack_12 | Knapsack | highs | optimal | 220.0 |
| orlib_knapsack_12 | Knapsack | scip | optimal | 220.0 |

## Quantum Simulator Evidence

| Command | Status | Runtime seconds |
|---|---:|---:|
| `python3 -m pytest tests/test_quantum_v2.py Catalyst-API/tests/test_gates.py Catalyst-API/tests/test_universal_gate_set.py Catalyst-API/tests/test_simulator.py -q` | passed | 0.357607 |
| `python3 -m pytest tests/sdk/test_public_benchmark_harness.py tests/sdk/test_proof_harness.py -q` | passed | 0.403279 |

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
