import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = ROOT / "results" / "quantum_benchmark_20260618"
DOC = ROOT / "docs" / "quantum_benchmark_evidence_2026_06_18.md"
QEDC_SUMMARY = PACKET_DIR / "qedc_level_1_3_summary.json"
SUPERMARQ_SUMMARY = PACKET_DIR / "supermarq_smoke.json"


def test_quantum_benchmark_packet_records_public_safe_scores():
    qedc = json.loads(QEDC_SUMMARY.read_text(encoding="utf-8"))
    supermarq = json.loads(SUPERMARQ_SUMMARY.read_text(encoding="utf-8"))

    assert qedc["backend"] == "Catalyst-Q"
    assert qedc["category"] == "virtual quantum execution backend/simulator"
    assert qedc["claim_scope"] == "application-benchmark reproduction"
    assert qedc["public_safe"] is True

    mean_fidelities = {
        result["benchmark"]: result["mean_fidelity"]
        for result in qedc["results"]
    }
    assert mean_fidelities == {
        "bernstein_vazirani": 1.0,
        "hidden_shift": 1.0,
        "quantum_fourier_transform": 1.0,
        "phase_estimation": 1.0,
        "grovers": 0.998869,
    }

    smoke_scores = {
        result["benchmark"]: result["score"]
        for result in supermarq["results"]
    }
    assert smoke_scores == {
        "ghz_4": 0.9996,
        "ghz_6": 0.998975,
        "mermin_bell_4": 1.0,
        "mermin_bell_6": 1.0,
    }


def test_quantum_benchmark_packet_omits_endpoint_and_release_details():
    text = "\n".join(
        [
            DOC.read_text(encoding="utf-8"),
            QEDC_SUMMARY.read_text(encoding="utf-8"),
            SUPERMARQ_SUMMARY.read_text(encoding="utf-8"),
        ]
    ).lower()

    blocked_fragments = [
        "a" + "pi.",
        "/exe" + "cute",
        "deploy" + "ment id",
        "deploy" + "ment version",
        "internal mechanics",
        "secret architecture",
    ]

    for fragment in blocked_fragments:
        assert fragment not in text
