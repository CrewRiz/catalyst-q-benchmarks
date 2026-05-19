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

## Full Evidence Package

`scripts/build_full_evidence_package.py` generates the current publishable scorecard. It combines:

- SDK route coverage across SAT, TSP, knapsack, portfolio, QUBO, and Max-Cut.
- Exact references for smoke instances.
- Simple heuristic baselines for comparison sanity checks.
- Live Catalyst-Q QUBO and Max-Cut API checks when `--execute-api` is enabled.
- A claim ledger that blocks broad SOTA language until external solver campaigns are present.

## Runtime Split

Use `requirements/benchmark-core.txt` locally and reserve
`requirements/benchmark-remote.txt` for remote runners. The heavy profile brings
in native optimization, SAT, quantum, and commercial solver clients that are not
appropriate for a 16 GB RAM / 256 GB disk laptop. Cloudflare should serve and
orchestrate evidence artifacts; GitHub Actions, Cloudflare Containers, or a
dedicated VM should execute CPU-heavy campaigns.
