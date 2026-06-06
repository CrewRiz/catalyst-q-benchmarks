from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FULL_EVIDENCE_WORKFLOW = ROOT / ".github" / "workflows" / "full-evidence.yml"


def test_public_full_evidence_workflow_is_secretless_and_cloudflare_free():
    workflow = FULL_EVIDENCE_WORKFLOW.read_text(encoding="utf-8")
    lowered = workflow.lower()

    forbidden_fragments = [
        "secrets.",
        "catalyst_q_api_key",
        "cloudflare_api_token",
        "cloudflare_account_id",
        "wrangler-action",
        "r2 object put",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in lowered


def test_public_full_evidence_workflow_does_not_run_on_pull_requests():
    workflow = FULL_EVIDENCE_WORKFLOW.read_text(encoding="utf-8").lower()

    assert "pull_request" not in workflow
    assert "contents: read" in workflow
