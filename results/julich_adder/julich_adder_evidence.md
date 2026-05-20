# Catalyst-Q Jülich 50-Qubit Adder Output Contract

This artifact reproduces and scales the public adder output contract. It validates requested output bits directly and records zero dense materialization; it does not claim dense-wavefunction enumeration.

## Jülich 50-Qubit Adder Output Contract

- Public inputs: `21346502 + 12207929`
- Public expected sum: `2^25 - 1`
- Public reported circuit size: `1001` gates
- Catalyst-Q verification mode: targeted adder output certificate

## Summary

- Cases: 6
- Exact cases: 6
- Zero-materialization cases: 6
- Cases beyond 50 qubits: 5
- Maximum total qubits: 1024
- Maximum dense memory label: 10^309.458836 bytes

## Cases

| ID | Total qubits | Inputs | Expected sum | Exact | Materialized states | Dense memory |
|---|---:|---|---|---:|---:|---|
| julich_adder_25x25 | 50 | 21346502 + 12207929 | 2^25 - 1 | True | 0 | 2^54 bytes |
| adder_ladder_32x32 | 64 | 3758096384 + 536870911 | 2^32 - 1 | True | 0 | 2^68 bytes |
| adder_ladder_64x64 | 128 | 16140901064495857664 + 2305843009213693951 | 2^64 - 1 | True | 0 | 2^132 bytes |
| adder_ladder_128x128 | 256 | 297747071055821155530452781502797185024 + 42535295865117307932921825928971026431 | 2^128 - 1 | True | 0 | 2^260 bytes |
| adder_ladder_256x256 | 512 | 101318078082651670995624611882601919371611236582435493534525386006923988434944 + 14474011154664524427946373126085988481658748083205070504932198000989141204991 | 2^256 - 1 | True | 0 | 2^516 bytes |
| adder_ladder_512x512 | 1024 | 11731831938699772462127271873430115361544445093018344205508116263256543526314353604701640010896040499228777875913175294497034647460453248703129442880323584 + 1675975991242824637446753124775730765934920727574049172215445180465220503759193372100234287270862928461253982273310756356719235351493321243304206125760511 | 2^512 - 1 | True | 0 | 2^1028 bytes |

## Sources

- juelich_press_release: https://www.fz-juelich.de/en/news/archive/press-release/2025/new-record-on-jupiter-simulating-a-50-qubit-quantum-computer
- juqcs_50_arxiv: https://arxiv.org/abs/2511.03359
- juqcs_50_pdf: https://arxiv.org/pdf/2511.03359
