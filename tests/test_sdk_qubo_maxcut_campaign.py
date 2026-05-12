import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MONOREPO_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

from catalyst_q_benchmarks.sdk_campaign import exact_maxcut, exact_qubo, run_sdk_qubo_maxcut_campaign


def test_exact_qubo_and_maxcut_references_are_deterministic():
    qubo_objective, qubo_assignment = exact_qubo([[1, -2], [-2, 1]], 0)
    cut_value, partition = exact_maxcut([(0, 1, 1.5), (1, 2, 2.0)], nodes=3)

    assert qubo_objective == -2
    assert qubo_assignment == [1, 1]
    assert cut_value == 3.5
    assert partition in ([0, 1, 0], [1, 0, 1])


def test_sdk_campaign_uses_real_catalyst_q_qubo_and_maxcut_builders(tmp_path, monkeypatch):
    monkeypatch.setenv("CATALYST_Q_HOME", str(tmp_path / "catalyst-q-home"))
    sdk_path = MONOREPO_ROOT / "sdk" / "python"

    artifacts = run_sdk_qubo_maxcut_campaign(output_dir=tmp_path, sdk_path=sdk_path)

    raw = pathlib.Path(artifacts["raw_jsonl"]).read_text().splitlines()
    records = [json.loads(line) for line in raw]
    sdk_records = [record for record in records if record["solver_id"] == "catalyst-q-sdk"]
    reference_records = [record for record in records if record["solver_id"] == "exact-enumeration-reference"]

    assert len(records) == 4
    assert len(sdk_records) == 2
    assert len(reference_records) == 2
    assert {record["command"] for record in sdk_records} == {"prepare_qubo", "prepare_maxcut"}
    assert {record["validator"]["route"] for record in sdk_records} == {
        "/v3turbo/solve/qubo",
        "/v3turbo/solve/maxcut",
    }
    assert all(record["status"] == "unknown" for record in sdk_records)
    assert all(record["status"] == "optimal" for record in reference_records)
    assert "Catalyst-Q SDK QUBO/Max-Cut Campaign" in pathlib.Path(artifacts["markdown"]).read_text()

