# Catalyst-Q Evidence Readiness

This report is generated from `benchmarks/suites.json`. It is a readiness report, not a solver superiority claim.

## Summary

- Suites tracked: 11
- Tier-one suites: 8
- Tier-two suites: 3
- Claim policy: No best-in-class claim is publishable without raw artifacts, validators, baseline versions, hardware metadata, and reproducible scripts.

## Suites

| Suite | Domain | Priority | Baselines | Claim target |
|---|---|---:|---|---|
| SAT Competition | SAT | tier_1 | Kissat, CaDiCaL, CryptoMiniSat, Mallob | Cost-normalized PAR-2 or time-to-valid-model on a named SAT Competition track. |
| MaxSAT Evaluation | MaxSAT | tier_1 | Open-WBO, MaxHS, LMHS, current evaluation entrants | Best objective or best cost-normalized solved count on a named complete or incomplete track. |
| TSPLIB95 | TSP | tier_1 | Concorde, LKH-3, OR-Tools routing | Best time-to-gap or cost-per-valid-tour on named TSPLIB subsets. |
| DIMACS TSP Challenge | TSP | tier_1 | DIMACS benchmark heuristic, LKH-3, Concorde where exact solve is feasible | Best scalability-adjusted tour quality on a named DIMACS TSP family. |
| OR-Library multidimensional knapsack | Knapsack | tier_1 | Gurobi, SCIP, OR-Tools CP-SAT, specialized branch-and-bound | Best cost-normalized feasible objective or proof rate on named OR-Library MKP files. |
| Pisinger hard knapsack families | Knapsack | tier_2 | specialized exact knapsack solvers, SCIP, Gurobi, OR-Tools CP-SAT | Strong performance on hard families where standard small knapsack benchmarks are too easy. |
| Biq Mac Library | QUBO/Max-Cut | tier_1 | Biq Mac, BiqCrunch, BiqBin, Gurobi, SCIP, D-Wave hybrid where accessible | Best cost-normalized time-to-best-known cut on named Biq Mac families. |
| QPLIB | QP/MIQP/MIQCP | tier_1 | Gurobi, SCIP, HiGHS for supported convex QP, BARON where licensed | Best developer-accessible QP/MIQP result on a named QPLIB subset. |
| MIPLIB 2017 | MIP | tier_1 | Gurobi, SCIP, HiGHS, CPLEX where licensed | Credibility benchmark for general optimization; not the first place to claim Catalyst-Q advantage. |
| QAPLIB | Quadratic Assignment | tier_2 | Gurobi, SCIP, specialized QAP heuristics, published QAPLIB best-known solutions | High-value proof point for assignment-structured optimization if Catalyst-Q wins time-to-good-enough. |
| Cloud/hardware competitor cost comparison | Quantum-inspired optimization | tier_2 | AWS Braket devices/simulators, D-Wave hybrid solvers, Fujitsu Digital Annealer where accessible, Toshiba SBM where accessible | Lowest cost per validated solution for named optimization workloads. |

## Next Evidence Required

- Add raw JSONL runs for Catalyst-Q and every baseline.
- Commit validator outputs and instance checksums.
- Generate objective, gap, runtime, and cost charts from raw artifacts.
- Promote claims only through the claims ladder in `docs/claims_policy.md`.

## Quantum Benchmark Evidence

The 2026-06-18 quantum benchmark packet records public-safe Catalyst-Q evidence as
a virtual quantum execution backend/simulator:

- Metriq submission under review: unitaryfoundation/metriq-data#459. The smaller
  #458 fallback was closed as superseded.
- QED-C Level 1-3 reproduction: four benchmark families at 1.000000 mean fidelity
  and Grover's Search at 0.998869 mean fidelity.
- SuperMarQ smoke: GHZ-4 at 0.999600, GHZ-6 at 0.998975, Mermin-Bell-4 at
  1.000000, and Mermin-Bell-6 at 1.000000.

Artifacts:

- `docs/quantum_benchmark_evidence_2026_06_18.md`
- `results/quantum_benchmark_20260618/qedc_level_1_3_summary.json`
- `results/quantum_benchmark_20260618/supermarq_smoke.json`
