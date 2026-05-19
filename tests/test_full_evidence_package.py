import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MONOREPO_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

from catalyst_q_benchmarks.full_evidence import (
    build_full_evidence_package,
    exact_knapsack,
    exact_sat,
    exact_tsp,
    _extract_api_objective,
    greedy_maxcut,
)


def test_exact_problem_references_are_valid_and_better_than_basic_heuristics():
    sat = exact_sat([[1, -2], [-1, 2], [1, 2]], variables=2)
    tsp = exact_tsp([[0, 2, 9, 10], [2, 0, 6, 4], [9, 6, 0, 3], [10, 4, 3, 0]])
    knapsack = exact_knapsack([4, 2, 3], [10, 4, 7], capacity=5)
    cut = greedy_maxcut([(0, 1, 1.0), (1, 2, 2.0), (0, 2, 0.5)], nodes=3)

    assert sat["satisfied_clauses"] == 3
    assert tsp["tour"][0] == 0
    assert tsp["distance"] == 18
    assert knapsack["value"] == 11
    assert cut["cut_value"] >= 2.0


def test_full_evidence_package_generates_claim_ledger_and_charts(tmp_path, monkeypatch):
    monkeypatch.setenv("CATALYST_Q_HOME", str(tmp_path / "catalyst-q-home"))
    high_qubit_dir = tmp_path / "high_qubit_exactness"
    high_qubit_dir.mkdir()
    (high_qubit_dir / "high_qubit_exactness.json").write_text(
        json.dumps(
            {
                "campaign": "high_qubit_exactness",
                "claim_scope": "query-native-targeted-exactness",
                "disclaimer": "Compact exact execution evidence only.",
                "summary": {
                    "total_cases": 2,
                    "exact_cases": 2,
                    "zero_materialization_cases": 2,
                    "max_qubits": 4096,
                    "max_gate_count": 131328,
                },
                "cases": [
                    {
                        "id": "supermarq_ghz_4096",
                        "suite": "SuperMarQ",
                        "qubits": 4096,
                        "gate_count": 4096,
                        "metric": "probability",
                        "public_strategy": "structured_entanglement_certificate",
                        "exact": True,
                        "materialized_states": 0,
                        "runtime_s": 0.02,
                    },
                    {
                        "id": "qedc_brickwork_echo_64",
                        "suite": "QED-C application-oriented",
                        "qubits": 64,
                        "gate_count": 764,
                        "metric": "probability",
                        "public_strategy": "adaptive_query_contraction",
                        "exact": True,
                        "materialized_states": 0,
                        "runtime_s": 12.6,
                    },
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    artifacts = build_full_evidence_package(
        output_dir=tmp_path,
        sdk_path=MONOREPO_ROOT / "sdk" / "python",
        execute_api=False,
    )

    data = json.loads(pathlib.Path(artifacts["json"]).read_text())
    markdown = pathlib.Path(artifacts["markdown"]).read_text()
    svg = pathlib.Path(artifacts["chart_svg"]).read_text()

    assert data["package"] == "catalyst-q-full-evidence"
    assert data["summary"]["route_coverage"] == "6/7"
    assert data["summary"]["live_exact_matches"] == "0/2"
    assert data["summary"]["live_heuristic_wins"] == "0/2"
    assert data["summary"]["external_solver_runs"] == 0
    assert data["summary"]["high_qubit_exact_cases"] == 2
    assert data["summary"]["high_qubit_max_qubits"] == 4096
    assert "No broad NP or SOTA claim is made" in markdown
    assert "Claim Ledger" in markdown
    assert "High-Qubit Exactness Evidence" in markdown
    assert "qedc_brickwork_echo_64" in markdown
    assert "Catalyst-Q Evidence Scorecard" in svg
    assert "Biq Mac Library" in json.dumps(data)


def test_full_evidence_extracts_demo_wrapped_and_worker_top_level_objectives():
    assert _extract_api_objective("QUBO", {"json": {"result": {"objective": -4}}}) == -4.0
    assert _extract_api_objective("QUBO", {"json": {"objective": -4}}) == -4.0
    assert _extract_api_objective("Max-Cut", {"json": {"result": {"cut_value": 9}}}) == 9.0
    assert _extract_api_objective("Max-Cut", {"json": {"cut_value": 9}}) == 9.0
