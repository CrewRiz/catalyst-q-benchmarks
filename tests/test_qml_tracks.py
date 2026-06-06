from pathlib import Path

from catalyst_q_benchmarks.qml_tracks import QML_TRACKS


ROOT = Path(__file__).resolve().parents[1]
QML_DOC = ROOT / "docs" / "qml_evidence_tracks.md"


def test_qml_tracks_define_the_first_three_evidence_lanes():
    track_ids = {track["id"] for track in QML_TRACKS}

    assert track_ids == {
        "quantum_oracle_sketching",
        "feature_encoding_workbench",
        "trainability_reservoir",
    }


def test_qml_tracks_have_buyer_value_and_artifact_contracts():
    for track in QML_TRACKS:
        assert track["title"]
        assert track["buyer_value"]
        assert track["primary_artifacts"]
        assert "claim_boundary" in track
        assert "Quantum Execution Record" in track["primary_artifacts"]


def test_qml_track_public_copy_avoids_private_architecture_terms():
    blocked_terms = [
        "geodesic",
        "hmk",
        "mathematically exact",
        "trade secret",
        "10k qubit",
    ]

    public_text = " ".join(
        str(value)
        for track in QML_TRACKS
        for value in track.values()
        if isinstance(value, str)
    ).lower()

    for term in blocked_terms:
        assert term not in public_text


def test_qml_evidence_doc_names_tracks_and_claim_boundary():
    text = QML_DOC.read_text(encoding="utf-8")

    required_phrases = [
        "Quantum Oracle Sketching",
        "Feature Encoding Workbench",
        "Trainability And Reservoir Track",
        "Quantum Execution Record",
        "Claim boundary",
        "External baselines",
    ]

    for phrase in required_phrases:
        assert phrase in text
