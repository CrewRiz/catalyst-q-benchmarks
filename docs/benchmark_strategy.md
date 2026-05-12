# Benchmark Strategy

The public evidence repo should earn credibility in two phases.

## Phase 1: Reproducible Harness

Build parsers, adapters, validators, and reports before publishing any strong claim.

- Freeze benchmark manifests with URLs, checksums, and license notes.
- Add solver adapters for Catalyst-Q, OR-Tools CP-SAT, SCIP, HiGHS, Kissat, Open-WBO, Concorde, and LKH-3.
- Store every run as JSONL with solver version, command line, seed, timeout, hardware, status, objective, runtime, memory, and validator result.
- Generate all charts from raw JSONL, never from hand-entered tables.

## Phase 2: Claim Campaigns

Run small public smoke suites in CI and full suites in controlled scheduled jobs.

- SAT/MaxSAT: solved count, PAR-2, certificate validity.
- TSP: valid tour rate, optimality gap, time to best, cost per valid tour.
- Knapsack/MKP: feasible objective, constraint violations, proof status.
- QUBO/Max-Cut: objective/cut value, best-known gap, repeatability across seeds.
- MIP/QPLIB: broad credibility and failure-mode analysis.

## Publication Rule

The public front page should show live examples and charts only after the raw artifacts are present in `results/raw/`. Until then, it should show benchmark readiness and explain exactly what will be measured.

