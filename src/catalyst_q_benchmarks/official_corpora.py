from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


SATLIB_UF20_URL = "https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf20-91.tar.gz"
ORLIB_MKNAP1_URL = "https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/mknap1.txt"
TSPLIB95_URLS = [
    "https://raw.githubusercontent.com/mastqe/tsplib/master/ulysses16.tsp",
    "https://raw.githubusercontent.com/mastqe/tsplib/master/ulysses22.tsp",
    "https://raw.githubusercontent.com/mastqe/tsplib/master/att48.tsp",
]
DIMACS_GSET_URLS = [
    "https://web.stanford.edu/~yyye/yyye/Gset/G1",
    "https://web.stanford.edu/~yyye/yyye/Gset/G2",
    "https://web.stanford.edu/~yyye/yyye/Gset/G3",
]
ORLIB_BQP_URLS = [
    "https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/bqp50.txt",
]
_SOLVER_VERSION_CACHE: Dict[str, str] = {}


def run_satlib_uf20(
    output_dir: Path,
    sdk_path: Optional[Path] = None,
    base_url: str = "https://api.strategic-innovations.ai/v3turbo",
    api_key: Optional[str] = None,
    execute_api: bool = False,
    limit: Optional[int] = None,
    start_index: int = 1,
    append: bool = False,
    policy_tier: str = "free",
    timeout: float = 30.0,
    external_solvers: Tuple[str, ...] = ("kissat", "cadical"),
) -> Dict[str, str]:
    sdk = _load_sdk(sdk_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "satlib_uf20_91.jsonl"
    summary_path = output_dir / "satlib_uf20_91_summary.json"
    report_path = output_dir / "satlib_uf20_91_report.md"
    records: List[Dict[str, Any]] = []
    started_campaign = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="catalyst_q_satlib_uf20_", dir="/private/tmp") as tmp_name:
        tmp = Path(tmp_name)
        archive = tmp / "uf20-91.tar.gz"
        download = _download(SATLIB_UF20_URL, archive)
        extract_dir = tmp / "extracted"
        extract_dir.mkdir()
        _safe_extract_tar_gz(archive, extract_dir)
        all_files = sorted(extract_dir.rglob("*.cnf"))
        files = all_files[max(0, start_index - 1) :]
        if limit is not None:
            files = files[: max(0, limit)]

        client = sdk["CatalystQClient"](api_key=api_key, base_url=base_url, policy=_usage_policy(sdk, policy_tier))
        if append and raw_path.exists():
            records.extend(_load_jsonl(raw_path))
        else:
            raw_path.write_text("", encoding="utf-8")
        for offset, cnf_path in enumerate(files, start=0):
            source_index = start_index + offset
            content = cnf_path.read_text(encoding="utf-8", errors="replace")
            variables, clauses = parse_dimacs_cnf(content)
            instance = _instance_metadata(cnf_path, content, variables, clauses)
            if execute_api:
                record = _run_catalyst_sat_api(
                    sdk=sdk,
                    client=client,
                    instance=instance,
                    clauses=clauses,
                    variables=variables,
                    solver_runs_this_month=source_index - 1,
                    timeout=timeout,
                )
            else:
                record = _prepare_catalyst_sat_request(
                    sdk=sdk,
                    client=client,
                    instance=instance,
                    clauses=clauses,
                    variables=variables,
                    solver_runs_this_month=source_index - 1,
                    timeout=timeout,
                )
            _append_record(raw_path, record)
            records.append(record)

            for solver in external_solvers:
                if shutil.which(solver) is None:
                    continue
                baseline = _run_sat_solver(solver, cnf_path, instance, clauses, variables, timeout)
                _append_record(raw_path, baseline)
                records.append(baseline)

            if source_index % 25 == 0 or offset + 1 == len(files):
                print(f"processed {source_index}/{len(all_files)} SATLIB uf20-91 instances", flush=True)

        summary = _summary(
            records=records,
            campaign="satlib_uf20_91_sequential",
            source_url=SATLIB_UF20_URL,
            download=download,
            selected_instances=len({record["instance_id"] for record in records}),
            total_available_instances=_count_available_cnf_files(extract_dir),
            runtime_s=time.perf_counter() - started_campaign,
            temp_directory_removed=True,
        )

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_render_satlib_report(summary, records), encoding="utf-8")
    return {"raw_jsonl": str(raw_path), "summary_json": str(summary_path), "markdown": str(report_path)}


def run_orlib_mknap1(
    output_dir: Path,
    sdk_path: Optional[Path] = None,
    base_url: str = "https://api.strategic-innovations.ai/v3turbo",
    api_key: Optional[str] = None,
    execute_api: bool = False,
    limit: Optional[int] = None,
    start_index: int = 1,
    append: bool = False,
    policy_tier: str = "free",
    timeout: float = 30.0,
    node_limit: int = 250_000,
) -> Dict[str, str]:
    sdk = _load_sdk(sdk_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "orlib_mknap1.jsonl"
    summary_path = output_dir / "orlib_mknap1_summary.json"
    report_path = output_dir / "orlib_mknap1_report.md"
    records: List[Dict[str, Any]] = []
    started_campaign = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="catalyst_q_orlib_mknap1_", dir="/private/tmp") as tmp_name:
        tmp = Path(tmp_name)
        data_path = tmp / "mknap1.txt"
        download = _download(ORLIB_MKNAP1_URL, data_path)
        instances = parse_orlib_mknap(data_path.read_text(encoding="utf-8", errors="replace"), ORLIB_MKNAP1_URL)
        selected = instances[max(0, start_index - 1) :]
        if limit is not None:
            selected = selected[: max(0, limit)]

        client = sdk["CatalystQClient"](api_key=api_key, base_url=base_url, policy=_usage_policy(sdk, policy_tier))
        if append and raw_path.exists():
            records.extend(_load_jsonl(raw_path))
        else:
            raw_path.write_text("", encoding="utf-8")

        for offset, instance in enumerate(selected, start=0):
            source_index = start_index + offset
            if execute_api:
                record = _run_catalyst_mkp_api(
                    sdk=sdk,
                    client=client,
                    instance=instance,
                    solver_runs_this_month=source_index - 1,
                    timeout=timeout,
                    node_limit=node_limit,
                )
            else:
                record = _prepare_catalyst_mkp_request(
                    sdk=sdk,
                    client=client,
                    instance=instance,
                    solver_runs_this_month=source_index - 1,
                    timeout=timeout,
                    node_limit=node_limit,
                )
            _append_record(raw_path, record)
            records.append(record)

            baseline = _run_exact_mkp_reference(instance, timeout=timeout, node_limit=max(node_limit, 1_000_000))
            _append_record(raw_path, baseline)
            records.append(baseline)

            print(f"processed {source_index}/{len(instances)} OR-Library mknap1 instances", flush=True)

        summary = _summary(
            records=records,
            campaign="orlib_mknap1_sequential",
            source_url=ORLIB_MKNAP1_URL,
            download=download,
            selected_instances=len({record["instance_id"] for record in records}),
            total_available_instances=len(instances),
            runtime_s=time.perf_counter() - started_campaign,
            temp_directory_removed=True,
        )

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_render_mknap_report(summary, records), encoding="utf-8")
    return {"raw_jsonl": str(raw_path), "summary_json": str(summary_path), "markdown": str(report_path)}


def parse_dimacs_cnf(text: str) -> Tuple[int, List[List[int]]]:
    variables = 0
    clauses: List[List[int]] = []
    current: List[int] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("c", "%", "0")):
            continue
        if line.startswith("p "):
            parts = line.split()
            if len(parts) >= 4 and parts[1].lower() == "cnf":
                variables = int(parts[2])
            continue
        for token in line.split():
            literal = int(token)
            if literal == 0:
                if current:
                    clauses.append(current)
                    current = []
            else:
                current.append(literal)
    if current:
        clauses.append(current)
    if variables <= 0 and clauses:
        variables = max(abs(literal) for clause in clauses for literal in clause)
    return variables, clauses


