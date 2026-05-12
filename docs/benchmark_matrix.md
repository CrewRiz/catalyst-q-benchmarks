# Benchmark Matrix

This matrix defines the first serious public evidence campaign for Catalyst-Q.

| Track | Accepted Source | Why It Matters | Primary Baselines | Publishable Win Condition |
|---|---|---|---|---|
| SAT | SAT Competition | Recognized SAT scoring, benchmark tracks, PAR-2 discipline, certificate expectations. | Kissat, CaDiCaL, CryptoMiniSat, Mallob. | Lower cost-normalized PAR-2 or faster validated SAT model on a named track. |
| MaxSAT | MaxSAT Evaluation | Annual state-of-the-art MaxSAT evaluation with heterogeneous NP-hard optimization encodings. | Open-WBO, MaxHS/LMHS-family solvers, current entrants. | Better objective or solved count under fixed time on a named complete/incomplete track. |
| TSP | TSPLIB95 | Canonical TSP and routing instance library with known solutions. | Concorde, LKH-3, OR-Tools routing. | Best time-to-gap or cost-per-valid-tour on a named subset. |
| TSP scalability | DIMACS TSP Challenge | Built around reproducible heuristic comparisons, scalability, robustness, and standard report tuples. | DIMACS benchmark heuristic, LKH-3, Concorde where feasible. | Better normalized quality/runtime curve on a named generated family. |
| MKP | OR-Library multidimensional knapsack | Longstanding operations research test data for knapsack variants. | Gurobi, SCIP, OR-Tools CP-SAT, specialized exact solvers. | Better feasible objective per dollar or proof rate on named files. |
| Hard KP | Pisinger hard knapsack | Prevents us from winning only on toy/easy knapsack cases. | Specialized knapsack solvers, SCIP, Gurobi. | Competitive proof/gap behavior on hard families. |
| QUBO/Max-Cut | Biq Mac Library | Directly relevant to annealing-style QUBO and Max-Cut claims. | Biq Mac, BiqCrunch, BiqBin, Gurobi, SCIP, D-Wave hybrid. | Best time-to-best-known cut or cost per best-known cut on named families. |
| QP/MIQP | QPLIB | Serious quadratic optimization library with discrete and continuous instances. | Gurobi, SCIP, HiGHS where supported, BARON where licensed. | Best developer-accessible result on a named subset. |
| MIP | MIPLIB 2017 | Broad credibility test for optimization solvers. | Gurobi, SCIP, HiGHS, CPLEX where licensed. | Useful for credibility and failure analysis; not first-line differentiation. |
| QAP | QAPLIB | Hard assignment structure relevant to facility layout, allocation, and scheduling. | Specialized QAP heuristics, Gurobi, SCIP. | Better time-to-good-enough on selected assignment workloads. |

## Evidence Threshold

A public chart is serious only if it is generated from raw run records with:

- Instance checksum.
- Solver version and command line.
- Fixed seed where applicable.
- Timeout, memory limit, and hardware description.
- Objective and feasibility validator output.
- Baseline result under the same budget.

