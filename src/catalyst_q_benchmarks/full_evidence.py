from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import shutil
import subprocess
import sys
import time
import tempfile
from itertools import permutations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .sdk_campaign import exact_maxcut, exact_qubo

PUBLIC_SOURCES = {
    "biq_mac": "https://biqmac.aau.at/biqmaclib.html",
    "tsplib": "https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/index.html",
    "miplib": "https://miplib.zib.de/",
    "qplib": "https://qplib.zib.de/",
    "or_library": "https://people.brunel.ac.uk/~mastjjb/jeb/orlib/mknapinfo.html",
    "sat_competition": "https://satcompetition.github.io/",
    "maxsat_evaluation": "https://maxsat-evaluations.github.io/",
    "scip": "https://scipopt.org/",
    "highs": "https://highs.dev/",
    "gurobi": "https://www.gurobi.com/solutions/",
}

SOURCE_LABELS = {
    "biq_mac": "Biq Mac Library",
    "tsplib": "TSPLIB95",
    "miplib": "MIPLIB",
    "qplib": "QPLIB",
    "or_library": "OR-Library",
    "sat_competition": "SAT Competition",
    "maxsat_evaluation": "MaxSAT Evaluation",
    "scip": "SCIP Optimization Suite",
    "highs": "HiGHS",
    "gurobi": "Gurobi Optimizer",
}


def build_full_evidence_package(
    output_dir: Path,
    sdk_path: Optional[Path] = None,
    monorepo_root: Optional[Path] = None,
    high_qubit_artifact: Optional[Path] = None,
    base_url: str = "https://api.strategic-innovations.ai/v3turbo",
    api_key: Optional[str] = None,
    execute_api: bool = False,
    run_external: bool = False,
    run_quantum_tests: bool = False,
    timeout: float = 30.0,
) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    sdk = _load_sdk(sdk_path)
    records = _baseline_records()
    sdk_records = _sdk_route_records(sdk, base_url=base_url, api_key=api_key, execute_api=execute_api, timeout=timeout)
    records.extend(sdk_records)
    if run_external:
        records.extend(_external_solver_records(timeout=timeout))
    quantum_evidence = _run_quantum_evidence(monorepo_root, timeout=timeout) if run_quantum_tests else []
    high_qubit_evidence = _load_high_qubit_evidence(output_dir, high_qubit_artifact)
    package = _package(records, execute_api, high_qubit_evidence)
    package["quantum_simulator_evidence"] = quantum_evidence
    package["high_qubit_exactness_evidence"] = high_qubit_evidence
    package["summary"]["quantum_test_commands_passed"] = sum(1 for row in quantum_evidence if row["status"] == "passed")
    package["summary"]["quantum_test_commands_total"] = len(quantum_evidence)

    json_path = output_dir / "full_evidence_package.json"
    markdown_path = output_dir / "full_evidence_package.md"
    chart_path = output_dir / "full_evidence_scorecard.svg"
    json_path.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_markdown(package), encoding="utf-8")
    chart_path.write_text(_render_scorecard_svg(package), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path), "chart_svg": str(chart_path)}


