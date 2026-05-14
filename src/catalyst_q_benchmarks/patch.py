import sys

target = "/Users/ghostmesh/catalyst-mcp/catalyst-q-benchmarks/src/catalyst_q_benchmarks/official_corpora.py"
with open(target, "r") as f:
    content = f.read()

# 1. Add import math
if "import math" not in content:
    content = content.replace("import json\n", "import json\nimport math\n")

# 2. Update _load_sdk
old_sdk = """        from catalyst_q import CatalystQClient, MultidimensionalKnapsackProblem, RainProtocolKey, SATProblem"""
new_sdk = """        from catalyst_q import CatalystQClient, MultidimensionalKnapsackProblem, RainProtocolKey, SATProblem, TSPProblem"""
content = content.replace(old_sdk, new_sdk)

old_return = """        "SATProblem": SATProblem,
        "UsagePolicy": UsagePolicy,"""
new_return = """        "SATProblem": SATProblem,
        "TSPProblem": TSPProblem,
        "UsagePolicy": UsagePolicy,"""
content = content.replace(old_return, new_return)

# 3. Insert TSPLIB code before def main
tsplib_code = """
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

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
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
    return "\\n".join(lines) + "\\n"

def main("""

content = content.replace("def main(", tsplib_code)

# 4. Update def main
old_main = """    parser.add_argument("--corpus", choices=["satlib-uf20", "orlib-mknap1"], default="satlib-uf20")"""
new_main = """    parser.add_argument("--corpus", choices=["satlib-uf20", "orlib-mknap1", "tsplib95"], default="satlib-uf20")"""
content = content.replace(old_main, new_main)

old_run = """    if args.corpus == "orlib-mknap1":
        artifacts = run_orlib_mknap1(
            output_dir=Path(args.output_dir),"""
new_run = """    if args.corpus == "tsplib95":
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
            output_dir=Path(args.output_dir),"""
content = content.replace(old_run, new_run)

with open(target, "w") as f:
    f.write(content)
print("Patch applied successfully.")
