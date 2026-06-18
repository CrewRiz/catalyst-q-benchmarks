# Public Announcement Draft

Date: 2026-06-18

Status: draft. Use as a request-for-review post unless Metriq review or
independent review has advanced enough to support a stronger announcement.

## Short Version

Catalyst-Q now has a public quantum benchmark evidence packet as a virtual
quantum execution backend/simulator.

The headline result is a Metriq submission under review with a local aggregate
validation value of 5,644,528,828.972562. We also published supporting QED-C
Level 1-3 reproduction artifacts and a SuperMarQ GHZ/Mermin-Bell smoke packet.

This is benchmark evidence, not a physical QPU claim. We are looking for
technical reviewers who can pressure-test the scoring interpretation, category
fit, and reproduction path.

Canonical evidence:

- Metriq review: unitaryfoundation/metriq-data#459
- Evidence packet: `docs/quantum_benchmark_evidence_2026_06_18.md`
- Machine-readable summaries: `results/quantum_benchmark_20260618/`

## Longer Version

Today I am publishing a Catalyst-Q quantum benchmark evidence packet.

Catalyst-Q is submitted as a virtual quantum execution backend/simulator. The
canonical Metriq submission is under review and produced a local aggregate
validation value of 5,644,528,828.972562 under the current Metriq scoring
scripts.

Supporting artifacts include QED-C Level 1-3 reproduction results and SuperMarQ
GHZ/Mermin-Bell smoke results. The public evidence packet is intentionally
conservative: it records measured benchmark outputs, checksums, public review
status, and claim boundaries.

What this is:

- Public benchmark evidence.
- A virtual backend/simulator submission.
- A request for serious technical review.

What this is not:

- A physical QPU claim.
- A cryptanalysis claim.
- A broad quantum advantage claim.
- A disclosure of backend implementation details.

The useful next step is scrutiny. I am looking for reviewers who can evaluate
benchmark validity, scoring interpretation, category fit, and the next
reproduction targets.

Reference context:

- Metriq: https://metriq.info/
- Metriq-gym benchmark docs: https://unitaryfoundation.github.io/metriq-gym/benchmarks/overview/
- Evidence packet: `docs/quantum_benchmark_evidence_2026_06_18.md`

## Outreach DM

Hi <name>, I am looking for skeptical technical review of a Catalyst-Q benchmark
packet. Catalyst-Q is submitted as a virtual quantum execution backend/simulator,
with a Metriq submission under review plus QED-C and SuperMarQ reproduction
artifacts. Would you be willing to spend 30 minutes pressure-testing the
benchmark interpretation and category fit?

Public packet: <link>

## Design Partner Note

Catalyst-Q is looking for a small number of design partners with hard simulation,
benchmark execution, or optimization workloads. The first conversation is not a
sales call; it is a scoped technical fit review around whether Catalyst-Q can
produce measurable evidence on a workload you already care about.
