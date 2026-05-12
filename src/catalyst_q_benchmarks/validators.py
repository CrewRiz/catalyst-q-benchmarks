from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple


def validate_result_record(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate the common raw-result envelope before suite-specific checks."""
    required = [
        "suite_id",
        "instance_id",
        "solver_id",
        "status",
        "runtime_s",
        "hardware",
        "validator",
    ]
    errors: List[str] = []
    for key in required:
        if key not in record:
            errors.append(f"missing {key}")

    if "runtime_s" in record and record["runtime_s"] < 0:
        errors.append("runtime_s must be non-negative")
    if "validator" in record and not isinstance(record["validator"], dict):
        errors.append("validator must be an object")
    if "status" in record and record["status"] not in {"optimal", "feasible", "infeasible", "unknown", "timeout", "error"}:
        errors.append("status is not recognized")

    return not errors, errors


def validate_tsp_tour(tour: Iterable[int], expected_nodes: int) -> Tuple[bool, List[str]]:
    nodes = list(tour)
    errors: List[str] = []

    if len(nodes) != expected_nodes:
        errors.append(f"expected {expected_nodes} nodes, got {len(nodes)}")
    if len(set(nodes)) != len(nodes):
        errors.append("tour contains duplicate nodes")
    if nodes and min(nodes) < 0:
        errors.append("tour contains negative node ids")
    if nodes and max(nodes) >= expected_nodes:
        errors.append("tour contains node id outside expected range")

    return not errors, errors

