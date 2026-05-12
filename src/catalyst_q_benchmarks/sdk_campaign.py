from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .manifest import REPO_ROOT

DEFAULT_INSTANCE_PATH = REPO_ROOT / "benchmarks" / "instances" / "qubo_maxcut_smoke.json"


def run_sdk_qubo_maxcut_campaign(
    output_dir: Path,
    sdk_path: Optional[Path] = None,
    base_url: str = "https://catalyst-q-sdk.strategic-innovations.workers.dev/v3turbo",
    api_key: Optional[str] = None,
    execute_api: bool = False,
    timeout: float = 30.0,
) -> Dict[str, str]:
    sdk = _load_sdk(sdk_path)
    instances = _load_instances(DEFAULT_INSTANCE_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "sdk_qubo_maxcut_smoke.jsonl"
    report_path = output_dir / "sdk_qubo_maxcut_smoke.md"
    records: List[Dict[str, Any]] = []

    client = sdk["CatalystQClient"](api_key=api_key, base_url=base_url)
    for index, instance in enumerate(instances):
        baseline = _exact_reference(instance)
        records.append(_reference_record(instance, baseline))
        records.append(
            _sdk_record(
                sdk=sdk,
                client=client,
                instance=instance,
                baseline=baseline,
                solver_runs_this_month=index,
                execute_api=execute_api,
                timeout=timeout,
            )
        )

    raw_path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")
    report_path.write_text(_render_campaign_report(records, execute_api), encoding="utf-8")
    return {"raw_jsonl": str(raw_path), "markdown": str(report_path)}


def _load_sdk(sdk_path: Optional[Path]) -> Dict[str, Any]:
    if sdk_path is not None:
        sys.path.insert(0, str(Path(sdk_path).resolve()))
    try:
        from catalyst_q import CatalystQClient, MaxCutProblem, QUBOProblem, RainProtocolKey
        from catalyst_rain import execute_prepared_request
    except ImportError as exc:  # pragma: no cover - exercised by users without installed SDK.
        raise RuntimeError(
            "Catalyst-Q SDK is required. Install catalyst-q or pass --sdk-path pointing at sdk/python."
        ) from exc
    return {
        "CatalystQClient": CatalystQClient,
        "MaxCutProblem": MaxCutProblem,
        "QUBOProblem": QUBOProblem,
        "RainProtocolKey": RainProtocolKey,
        "execute_prepared_request": execute_prepared_request,
    }


def _load_instances(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "0.1.0":
        raise ValueError("unsupported instance schema")
    return list(payload["instances"])


def _sdk_record(
    sdk: Dict[str, Any],
    client: Any,
    instance: Dict[str, Any],
    baseline: Dict[str, Any],
    solver_runs_this_month: int,
    execute_api: bool,
    timeout: float,
) -> Dict[str, Any]:
    started = time.perf_counter()
    rain_key = sdk["RainProtocolKey"].create(workflow_id=f"sdk-campaign-{instance['id']}", capacity=1024)
    if instance["kind"] == "qubo":
        problem = sdk["QUBOProblem"](matrix=instance["matrix"], offset=instance.get("offset", 0.0))
        prepared = client.prepare_qubo(problem, rain_key=rain_key, solver_runs_this_month=solver_runs_this_month)
        operation = "prepare_qubo"
    elif instance["kind"] == "maxcut":
        problem = sdk["MaxCutProblem"](edges=[tuple(edge) for edge in instance["edges"]], nodes=instance["nodes"])
        prepared = client.prepare_maxcut(problem, rain_key=rain_key, solver_runs_this_month=solver_runs_this_month)
        operation = "prepare_maxcut"
    else:
        raise ValueError(f"unsupported SDK campaign kind: {instance['kind']}")

    runtime_s = time.perf_counter() - started
    validator: Dict[str, Any] = {
        "valid": True,
        "kind": "sdk_request_prepared",
        "route": _route_path(prepared.url),
        "method": prepared.method,
        "billing_estimate": prepared.json.get("billing_estimate", {}),
        "reference_objective": baseline["objective"],
    }
    status = "unknown"
    objective: Optional[float] = None
    if execute_api:
        api_result = sdk["execute_prepared_request"](prepared, timeout=timeout)
        validator["api_execution"] = api_result
        extracted = _extract_api_objective(instance["kind"], api_result)
        objective = extracted
        if extracted is not None:
            validator["matches_reference"] = abs(extracted - baseline["objective"]) <= 1e-9
            status = "optimal" if validator["matches_reference"] else "feasible"

    return {
        "suite_id": "biq_mac_maxcut_bqp",
        "instance_id": instance["id"],
        "instance_sha256": _sha256_json(instance),
        "solver_id": "catalyst-q-sdk",
        "solver_version": "local-or-installed",
        "command": operation,
        "seed": None,
        "timeout_s": timeout,
        "runtime_s": round(runtime_s, 9),
        "status": status,
        "objective": objective,
        "hardware": _hardware(),
        "validator": validator,
    }


def _reference_record(instance: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "suite_id": "biq_mac_maxcut_bqp",
        "instance_id": instance["id"],
        "instance_sha256": _sha256_json(instance),
        "solver_id": "exact-enumeration-reference",
        "solver_version": "0.1.0",
        "command": f"exact_{instance['kind']}_enumeration",
        "seed": None,
        "timeout_s": 30.0,
        "runtime_s": baseline["runtime_s"],
        "status": "optimal",
        "objective": baseline["objective"],
        "hardware": _hardware(),
        "validator": {
            "valid": True,
            "kind": f"exact_{instance['kind']}_certificate",
            "assignment": baseline["assignment"],
        },
    }


def _exact_reference(instance: Dict[str, Any]) -> Dict[str, Any]:
    started = time.perf_counter()
    if instance["kind"] == "qubo":
        objective, assignment = exact_qubo(instance["matrix"], instance.get("offset", 0.0))
    elif instance["kind"] == "maxcut":
        objective, assignment = exact_maxcut(instance["edges"], instance["nodes"])
    else:
        raise ValueError(f"unsupported instance kind: {instance['kind']}")
    return {
        "objective": objective,
        "assignment": assignment,
        "runtime_s": round(time.perf_counter() - started, 9),
    }


def exact_qubo(matrix: List[List[float]], offset: float = 0.0) -> Tuple[float, List[int]]:
    n = len(matrix)
    best_value = float("inf")
    best_assignment: List[int] = []
    for mask in range(1 << n):
        assignment = [(mask >> bit) & 1 for bit in range(n)]
        value = offset
        for row in range(n):
            for col in range(n):
                value += matrix[row][col] * assignment[row] * assignment[col]
        if value < best_value:
            best_value = value
            best_assignment = assignment
    return round(best_value, 9), best_assignment


def exact_maxcut(edges: Iterable[Iterable[float]], nodes: int) -> Tuple[float, List[int]]:
    parsed = [(int(edge[0]), int(edge[1]), float(edge[2])) for edge in edges]
    best_value = float("-inf")
    best_partition: List[int] = []
    for mask in range(1 << nodes):
        partition = [(mask >> bit) & 1 for bit in range(nodes)]
        value = sum(weight for u, v, weight in parsed if partition[u] != partition[v])
        if value > best_value:
            best_value = value
            best_partition = partition
    return round(best_value, 9), best_partition


def _extract_api_objective(kind: str, api_result: Dict[str, Any]) -> Optional[float]:
    payload = api_result.get("json")
    if not isinstance(payload, dict):
        return None
    result = payload.get("result", payload)
    if not isinstance(result, dict):
        return None
    key = "objective" if kind == "qubo" else "cut_value"
    value = result.get(key)
    return float(value) if isinstance(value, (int, float)) else None


def _route_path(url: str) -> str:
    marker = "/v3turbo"
    return url[url.index(marker) :] if marker in url else url


def _sha256_json(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _hardware() -> Dict[str, str]:
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def _render_campaign_report(records: List[Dict[str, Any]], execute_api: bool) -> str:
    sdk_rows = [record for record in records if record["solver_id"] == "catalyst-q-sdk"]
    reference_rows = [record for record in records if record["solver_id"] == "exact-enumeration-reference"]
    lines = [
        "# Catalyst-Q SDK QUBO/Max-Cut Campaign",
        "",
        "This campaign exercises the public Catalyst-Q SDK QUBO and Max-Cut request builders and records exact reference certificates.",
        "It does not disclose proprietary execution internals.",
        "",
        "## Summary",
        "",
        f"- SDK rows: {len(sdk_rows)}",
        f"- Exact reference rows: {len(reference_rows)}",
        f"- Live API execution: {'enabled' if execute_api else 'disabled'}",
        "",
        "## Results",
        "",
        "| Instance | Solver | Status | Objective | Validator |",
        "|---|---|---:|---:|---|",
    ]
    for record in records:
        lines.append(
            "| {instance} | {solver} | {status} | {objective} | {validator} |".format(
                instance=record["instance_id"],
                solver=record["solver_id"],
                status=record["status"],
                objective="" if record["objective"] is None else record["objective"],
                validator=record["validator"]["kind"],
            )
        )
    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Catalyst-Q SDK QUBO/Max-Cut evidence campaign.")
    parser.add_argument("--output-dir", default="results/raw", help="Directory for JSONL and Markdown artifacts.")
    parser.add_argument("--sdk-path", default=None, help="Optional path to local sdk/python checkout.")
    parser.add_argument("--base-url", default="https://catalyst-q-sdk.strategic-innovations.workers.dev/v3turbo")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--execute-api", action="store_true")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)
    artifacts = run_sdk_qubo_maxcut_campaign(
        output_dir=Path(args.output_dir),
        sdk_path=Path(args.sdk_path) if args.sdk_path else None,
        base_url=args.base_url,
        api_key=args.api_key,
        execute_api=args.execute_api,
        timeout=args.timeout,
    )
    print(f"Wrote {artifacts['raw_jsonl']}")
    print(f"Wrote {artifacts['markdown']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

