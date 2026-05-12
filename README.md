# Catalyst-Q Public Benchmark Evidence

This repository is the public evidence track for Catalyst-Q. Its job is to make Catalyst-Q SDK and API claims reproducible against respected benchmark suites without exposing proprietary execution internals.

The current status is scaffolded evidence, not a final best-in-class claim. A claim becomes publishable only when the repo contains raw solver outputs, instance manifests with checksums, validator output, baseline versions, hardware metadata, and generated charts from the same artifacts.

## What This Repo Measures

Catalyst-Q will be evaluated on buyer-relevant and researcher-relevant axes:

- Validated solution quality: objective value, optimality gap, constraint violations, SAT assignment checks, UNSAT proof checks where available.
- Time to useful answer: wall time, solver time, time to first feasible, time to best feasible.
- Cost-normalized performance: API cost per valid solution, cost per 1 percent optimality gap, cost per solved instance.
- Scalability: instance size, variable count, qubit/circuit size where applicable, memory, retry rate.
- Reproducibility: fixed seeds, solver versions, hardware metadata, instance checksums, raw logs.

## Benchmark Tracks

The tier-one public evidence tracks are:

- SAT: SAT Competition benchmarks and scoring discipline.
- MaxSAT: MaxSAT Evaluation benchmarks and complete/incomplete tracks.
- TSP and routing: TSPLIB95 plus DIMACS TSP Challenge reporting style.
- Knapsack and multidimensional knapsack: OR-Library and hard knapsack families.
- QUBO, BQP, and Max-Cut: Biq Mac Library and QPLIB binary/discrete instances.
- General MIP and MIQP: MIPLIB 2017 and QPLIB for broader solver credibility.
- Quadratic assignment: QAPLIB for hard assignment structure.

## Baseline Solvers

The public comparisons should include strong, recognizable baselines:

- SAT: Kissat, CaDiCaL, CryptoMiniSat, and a parallel SAT baseline where appropriate.
- MaxSAT: Open-WBO, MaxHS/LMHS-family solvers, and current MaxSAT Evaluation entrants where runnable.
- TSP: Concorde for exact TSP, LKH-3 for heuristic TSP, and OR-Tools routing for developer baseline.
- MIP/MIQP/QP: Gurobi where licensed, SCIP, HiGHS, and OR-Tools CP-SAT where the model fits.
- QUBO/Max-Cut: Biq Mac/BiqCrunch/BiqBin where accessible, D-Wave hybrid solvers where account access is available, and commercial quantum-inspired systems only when their terms allow publication.

## Claim Ladder

- Evidence-ready: The harness runs and validates outputs.
- Competitive: Catalyst-Q is within a published threshold against strong baselines on a named suite.
- Best-in-class candidate: Catalyst-Q wins a named metric on a named suite under a fixed budget.
- Best-in-class: Catalyst-Q wins after reruns, validators, raw artifacts, and baseline configs are public.

No broad "solves NP" or "best at NP solvers" language belongs in this repository. The strongest credible claim is narrow: for example, "best cost-normalized time-to-1-percent gap on this named TSPLIB subset under this hardware and time budget."

## Quick Start

```bash
python3 -m pytest tests -q
python3 scripts/run_public_evidence.py --output results/evidence_index.md
```

The script generates a readiness report from the benchmark manifest. Real benchmark runs should write raw JSONL records into `results/raw/` and regenerated reports into `results/`.

## Repo Map

- `benchmarks/suites.json`: accepted benchmark suites, baselines, metrics, validators, and claim targets.
- `docs/benchmark_matrix.md`: why each track matters and what a publishable win means.
- `docs/execution_protocol.md`: raw result schema and benchmark budget rules.
- `docs/claims_policy.md`: language allowed before and after validated runs.
- `results/evidence_index.md`: generated readiness report.
- `assets/charts/evidence_coverage.svg`: generated coverage chart.
- `schemas/result.schema.json`: raw JSONL result record schema.

## Source Discipline

Public docs cite official benchmark or solver sources where possible. Proprietary algorithms, private proof text, internal state naming, and server implementation details do not belong here.
