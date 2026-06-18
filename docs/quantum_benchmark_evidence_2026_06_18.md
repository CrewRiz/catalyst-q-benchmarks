# Catalyst-Q Quantum Benchmark Evidence

Date: 2026-06-18

This packet records public benchmark evidence for Catalyst-Q as a virtual quantum
execution backend/simulator. It preserves measured scores, source benchmark names,
checksums, and public review status while omitting implementation details.

## Public Scope

- Classification: Catalyst-Q virtual quantum execution backend/simulator.
- Evidence type: benchmark reproduction artifacts and public submission links.
- Claim level: measured benchmark results under named benchmark suites.
- Boundary: this is not a physical QPU claim, cryptanalysis claim, broad quantum
  advantage claim, or universal circuit-exactness claim.

## Metriq Status

| Submission | Status | Public-safe note |
|---|---|---|
| unitaryfoundation/metriq-data#459 | Open review | Canonical recovered EPLG submission; local aggregate validation recorded as 5,644,528,828.972562. |
| unitaryfoundation/metriq-data#458 | Closed | Smaller fallback submission, superseded by the canonical #459 packet. |

The Metriq aggregate is recorded here as submitted evidence under review, not as an
accepted leaderboard rank until upstream review completes.

## QED-C Level 1-3 Reproduction

| QED-C benchmark | Widths | Mean fidelity |
|---|---:|---:|
| Bernstein-Vazirani | 3-6 | 1.000000 |
| Hidden Shift | 2, 4, 6 | 1.000000 |
| Quantum Fourier Transform | 2-6 | 1.000000 |
| Phase Estimation | 3-6 | 1.000000 |
| Grover's Search | 2-5 | 0.998869 |

Artifact: `results/quantum_benchmark_20260618/qedc_level_1_3_summary.json`

## SuperMarQ Smoke

| SuperMarQ benchmark | Qubits | Shots | Score |
|---|---:|---:|---:|
| GHZ | 4 | 500 | 0.999600 |
| GHZ | 6 | 500 | 0.998975 |
| Mermin-Bell | 4 | 500 | 1.000000 |
| Mermin-Bell | 6 | 500 | 1.000000 |

Artifact: `results/quantum_benchmark_20260618/supermarq_smoke.json`

## Checksums

```text
683bc2ddfe2f4383f304d9c8a0d3210cbc3424e58582ee3ab395d937a669827a  catalystq_bernstein_vazirani.json
ba266b81c76068aeddc9c922dba0eae49318a8a25d968ab08806fcefbbd60fca  catalystq_hidden_shift.json
1af5894a6c7f00efa729f02d784339e46290b14d887e0642a8eb97bcb7848ebd  catalystq_quantum_fourier_transform.json
5d0e8950d77da19004fa943053de9b9cccf2cbbea7d81ab63fb3565f81758f0d  catalystq_phase_estimation.json
e5cc1ebb1c31b7c83386aa7d67b8c0dcf59d5e5350d515588ed4cae2b9892935  catalystq_grovers.json
0fd555bc099071c17312519edf871d9217dc546ab3da7a35ebc5be0cc8fd3e27  catalystq_supermarq_smoke_20260618_032529.json
```

## Public Review Language

Use this wording in public review threads:

> Catalyst-Q has public benchmark evidence as a virtual quantum execution
> backend/simulator, including a Metriq submission under review, QED-C Level 1-3
> reproduction artifacts, and a SuperMarQ GHZ/Mermin-Bell smoke packet. These
> artifacts report measured benchmark scores only and do not make physical QPU,
> cryptanalysis, or broad advantage claims.
