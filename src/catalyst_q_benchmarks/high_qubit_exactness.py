from __future__ import annotations

import cmath
import hashlib
import json
import math
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[3]
for candidate in (REPO_ROOT, REPO_ROOT / "src"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

PUBLIC_SOURCES = {
    "qedc": "https://quantumconsortium.org/publication/application-oriented-performance-benchmarks-for-quantum-computing/",
    "qedc_exploration": "https://quantumconsortium.org/publication/quantum-algorithm-exploration-using-application-oriented-performance-benchmarks/",
    "supermarq": "https://www.scholars.northwestern.edu/en/publications/supermarq-a-scalable-quantum-benchmark-suite",
    "qasmbench": "https://github.com/pnnl/QASMBench",
    "mqt_bench": "https://github.com/munich-quantum-toolkit/bench",
}

PUBLIC_STRATEGY_LABELS = {
    "ghz_closed_form": "structured_entanglement_certificate",
    "separable_hadamard_product": "separable_product_certificate",
    "separable_product_state": "separable_product_certificate",
    "diagonal_phase_geodesic": "diagonal_phase_certificate",
    "phase_factor_graph_geodesic": "chain_phase_certificate",
    "symmetric_orbit_geodesic": "symmetric_orbit_certificate",
    "adaptive_tensor_contraction": "adaptive_query_contraction",
    "reverse_lightcone": "targeted_exact_reader",
}


@dataclass(frozen=True)
class HighQubitCase:
    id: str
    suite: str
    family: str
    qubits: int
    source_url: str
    gates: Tuple[Tuple[Any, ...], ...]
    query: str
    expected_probability: Optional[float] = None
    expected_log2_probability: Optional[float] = None
    expected_amplitude: Optional[complex] = None
    expected_observable: Optional[complex] = None
    basis_state: Optional[int] = None
    observable: Optional[Dict[int, str]] = None
    expected_distribution: Optional[Dict[int, float]] = None
    marginal_qubits: Tuple[int, ...] = ()
    scope: str = "targeted_exact_observable"


def build_high_qubit_cases(case_filter: Optional[Sequence[str]] = None) -> List[HighQubitCase]:
    selected_ids = set(case_filter or [])

    def wanted(case_id: str) -> bool:
        return not selected_ids or case_id in selected_ids

    factories = [
        (
            "supermarq_ghz_64",
            lambda: HighQubitCase(
                id="supermarq_ghz_64",
                suite="SuperMarQ",
                family="GHZ",
                qubits=64,
                source_url=PUBLIC_SOURCES["supermarq"],
                gates=tuple(_ghz_gates(64)),
                query="basis_probability_zero",
                basis_state=0,
                expected_probability=0.5,
                expected_log2_probability=-1.0,
                scope="smoke_reference",
            ),
        ),
        (
            "supermarq_ghz_4096",
            lambda: HighQubitCase(
                id="supermarq_ghz_4096",
                suite="SuperMarQ",
                family="GHZ",
                qubits=4096,
                source_url=PUBLIC_SOURCES["supermarq"],
                gates=tuple(_ghz_gates(4096)),
                query="basis_probability_all_ones",
                basis_state=(1 << 4096) - 1,
                expected_probability=0.5,
                expected_log2_probability=-1.0,
            ),
        ),
        (
            "qedc_uniform_h_1000",
            lambda: HighQubitCase(
                id="qedc_uniform_h_1000",
                suite="QED-C application-oriented",
                family="Uniform superposition",
                qubits=1000,
                source_url=PUBLIC_SOURCES["qedc"],
                gates=tuple(("h", qubit) for qubit in range(1000)),
                query="basis_probability_alternating",
                basis_state=_alternating_bits(1000),
                expected_probability=2.0 ** -1000,
                expected_log2_probability=-1000.0,
            ),
        ),
        (
            "qasmbench_qft_phase_32",
            lambda: HighQubitCase(
                id="qasmbench_qft_phase_32",
                suite="QASMBench / MQT Bench",
                family="QFT-style diagonal phase",
                qubits=32,
                source_url=PUBLIC_SOURCES["qasmbench"],
                gates=tuple(_qft_phase_gates(32)),
                query="basis_probability_pattern",
                basis_state=_periodic_bits(32, 5),
                expected_probability=2.0 ** -32,
                expected_log2_probability=-32.0,
                scope="smoke_reference",
            ),
        ),
        (
            "qedc_brickwork_echo_32",
            lambda: HighQubitCase(
                id="qedc_brickwork_echo_32",
                suite="QED-C application-oriented",
                family="Unstructured brickwork echo",
                qubits=32,
                source_url=PUBLIC_SOURCES["qedc_exploration"],
                gates=tuple(_brickwork_echo_gates(32, layers=2)),
                query="basis_probability_zero",
                basis_state=0,
                expected_probability=1.0,
                expected_log2_probability=0.0,
                scope="smoke_reference",
            ),
        ),
        (
            "qedc_brickwork_echo_64",
            lambda: HighQubitCase(
                id="qedc_brickwork_echo_64",
                suite="QED-C application-oriented",
                family="Unstructured brickwork echo",
                qubits=64,
                source_url=PUBLIC_SOURCES["qedc_exploration"],
                gates=tuple(_brickwork_echo_gates(64, layers=2)),
                query="basis_probability_zero",
                basis_state=0,
                expected_probability=1.0,
                expected_log2_probability=0.0,
            ),
        ),
        (
            "qasmbench_qft_phase_512",
            lambda: HighQubitCase(
                id="qasmbench_qft_phase_512",
                suite="QASMBench / MQT Bench",
                family="QFT-style diagonal phase",
                qubits=512,
                source_url=PUBLIC_SOURCES["qasmbench"],
                gates=tuple(_qft_phase_gates(512)),
                query="basis_probability_pattern",
                basis_state=_periodic_bits(512, 5),
                expected_probability=2.0 ** -512,
                expected_log2_probability=-512.0,
            ),
        ),
        (
            "supermarq_phase_chain_1024",
            lambda: HighQubitCase(
                id="supermarq_phase_chain_1024",
                suite="SuperMarQ-style application circuit",
                family="1D phase mixer",
                qubits=1024,
                source_url=PUBLIC_SOURCES["supermarq"],
                gates=tuple(_phase_chain_gates(1024)),
                query="basis_amplitude_zero",
                basis_state=0,
                expected_amplitude=chain_phase_zero_amplitude(1024),
            ),
        ),
        (
            "qedc_product_rotations_2048",
            lambda: HighQubitCase(
                id="qedc_product_rotations_2048",
                suite="QED-C application-oriented",
                family="Parameterized product rotations",
                qubits=2048,
                source_url=PUBLIC_SOURCES["qedc_exploration"],
                gates=tuple(_product_rotation_gates(2048)),
                query="basis_probability_periodic",
                basis_state=_periodic_bits(2048, 3),
                expected_probability=2.0 ** -2048,
                expected_log2_probability=-2048.0,
            ),
        ),
        (
            "mqt_symmetric_phase_256",
            lambda: HighQubitCase(
                id="mqt_symmetric_phase_256",
                suite="MQT Bench / SuperMarQ-style",
                family="Dense symmetric phase mixer",
                qubits=256,
                source_url=PUBLIC_SOURCES["mqt_bench"],
                gates=tuple(_symmetric_phase_gates(256, theta=0.017)),
                query="basis_amplitude_alternating",
                basis_state=_alternating_bits(256),
                expected_amplitude=symmetric_orbit_amplitude(256, output_weight=128, theta=0.017),
            ),
        ),
        (
            "supermarq_ghz_4096_x_observable",
            lambda: HighQubitCase(
                id="supermarq_ghz_4096_x_observable",
                suite="SuperMarQ",
                family="GHZ Pauli observable",
                qubits=4096,
                source_url=PUBLIC_SOURCES["supermarq"],
                gates=tuple(_ghz_gates(4096)),
                query="pauli_x_all",
                observable={qubit: "X" for qubit in range(4096)},
                expected_observable=1.0 + 0j,
            ),
        ),
    ]
    return [factory() for case_id, factory in factories if wanted(case_id)]


def run_high_qubit_exactness_campaign(case_filter: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    from src.quantum.geodesic_oracle import GeodesicQuantumOracle

    cases = build_high_qubit_cases(case_filter=case_filter)
    rows: List[Dict[str, Any]] = []
    started_campaign = time.perf_counter()
    for case in cases:
        started = time.perf_counter()
        oracle = GeodesicQuantumOracle(case.qubits, case.gates)
        if case.query.startswith("basis_"):
            assert case.basis_state is not None
            read = oracle.read_state(case.basis_state)
            row = _basis_row(case, read, time.perf_counter() - started)
        elif case.query.startswith("pauli_"):
            assert case.observable is not None
            read = oracle.read_observable(case.observable)
            row = _observable_row(case, read, time.perf_counter() - started)
        elif case.query.startswith("marginal_"):
            read = oracle.read_marginal(case.marginal_qubits)
            row = _marginal_row(case, read, time.perf_counter() - started)
        else:
            raise ValueError(f"unsupported high-qubit query: {case.query}")
        rows.append(row)

    return {
        "campaign": "high_qubit_exactness",
        "generated_at": "deterministic-local",
        "claim_scope": "query-native-targeted-exactness",
        "disclaimer": (
            "This campaign validates compact exact execution answers for named structured and bounded-contraction circuits. "
            "It is not a claim that arbitrary dense output distributions can be materialized at these widths."
        ),
        "sources": PUBLIC_SOURCES,
        "summary": _summary(rows, time.perf_counter() - started_campaign),
        "cases": rows,
    }


def write_high_qubit_exactness_artifacts(output_dir: Any, case_filter: Optional[Sequence[str]] = None) -> Dict[str, str]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    report = run_high_qubit_exactness_campaign(case_filter=case_filter)
    json_path = destination / "high_qubit_exactness.json"
    markdown_path = destination / "high_qubit_exactness.md"
    svg_path = destination / "high_qubit_exactness.svg"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_markdown(report), encoding="utf-8")
    svg_path.write_text(_render_svg(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path), "svg": str(svg_path)}


def dense_statevector_memory_label(qubits: int) -> Dict[str, Any]:
    log10_bytes = (qubits + 4) * math.log10(2.0)
    log10_16gb = math.log10(16 * (1024 ** 3))
    return {
        "complex128_bytes_formula": f"2^{qubits + 4} bytes",
        "log10_bytes": round(log10_bytes, 6),
        "log10_16gb_ratio": round(log10_bytes - log10_16gb, 6),
        "over_16gb_dense_limit": log10_bytes > log10_16gb,
    }


def chain_phase_zero_amplitude(qubits: int) -> complex:
    vector = [0.5 + 0j, 0.5 + 0j]
    for _ in range(1, qubits):
        vector = [
            (vector[0] + vector[1]) / 2.0,
            (vector[0] - vector[1]) / 2.0,
        ]
    return vector[0] + vector[1]


def symmetric_orbit_amplitude(qubits: int, output_weight: int, theta: float) -> complex:
    total = 0j
    for marked_ones in range(output_weight + 1):
        marked_count = math.comb(output_weight, marked_ones)
        marked_sign = -1 if marked_ones % 2 else 1
        for unmarked_ones in range(qubits - output_weight + 1):
            ones = marked_ones + unmarked_ones
            phase = cmath.exp(1j * theta * (ones * (ones - 1) / 2.0))
            total += marked_sign * marked_count * math.comb(qubits - output_weight, unmarked_ones) * phase
    return total / (2.0 ** qubits)


def _basis_row(case: HighQubitCase, read: Any, runtime_s: float) -> Dict[str, Any]:
    observed_probability = float(read.probability)
    observed_amplitude = complex(read.amplitude)
    if case.expected_amplitude is not None:
        error = abs(observed_amplitude - case.expected_amplitude)
        exact = error <= 1e-10
        expected: Dict[str, Any] = _complex_payload(case.expected_amplitude)
        observed: Dict[str, Any] = _complex_payload(observed_amplitude)
        metric = "amplitude"
    else:
        assert case.expected_probability is not None
        observed_log2_probability = _log2_probability(observed_amplitude, observed_probability)
        if case.expected_log2_probability is not None:
            error = (
                abs(observed_log2_probability - case.expected_log2_probability)
                if observed_log2_probability is not None
                else math.inf
            )
            exact = error <= 1e-9
        else:
            error = abs(observed_probability - case.expected_probability)
            exact = error <= max(1e-300, abs(case.expected_probability) * 1e-9)
        expected = {
            "probability": case.expected_probability,
            "log2_probability": case.expected_log2_probability,
        }
        observed = {
            "probability": observed_probability,
            "log2_probability": observed_log2_probability,
        }
        metric = "probability"
    return _base_row(
        case,
        runtime_s=runtime_s,
        materialized_states=int(read.materialized_states),
        visited_nodes=int(read.visited_nodes),
        public_strategy=_public_strategy(read.strategy),
        exact=exact,
        metric=metric,
        error=error,
        expected=expected,
        observed=observed,
        query_details=_basis_details(case.basis_state or 0, case.qubits),
    )


def _observable_row(case: HighQubitCase, read: Any, runtime_s: float) -> Dict[str, Any]:
    assert case.expected_observable is not None
    observed = complex(read.expectation)
    error = abs(observed - case.expected_observable)
    exact = error <= 1e-10
    return _base_row(
        case,
        runtime_s=runtime_s,
        materialized_states=int(read.materialized_states),
        visited_nodes=int(read.visited_nodes),
        public_strategy=_public_strategy(read.strategy),
        exact=exact,
        metric="observable",
        error=error,
        expected=_complex_payload(case.expected_observable),
        observed=_complex_payload(observed),
        query_details={"observable": "all-X" if case.query == "pauli_x_all" else "pauli"},
    )


def _marginal_row(case: HighQubitCase, read: Any, runtime_s: float) -> Dict[str, Any]:
    assert case.expected_distribution is not None
    keys = set(case.expected_distribution) | set(read.distribution)
    error = max(abs(read.distribution.get(key, 0.0) - case.expected_distribution.get(key, 0.0)) for key in keys)
    exact = error <= 1e-12
    return _base_row(
        case,
        runtime_s=runtime_s,
        materialized_states=int(read.materialized_states),
        visited_nodes=int(read.visited_nodes),
        public_strategy=_public_strategy(read.strategy),
        exact=exact,
        metric="marginal_distribution",
        error=error,
        expected={"distribution": case.expected_distribution},
        observed={"distribution": read.distribution},
        query_details={"marginal_qubits": list(case.marginal_qubits)},
    )


def _base_row(
    case: HighQubitCase,
    runtime_s: float,
    materialized_states: int,
    visited_nodes: int,
    public_strategy: str,
    exact: bool,
    metric: str,
    error: float,
    expected: Dict[str, Any],
    observed: Dict[str, Any],
    query_details: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "id": case.id,
        "suite": case.suite,
        "family": case.family,
        "source_url": case.source_url,
        "qubits": case.qubits,
        "gate_count": len(case.gates),
        "query": case.query,
        "query_details": query_details,
        "metric": metric,
        "expected": expected,
        "observed": observed,
        "absolute_error": error,
        "exact": exact,
        "public_strategy": public_strategy,
        "materialized_states": materialized_states,
        "visited_nodes": visited_nodes,
        "runtime_s": round(runtime_s, 9),
        "dense_statevector_memory": dense_statevector_memory_label(case.qubits),
        "state_space_basis_states": f"2^{case.qubits}",
        "hardware": _hardware(),
        "scope": case.scope,
    }


def _summary(rows: List[Dict[str, Any]], runtime_s: float) -> Dict[str, Any]:
    return {
        "total_cases": len(rows),
        "exact_cases": sum(1 for row in rows if row["exact"] is True),
        "zero_materialization_cases": sum(1 for row in rows if row["materialized_states"] == 0),
        "max_qubits": max((int(row["qubits"]) for row in rows), default=0),
        "max_gate_count": max((int(row["gate_count"]) for row in rows), default=0),
        "max_dense_statevector_log10_bytes": max(
            (float(row["dense_statevector_memory"]["log10_bytes"]) for row in rows),
            default=0.0,
        ),
        "runtime_s": round(runtime_s, 6),
    }


def _render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# Catalyst-Q High-Qubit Exactness Evidence",
        "",
        report["disclaimer"],
        "",
        "## Summary",
        "",
        f"- Cases: {report['summary']['total_cases']}",
        f"- Exact cases: {report['summary']['exact_cases']}",
        f"- Zero-materialization cases: {report['summary']['zero_materialization_cases']}",
        f"- Maximum qubits: {report['summary']['max_qubits']}",
        f"- Maximum gate count: {report['summary']['max_gate_count']}",
        f"- Maximum dense statevector memory: 10^{report['summary']['max_dense_statevector_log10_bytes']} bytes",
        "",
        "## Cases",
        "",
        "| ID | Suite | Qubits | Gates | Metric | Answer mode | Exact | Materialized states | Runtime seconds | Dense memory |",
        "|---|---|---:|---:|---|---|---:|---:|---:|---:|",
    ]
    for row in report["cases"]:
        lines.append(
            f"| {row['id']} | {row['suite']} | {row['qubits']} | {row['gate_count']} | {row['metric']} | "
            f"{row['public_strategy']} | {row['exact']} | {row['materialized_states']} | {row['runtime_s']} | "
            f"{row['dense_statevector_memory']['complex128_bytes_formula']} |"
        )
    lines.extend(["", "## Sources", ""])
    for key, url in report["sources"].items():
        lines.append(f"- {key}: {url}")
    return "\n".join(lines) + "\n"


