# Jülich Adder Record Attempt

This document defines the Catalyst-Q evidence target for the public Jülich
50-qubit adder benchmark.

## Public Reference

Forschungszentrum Jülich reported a 50-qubit universal quantum computer
simulation on JUPITER using JUQCS-50. The related paper includes an adder
application with two 25-bit input registers:

- `21346502 + 12207929`
- expected result: `33554431`, equal to `2^25 - 1`
- reported adder circuit size: `1001` gates
- public correctness check: all 25 result-register Z expectations are `1.00`

Sources:

- https://www.fz-juelich.de/en/news/archive/press-release/2025/new-record-on-jupiter-simulating-a-50-qubit-quantum-computer
- https://arxiv.org/abs/2511.03359
- https://arxiv.org/pdf/2511.03359

## Catalyst-Q Evidence Target

Catalyst-Q reproduces the public adder output contract as a targeted certificate:
the expected result bits are read directly from the adder semantics, without
allocating the dense `2^50` state.

The first artifact row uses the exact public Jülich inputs. Additional rows use
larger register widths with inputs chosen so the expected sum is `2^M - 1`.
That makes the output bits all ones, matching the public Jülich visual check
while extending the width beyond 50 total qubits.

## Claim Boundary

Allowed wording:

- "Catalyst-Q reproduces the Jülich 50-qubit adder output contract."
- "Catalyst-Q extends the same targeted adder verification pattern beyond 50 qubits."
- "The artifact records zero dense state materialization."

Avoid wording:

- Statements that recast this as a dense-wavefunction race with JUQCS-50.
- Statements that imply Catalyst-Q allocated every 50-qubit amplitude.
- Statements that generalize this targeted certificate to every dense circuit.

## Reproduce

```bash
PYTHONPATH=src python3 scripts/run_julich_adder_evidence.py
```

Generated artifacts:

- `results/julich_adder/julich_adder_evidence.json`
- `results/julich_adder/julich_adder_evidence.md`
- `results/julich_adder/julich_adder_evidence.svg`
