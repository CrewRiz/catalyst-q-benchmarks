from __future__ import annotations

from typing import Final, Tuple, TypedDict


class QMLEvidenceTrack(TypedDict):
    id: str
    title: str
    buyer_value: str
    primary_artifacts: str
    claim_boundary: str


QML_TRACKS: Final[Tuple[QMLEvidenceTrack, ...]] = (
    {
        "id": "quantum_oracle_sketching",
        "title": "Quantum Oracle Sketching",
        "buyer_value": (
            "Evaluate whether a large classical dataset has a credible compact QML-style "
            "sketching path before the buyer funds a larger research program."
        ),
        "primary_artifacts": (
            "experiment protocol, baseline comparison, Catalyst-Q benchmark record, "
            "Quantum Execution Record, claim-boundary memo"
        ),
        "claim_boundary": (
            "Publish only named datasets, committed inputs, baselines, validators, and "
            "measured outcomes. Do not claim broad superiority without external baselines."
        ),
    },
    {
        "id": "feature_encoding_workbench",
        "title": "Feature Encoding Workbench",
        "buyer_value": (
            "Compare basis, angle, dense-angle, amplitude, IQP, and re-uploading encodings "
            "against depth, qubit, noise, and accuracy constraints."
        ),
        "primary_artifacts": (
            "encoding decision record, sweep report, Catalyst-Q benchmark record, "
            "Quantum Execution Record, claim-boundary memo"
        ),
        "claim_boundary": (
            "Report encoding-specific results only for named datasets and circuit families."
        ),
    },
    {
        "id": "trainability_reservoir",
        "title": "Trainability And Reservoir Track",
        "buyer_value": (
            "Map whether a candidate QML circuit family can train, avoid barren-plateau "
            "failure modes, and produce stable evidence for a downstream task."
        ),
        "primary_artifacts": (
            "gradient map, reservoir benchmark report, Catalyst-Q benchmark record, "
            "Quantum Execution Record, claim-boundary memo"
        ),
        "claim_boundary": (
            "Treat trainability as task-specific evidence, not a universal performance claim."
        ),
    },
)
