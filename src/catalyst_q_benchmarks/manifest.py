from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "suites.json"


def load_manifest(path: Optional[Path] = None) -> Dict[str, Any]:
    manifest_path = Path(path) if path is not None else DEFAULT_MANIFEST_PATH
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    _validate_manifest(data)
    return data


def load_suites(path: Optional[Path] = None, priority: Optional[str] = None) -> List[Dict[str, Any]]:
    suites = load_manifest(path)["suites"]
    if priority is None:
        return suites
    return [suite for suite in suites if suite["priority"] == priority]


def _validate_manifest(data: Dict[str, Any]) -> None:
    if data.get("schema_version") != "0.1.0":
        raise ValueError("unsupported benchmark manifest schema")
    suites = data.get("suites")
    if not isinstance(suites, list) or not suites:
        raise ValueError("benchmark manifest must contain suites")

    required = {
        "id",
        "domain",
        "priority",
        "source",
        "url",
        "official_scope",
        "metrics",
        "baselines",
        "validators",
        "claim_target",
    }
    seen = set()
    for suite in suites:
        missing = required - set(suite)
        if missing:
            raise ValueError(f"benchmark suite {suite.get('id', '<unknown>')} missing {sorted(missing)}")
        suite_id = suite["id"]
        if suite_id in seen:
            raise ValueError(f"duplicate benchmark suite id: {suite_id}")
        seen.add(suite_id)
        if not suite["url"].startswith("https://"):
            raise ValueError(f"benchmark suite {suite_id} must use an https URL")
        for list_field in ("metrics", "baselines", "validators"):
            if not suite[list_field]:
                raise ValueError(f"benchmark suite {suite_id} must define {list_field}")

