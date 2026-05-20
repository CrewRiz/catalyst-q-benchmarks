from __future__ import annotations

import json
import pathlib

import pytest

from catalyst_q_benchmarks.julich_adder import (
    build_julich_50_case,
    build_scaling_cases,
    dense_statevector_memory_label,
    run_julich_adder_evidence,
    write_julich_adder_artifacts,
)


def test_julich_50_case_matches_public_adder_contract():
    case = build_julich_50_case()

    assert case.register_bits == 25
    assert case.total_qubits == 50
    assert case.left_input == 21_346_502
    assert case.right_input == 12_207_929
    assert case.expected_sum == (1 << 25) - 1
    assert case.reported_julich_gate_count == 1001
    assert case.output_bits_little_endian == tuple([1] * 25)


def test_julich_adder_report_reproduces_50q_and_extends_beyond_it():
    report = run_julich_adder_evidence(ladder_register_bits=(25, 32, 64, 128))
    by_id = {row["id"]: row for row in report["cases"]}

    assert report["claim_scope"] == "targeted-adder-output-contract"
    assert report["summary"]["julich_50_reproduced"] is True
    assert report["summary"]["max_total_qubits"] == 256
    assert report["summary"]["cases_beyond_50_qubits"] == 3
    assert by_id["julich_adder_25x25"]["total_qubits"] == 50
    assert by_id["julich_adder_25x25"]["matches_public_julich_case"] is True
    assert by_id["adder_ladder_128x128"]["exact"] is True
    assert all(row["materialized_states"] == 0 for row in report["cases"])
    assert all(row["output_bits_are_all_one"] is True for row in report["cases"])


def test_dense_statevector_memory_label_uses_log_scale():
    label = dense_statevector_memory_label(50)

    assert label["complex128_bytes_formula"] == "2^54 bytes"
    assert label["log10_bytes"] == pytest.approx(16.25562, abs=1e-6)
    assert label["over_16gb_dense_limit"] is True


def test_artifact_writer_outputs_public_safe_json_markdown_and_svg(tmp_path):
    artifacts = write_julich_adder_artifacts(tmp_path, ladder_register_bits=(25, 32, 64))
    json_path = pathlib.Path(artifacts["json"])
    markdown_path = pathlib.Path(artifacts["markdown"])
    svg_path = pathlib.Path(artifacts["svg"])

    report = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    svg = svg_path.read_text(encoding="utf-8")
    folded = markdown.lower()

    assert report["summary"]["total_cases"] == 3
    assert "Jülich 50-Qubit Adder Output Contract" in markdown
    assert "21346502" in markdown
    assert "12207929" in markdown
    assert "2^25 - 1" in markdown
    assert "full dense statevector record" not in folded
    assert "arbitrary dense circuit" not in folded
    assert "Catalyst-Q Jülich Adder Evidence" in svg
