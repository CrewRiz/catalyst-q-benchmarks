# Benchmark Expansion Targets

Date: 2026-06-18

This target map prioritizes benchmark suites that can build confidence around
Catalyst-Q without exposing private implementation details.

## Priority 1: Public Quantum Benchmark Anchors

| Target | Why it matters | Next action | Public claim posture |
|---|---|---|---|
| Metriq / metriq-gym | Public scoreboard, benchmark runner, and reviewable dataset for heterogeneous quantum devices and backends. | Defend unitaryfoundation/metriq-data#459 and request proper `data` / `source:metriq-gym` labels from maintainers. | Submission under review; not accepted rank until merged. |
| QED-C Application-Oriented Benchmarks | Recognized application-oriented suite for end-user quantum performance evaluation. | Expand beyond Level 1-3 smoke into selected higher-width families with clean artifacts. | Reproduction evidence for a virtual backend/simulator. |
| SuperMarQ | Application-oriented suite with scalable benchmarks and feature-vector coverage. | Add more SuperMarQ workloads after GHZ/Mermin-Bell smoke is stable. | Smoke and reproduction evidence, not hardware claims. |
| MQT Bench | Broad circuit benchmark library across abstraction levels. | Generate a small public-safe Catalyst-Q run matrix across representative circuits. | Circuit benchmark coverage evidence. |

## Priority 2: Useful Follow-On Suites

| Target | Why it matters | Suggested slice |
|---|---|---|
| QASMBench | Large circuit corpus used in quantum compiler and architecture research. | Select a small, named subset with committed checksums and expected outputs. |
| Qiskit benchmark circuits | Familiar to enterprise and research reviewers. | Use common algorithm families with transparent parameters and artifact checksums. |
| Optimization corpora already tracked here | Bridges quantum simulation evidence with business-relevant optimization. | Continue SAT, MaxSAT, QUBO/Max-Cut, TSP, and knapsack under strict validator rules. |

## Evidence Requirements

Every new benchmark packet should include:

- Suite name and version or commit.
- Circuit or instance checksum.
- Backend classification.
- Shot count or exact-read scope.
- Runtime and scoring metric.
- Exclusions and known failures.
- Public claim boundary.
- Reproduction command or reviewer pathway that does not expose implementation
  details.

## Reporting Norms

Use the same evidence threshold for every new target:

- Submitted results are not accepted results until the upstream project says so.
- Experimental or category-mismatched comparisons must be labeled clearly.
- Every comparison needs a stated basis: suite version, metric, category,
  scoring path, and artifact source.
- Reviewer-facing packets should reveal enough context to evaluate the benchmark
  without revealing backend implementation details.

## Anti-Goals

- Do not chase every benchmark at once.
- Do not publish private endpoints, release ids, routing details, or backend
  implementation notes.
- Do not describe results as accepted leaderboard status before upstream merge.
- Do not compare against physical QPUs without explaining the category boundary.

## Recommended Next Batch

1. Metriq label/review follow-up for #459.
2. QED-C Level 4-5 pilot packet, if runtime and scoring remain stable.
3. SuperMarQ expansion to Hamiltonian Simulation and QAOA-style workloads.
4. MQT Bench representative circuit matrix with 5-10 named circuits.

## Reference Links

- Metriq: https://metriq.info/
- Metriq-gym benchmark docs: https://unitaryfoundation.github.io/metriq-gym/benchmarks/overview/
- QED-C Application-Oriented Benchmarks: https://github.com/SRI-International/QC-App-Oriented-Benchmarks
- SuperMarQ docs: https://superstaq.readthedocs.io/en/v0.5.26/apps/supermarq/supermarq.html
- MQT Bench: https://github.com/munich-quantum-toolkit/bench
- SPEC Fair Use Rules: https://www.spec.org/products/fairuse/
- MLCommons inference submission guide: https://docs.mlcommons.org/inference/submission/
