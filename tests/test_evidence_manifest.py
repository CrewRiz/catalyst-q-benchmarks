import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from catalyst_q_benchmarks import build_readiness_report, load_manifest, load_suites
from catalyst_q_benchmarks.report import build_readiness_svg
from catalyst_q_benchmarks.validators import validate_result_record, validate_tsp_tour


def test_manifest_tracks_respected_public_benchmark_suites():
    manifest = load_manifest()
    suite_ids = {suite["id"] for suite in manifest["suites"]}

    assert manifest["schema_version"] == "0.1.0"
    assert {
        "sat_competition_main",
        "maxsat_evaluation",
        "tsplib95",
        "dimacs_tsp_challenge",
        "or_library_mknap",
        "biq_mac_maxcut_bqp",
        "qplib",
        "miplib2017",
        "qaplib",
    }.issubset(suite_ids)
    assert len(load_suites(priority="tier_1")) >= 7


def test_manifest_does_not_publish_private_terms():
    text = json.dumps(load_manifest()).lower()
    forbidden_terms = [
        "hypervectormemorykey",
        "hypervector memory key",
        "geodesic oracle",
        "post-cartesian",
        "phaseholovector",
        "src.quantum",
    ]

    for term in forbidden_terms:
        assert term not in text


def test_readiness_report_is_careful_about_claims():
    report = build_readiness_report()

    assert "readiness report, not a solver superiority claim" in report
    assert "Claim policy" in report
    assert "best at NP" not in report
    assert "solves NP" not in report


def test_svg_chart_is_generated_from_manifest():
    svg = build_readiness_svg()

    assert svg.startswith("<svg")
    assert "Catalyst-Q Evidence Coverage" in svg
    assert "TSP" in svg


def test_common_result_record_validator():
    valid, errors = validate_result_record(
        {
            "suite_id": "tsplib95",
            "instance_id": "berlin52",
            "solver_id": "catalyst-q",
            "status": "feasible",
            "runtime_s": 1.25,
            "hardware": {"machine": "ci"},
            "validator": {"valid": True},
        }
    )

    assert valid is True
    assert errors == []

    valid, errors = validate_result_record({"runtime_s": -1, "status": "done"})
    assert valid is False
    assert "runtime_s must be non-negative" in errors
    assert "status is not recognized" in errors


def test_tsp_tour_validator():
    assert validate_tsp_tour([0, 1, 2, 3], expected_nodes=4) == (True, [])

    valid, errors = validate_tsp_tour([0, 1, 1, 4], expected_nodes=4)
    assert valid is False
    assert "tour contains duplicate nodes" in errors
    assert "tour contains node id outside expected range" in errors