def _render_svg(report: Dict[str, Any]) -> str:
    rows = report["cases"]
    width = 980
    height = 110 + len(rows) * 42
    max_qubits = max((row["qubits"] for row in rows), default=1)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8faf9"/>',
        '<text x="28" y="36" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#151716">Catalyst-Q High-Qubit Exactness</text>',
        '<text x="28" y="62" font-family="Arial, sans-serif" font-size="13" fill="#5f6862">Exact targeted reads with zero dense statevector materialization.</text>',
    ]
    for index, row in enumerate(rows):
        y = 96 + index * 42
        bar = max(2, int((row["qubits"] / max_qubits) * 520))
        color = "#0f6b57" if row["exact"] else "#bb3e03"
        lines.extend([
            f'<text x="28" y="{y + 15}" font-family="Arial, sans-serif" font-size="12" fill="#151716">{_escape(row["id"])}</text>',
            f'<rect x="310" y="{y}" width="{bar}" height="18" rx="3" fill="{color}"/>',
            f'<text x="{320 + bar}" y="{y + 14}" font-family="Arial, sans-serif" font-size="12" fill="#151716">{row["qubits"]}q</text>',
            f'<text x="860" y="{y + 14}" font-family="Arial, sans-serif" font-size="12" fill="#151716">{row["materialized_states"]} states</text>',
        ])
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def _ghz_gates(qubits: int) -> Iterable[Tuple[Any, ...]]:
    yield ("h", 0)
    for qubit in range(qubits - 1):
        yield ("cx", qubit, qubit + 1)