def canonical_dimacs_cnf(variables: int, clauses: List[List[int]]) -> str:
    lines = [f"p cnf {variables} {len(clauses)}"]
    for clause in clauses:
        lines.append(" ".join(str(literal) for literal in clause) + " 0")
    return "\n".join(lines) + "\n"


def parse_orlib_mknap(text: str, source_url: str = ORLIB_MKNAP1_URL) -> List[Dict[str, Any]]:
    tokens = text.split()
    if not tokens:
        return []
    cursor = 0
    count = int(float(tokens[cursor]))
    cursor += 1
    instances: List[Dict[str, Any]] = []
    for index in range(1, count + 1):
        n_items = int(float(tokens[cursor]))
        n_constraints = int(float(tokens[cursor + 1]))
        optimum = float(tokens[cursor + 2])
        cursor += 3
        values = [float(token) for token in tokens[cursor : cursor + n_items]]
        cursor += n_items
        constraints: List[List[float]] = []
        for _ in range(n_constraints):
            constraints.append([float(token) for token in tokens[cursor : cursor + n_items]])
            cursor += n_items
        capacities = [float(token) for token in tokens[cursor : cursor + n_constraints]]
        cursor += n_constraints
        canonical = json.dumps(
            {
                "values": values,
                "constraints": constraints,
                "capacities": capacities,
                "optimum": optimum,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        instances.append(
            {
                "suite_id": "orlib_mknap1",
                "instance_id": f"mknap1_{index:02d}",
                "instance_path": "mknap1.txt",
                "instance_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
                "items": n_items,
                "constraints_count": n_constraints,
                "optimum": optimum,
                "values": values,
                "constraints": constraints,
                "capacities": capacities,
                "source": source_url,
            }
        )
    if cursor != len(tokens):
        raise ValueError(f"unparsed OR-Library mknap tokens: {len(tokens) - cursor}")
    return instances


def _load_sdk(sdk_path: Optional[Path]) -> Dict[str, Any]:
    if sdk_path is not None:
        sys.path.insert(0, str(Path(sdk_path).resolve()))
    try:
        from catalyst_q import CatalystQClient, MultidimensionalKnapsackProblem, RainProtocolKey, SATProblem, TSPProblem, MaxCutProblem, QUBOProblem
        from catalyst_rain import UsagePolicy, execute_prepared_request
    except ImportError as exc:  # pragma: no cover - user environment dependent.
        raise RuntimeError("Install catalyst-q or pass --sdk-path pointing at sdk/python.") from exc
    return {
        "CatalystQClient": CatalystQClient,
        "MultidimensionalKnapsackProblem": MultidimensionalKnapsackProblem,
        "RainProtocolKey": RainProtocolKey,
        "SATProblem": SATProblem,
        "TSPProblem": TSPProblem,
        "MaxCutProblem": MaxCutProblem,
        "QUBOProblem": QUBOProblem,
        "UsagePolicy": UsagePolicy,
        "execute_prepared_request": execute_prepared_request,
    }


def _usage_policy(sdk: Dict[str, Any], tier: str) -> Any:
    policies = {
        "free": sdk["UsagePolicy"].free,
        "starter": sdk["UsagePolicy"].starter,
        "pro": sdk["UsagePolicy"].pro,
        "enterprise": sdk["UsagePolicy"].enterprise,
    }
    return policies[tier]()


def _download(url: str, destination: Path) -> Dict[str, Any]:
    started = time.perf_counter()
    with urllib.request.urlopen(url, timeout=60) as response:
        body = response.read()
        headers = dict(response.headers.items())
    destination.write_bytes(body)
    return {
        "url": url,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "elapsed_s": round(time.perf_counter() - started, 6),
        "last_modified": headers.get("Last-Modified"),
        "content_type": headers.get("Content-Type"),
    }


def _safe_extract_tar_gz(archive: Path, destination: Path) -> None:
    with tarfile.open(archive, "r:gz") as tar:
        destination_resolved = destination.resolve()
        for member in tar.getmembers():
            member_path = (destination / member.name).resolve()
            if destination_resolved not in member_path.parents and member_path != destination_resolved:
                raise ValueError(f"unsafe tar member path: {member.name}")
        tar.extractall(destination)


def _count_available_cnf_files(extract_dir: Path) -> int:
    return sum(1 for _ in extract_dir.rglob("*.cnf"))


def _instance_metadata(cnf_path: Path, content: str, variables: int, clauses: List[List[int]]) -> Dict[str, Any]:
    return {
        "suite_id": "satlib_uf20_91",
        "instance_id": cnf_path.stem,
        "instance_path": cnf_path.name,
        "instance_sha256": hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest(),
        "variables": variables,
        "clauses": len(clauses),
    }


def _prepare_catalyst_sat_request(
    sdk: Dict[str, Any],
    client: Any,
    instance: Dict[str, Any],
    clauses: List[List[int]],
    variables: int,
    solver_runs_this_month: int,
    timeout: float,
) -> Dict[str, Any]:
    started = time.perf_counter()
    rain_key = sdk["RainProtocolKey"].create(workflow_id=f"satlib-uf20-91-{instance['instance_id']}", capacity=1024)
    problem = sdk["SATProblem"](clauses, variables)
    prepared = client.prepare_sat(problem, rain_key=rain_key, solver_runs_this_month=solver_runs_this_month)
    return _base_record(
        instance=instance,
        solver_id="catalyst-q-sdk-request",
        command="prepare_sat",
        timeout=timeout,
        runtime_s=time.perf_counter() - started,
        status="unknown",
        objective=None,
        validator={
            "valid": True,
            "kind": "sdk_request_prepared",
            "route": _route_path(prepared.url),
            "method": prepared.method,
            "billing_estimate": prepared.json.get("billing_estimate", {}),
        },
    )


def _run_catalyst_sat_api(
    sdk: Dict[str, Any],
    client: Any,
    instance: Dict[str, Any],
    clauses: List[List[int]],
    variables: int,
    solver_runs_this_month: int,
    timeout: float,
) -> Dict[str, Any]:
    started = time.perf_counter()
    rain_key = sdk["RainProtocolKey"].create(workflow_id=f"satlib-uf20-91-{instance['instance_id']}", capacity=1024)
    problem = sdk["SATProblem"](clauses, variables)
    prepared = client.prepare_sat(problem, rain_key=rain_key, solver_runs_this_month=solver_runs_this_month)
    api_result = sdk["execute_prepared_request"](prepared, timeout=timeout)
    payload = api_result.get("json") if isinstance(api_result.get("json"), dict) else {}
    violations = payload.get("violations") if isinstance(payload, dict) else None
    satisfied = len(clauses) - int(violations) if isinstance(violations, int) else None
    valid = api_result.get("ok") is True and violations == 0
    status = "optimal" if valid else "feasible" if api_result.get("ok") is True else "error"
    return _base_record(
        instance=instance,
        solver_id="catalyst-q-sdk-live",
        command="prepare_sat + execute_prepared_request",
        timeout=timeout,
        runtime_s=time.perf_counter() - started,
        status=status,
        objective=satisfied,
        validator={
            "valid": valid,
            "kind": "satlib_api_zero_violations",
            "route": _route_path(prepared.url),
            "billing_estimate": prepared.json.get("billing_estimate", {}),
            "api_execution": api_result,
            "violations": violations,
            "satisfiable": payload.get("satisfiable") if isinstance(payload, dict) else None,
        },
    )


def _run_sat_solver(
    solver: str,
    cnf_path: Path,
    instance: Dict[str, Any],
    clauses: List[List[int]],
    variables: int,
    timeout: float,
) -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        with tempfile.TemporaryDirectory(prefix="catalyst_q_sat_solver_", dir="/private/tmp") as tmp_name:
            solver_cnf = Path(tmp_name) / cnf_path.name
            solver_cnf.write_text(canonical_dimacs_cnf(variables, clauses), encoding="utf-8")
            proc = subprocess.run(
                [solver, str(solver_cnf)],
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        runtime_s = time.perf_counter() - started
        assignment = _parse_sat_assignment(proc.stdout, variables)
        satisfied = _sat_count(clauses, assignment) if assignment else 0
        valid = satisfied == len(clauses) and proc.returncode in {0, 10}
        status = "optimal" if valid else "feasible" if proc.returncode in {0, 10, 20} else "error"
        return _base_record(
            instance=instance,
            solver_id=solver,
            command=f"{solver} canonical-{cnf_path.name}",
            timeout=timeout,
            runtime_s=runtime_s,
            status=status,
            objective=satisfied,
            validator={
                "valid": valid,
                "kind": "external_sat_assignment",
                "returncode": proc.returncode,
                "satisfied_clauses": satisfied,
                "total_clauses": len(clauses),
                "assignment_sha256": hashlib.sha256(json.dumps(assignment).encode("utf-8")).hexdigest(),
                "stdout_sha256": hashlib.sha256(proc.stdout.encode("utf-8", errors="replace")).hexdigest(),
                "stderr_sha256": hashlib.sha256(proc.stderr.encode("utf-8", errors="replace")).hexdigest(),
                "input_normalization": "stripped SATLIB trailer and rewrote canonical DIMACS CNF for solver compatibility",
            },
        )
    except subprocess.TimeoutExpired as exc:
        return _base_record(
            instance=instance,
            solver_id=solver,
            command=f"{solver} canonical-{cnf_path.name}",
            timeout=timeout,
            runtime_s=time.perf_counter() - started,
            status="timeout",
            objective=None,
            validator={"valid": False, "kind": "external_sat_timeout", "error": str(exc)},
        )
    except Exception as exc:  # noqa: BLE001 - raw records should capture unexpected baseline errors.
        return _base_record(
            instance=instance,
            solver_id=solver,
            command=f"{solver} canonical-{cnf_path.name}",
            timeout=timeout,
            runtime_s=time.perf_counter() - started,
            status="error",
            objective=None,
            validator={"valid": False, "kind": "external_sat_error", "error": str(exc)},
        )


def _prepare_catalyst_mkp_request(
    sdk: Dict[str, Any],
    client: Any,
    instance: Dict[str, Any],
    solver_runs_this_month: int,
    timeout: float,
    node_limit: int,
) -> Dict[str, Any]:
    started = time.perf_counter()
    rain_key = sdk["RainProtocolKey"].create(workflow_id=f"orlib-mknap1-{instance['instance_id']}", capacity=2048)
    problem = sdk["MultidimensionalKnapsackProblem"](
        values=instance["values"],
        constraints=instance["constraints"],
        capacities=instance["capacities"],
        node_limit=node_limit,
    )
    prepared = client.prepare_knapsack(problem, rain_key=rain_key, solver_runs_this_month=solver_runs_this_month)
    return _base_record(
        instance=instance,
        solver_id="catalyst-q-sdk-request",
        command="prepare_knapsack",
        timeout=timeout,
        runtime_s=time.perf_counter() - started,
        status="unknown",
        objective=None,
        validator={
            "valid": True,
            "kind": "sdk_request_prepared",
            "route": _route_path(prepared.url),
            "method": prepared.method,
            "billing_estimate": prepared.json.get("billing_estimate", {}),
        },
        domain="MKP",
        source_url=ORLIB_MKNAP1_URL,
    )


def _run_catalyst_mkp_api(
    sdk: Dict[str, Any],
    client: Any,
    instance: Dict[str, Any],
    solver_runs_this_month: int,
    timeout: float,
    node_limit: int,
) -> Dict[str, Any]:
    started = time.perf_counter()
    rain_key = sdk["RainProtocolKey"].create(workflow_id=f"orlib-mknap1-{instance['instance_id']}", capacity=2048)
    problem = sdk["MultidimensionalKnapsackProblem"](
        values=instance["values"],
        constraints=instance["constraints"],
        capacities=instance["capacities"],
        node_limit=node_limit,
    )
    prepared = client.prepare_knapsack(problem, rain_key=rain_key, solver_runs_this_month=solver_runs_this_month)
    api_result = sdk["execute_prepared_request"](prepared, timeout=timeout)
    payload = api_result.get("json") if isinstance(api_result.get("json"), dict) else {}
    selected = payload.get("selected") if isinstance(payload, dict) else None
    objective = float(payload.get("totalValue")) if isinstance(payload.get("totalValue"), (int, float)) else None
    validation = _validate_mkp_solution(instance, selected, objective)
    valid = api_result.get("ok") is True and validation["valid"]
    status = "optimal" if valid and validation["optimal"] else "feasible" if valid else "error"
    return _base_record(
        instance=instance,
        solver_id="catalyst-q-sdk-live",
        command="prepare_knapsack + execute_prepared_request",
        timeout=timeout,
        runtime_s=time.perf_counter() - started,
        status=status,
        objective=objective,
        validator={
            **validation,
            "kind": "orlib_mkp_api_solution",
            "route": _route_path(prepared.url),
            "billing_estimate": prepared.json.get("billing_estimate", {}),
            "api_execution": api_result,
            "proven_optimal": payload.get("provenOptimal") if isinstance(payload, dict) else None,
            "node_count": payload.get("nodeCount") if isinstance(payload, dict) else None,
        },
        domain="MKP",
        source_url=ORLIB_MKNAP1_URL,
    )


def _run_exact_mkp_reference(instance: Dict[str, Any], timeout: float, node_limit: int) -> Dict[str, Any]:
    started = time.perf_counter()
    result = _exact_mkp_branch_and_bound(instance, timeout=timeout, node_limit=node_limit)
    validation = _validate_mkp_solution(instance, result["selected"], result["value"])
    return _base_record(
        instance=instance,
        solver_id="orlib-exact-bb-reference",
        command="surrogate-fractional branch-and-bound",
        timeout=timeout,
        runtime_s=time.perf_counter() - started,
        status="optimal" if result["proven_optimal"] and validation["optimal"] else "feasible",
        objective=result["value"],
        validator={
            **validation,
            "kind": "orlib_mkp_exact_reference",
            "proven_optimal": result["proven_optimal"],
            "node_count": result["node_count"],
            "optimality_gap": result["optimality_gap"],
        },
        domain="MKP",
        source_url=ORLIB_MKNAP1_URL,
    )


def _base_record(
    instance: Dict[str, Any],
    solver_id: str,
    command: str,
    timeout: float,
    runtime_s: float,
    status: str,
    objective: Optional[float],
    validator: Dict[str, Any],
    domain: str = "SAT",
    source_url: str = SATLIB_UF20_URL,
) -> Dict[str, Any]:
    metadata = {
        key: instance[key]
        for key in ("variables", "clauses", "items", "constraints_count", "optimum")
        if key in instance
    }
    metadata["source"] = source_url
    return {
        "suite_id": instance["suite_id"],
        "domain": domain,
        "instance_id": instance["instance_id"],
        "instance_sha256": instance["instance_sha256"],
        "instance_metadata": metadata,
        "solver_id": solver_id,
        "solver_version": _solver_version(solver_id),
        "command": command,
        "seed": None,
        "timeout_s": timeout,
        "runtime_s": round(runtime_s, 9),
        "status": status,
        "objective": objective,
        "hardware": _hardware(),
        "validator": validator,
    }


def _summary(
    records: List[Dict[str, Any]],
    campaign: str,
    source_url: str,
    download: Dict[str, Any],
    selected_instances: int,
    total_available_instances: int,
    runtime_s: float,
    temp_directory_removed: bool,
) -> Dict[str, Any]:
    solvers = sorted({record["solver_id"] for record in records})
    by_solver: Dict[str, Dict[str, Any]] = {}
    for solver in solvers:
        rows = [record for record in records if record["solver_id"] == solver]
        valid = [record for record in rows if record["validator"].get("valid") is True]
        by_solver[solver] = {
            "records": len(rows),
            "valid_records": len(valid),
            "valid_rate": round(len(valid) / len(rows), 6) if rows else 0,
            "median_runtime_s": _median([float(record["runtime_s"]) for record in rows]),
            "total_runtime_s": round(sum(float(record["runtime_s"]) for record in rows), 6),
        }
    return {
        "campaign": campaign,
        "source_url": source_url,
        "download": download,
        "selected_instances": selected_instances,
        "total_available_instances": total_available_instances,
        "records": len(records),
        "solvers": solvers,
        "by_solver": by_solver,
        "runtime_s": round(runtime_s, 6),
        "temp_directory_removed": temp_directory_removed,
        "claim_scope": "official-corpus-run",
        "disclaimer": "This is sequential benchmark evidence on a named official corpus. It is not a broad NP or SOTA proof.",
    }


def _render_satlib_report(summary: Dict[str, Any], records: List[Dict[str, Any]]) -> str:
    lines = [
        "# SATLIB uf20-91 Sequential Evidence Run",
        "",
        summary["disclaimer"],
        "",
        "## Corpus",
        "",
        f"- Source: {summary['source_url']}",
        f"- Download bytes: {summary['download']['bytes']}",
        f"- Download SHA256: `{summary['download']['sha256']}`",
        f"- Available CNF instances: {summary['total_available_instances']}",
        f"- Selected CNF instances: {summary['selected_instances']}",
        f"- Temp corpus cache removed: {summary['temp_directory_removed']}",
        "",
        "## Solver Summary",
        "",
        "| Solver | Records | Valid records | Valid rate | Median runtime seconds | Total runtime seconds |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for solver, row in summary["by_solver"].items():
        lines.append(
            f"| {solver} | {row['records']} | {row['valid_records']} | {row['valid_rate']} | {row['median_runtime_s']} | {row['total_runtime_s']} |"
        )
    lines.extend(["", "## First 20 Result Rows", "", "| Instance | Solver | Status | Objective | Runtime seconds | Valid |", "|---|---|---:|---:|---:|---:|"])
    for record in records[:20]:
        objective = "" if record["objective"] is None else record["objective"]
        lines.append(
            f"| {record['instance_id']} | {record['solver_id']} | {record['status']} | {objective} | {record['runtime_s']} | {record['validator'].get('valid')} |"
        )
    return "\n".join(lines) + "\n"


def _render_mknap_report(summary: Dict[str, Any], records: List[Dict[str, Any]]) -> str:
    lines = [
        "# OR-Library mknap1 Sequential Evidence Run",
        "",
        summary["disclaimer"],
        "",
        "## Corpus",
        "",
        f"- Source: {summary['source_url']}",
        f"- Download bytes: {summary['download']['bytes']}",
        f"- Download SHA256: `{summary['download']['sha256']}`",
        f"- Available instances: {summary['total_available_instances']}",
        f"- Selected instances: {summary['selected_instances']}",
        f"- Temp corpus cache removed: {summary['temp_directory_removed']}",
        "",
        "## Solver Summary",
        "",
        "| Solver | Records | Valid records | Valid rate | Median runtime seconds | Total runtime seconds |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for solver, row in summary["by_solver"].items():
        lines.append(
            f"| {solver} | {row['records']} | {row['valid_records']} | {row['valid_rate']} | {row['median_runtime_s']} | {row['total_runtime_s']} |"
        )
    lines.extend(["", "## Result Rows", "", "| Instance | Solver | Status | Objective | Official optimum | Gap | Runtime seconds | Valid |", "|---|---|---:|---:|---:|---:|---:|---:|"])
    for record in records:
        metadata = record["instance_metadata"]
        validator = record["validator"]
        objective = "" if record["objective"] is None else record["objective"]
        lines.append(
            f"| {record['instance_id']} | {record['solver_id']} | {record['status']} | {objective} | {metadata.get('optimum', '')} | {validator.get('optimality_gap', '')} | {record['runtime_s']} | {validator.get('valid')} |"
        )
    return "\n".join(lines) + "\n"


def _validate_mkp_solution(
    instance: Dict[str, Any],
    selected: Any,
    objective: Optional[float],
) -> Dict[str, Any]:
    if not isinstance(selected, list) or not all(isinstance(item, (int, float)) for item in selected):
        return {"valid": False, "optimal": False, "error": "selected must be a numeric list"}
    item_indexes = [int(item) for item in selected]
    values = instance["values"]
    constraints = instance["constraints"]
    capacities = instance["capacities"]
    if any(item < 0 or item >= len(values) for item in item_indexes):
        return {"valid": False, "optimal": False, "error": "selected item index out of range"}
    total_value = sum(float(values[item]) for item in item_indexes)
    total_weights = [
        sum(float(row[item]) for item in item_indexes)
        for row in constraints
    ]
    feasible = all(weight <= float(capacity) + 1e-9 for weight, capacity in zip(total_weights, capacities))
    objective_matches = objective is not None and abs(float(objective) - total_value) <= 1e-6
    optimum = float(instance.get("optimum") or 0)
    gap = None if optimum <= 0 else round(optimum - total_value, 9)
    optimal = feasible and objective_matches and (optimum <= 0 or abs(total_value - optimum) <= 1e-6)
    return {
        "valid": feasible and objective_matches,
        "optimal": optimal,
        "total_value_from_selection": total_value,
        "total_weights": total_weights,
        "capacities": capacities,
        "official_optimum": optimum,
        "optimality_gap": gap,
    }


def _exact_mkp_branch_and_bound(instance: Dict[str, Any], timeout: float, node_limit: int) -> Dict[str, Any]:
    values = [float(value) for value in instance["values"]]
    constraints = [[float(value) for value in row] for row in instance["constraints"]]
    capacities = [float(value) for value in instance["capacities"]]
    n_items = len(values)
    n_constraints = len(capacities)
    started = time.perf_counter()
    surrogate_weights = [
        sum((constraints[row][item] / capacities[row]) if capacities[row] else float("inf") for row in range(n_constraints))
        for item in range(n_items)
    ]
    order = sorted(range(n_items), key=lambda item: _density(values[item], surrogate_weights[item]), reverse=True)
    ordered_values = [values[item] for item in order]
    ordered_weights = [[row[item] for item in order] for row in constraints]
    ordered_surrogate_weights = [surrogate_weights[item] for item in order]
    suffix = [0.0] * (n_items + 1)
    for index in range(n_items - 1, -1, -1):
        suffix[index] = suffix[index + 1] + ordered_values[index]
    single_orders = [
        sorted(range(n_items), key=lambda position: _density(ordered_values[position], ordered_weights[row][position]), reverse=True)
        for row in range(n_constraints)
    ]
    surrogate_order = sorted(
        range(n_items),
        key=lambda position: _density(ordered_values[position], ordered_surrogate_weights[position]),
        reverse=True,
    )

    best = _greedy_mkp(values, constraints, capacities, order)
    for row in range(n_constraints):
        candidate_order = sorted(range(n_items), key=lambda item: _density(values[item], constraints[row][item]), reverse=True)
        candidate = _greedy_mkp(values, constraints, capacities, candidate_order)
        if candidate["value"] > best["value"]:
            best = candidate

    node_count = 0
    best_bound = float(best["value"])
    proven_optimal = True

    def fractional_bound(positions: List[int], index: int, remaining_capacity: float, weights: List[float], value: float) -> float:
        upper = value
        remaining = max(0.0, remaining_capacity)
        for position in positions:
            if position < index:
                continue
            weight = weights[position]
            if weight <= 0:
                upper += ordered_values[position]
            elif weight <= remaining:
                remaining -= weight
                upper += ordered_values[position]
            else:
                upper += ordered_values[position] * (remaining / weight)
                break
        return upper

    def upper_bound(index: int, value: float, used: List[float]) -> float:
        bound = value + suffix[index]
        remaining_surrogate = sum(
            max(0.0, (capacities[row] - used[row]) / capacities[row]) if capacities[row] else 0.0
            for row in range(n_constraints)
        )
        bound = min(bound, fractional_bound(surrogate_order, index, remaining_surrogate, ordered_surrogate_weights, value))
        for row in range(n_constraints):
            bound = min(bound, fractional_bound(single_orders[row], index, capacities[row] - used[row], ordered_weights[row], value))
        return bound

    def search(index: int, value: float, used: List[float], selected_positions: List[int]) -> None:
        nonlocal best, node_count, best_bound, proven_optimal
        node_count += 1
        if node_count > node_limit or time.perf_counter() - started > timeout:
            proven_optimal = False
            best_bound = max(best_bound, upper_bound(index, value, used))
            return
        if value + suffix[index] <= float(best["value"]) + 1e-9:
            return
        bound = upper_bound(index, value, used)
        best_bound = max(best_bound, bound)
        if bound <= float(best["value"]) + 1e-9:
            return
        if index == n_items:
            if value > float(best["value"]):
                best = {"value": value, "selected": [order[position] for position in selected_positions]}
            return
        feasible = all(
            used[row] + ordered_weights[row][index] <= capacities[row] + 1e-9
            for row in range(n_constraints)
        )
        if feasible:
            for row in range(n_constraints):
                used[row] += ordered_weights[row][index]
            selected_positions.append(index)
            search(index + 1, value + ordered_values[index], used, selected_positions)
            selected_positions.pop()
            for row in range(n_constraints):
                used[row] -= ordered_weights[row][index]
        search(index + 1, value, used, selected_positions)

    search(0, 0.0, [0.0] * n_constraints, [])
    return {
        "value": best["value"],
        "selected": sorted(best["selected"]),
        "proven_optimal": proven_optimal,
        "node_count": node_count,
        "optimality_gap": 0.0 if proven_optimal else max(0.0, best_bound - float(best["value"])),
    }


def _density(value: float, weight: float) -> float:
    return float("inf") if weight <= 0 else value / weight


def _greedy_mkp(
    values: List[float],
    constraints: List[List[float]],
    capacities: List[float],
    order: List[int],
) -> Dict[str, Any]:
    used = [0.0] * len(capacities)
    selected: List[int] = []
    total = 0.0
    for item in order:
        if all(used[row] + constraints[row][item] <= capacities[row] + 1e-9 for row in range(len(capacities))):
            for row in range(len(capacities)):
                used[row] += constraints[row][item]
            selected.append(item)
            total += values[item]
    return {"value": total, "selected": selected}


def _append_record(path: Path, record: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _sat_count(clauses: List[List[int]], assignment: List[int]) -> int:
    count = 0
    for clause in clauses:
        if any((literal > 0 and assignment[abs(literal) - 1]) or (literal < 0 and not assignment[abs(literal) - 1]) for literal in clause):
            count += 1
    return count


def _parse_sat_assignment(output: str, variables: int) -> List[int]:
    values: Dict[int, int] = {}
    for line in output.splitlines():
        if line.startswith("v "):
            for token in line.split()[1:]:
                literal = int(token)
                if literal == 0:
                    continue
                values[abs(literal)] = 1 if literal > 0 else 0
    return [values.get(index, 0) for index in range(1, variables + 1)]


def _route_path(url: str) -> str:
    marker = "/v3turbo"
    return url[url.index(marker) :] if marker in url else url


def _solver_version(solver_id: str) -> str:
    cached = _SOLVER_VERSION_CACHE.get(solver_id)
    if cached is not None:
        return cached
    if solver_id.startswith("catalyst-q"):
        _SOLVER_VERSION_CACHE[solver_id] = "0.1.3"
        return "0.1.3"
    if shutil.which(solver_id) is None:
        _SOLVER_VERSION_CACHE[solver_id] = "not-installed"
        return "not-installed"
    try:
        proc = subprocess.run([solver_id, "--version"], text=True, capture_output=True, timeout=3, check=False)
    except Exception:  # noqa: BLE001 - version probing is best-effort metadata.
        _SOLVER_VERSION_CACHE[solver_id] = "local"
        return "local"
    text = (proc.stdout or proc.stderr).strip().splitlines()
    version = text[0][:160] if text else "local"
    _SOLVER_VERSION_CACHE[solver_id] = version
    return version


def _median(values: List[float]) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return round(ordered[middle], 9)
    return round((ordered[middle - 1] + ordered[middle]) / 2.0, 9)


def _hardware() -> Dict[str, str]:
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }



def run_tsplib95(
    output_dir: Path,
    sdk_path: Optional[Path] = None,
    base_url: str = "https://api.strategic-innovations.ai/v3turbo",
    api_key: Optional[str] = None,
    execute_api: bool = False,
    limit: Optional[int] = None,
    start_index: int = 1,
    append: bool = False,
    policy_tier: str = "free",
    timeout: float = 30.0,
) -> Dict[str, str]:
    sdk = _load_sdk(sdk_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "tsplib95.jsonl"
    summary_path = output_dir / "tsplib95_summary.json"
    report_path = output_dir / "tsplib95_report.md"
    records: List[Dict[str, Any]] = []
    started_campaign = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="catalyst_q_tsplib95_", dir="/private/tmp") as tmp_name:
        tmp = Path(tmp_name)
        client = sdk["CatalystQClient"](api_key=api_key, base_url=base_url, policy=_usage_policy(sdk, policy_tier))
        
        if append and raw_path.exists():
            records.extend(_load_jsonl(raw_path))
        else:
            raw_path.write_text("", encoding="utf-8")

        urls = TSPLIB95_URLS[max(0, start_index - 1):]
        if limit is not None:
            urls = urls[: max(0, limit)]

        for offset, url in enumerate(urls, start=0):
            source_index = start_index + offset
            filename = url.split('/')[-1]
            data_path = tmp / filename
            download = _download(url, data_path)
            content = data_path.read_text(encoding="utf-8", errors="replace")
            instance, distances = parse_tsplib(content, url, filename)
            
            if execute_api:
                record = _run_catalyst_tsp_api(sdk, client, instance, distances, source_index - 1, timeout)
            else:
                record = _prepare_catalyst_tsp_request(sdk, client, instance, distances, source_index - 1, timeout)
            
            _append_record(raw_path, record)
            records.append(record)

            baseline = _run_nearest_neighbor_baseline(instance, distances, timeout)
            _append_record(raw_path, baseline)
            records.append(baseline)

            print(f"processed {source_index}/{len(TSPLIB95_URLS)} TSPLIB95 instances", flush=True)

        summary = _summary(
            records=records,
            campaign="tsplib95_sequential",
            source_url="http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/",
            download={"url": "multiple"},
            selected_instances=len({record["instance_id"] for record in records}),
            total_available_instances=len(TSPLIB95_URLS),
            runtime_s=time.perf_counter() - started_campaign,
            temp_directory_removed=True,
        )

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_render_tsplib_report(summary, records), encoding="utf-8")
    return {"raw_jsonl": str(raw_path), "summary_json": str(summary_path), "markdown": str(report_path)}

def parse_tsplib(text: str, source_url: str, filename: str) -> Tuple[Dict[str, Any], List[List[float]]]:
    lines = text.splitlines()
    dimension = 0
    name = filename.replace('.tsp', '')
    coords: List[Tuple[float, float]] = []
    in_node_coord_section = False

    for line in lines:
        line = line.strip()
        if not line or line == "EOF":
            continue
        if line.startswith("NAME"):
            parts = line.split(":")
            if len(parts) > 1:
                name = parts[1].strip()
        elif line.startswith("DIMENSION"):
            parts = line.split(":")
            if len(parts) > 1:
                dimension = int(parts[1].strip())
        elif line.startswith("NODE_COORD_SECTION"):
            in_node_coord_section = True
        elif in_node_coord_section:
            parts = line.split()
            if len(parts) >= 3:
                coords.append((float(parts[1]), float(parts[2])))

    n = len(coords)
    distances = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = coords[i][0] - coords[j][0]
                dy = coords[i][1] - coords[j][1]
                distances[i][j] = float(round(math.sqrt(dx*dx + dy*dy)))

    instance = {
        "suite_id": "tsplib95",
        "instance_id": name,
        "instance_path": filename,
        "instance_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "dimension": dimension,
        "source": source_url,
    }
    return instance, distances

def _prepare_catalyst_tsp_request(sdk: Dict[str, Any], client: Any, instance: Dict[str, Any], distances: List[List[float]], solver_runs: int, timeout: float) -> Dict[str, Any]:
    started = time.perf_counter()
    rain_key = sdk["RainProtocolKey"].create(workflow_id=f"tsplib95-{instance['instance_id']}", capacity=1024)
    problem = sdk["TSPProblem"](distances)
    prepared = client.prepare_tsp(problem, rain_key=rain_key, solver_runs_this_month=solver_runs)
    return _base_record(
        instance=instance, solver_id="catalyst-q-sdk-request", command="prepare_tsp", timeout=timeout,
        runtime_s=time.perf_counter() - started, status="unknown", objective=None,
        validator={"valid": True, "kind": "sdk_request_prepared", "route": _route_path(prepared.url)},
        domain="TSP", source_url=instance["source"]
    )

def _run_catalyst_tsp_api(sdk: Dict[str, Any], client: Any, instance: Dict[str, Any], distances: List[List[float]], solver_runs: int, timeout: float) -> Dict[str, Any]:
    started = time.perf_counter()
    rain_key = sdk["RainProtocolKey"].create(workflow_id=f"tsplib95-{instance['instance_id']}", capacity=1024)
    problem = sdk["TSPProblem"](distances)
    prepared = client.prepare_tsp(problem, rain_key=rain_key, solver_runs_this_month=solver_runs)
    api_result = sdk["execute_prepared_request"](prepared, timeout=timeout)
    payload = api_result.get("json") if isinstance(api_result.get("json"), dict) else {}
    objective = float(payload.get("distance")) if payload.get("distance") is not None else None
    valid = api_result.get("ok") is True and objective is not None
    status = "feasible" if valid else "error"
    return _base_record(
        instance=instance, solver_id="catalyst-q-sdk-live", command="prepare_tsp + execute", timeout=timeout,
        runtime_s=time.perf_counter() - started, status=status, objective=objective,
        validator={"valid": valid, "kind": "tsp_api_solution", "api_execution": api_result},
        domain="TSP", source_url=instance["source"]
    )

def _run_nearest_neighbor_baseline(instance: Dict[str, Any], distances: List[List[float]], timeout: float) -> Dict[str, Any]:
    started = time.perf_counter()
    n = len(distances)
    tour = [0]
    unvisited = set(range(1, n))
    while unvisited:
        last = tour[-1]
        nxt = min(unvisited, key=lambda node: distances[last][node])
        tour.append(nxt)
        unvisited.remove(nxt)
    
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                candidate = tour[:i] + list(reversed(tour[i:j])) + tour[j:]
                cand_dist = sum(distances[candidate[k]][candidate[(k + 1) % n]] for k in range(n))
                curr_dist = sum(distances[tour[k]][tour[(k + 1) % n]] for k in range(n))
                if cand_dist < curr_dist:
                    tour = candidate
                    improved = True
                    
    distance = sum(distances[tour[k]][tour[(k + 1) % n]] for k in range(n))
    return _base_record(
        instance=instance, solver_id="nearest-neighbor-2opt-baseline", command="nn+2opt", timeout=timeout,
        runtime_s=time.perf_counter() - started, status="feasible", objective=distance,
        validator={"valid": True, "kind": "baseline_tsp_solution", "distance": distance},
        domain="TSP", source_url=instance["source"]
    )

def _render_tsplib_report(summary: Dict[str, Any], records: List[Dict[str, Any]]) -> str:
    lines = [
        "# TSPLIB95 Sequential Evidence Run", "", summary["disclaimer"], "", "## Corpus", "",
        f"- Source: {summary['source_url']}", f"- Available instances: {summary['total_available_instances']}",
        f"- Selected instances: {summary['selected_instances']}", "", "## Solver Summary", "",
        "| Solver | Records | Valid records | Valid rate | Median runtime seconds | Total runtime seconds |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for solver, row in summary["by_solver"].items():
        lines.append(f"| {solver} | {row['records']} | {row['valid_records']} | {row['valid_rate']} | {row['median_runtime_s']} | {row['total_runtime_s']} |")
    lines.extend(["", "## Result Rows", "", "| Instance | Solver | Status | Objective | Runtime seconds | Valid |", "|---|---|---:|---:|---:|---:|"])
    for record in records:
        objective = "" if record["objective"] is None else record["objective"]
        lines.append(f"| {record['instance_id']} | {record['solver_id']} | {record['status']} | {objective} | {record['runtime_s']} | {record['validator'].get('valid')} |")
    return "\n".join(lines) + "\n"


def run_dimacs_maxcut(
    output_dir: Path,
    sdk_path: Optional[Path] = None,
    base_url: str = "https://api.strategic-innovations.ai/v3turbo",
    api_key: Optional[str] = None,
    execute_api: bool = False,
    limit: Optional[int] = None,
    start_index: int = 1,
    append: bool = False,
    policy_tier: str = "free",
    timeout: float = 30.0,
) -> Dict[str, str]:
    sdk = _load_sdk(sdk_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "dimacs_maxcut.jsonl"
    summary_path = output_dir / "dimacs_maxcut_summary.json"
    report_path = output_dir / "dimacs_maxcut_report.md"
    records: List[Dict[str, Any]] = []
    started_campaign = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="catalyst_q_dimacs_", dir="/private/tmp") as tmp_name:
        tmp = Path(tmp_name)
        client = sdk["CatalystQClient"](api_key=api_key, base_url=base_url, policy=_usage_policy(sdk, policy_tier))
        
        if append and raw_path.exists():
            records.extend(_load_jsonl(raw_path))
        else:
            raw_path.write_text("", encoding="utf-8")

        urls = DIMACS_GSET_URLS[max(0, start_index - 1):]
        if limit is not None:
            urls = urls[: max(0, limit)]

        for offset, url in enumerate(urls, start=0):
            source_index = start_index + offset
            filename = url.split('/')[-1]
            data_path = tmp / filename
            download = _download(url, data_path)
            content = data_path.read_text(encoding="utf-8", errors="replace")
            instance, edges, nodes = parse_dimacs_gset(content, url, filename)
            
            if execute_api:
                record = _run_catalyst_maxcut_api(sdk, client, instance, edges, nodes, source_index - 1, timeout)
            else:
                record = _prepare_catalyst_maxcut_request(sdk, client, instance, edges, nodes, source_index - 1, timeout)
            
            _append_record(raw_path, record)
            records.append(record)

            baseline = _run_greedy_maxcut_baseline(instance, edges, nodes, timeout)
            _append_record(raw_path, baseline)
            records.append(baseline)

            print(f"processed {source_index}/{len(DIMACS_GSET_URLS)} DIMACS G-Set instances", flush=True)

        summary = _summary(
            records=records,
            campaign="dimacs_maxcut_sequential",
            source_url="https://web.stanford.edu/~yyye/yyye/Gset/",
            download={"url": "multiple"},
            selected_instances=len({record["instance_id"] for record in records}),
            total_available_instances=len(DIMACS_GSET_URLS),
            runtime_s=time.perf_counter() - started_campaign,
            temp_directory_removed=True,
        )

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_render_dimacs_report(summary, records), encoding="utf-8")
    return {"raw_jsonl": str(raw_path), "summary_json": str(summary_path), "markdown": str(report_path)}

def parse_dimacs_gset(text: str, source_url: str, filename: str) -> Tuple[Dict[str, Any], List[Tuple[int, int, float]], int]:
    lines = text.splitlines()
    edges: List[Tuple[int, int, float]] = []
    nodes = 0
    num_edges = 0
    
    first_line = True
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if first_line and len(parts) >= 2:
            nodes = int(parts[0])
            num_edges = int(parts[1])
            first_line = False
        elif len(parts) >= 3:
            u, v, w = int(parts[0]), int(parts[1]), float(parts[2])
            # Zero indexed for Catalyst API
            edges.append((u - 1, v - 1, w))

    instance = {
        "suite_id": "dimacs_gset",
        "instance_id": filename,
        "instance_path": filename,
        "instance_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "dimension": nodes,
        "source": source_url,
    }
    return instance, edges, nodes

def _prepare_catalyst_maxcut_request(sdk: Dict[str, Any], client: Any, instance: Dict[str, Any], edges: List[Tuple[int, int, float]], nodes: int, solver_runs: int, timeout: float) -> Dict[str, Any]:
    started = time.perf_counter()
    rain_key = sdk["RainProtocolKey"].create(workflow_id=f"dimacs-{instance['instance_id']}", capacity=1024)
    problem = sdk["MaxCutProblem"](edges, nodes)
    prepared = client.prepare_maxcut(problem, rain_key=rain_key, solver_runs_this_month=solver_runs)
    return _base_record(
        instance=instance, solver_id="catalyst-q-sdk-request", command="prepare_maxcut", timeout=timeout,
        runtime_s=time.perf_counter() - started, status="unknown", objective=None,
        validator={"valid": True, "kind": "sdk_request_prepared", "route": _route_path(prepared.url)},
        domain="Max-Cut", source_url=instance["source"]
    )

def _run_catalyst_maxcut_api(sdk: Dict[str, Any], client: Any, instance: Dict[str, Any], edges: List[Tuple[int, int, float]], nodes: int, solver_runs: int, timeout: float) -> Dict[str, Any]:
    started = time.perf_counter()
    rain_key = sdk["RainProtocolKey"].create(workflow_id=f"dimacs-{instance['instance_id']}", capacity=1024)
    problem = sdk["MaxCutProblem"](edges, nodes)
    prepared = client.prepare_maxcut(problem, rain_key=rain_key, solver_runs_this_month=solver_runs)
    api_result = sdk["execute_prepared_request"](prepared, timeout=timeout)
    payload = api_result.get("json") if isinstance(api_result.get("json"), dict) else {}
    objective = float(payload.get("cut_value")) if payload.get("cut_value") is not None else None
    valid = api_result.get("ok") is True and objective is not None
    status = "feasible" if valid else "error"
    return _base_record(
        instance=instance, solver_id="catalyst-q-sdk-live", command="prepare_maxcut + execute", timeout=timeout,
        runtime_s=time.perf_counter() - started, status=status, objective=objective,
        validator={"valid": valid, "kind": "maxcut_api_solution", "api_execution": api_result},
        domain="Max-Cut", source_url=instance["source"]
    )

def _run_greedy_maxcut_baseline(instance: Dict[str, Any], edges: List[Tuple[int, int, float]], nodes: int, timeout: float) -> Dict[str, Any]:
    started = time.perf_counter()
    partition = [0] * nodes
    for node in range(nodes):
        zero = partition[:]
        zero[node] = 0
        one = partition[:]
        one[node] = 1
        val_zero = sum(w for u, v, w in edges if zero[u] != zero[v])
        val_one = sum(w for u, v, w in edges if one[u] != one[v])
        partition = one if val_one > val_zero else zero
    
    cut_value = sum(w for u, v, w in edges if partition[u] != partition[v])
    return _base_record(
        instance=instance, solver_id="greedy-partition-baseline", command="greedy-maxcut", timeout=timeout,
        runtime_s=time.perf_counter() - started, status="feasible", objective=cut_value,
        validator={"valid": True, "kind": "baseline_maxcut_solution", "cut_value": cut_value},
        domain="Max-Cut", source_url=instance["source"]
    )

def _render_dimacs_report(summary: Dict[str, Any], records: List[Dict[str, Any]]) -> str:
    lines = [
        "# DIMACS / G-Set Max-Cut Sequential Evidence Run", "", summary["disclaimer"], "", "## Corpus", "",
        f"- Source: {summary['source_url']}", f"- Available instances: {summary['total_available_instances']}",
        f"- Selected instances: {summary['selected_instances']}", "", "## Solver Summary", "",
        "| Solver | Records | Valid records | Valid rate | Median runtime seconds | Total runtime seconds |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for solver, row in summary["by_solver"].items():
        lines.append(f"| {solver} | {row['records']} | {row['valid_records']} | {row['valid_rate']} | {row['median_runtime_s']} | {row['total_runtime_s']} |")
    lines.extend(["", "## Result Rows", "", "| Instance | Solver | Status | Objective | Runtime seconds | Valid |", "|---|---|---:|---:|---:|---:|"])
    for record in records:
        objective = "" if record["objective"] is None else record["objective"]
        lines.append(f"| {record['instance_id']} | {record['solver_id']} | {record['status']} | {objective} | {record['runtime_s']} | {record['validator'].get('valid')} |")
    return "\n".join(lines) + "\n"


def run_qubo_bqp(
    output_dir: Path,
    sdk_path: Optional[Path] = None,
    base_url: str = "https://api.strategic-innovations.ai/v3turbo",
    api_key: Optional[str] = None,
    execute_api: bool = False,
    limit: Optional[int] = None,
    start_index: int = 1,
    append: bool = False,
    policy_tier: str = "free",
    timeout: float = 30.0,
) -> Dict[str, str]:
    sdk = _load_sdk(sdk_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "orlib_bqp.jsonl"
    summary_path = output_dir / "orlib_bqp_summary.json"
    report_path = output_dir / "orlib_bqp_report.md"
    records: List[Dict[str, Any]] = []
    started_campaign = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="catalyst_q_bqp_", dir="/private/tmp") as tmp_name:
        tmp = Path(tmp_name)
        client = sdk["CatalystQClient"](api_key=api_key, base_url=base_url, policy=_usage_policy(sdk, policy_tier))
        
        if append and raw_path.exists():
            records.extend(_load_jsonl(raw_path))
        else:
            raw_path.write_text("", encoding="utf-8")

        urls = ORLIB_BQP_URLS[max(0, start_index - 1):]
        if limit is not None:
            urls = urls[: max(0, limit)]

        for offset, url in enumerate(urls, start=0):
            source_index = start_index + offset
            filename = url.split('/')[-1]
            data_path = tmp / filename
            download = _download(url, data_path)
            content = data_path.read_text(encoding="utf-8", errors="replace")
            instances = parse_orlib_bqp(content, url, filename)
            
            for inst_idx, (instance, matrix) in enumerate(instances):
                if limit is not None and inst_idx >= limit:
                    break
                if execute_api:
                    record = _run_catalyst_qubo_api(sdk, client, instance, matrix, inst_idx, timeout)
                else:
                    record = _prepare_catalyst_qubo_request(sdk, client, instance, matrix, inst_idx, timeout)
                
                _append_record(raw_path, record)
                records.append(record)

                baseline = _run_greedy_qubo_baseline(instance, matrix, timeout)
                _append_record(raw_path, baseline)
                records.append(baseline)

            print(f"processed {source_index}/{len(ORLIB_BQP_URLS)} OR-Library BQP sets", flush=True)

        summary = _summary(
            records=records,
            campaign="orlib_bqp_sequential",
            source_url="https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/",
            download={"url": "multiple"},
            selected_instances=len({record["instance_id"] for record in records}),
            total_available_instances=sum(len(parse_orlib_bqp(_download(u, tmp/u.split('/')[-1]), u, u.split('/')[-1])) for u in ORLIB_BQP_URLS) if limit is None else limit,
            runtime_s=time.perf_counter() - started_campaign,
            temp_directory_removed=True,
        )

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_render_qubo_report(summary, records), encoding="utf-8")
    return {"raw_jsonl": str(raw_path), "summary_json": str(summary_path), "markdown": str(report_path)}

def parse_orlib_bqp(text: str, source_url: str, filename: str) -> List[Tuple[Dict[str, Any], List[List[float]]]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    
    num_instances = int(lines[0])
    instances = []
    idx = 1
    
    for inst_num in range(num_instances):
        if idx >= len(lines): break
        parts = lines[idx].split()
        if len(parts) < 2:
            idx += 1
            parts = lines[idx].split()
        nodes = int(parts[0])
        num_entries = int(parts[1])
        idx += 1
        
        matrix = [[0.0] * nodes for _ in range(nodes)]
        for _ in range(num_entries):
            u, v, w = map(float, lines[idx].split())
            u, v = int(u) - 1, int(v) - 1
            matrix[u][v] = w
            if u != v:
                matrix[v][u] = w
            idx += 1
            
        instance = {
            "suite_id": "orlib_bqp",
            "instance_id": f"{filename.replace('.txt', '')}_{inst_num+1}",
            "instance_path": filename,
            "instance_sha256": hashlib.sha256(str(matrix).encode("utf-8")).hexdigest(),
            "dimension": nodes,
            "source": source_url,
        }
        instances.append((instance, matrix))
        
    return instances

def _prepare_catalyst_qubo_request(sdk: Dict[str, Any], client: Any, instance: Dict[str, Any], matrix: List[List[float]], solver_runs: int, timeout: float) -> Dict[str, Any]:
    started = time.perf_counter()
    rain_key = sdk["RainProtocolKey"].create(workflow_id=f"bqp-{instance['instance_id']}", capacity=1024)
    problem = sdk["QUBOProblem"](matrix)
    prepared = client.prepare_qubo(problem, rain_key=rain_key, solver_runs_this_month=solver_runs)
    return _base_record(
        instance=instance, solver_id="catalyst-q-sdk-request", command="prepare_qubo", timeout=timeout,
        runtime_s=time.perf_counter() - started, status="unknown", objective=None,
        validator={"valid": True, "kind": "sdk_request_prepared", "route": _route_path(prepared.url)},
        domain="QUBO", source_url=instance["source"]
    )

def _run_catalyst_qubo_api(sdk: Dict[str, Any], client: Any, instance: Dict[str, Any], matrix: List[List[float]], solver_runs: int, timeout: float) -> Dict[str, Any]:
    started = time.perf_counter()
    rain_key = sdk["RainProtocolKey"].create(workflow_id=f"bqp-{instance['instance_id']}", capacity=1024)
    problem = sdk["QUBOProblem"](matrix)
    prepared = client.prepare_qubo(problem, rain_key=rain_key, solver_runs_this_month=solver_runs)
    api_result = sdk["execute_prepared_request"](prepared, timeout=timeout)
    payload = api_result.get("json") if isinstance(api_result.get("json"), dict) else {}
    objective = float(payload.get("objective")) if payload.get("objective") is not None else None
    valid = api_result.get("ok") is True and objective is not None
    status = "feasible" if valid else "error"
    return _base_record(
        instance=instance, solver_id="catalyst-q-sdk-live", command="prepare_qubo + execute", timeout=timeout,
        runtime_s=time.perf_counter() - started, status=status, objective=objective,
        validator={"valid": valid, "kind": "qubo_api_solution", "api_execution": api_result},
        domain="QUBO", source_url=instance["source"]
    )

def _run_greedy_qubo_baseline(instance: Dict[str, Any], matrix: List[List[float]], timeout: float) -> Dict[str, Any]:
    started = time.perf_counter()
    n = len(matrix)
    assignment = [0] * n
    best = sum(matrix[r][c] * assignment[r] * assignment[c] for r in range(n) for c in range(n))
    improved = True
    while improved:
        improved = False
        for idx in range(n):
            candidate = assignment[:]
            candidate[idx] = 1 - candidate[idx]
            value = sum(matrix[r][c] * candidate[r] * candidate[c] for r in range(n) for c in range(n))
            if value < best:
                assignment, best, improved = candidate, value, True
                
    return _base_record(
        instance=instance, solver_id="single-flip-greedy-baseline", command="greedy-qubo", timeout=timeout,
        runtime_s=time.perf_counter() - started, status="feasible", objective=best,
        validator={"valid": True, "kind": "baseline_qubo_solution", "objective": best},
        domain="QUBO", source_url=instance["source"]
    )

def _render_qubo_report(summary: Dict[str, Any], records: List[Dict[str, Any]]) -> str:
    lines = [
        "# OR-Library BQP / QUBO Sequential Evidence Run", "", summary["disclaimer"], "", "## Corpus", "",
        f"- Source: {summary['source_url']}", f"- Available instances: {summary['total_available_instances']}",
        f"- Selected instances: {summary['selected_instances']}", "", "## Solver Summary", "",
        "| Solver | Records | Valid records | Valid rate | Median runtime seconds | Total runtime seconds |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for solver, row in summary["by_solver"].items():
        lines.append(f"| {solver} | {row['records']} | {row['valid_records']} | {row['valid_rate']} | {row['median_runtime_s']} | {row['total_runtime_s']} |")
    lines.extend(["", "## Result Rows", "", "| Instance | Solver | Status | Objective | Runtime seconds | Valid |", "|---|---|---:|---:|---:|---:|"])
    for record in records:
        objective = "" if record["objective"] is None else record["objective"]
        lines.append(f"| {record['instance_id']} | {record['solver_id']} | {record['status']} | {objective} | {record['runtime_s']} | {record['validator'].get('valid')} |")
    return "\n".join(lines) + "\n"

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run one official Catalyst-Q benchmark corpus sequentially.")
    parser.add_argument("--corpus", choices=["satlib-uf20", "orlib-mknap1", "tsplib95", "dimacs-maxcut", "orlib-bqp"], default="satlib-uf20")
    parser.add_argument("--output-dir", default="results/official_corpora/satlib_uf20_91")
    parser.add_argument("--sdk-path", default=None)
    parser.add_argument("--base-url", default="https://api.strategic-innovations.ai/v3turbo")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--execute-api", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--start-index", type=int, default=1, help="1-based corpus index to start from.")
    parser.add_argument("--append", action="store_true", help="Append to existing raw JSONL and include prior rows in the summary.")
    parser.add_argument(
        "--policy-tier",
        choices=["free", "starter", "pro", "enterprise"],
        default="free",
        help="Local SDK usage policy for request preparation. Use enterprise only for internal benchmark campaigns.",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--node-limit", type=int, default=250_000)
    args = parser.parse_args(argv)
    if args.corpus == "orlib-bqp":
        artifacts = run_qubo_bqp(
            output_dir=Path(args.output_dir),
            sdk_path=Path(args.sdk_path) if args.sdk_path else None,
            base_url=args.base_url,
            api_key=args.api_key,
            execute_api=args.execute_api,
            limit=args.limit,
            start_index=args.start_index,
            append=args.append,
            policy_tier=args.policy_tier,
            timeout=args.timeout,
        )
    elif args.corpus == "dimacs-maxcut":
        artifacts = run_dimacs_maxcut(
            output_dir=Path(args.output_dir),
            sdk_path=Path(args.sdk_path) if args.sdk_path else None,
            base_url=args.base_url,
            api_key=args.api_key,
            execute_api=args.execute_api,
            limit=args.limit,
            start_index=args.start_index,
            append=args.append,
            policy_tier=args.policy_tier,
            timeout=args.timeout,
        )
    elif args.corpus == "tsplib95":
        artifacts = run_tsplib95(
            output_dir=Path(args.output_dir),
            sdk_path=Path(args.sdk_path) if args.sdk_path else None,
            base_url=args.base_url,
            api_key=args.api_key,
            execute_api=args.execute_api,
            limit=args.limit,
            start_index=args.start_index,
            append=args.append,
            policy_tier=args.policy_tier,
            timeout=args.timeout,
        )
    elif args.corpus == "orlib-mknap1":
        artifacts = run_orlib_mknap1(
            output_dir=Path(args.output_dir),
            sdk_path=Path(args.sdk_path) if args.sdk_path else None,
            base_url=args.base_url,
            api_key=args.api_key,
            execute_api=args.execute_api,
            limit=args.limit,
            start_index=args.start_index,
            append=args.append,
            policy_tier=args.policy_tier,
            timeout=args.timeout,
            node_limit=args.node_limit,
        )
    else:
        artifacts = run_satlib_uf20(
            output_dir=Path(args.output_dir),
            sdk_path=Path(args.sdk_path) if args.sdk_path else None,
            base_url=args.base_url,
            api_key=args.api_key,
            execute_api=args.execute_api,
            limit=args.limit,
            start_index=args.start_index,
            append=args.append,
            policy_tier=args.policy_tier,
            timeout=args.timeout,
        )
    for label, path in artifacts.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