def _baseline_records() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    sat_clauses = [[1, -2, 3], [-1, 2], [2, 3], [-3, 4], [-1, -4], [1, 4]]
    records.append(_record("sat_smoke_4", "SAT", "exact-enumeration-reference", exact_sat(sat_clauses, 4), "optimal"))
    records.append(_record("sat_smoke_4", "SAT", "majority-literal-baseline", majority_sat(sat_clauses, 4), "feasible"))

    tsp_distances = _euclidean_tsp_distances([(0, 0), (2, 8), (3, 3), (8, 7), (9, 1), (12, 5), (14, 0), (15, 8)])
    records.append(_record("tsplib_style_8", "TSP", "exact-enumeration-reference", exact_tsp(tsp_distances), "optimal"))
    records.append(_record("tsplib_style_8", "TSP", "nearest-neighbor-2opt-baseline", nearest_neighbor_two_opt(tsp_distances), "feasible"))

    weights = [10, 20, 30, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    values = [60, 100, 120, 11, 13, 20, 21, 31, 32, 40, 45, 47]
    records.append(_record("orlib_knapsack_12", "Knapsack", "exact-dp-reference", exact_knapsack(weights, values, 50), "optimal"))
    records.append(_record("orlib_knapsack_12", "Knapsack", "density-greedy-baseline", greedy_knapsack(weights, values, 50), "feasible"))

    qubo_matrix = _qubo_matrix()
    qubo_objective, qubo_assignment = exact_qubo(qubo_matrix, 0.0)
    records.append(_record("biqmac_qubo_6", "QUBO", "exact-enumeration-reference", {"objective": qubo_objective, "assignment": qubo_assignment}, "optimal"))
    records.append(_record("biqmac_qubo_6", "QUBO", "single-flip-greedy-baseline", greedy_qubo(qubo_matrix), "feasible"))

    maxcut_edges = _maxcut_edges()
    cut_value, partition = exact_maxcut(maxcut_edges, 6)
    records.append(_record("biqmac_maxcut_6", "Max-Cut", "exact-enumeration-reference", {"objective": cut_value, "assignment": partition, "cut_value": cut_value}, "optimal"))
    records.append(_record("biqmac_maxcut_6", "Max-Cut", "greedy-partition-baseline", greedy_maxcut(maxcut_edges, 6), "feasible"))

    return records


def _sdk_route_records(
    sdk: Dict[str, Any],
    base_url: str,
    api_key: Optional[str],
    execute_api: bool,
    timeout: float,
) -> List[Dict[str, Any]]:
    client = sdk["CatalystQClient"](api_key=api_key, base_url=base_url)
    key = sdk["RainProtocolKey"].create(workflow_id="full-evidence-package", capacity=1024)
    routes = [
        ("sat_smoke_4", "SAT", "prepare_sat", client.prepare_sat(sdk["SATProblem"]([[1, -2, 3], [-1, 2]], 3), rain_key=key, solver_runs_this_month=0)),
        ("tsplib_style_8", "TSP", "prepare_tsp", client.prepare_tsp(sdk["TSPProblem"](_euclidean_tsp_distances([(0, 0), (2, 8), (3, 3), (8, 7), (9, 1), (12, 5), (14, 0), (15, 8)])), rain_key=key, solver_runs_this_month=1)),
        ("orlib_knapsack_12", "Knapsack", "prepare_knapsack", client.prepare_knapsack(sdk["KnapsackProblem"]([10, 20, 30, 5, 7, 11, 13, 17, 19, 23, 29, 31], [60, 100, 120, 11, 13, 20, 21, 31, 32, 40, 45, 47], 50), rain_key=key, solver_runs_this_month=2)),
        ("portfolio_smoke_8", "Portfolio", "prepare_portfolio", client.prepare_portfolio(sdk["PortfolioProblem"]([0.031, 0.044, 0.038, 0.052, 0.027, 0.049, 0.035, 0.041], [[0.01 if i == j else 0.002 for j in range(8)] for i in range(8)], 0.45), rain_key=key, solver_runs_this_month=3)),
        ("biqmac_qubo_6", "QUBO", "prepare_qubo", client.prepare_qubo(sdk["QUBOProblem"](_qubo_matrix()), rain_key=key, solver_runs_this_month=4)),
        ("biqmac_maxcut_6", "Max-Cut", "prepare_maxcut", client.prepare_maxcut(sdk["MaxCutProblem"](_maxcut_edges(), 6), rain_key=key, solver_runs_this_month=5)),
        ("cafa6_dag_optimization_12", "DAG Optimization", "prepare_dag_closure", client.prepare_dag_closure(sdk["MaximumWeightClosureProblem"]([12.5, 8.0, -5.0, 15.0, -10.0, 20.0, -2.5, 7.0, -1.0, 5.0, -8.0, 30.0], [(2, 0), (3, 1), (4, 2), (5, 3), (6, 4), (7, 5), (8, 2), (9, 3), (10, 8), (11, 6), (11, 7)], 10.0), rain_key=key, solver_runs_this_month=6)),
    ]
    records: List[Dict[str, Any]] = []
    for instance_id, domain, command, prepared in routes:
        started = time.perf_counter()
        validator: Dict[str, Any] = {
            "valid": True,
            "kind": "sdk_request_prepared",
            "route": _route_path(prepared.url),
            "billing_estimate": prepared.json.get("billing_estimate", {}),
        }
        objective = None
        status = "unknown"
        if execute_api and domain in {"QUBO", "Max-Cut"}:
            api_result = sdk["execute_prepared_request"](prepared, timeout=timeout)
            validator["api_execution"] = api_result
            objective = _extract_api_objective(domain, api_result)
            reference = -4.0 if domain == "QUBO" else 9.0
            validator["reference_objective"] = reference
            validator["matches_reference"] = objective is not None and abs(objective - reference) <= 1e-9
            status = "optimal" if validator["matches_reference"] else "feasible"
        records.append(
            _record(
                instance_id,
                domain,
                "catalyst-q-sdk-live" if execute_api and domain in {"QUBO", "Max-Cut"} else "catalyst-q-sdk-request",
                {"objective": objective, "runtime_s": time.perf_counter() - started, "validator": validator},
                status,
                command=command,
            )
        )
    return records


def _load_sdk(sdk_path: Optional[Path]) -> Dict[str, Any]:
    if sdk_path is not None:
        sys.path.insert(0, str(Path(sdk_path).resolve()))
    try:
        from catalyst_q import (
            CatalystQClient,
            KnapsackProblem,
            MaxCutProblem,
            PortfolioProblem,
            QUBOProblem,
            RainProtocolKey,
            SATProblem,
            TSPProblem,
            MaximumWeightClosureProblem,
        )
        from catalyst_rain import execute_prepared_request
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install catalyst-q or pass --sdk-path pointing at sdk/python.") from exc
    return locals()


def exact_sat(clauses: List[List[int]], variables: int) -> Dict[str, Any]:
    best_assignment: List[int] = []
    best_count = -1
    for mask in range(1 << variables):
        assignment = [(mask >> bit) & 1 for bit in range(variables)]
        count = _sat_count(clauses, assignment)
        if count > best_count:
            best_count = count
            best_assignment = assignment
    return {"objective": best_count, "satisfied_clauses": best_count, "total_clauses": len(clauses), "assignment": best_assignment}


def majority_sat(clauses: List[List[int]], variables: int) -> Dict[str, Any]:
    scores = [0] * variables
    for clause in clauses:
        for literal in clause:
            scores[abs(literal) - 1] += 1 if literal > 0 else -1
    assignment = [1 if score >= 0 else 0 for score in scores]
    count = _sat_count(clauses, assignment)
    return {"objective": count, "satisfied_clauses": count, "total_clauses": len(clauses), "assignment": assignment}


def exact_tsp(distances: List[List[float]]) -> Dict[str, Any]:
    n = len(distances)
    best_tour: List[int] = []
    best_distance = float("inf")
    for middle in permutations(range(1, n)):
        tour = [0, *middle]
        distance = _tour_distance(tour, distances)
        if distance < best_distance:
            best_distance = distance
            best_tour = tour
    return {"objective": best_distance, "distance": best_distance, "tour": best_tour}


def nearest_neighbor_two_opt(distances: List[List[float]]) -> Dict[str, Any]:
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
                if _tour_distance(candidate, distances) < _tour_distance(tour, distances):
                    tour = candidate
                    improved = True
    distance = _tour_distance(tour, distances)
    return {"objective": distance, "distance": distance, "tour": tour}


def exact_knapsack(weights: List[int], values: List[int], capacity: int) -> Dict[str, Any]:
    best_value = -1
    best_weight = 0
    best_items: List[int] = []
    for mask in range(1 << len(weights)):
        items = [idx for idx in range(len(weights)) if (mask >> idx) & 1]
        weight = sum(weights[idx] for idx in items)
        value = sum(values[idx] for idx in items)
        if weight <= capacity and value > best_value:
            best_value, best_weight, best_items = value, weight, items
    return {"objective": best_value, "value": best_value, "weight": best_weight, "items": best_items}


def greedy_knapsack(weights: List[int], values: List[int], capacity: int) -> Dict[str, Any]:
    order = sorted(range(len(weights)), key=lambda idx: values[idx] / weights[idx], reverse=True)
    items: List[int] = []
    weight = 0
    value = 0
    for idx in order:
        if weight + weights[idx] <= capacity:
            items.append(idx)
            weight += weights[idx]
            value += values[idx]
    return {"objective": value, "value": value, "weight": weight, "items": items}


def greedy_qubo(matrix: List[List[float]]) -> Dict[str, Any]:
    assignment = [0] * len(matrix)
    best = _qubo_value(matrix, assignment)
    improved = True
    while improved:
        improved = False
        for idx in range(len(matrix)):
            candidate = assignment[:]
            candidate[idx] = 1 - candidate[idx]
            value = _qubo_value(matrix, candidate)
            if value < best:
                assignment, best, improved = candidate, value, True
    return {"objective": best, "assignment": assignment}


def greedy_maxcut(edges: Iterable[Tuple[int, int, float]], nodes: int) -> Dict[str, Any]:
    parsed = list(edges)
    partition = [0] * nodes
    for node in range(nodes):
        zero = partition[:]
        zero[node] = 0
        one = partition[:]
        one[node] = 1
        partition = one if _maxcut_value(parsed, one) > _maxcut_value(parsed, zero) else zero
    value = _maxcut_value(parsed, partition)
    return {"objective": value, "cut_value": value, "assignment": partition}


def _package(records: List[Dict[str, Any]], execute_api: bool, high_qubit_evidence: Dict[str, Any]) -> Dict[str, Any]:
    live = [record for record in records if record["solver_id"] == "catalyst-q-sdk-live"]
    live_matches = [record for record in live if record["validator"].get("matches_reference") is True]
    heuristic_wins = _heuristic_wins(records)
    coverage = {record["validator"].get("route") for record in records if record["solver_id"].startswith("catalyst-q-sdk")}
    high_qubit_summary = high_qubit_evidence.get("summary", {}) if high_qubit_evidence.get("available") else {}
    claims = _claim_ledger(records, heuristic_wins, high_qubit_evidence)
    return {
        "package": "catalyst-q-full-evidence",
        "generated_at": "deterministic-local" if not execute_api else "live-api-run",
        "sources": PUBLIC_SOURCES,
        "source_labels": SOURCE_LABELS,
        "summary": {
            "route_coverage": f"{len(coverage)}/7",
            "live_exact_matches": f"{len(live_matches)}/2",
            "live_heuristic_wins": f"{heuristic_wins}/2",
            "external_solver_runs": 0,
            "external_solver_records": sum(1 for record in records if record["solver_id"] in {"kissat", "cadical", "highs", "scip"}),
            "records": len(records),
            "publishable_claims": sum(1 for claim in claims if claim["status"] == "publishable"),
            "high_qubit_cases": int(high_qubit_summary.get("total_cases", 0)),
            "high_qubit_exact_cases": int(high_qubit_summary.get("exact_cases", 0)),
            "high_qubit_zero_materialization_cases": int(high_qubit_summary.get("zero_materialization_cases", 0)),
            "high_qubit_max_qubits": int(high_qubit_summary.get("max_qubits", 0)),
            "high_qubit_max_gate_count": int(high_qubit_summary.get("max_gate_count", 0)),
        },
        "records": records,
        "claims": claims,
        "external_baselines": _external_baselines(),
        "disclaimer": "No broad NP or SOTA claim is made. Claims are limited to named artifacts and validators.",
    }


def _claim_ledger(records: List[Dict[str, Any]], heuristic_wins: int, high_qubit_evidence: Dict[str, Any]) -> List[Dict[str, str]]:
    claims = [
        {
            "claim": "Catalyst-Q SDK exposes all seven public NP helper routes: SAT, TSP, knapsack/MKP, portfolio, QUBO, Max-Cut, and DAG Optimization.",
            "status": "publishable" if sum(1 for record in records if record["solver_id"].startswith("catalyst-q-sdk")) == 7 else "blocked",
            "evidence": "SDK prepared-request records with route validators.",
        }
    ]
    for domain, objective in [("QUBO", -4.0), ("Max-Cut", 9.0)]:
        matching = [
            record for record in records
            if record["domain"] == domain and record["solver_id"] == "catalyst-q-sdk-live" and record["status"] == "optimal"
        ]
        claims.append(
            {
                "claim": f"Catalyst-Q live SDK/API matches the exact {domain} reference objective {objective} on the bundled smoke instance.",
                "status": "publishable" if matching else "blocked-until-live-api-run",
                "evidence": f"Raw record validator.matches_reference for {domain}.",
            }
        )
    claims.append(
        {
            "claim": "Catalyst-Q live SDK/API beats the included greedy heuristic baselines on the bundled QUBO and Max-Cut smoke instances.",
            "status": "publishable" if heuristic_wins == 2 else "blocked-until-live-api-run",
            "evidence": "QUBO is lower-is-better and Max-Cut is higher-is-better against local heuristic baseline records.",
        }
    )
    high_summary = high_qubit_evidence.get("summary", {}) if high_qubit_evidence.get("available") else {}
    high_total = int(high_summary.get("total_cases", 0))
    high_exact = int(high_summary.get("exact_cases", 0))
    high_zero = int(high_summary.get("zero_materialization_cases", 0))
    high_max_qubits = int(high_summary.get("max_qubits", 0))
    claims.append(
        {
            "claim": (
                "Catalyst-Q compact execution validates exact targeted answers with zero dense state materialization "
                f"across {high_total} high-qubit benchmark cases up to {high_max_qubits} qubits."
            ),
            "status": "publishable" if high_total and high_exact == high_total and high_zero == high_total else "blocked-until-high-qubit-campaign",
            "evidence": "High-qubit exactness artifact summary and per-case validator rows.",
        }
    )
    claims.append(
        {
            "claim": "Catalyst-Q is broadly best-in-class against commercial and academic SOTA solvers.",
            "status": "not-yet-supported",
            "evidence": "Requires full Biq Mac/Gset/QPLIB/TSPLIB/SAT/MaxSAT campaigns against external baselines.",
        }
    )
    return claims


def _external_baselines() -> List[Dict[str, Any]]:
    tools = [
        ("gurobi_cl", "Gurobi", PUBLIC_SOURCES["gurobi"]),
        ("scip", "SCIP", PUBLIC_SOURCES["scip"]),
        ("highs", "HiGHS", PUBLIC_SOURCES["highs"]),
        ("kissat", "Kissat", PUBLIC_SOURCES["sat_competition"]),
        ("cadical", "CaDiCaL", PUBLIC_SOURCES["sat_competition"]),
        ("concorde", "Concorde", PUBLIC_SOURCES["tsplib"]),
        ("LKH", "LKH", PUBLIC_SOURCES["tsplib"]),
    ]
    return [{"tool": binary, "solver": name, "source": source, "available": shutil.which(binary) is not None} for binary, name, source in tools]


def _load_high_qubit_evidence(output_dir: Path, high_qubit_artifact: Optional[Path]) -> Dict[str, Any]:
    path = high_qubit_artifact or output_dir / "high_qubit_exactness" / "high_qubit_exactness.json"
    if not path.exists():
        return {"available": False, "artifact": str(path)}

    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    cases = [
        {
            "id": row.get("id"),
            "suite": row.get("suite"),
            "qubits": row.get("qubits"),
            "gate_count": row.get("gate_count"),
            "metric": row.get("metric"),
            "public_strategy": row.get("public_strategy"),
            "exact": row.get("exact"),
            "materialized_states": row.get("materialized_states"),
            "runtime_s": row.get("runtime_s"),
        }
        for row in data.get("cases", [])
    ]
    return {
        "available": True,
        "artifact": str(path),
        "artifact_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "campaign": data.get("campaign"),
        "claim_scope": data.get("claim_scope"),
        "disclaimer": data.get("disclaimer"),
        "summary": data.get("summary", {}),
        "cases": cases,
    }


def _external_solver_records(timeout: float) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    clauses = [[1, -2, 3], [-1, 2], [2, 3], [-3, 4], [-1, -4], [1, 4]]
    variables = 4
    for solver in ("kissat", "cadical"):
        if shutil.which(solver):
            records.append(_run_sat_solver(solver, clauses, variables, timeout))

    weights = [10, 20, 30, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    values = [60, 100, 120, 11, 13, 20, 21, 31, 32, 40, 45, 47]
    for solver in ("highs", "scip"):
        if shutil.which(solver):
            records.append(_run_knapsack_mip_solver(solver, weights, values, 50, timeout))
    return records


def _run_sat_solver(solver: str, clauses: List[List[int]], variables: int, timeout: float) -> Dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        cnf = Path(tmp) / "sat_smoke_4.cnf"
        cnf.write_text(_dimacs_cnf(clauses, variables), encoding="utf-8")
        started = time.perf_counter()
        proc = subprocess.run([solver, str(cnf)], text=True, capture_output=True, timeout=timeout, check=False)
        runtime = time.perf_counter() - started
    assignment = _parse_sat_assignment(proc.stdout, variables)
    satisfied = _sat_count(clauses, assignment) if assignment else 0
    status = "optimal" if satisfied == len(clauses) and proc.returncode in {0, 10} else "feasible"
    return _record(
        "sat_smoke_4",
        "SAT",
        solver,
        {
            "objective": satisfied,
            "runtime_s": runtime,
            "validator": {
                "valid": satisfied == len(clauses),
                "kind": "external_sat_assignment",
                "returncode": proc.returncode,
                "assignment": assignment,
                "stdout_sha256": hashlib.sha256(proc.stdout.encode("utf-8", errors="replace")).hexdigest(),
            },
        },
        status,
        command=f"{solver} sat_smoke_4.cnf",
    )


def _run_knapsack_mip_solver(solver: str, weights: List[int], values: List[int], capacity: int, timeout: float) -> Dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        lp = Path(tmp) / "orlib_knapsack_12.lp"
        lp.write_text(_knapsack_lp(weights, values, capacity), encoding="utf-8")
        started = time.perf_counter()
        if solver == "highs":
            sol = Path(tmp) / "orlib_knapsack_12.sol"
            proc = subprocess.run([solver, "--model_file", str(lp), "--solution_file", str(sol), "--time_limit", str(timeout)], text=True, capture_output=True, timeout=timeout + 2, check=False)
            objective = _parse_highs_objective(sol.read_text(encoding="utf-8") if sol.exists() else proc.stdout)
        else:
            proc = subprocess.run([solver, "-f", str(lp)], text=True, capture_output=True, timeout=timeout + 2, check=False)
            objective = _parse_scip_objective(proc.stdout)
        runtime = time.perf_counter() - started
    status = "optimal" if objective == 220 else "feasible"
    return _record(
        "orlib_knapsack_12",
        "Knapsack",
        solver,
        {
            "objective": objective,
            "runtime_s": runtime,
            "validator": {
                "valid": objective is not None,
                "kind": "external_mip_objective",
                "returncode": proc.returncode,
                "stdout_sha256": hashlib.sha256(proc.stdout.encode("utf-8", errors="replace")).hexdigest(),
            },
        },
        status,
        command=f"{solver} orlib_knapsack_12.lp",
    )


def _run_quantum_evidence(monorepo_root: Optional[Path], timeout: float) -> List[Dict[str, Any]]:
    root = Path(monorepo_root) if monorepo_root is not None else Path.cwd().parent
    commands = [
        ["python3", "-m", "pytest", "tests/test_quantum_v2.py", "Catalyst-API/tests/test_gates.py", "Catalyst-API/tests/test_universal_gate_set.py", "Catalyst-API/tests/test_simulator.py", "-q"],
        ["python3", "-m", "pytest", "tests/sdk/test_public_benchmark_harness.py", "tests/sdk/test_proof_harness.py", "-q"],
    ]
    rows: List[Dict[str, Any]] = []
    for command in commands:
        started = time.perf_counter()
        proc = subprocess.run(command, cwd=str(root), text=True, capture_output=True, timeout=timeout, check=False)
        rows.append(
            {
                "command": " ".join(command),
                "status": "passed" if proc.returncode == 0 else "failed",
                "returncode": proc.returncode,
                "runtime_s": round(time.perf_counter() - started, 6),
                "stdout_tail": proc.stdout[-1000:],
                "stderr_tail": proc.stderr[-1000:],
                "stdout_sha256": hashlib.sha256(proc.stdout.encode("utf-8", errors="replace")).hexdigest(),
            }
        )
    return rows


def _record(instance_id: str, domain: str, solver_id: str, result: Dict[str, Any], status: str, command: Optional[str] = None) -> Dict[str, Any]:
    validator = result.get("validator", {"valid": True, "kind": "objective_recomputed"})
    return {
        "suite_id": _suite_id(domain),
        "instance_id": instance_id,
        "instance_sha256": _sha256_json({"instance_id": instance_id, "domain": domain}),
        "domain": domain,
        "solver_id": solver_id,
        "solver_version": "0.1.0" if "reference" in solver_id or "baseline" in solver_id else "local-or-hosted",
        "command": command or solver_id,
        "seed": None,
        "timeout_s": 30.0,
        "runtime_s": round(float(result.get("runtime_s", 0.0)), 9),
        "status": status,
        "objective": result.get("objective"),
        "hardware": _hardware(),
        "validator": validator,
    }


def _suite_id(domain: str) -> str:
    return {
        "SAT": "sat_competition_main",
        "TSP": "tsplib95",
        "Knapsack": "or_library_mknap",
        "QUBO": "biq_mac_maxcut_bqp",
        "Max-Cut": "biq_mac_maxcut_bqp",
        "Portfolio": "qplib",
        "DAG Optimization": "catalyst_biocomputation",
    }[domain]


def _render_markdown(package: Dict[str, Any]) -> str:
    lines = [
        "# Catalyst-Q Full Evidence Package",
        "",
        package["disclaimer"],
        "",
        "## Summary",
        "",
        f"- Route coverage: {package['summary']['route_coverage']}",
        f"- Live exact matches: {package['summary']['live_exact_matches']}",
        f"- Live heuristic wins: {package['summary']['live_heuristic_wins']}",
        f"- Records: {package['summary']['records']}",
        f"- Publishable claims: {package['summary']['publishable_claims']}",
        f"- External solver records: {package['summary']['external_solver_records']}",
        f"- Quantum test commands passed: {package['summary']['quantum_test_commands_passed']}/{package['summary']['quantum_test_commands_total']}",
        f"- High-qubit exact cases: {package['summary']['high_qubit_exact_cases']}/{package['summary']['high_qubit_cases']}",
        f"- High-qubit max width: {package['summary']['high_qubit_max_qubits']} qubits",
        "",
        "## Claim Ledger",
        "",
        "| Claim | Status | Evidence |",
        "|---|---|---|",
    ]
    for claim in package["claims"]:
        lines.append(f"| {claim['claim']} | {claim['status']} | {claim['evidence']} |")
    lines.extend(["", "## Results", "", "| Instance | Domain | Solver | Status | Objective |", "|---|---|---|---:|---:|"])
    for record in package["records"]:
        objective = "" if record["objective"] is None else record["objective"]
        lines.append(f"| {record['instance_id']} | {record['domain']} | {record['solver_id']} | {record['status']} | {objective} |")
    if package.get("quantum_simulator_evidence"):
        lines.extend(["", "## Quantum Simulator Evidence", "", "| Command | Status | Runtime seconds |", "|---|---:|---:|"])
        for row in package["quantum_simulator_evidence"]:
            lines.append(f"| `{row['command']}` | {row['status']} | {row['runtime_s']} |")
    high_qubit = package.get("high_qubit_exactness_evidence", {})
    if high_qubit.get("available"):
        lines.extend([
            "",
            "## High-Qubit Exactness Evidence",
            "",
            high_qubit.get("disclaimer", ""),
            "",
            "| Case | Suite | Qubits | Gates | Answer mode | Exact | Materialized states | Runtime seconds |",
            "|---|---|---:|---:|---|---:|---:|---:|",
        ])
        for row in high_qubit.get("cases", []):
            lines.append(
                f"| {row['id']} | {row['suite']} | {row['qubits']} | {row['gate_count']} | "
                f"{row['public_strategy']} | {row['exact']} | {row['materialized_states']} | {row['runtime_s']} |"
            )
        lines.extend([
            "",
            f"Artifact SHA-256: `{high_qubit.get('artifact_sha256')}`",
        ])
    lines.extend(["", "## External SOTA Baseline Readiness", "", "| Solver | Tool | Available Here | Source |", "|---|---|---:|---|"])
    for solver in package["external_baselines"]:
        lines.append(f"| {solver['solver']} | `{solver['tool']}` | {solver['available']} | {solver['source']} |")
    lines.extend(["", "## Sources", ""])
    for key, url in package["sources"].items():
        lines.append(f"- {key}: {url}")
    return "\n".join(lines) + "\n"


def _render_scorecard_svg(package: Dict[str, Any]) -> str:
    metrics = [
        ("Route coverage", int(package["summary"]["route_coverage"].split("/")[0]), 7),
        ("Live exact matches", int(package["summary"]["live_exact_matches"].split("/")[0]), 2),
        ("Heuristic wins", int(package["summary"]["live_heuristic_wins"].split("/")[0]), 2),
        ("External solver records", int(package["summary"]["external_solver_records"]), 4),
        ("Quantum test commands", int(package["summary"]["quantum_test_commands_passed"]), max(1, int(package["summary"]["quantum_test_commands_total"]))),
        ("High-qubit exact cases", int(package["summary"]["high_qubit_exact_cases"]), max(1, int(package["summary"]["high_qubit_cases"]))),
        ("Publishable claims", int(package["summary"]["publishable_claims"]), len(package["claims"])),
    ]
    width = 900
    height = 340
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="36" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#111827">Catalyst-Q Evidence Scorecard</text>',
    ]
    y = 78
    for label, value, total in metrics:
        bar = int(560 * value / max(1, total))
        lines.append(f'<text x="24" y="{y + 18}" font-family="Arial, sans-serif" font-size="15" fill="#111827">{label}</text>')
        lines.append(f'<rect x="220" y="{y}" width="560" height="24" fill="#e5e7eb"/>')
        lines.append(f'<rect x="220" y="{y}" width="{bar}" height="24" fill="#0f6b57"/>')
        lines.append(f'<text x="794" y="{y + 18}" font-family="Arial, sans-serif" font-size="14" fill="#111827">{value}/{total}</text>')
        y += 42
    lines.append("</svg>")
    return "\n".join(lines)


def _sat_count(clauses: List[List[int]], assignment: List[int]) -> int:
    count = 0
    for clause in clauses:
        if any((literal > 0 and assignment[abs(literal) - 1]) or (literal < 0 and not assignment[abs(literal) - 1]) for literal in clause):
            count += 1
    return count


def _euclidean_tsp_distances(points: Sequence[Tuple[int, int]]) -> List[List[int]]:
    return [[round(math.hypot(x1 - x0, y1 - y0)) for x1, y1 in points] for x0, y0 in points]


def _tour_distance(tour: List[int], distances: List[List[float]]) -> float:
    return sum(distances[tour[idx]][tour[(idx + 1) % len(tour)]] for idx in range(len(tour)))


def _qubo_matrix() -> List[List[float]]:
    return [
        [1.0, -2.0, 0.5, 0.0, -1.0, 0.25],
        [-2.0, 1.5, -1.0, 0.75, 0.0, -0.5],
        [0.5, -1.0, 2.0, -1.25, 0.5, 0.0],
        [0.0, 0.75, -1.25, 1.0, -0.75, 1.0],
        [-1.0, 0.0, 0.5, -0.75, 1.75, -1.5],
        [0.25, -0.5, 0.0, 1.0, -1.5, 1.25],
    ]


def _maxcut_edges() -> List[Tuple[int, int, float]]:
    return [(0, 1, 1.0), (0, 2, 1.5), (1, 2, 0.75), (1, 3, 2.0), (2, 4, 1.25), (3, 4, 1.0), (3, 5, 1.75), (4, 5, 0.5), (0, 5, 1.0)]


def _qubo_value(matrix: List[List[float]], assignment: List[int]) -> float:
    return sum(matrix[row][col] * assignment[row] * assignment[col] for row in range(len(assignment)) for col in range(len(assignment)))


def _maxcut_value(edges: Iterable[Tuple[int, int, float]], partition: List[int]) -> float:
    return sum(weight for u, v, weight in edges if partition[u] != partition[v])


def _extract_api_objective(domain: str, api_result: Dict[str, Any]) -> Optional[float]:
    payload = api_result.get("json")
    if not isinstance(payload, dict):
        return None
    result = payload.get("result", payload)
    if not isinstance(result, dict):
        return None
    key = "objective" if domain == "QUBO" else "cut_value"
    value = result.get(key)
    return float(value) if isinstance(value, (int, float)) else None


def _dimacs_cnf(clauses: List[List[int]], variables: int) -> str:
    lines = [f"p cnf {variables} {len(clauses)}"]
    for clause in clauses:
        lines.append(" ".join(str(literal) for literal in clause) + " 0")
    return "\n".join(lines) + "\n"


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


def _knapsack_lp(weights: List[int], values: List[int], capacity: int) -> str:
    terms = " + ".join(f"{value} x{idx}" for idx, value in enumerate(values))
    cap = " + ".join(f"{weight} x{idx}" for idx, weight in enumerate(weights))
    variables = " ".join(f"x{idx}" for idx in range(len(weights)))
    return f"Maximize\n obj: {terms}\nSubject To\n cap: {cap} <= {capacity}\nBinary\n {variables}\nEnd\n"


def _parse_highs_objective(output: str) -> Optional[float]:
    match = re.search(r"Objective\s+([-+0-9.]+)", output)
    return float(match.group(1)) if match else None


def _parse_scip_objective(output: str) -> Optional[float]:
    match = re.search(r"Primal Bound\s*:\s*([-+0-9.eE]+)", output)
    return float(match.group(1)) if match else None


def _heuristic_wins(records: List[Dict[str, Any]]) -> int:
    by_domain = {}
    for record in records:
        by_domain.setdefault(record["domain"], []).append(record)
    wins = 0
    qubo_live = _objective(by_domain.get("QUBO", []), "catalyst-q-sdk-live")
    qubo_greedy = _objective(by_domain.get("QUBO", []), "single-flip-greedy-baseline")
    if qubo_live is not None and qubo_greedy is not None and qubo_live < qubo_greedy:
        wins += 1
    cut_live = _objective(by_domain.get("Max-Cut", []), "catalyst-q-sdk-live")
    cut_greedy = _objective(by_domain.get("Max-Cut", []), "greedy-partition-baseline")
    if cut_live is not None and cut_greedy is not None and cut_live > cut_greedy:
        wins += 1
    return wins


def _objective(records: List[Dict[str, Any]], solver_id: str) -> Optional[float]:
    for record in records:
        if record["solver_id"] == solver_id and isinstance(record["objective"], (int, float)):
            return float(record["objective"])
    return None


def _route_path(url: str) -> str:
    marker = "/v3turbo"
    return url[url.index(marker) :] if marker in url else url


def _sha256_json(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _hardware() -> Dict[str, str]:
    return {"platform": platform.platform(), "python": platform.python_version(), "machine": platform.machine()}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build Catalyst-Q full evidence package.")
    parser.add_argument("--output-dir", default="results")
    parser.add_argument("--sdk-path", default=None)
    parser.add_argument("--base-url", default="https://api.strategic-innovations.ai/v3turbo")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--execute-api", action="store_true")
    parser.add_argument("--run-external", action="store_true")
    parser.add_argument("--run-quantum-tests", action="store_true")
    parser.add_argument("--monorepo-root", default=None)
    parser.add_argument("--high-qubit-artifact", default=None)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)
    artifacts = build_full_evidence_package(
        output_dir=Path(args.output_dir),
        sdk_path=Path(args.sdk_path) if args.sdk_path else None,
        monorepo_root=Path(args.monorepo_root) if args.monorepo_root else None,
        high_qubit_artifact=Path(args.high_qubit_artifact) if args.high_qubit_artifact else None,
        base_url=args.base_url,
        api_key=args.api_key,
        execute_api=args.execute_api,
        run_external=args.run_external,
        run_quantum_tests=args.run_quantum_tests,
        timeout=args.timeout,
    )
    print(f"Wrote {artifacts['json']}")
    print(f"Wrote {artifacts['markdown']}")
    print(f"Wrote {artifacts['chart_svg']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