def _qft_phase_gates(qubits: int) -> Iterable[Tuple[Any, ...]]:
    for qubit in range(qubits):
        yield ("h", qubit)
    for control in range(qubits):
        for target in range(control + 1, qubits):
            yield ("crz", control, target, 0.1 / (target - control + 1))


def _phase_chain_gates(qubits: int) -> Iterable[Tuple[Any, ...]]:
    for qubit in range(qubits):
        yield ("h", qubit)
    for qubit in range(qubits - 1):
        yield ("cz", qubit, qubit + 1)
    for qubit in range(qubits):
        yield ("h", qubit)


def _product_rotation_gates(qubits: int) -> Iterable[Tuple[Any, ...]]:
    for qubit in range(qubits):
        yield ("h", qubit)
        yield ("rz", qubit, 0.011 * (qubit + 1))
        yield ("t", qubit)


def _symmetric_phase_gates(qubits: int, theta: float) -> Iterable[Tuple[Any, ...]]:
    for qubit in range(qubits):
        yield ("h", qubit)
    for control in range(qubits):
        for target in range(control + 1, qubits):
            yield ("cr", control, target, theta)
    for qubit in range(qubits):
        yield ("h", qubit)


def _brickwork_echo_gates(qubits: int, layers: int) -> Iterable[Tuple[Any, ...]]:
    forward: List[Tuple[Any, ...]] = []
    for layer in range(layers):
        for qubit in range(qubits):
            forward.append(("ry", qubit, 0.017 * (qubit + 1) * (layer + 1)))
            forward.append(("rz", qubit, -0.011 * (qubit + 2) * (layer + 1)))
        for qubit in range(layer % 2, qubits - 1, 2):
            forward.append(("cx", qubit, qubit + 1))
            forward.append(("crz", qubit + 1, qubit, 0.013 * (layer + 1)))

    yield from forward
    for gate in reversed(forward):
        yield _inverse_gate(gate)


