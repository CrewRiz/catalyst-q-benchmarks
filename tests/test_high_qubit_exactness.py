from __future__ import annotations

import json

import pytest

from catalyst_q_benchmarks.high_qubit_exactness import (
    chain_phase_zero_amplitude,
    dense_statevector_memory_label,
    run_high_qubit_exactness_campaign,
    symmetric_orbit_amplitude,
)
from src.quantum.geodesic_oracle import GeodesicQuantumOracle


def test_dense_statevector_memory_label_uses_log_scale_without_huge_integers():
    label = dense_statevector_memory_label(1000)

    assert label["complex128_bytes_formula"] == "2^1004 bytes"
    assert label["log10_bytes"] == pytest.approx(302.234116, abs=1e-6)
    assert label["over_16gb_dense_limit"] is True


def test_independent_chain_phase_certificate_matches_small_exact_values():
    assert chain_phase_zero_amplitude(1) == pytest.approx(1.0 + 0j)
    assert chain_phase_zero_amplitude(2) == pytest.approx(0.5 + 0j)
    assert chain_phase_zero_amplitude(3) == pytest.approx(0.5 + 0j)


def test_symmetric_orbit_certificate_is_permutation_invariant_for_fixed_output_weight():
    theta = 0.17
    gates = [("h", qubit) for qubit in range(8)]
    gates.extend(("cr", i, j, theta) for i in range(8) for j in range(i + 1, 8))
    gates.extend(("h", qubit) for qubit in range(8))
    oracle = GeodesicQuantumOracle(8, gates)
    expected = symmetric_orbit_amplitude(8, output_weight=2, theta=theta)

    assert oracle.read_state(0b00000011).amplitude == pytest.approx(expected, abs=1e-12)
    assert oracle.read_state(0b00100100).amplitude == pytest.approx(expected, abs=1e-12)


def test_high_qubit_campaign_smoke_outputs_public_safe_artifact():
    report = run_high_qubit_exactness_campaign(
        case_filter=["supermarq_ghz_64", "qasmbench_qft_phase_32", "qedc_brickwork_echo_32"]
    )
    blob = json.dumps(report, sort_keys=True)

    assert report["summary"]["total_cases"] == 3
    assert report["summary"]["exact_cases"] == 3
    assert report["summary"]["max_qubits"] == 64
    assert all(row["materialized_states"] == 0 for row in report["cases"])
    assert all(row["exact"] is True for row in report["cases"])
    assert any(row["public_strategy"] == "adaptive_query_contraction" for row in report["cases"])
    for forbidden in [
        "GeodesicQuantumOracle",
        "HypervectorMemoryKey",
        "PhaseHoloVector",
        "post-cartesian",
        "src.quantum",
        "geodesic oracle",
    ]:
        assert forbidden not in blob
