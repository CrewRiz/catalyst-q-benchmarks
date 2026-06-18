# Catalyst-Q Technical Diligence Packet

Date: 2026-06-18

## One-Sentence Summary

Catalyst-Q is a virtual quantum execution backend/simulator with a public Metriq
submission under review and supporting QED-C and SuperMarQ reproduction artifacts.

## What Is Being Submitted

The canonical Metriq submission is unitaryfoundation/metriq-data#459. It records
a Catalyst-Q benchmark packet that produced a local aggregate validation value of
5,644,528,828.972562 under the current Metriq scoring scripts.

The aggregate is submitted evidence under review. It is not represented here as
an accepted leaderboard rank until the upstream review process completes.

## Supporting Reproduction Artifacts

| Suite | Scope | Result summary |
|---|---|---|
| QED-C Application-Oriented Benchmarks | Level 1-3 reproduction | Bernstein-Vazirani, Hidden Shift, Quantum Fourier Transform, and Phase Estimation at 1.000000 mean fidelity; Grover's Search at 0.998869. |
| SuperMarQ | GHZ and Mermin-Bell smoke | GHZ-4 at 0.999600, GHZ-6 at 0.998975, Mermin-Bell-4 at 1.000000, Mermin-Bell-6 at 1.000000. |

Machine-readable summaries are committed under
`results/quantum_benchmark_20260618/`.

## What Reviewers Should Check

1. Are the benchmark records formatted correctly for the target benchmark suite?
2. Are the reported scores consistent with the committed artifacts?
3. Is Catalyst-Q categorized appropriately as a virtual quantum execution
   backend/simulator?
4. Does the Metriq aggregate follow from the current Metriq scoring scripts?
5. Are any benchmark exclusions or caveats material to the interpretation?

## What This Does Not Claim

- It does not claim Catalyst-Q is a physical QPU.
- It does not claim cryptanalysis capability.
- It does not claim broad quantum advantage.
- It does not claim universal circuit exactness.
- It does not disclose or require backend implementation details for public
  benchmark review.

## Public Review Language

Use this wording when sharing the packet:

> Catalyst-Q has public benchmark evidence as a virtual quantum execution
> backend/simulator, including a Metriq submission under review, QED-C Level 1-3
> reproduction artifacts, and a SuperMarQ GHZ/Mermin-Bell smoke packet. We are
> seeking technical review of the benchmark interpretation and category fit.

## Reviewer Notes

The right review posture is skeptical and artifact-first. The benchmark evidence
should stand or fall on public records, reproducibility, scoring interpretation,
and category clarity, without relying on private architecture claims.