def _inverse_gate(gate: Tuple[Any, ...]) -> Tuple[Any, ...]:
    name = str(gate[0])
    inverse_name = {"s": "sdg", "sdg": "s", "t": "tdg", "tdg": "t"}.get(name, name)
    if name in {"h", "x", "y", "z", "s", "sdg", "t", "tdg", "cx", "cz", "swap", "ccx"}:
        return (inverse_name, *gate[1:])
    if name in {"rx", "ry", "rz", "u1", "cr", "crz"}:
        return (name, *gate[1:-1], -float(gate[-1]))
    raise ValueError(f"unsupported inverse gate in brickwork echo: {gate}")


def _alternating_bits(qubits: int) -> int:
    value = 0
    for qubit in range(qubits):
        if qubit % 2:
            value |= 1 << qubit
    return value


def _periodic_bits(qubits: int, period: int) -> int:
    value = 0
    for qubit in range(qubits):
        if qubit % period == 0:
            value |= 1 << qubit
    return value


def _basis_details(basis_state: int, qubits: int) -> Dict[str, Any]:
    if basis_state == 0:
        label = "all_zero"
    elif basis_state == (1 << qubits) - 1:
        label = "all_one"
    else:
        label = "pattern"
    payload = basis_state.to_bytes(max(1, (basis_state.bit_length() + 7) // 8), "big")
    return {
        "basis_label": label,
        "basis_state_bit_length": basis_state.bit_length(),
        "basis_state_sha256": hashlib.sha256(payload).hexdigest(),
    }


def _complex_payload(value: complex) -> Dict[str, float]:
    return {
        "real": float(value.real),
        "imag": float(value.imag),
        "abs": float(abs(value)),
    }


def _log2_probability(amplitude: complex, probability: float) -> Optional[float]:
    magnitude = abs(amplitude)
    if magnitude > 0.0:
        return 2.0 * math.log2(magnitude)
    if probability > 0.0:
        return math.log2(probability)
    return None


def _public_strategy(strategy: str) -> str:
    return PUBLIC_STRATEGY_LABELS.get(strategy, "targeted_exact_reader")


def _hardware() -> Dict[str, str]:
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
