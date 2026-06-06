# Catalyst-Q Benchmark Evidence

**Generated:** May 2026

This repository is evidence infrastructure for Catalyst-Q. It contains
benchmark manifests, validators, raw result formats, and generated scorecards
for named public workloads.

The benchmark claim boundary is intentionally narrow:

- Catalyst-Q results are publishable only for named instances with committed
  inputs, raw records, validators, and reproducible artifacts.
- High-qubit circuit evidence is query-native targeted exactness for supported
  structured and bounded-contraction families. It is not a claim that arbitrary
  dense output distributions can be materialized at those widths.
- Solver comparisons require external baseline runs before broad SOTA language
  is allowed.

## Generated Evidence Package

`scripts/build_full_evidence_package.py` generates the current scorecard from
raw records and high-qubit exactness artifacts.

Checked-in files under `results/` are generated snapshots. Regenerate the
package before publishing fresh claims or assuming it reflects uncommitted
source changes.

Publishable evidence includes:

- SDK route coverage for SAT, TSP, knapsack/MKP, portfolio, QUBO, Max-Cut, and
  DAG optimization request surfaces.
- Exact reference objectives for bundled smoke instances.
- Live Catalyst-Q QUBO and Max-Cut API checks when `--execute-api` is enabled.
- Compact exact high-qubit targeted answers with zero dense state
  materialization across the generated high-qubit campaign.

The generated package lives in `results/full_evidence_package.md`.

## Benchmark Surfaces

| Surface | What is measured | Claim status |
|---|---|---|
| Public solver routes | Request validity, objective extraction, exact smoke references | Publishable per named record |
| QUBO and Max-Cut smoke runs | Live API objective vs exact reference and simple heuristic baseline | Publishable when raw live records are present |
| High-qubit exactness | Targeted probabilities, amplitudes, marginals, and observables | Publishable for named supported query families |
| External SOTA campaigns | SAT, MaxSAT, TSPLIB, OR-Library, Biq Mac, QPLIB, MIPLIB, QAPLIB | Not yet complete |

## Reproduce Locally

```bash
python3 -m pytest tests -q
PYTHONPATH=src python3 scripts/run_high_qubit_exactness.py
PYTHONPATH=src python3 scripts/build_full_evidence_package.py
```

Use live API execution only when intentionally collecting remote evidence:

```bash
PYTHONPATH=src python3 scripts/build_full_evidence_package.py --execute-api
```

## Claim Policy

See `docs/claims_policy.md`. In short: publish measured, named outcomes; do not
publish generalized complexity, universal quantum simulation, or
category-leadership claims without the corresponding raw campaigns and external
baselines.
