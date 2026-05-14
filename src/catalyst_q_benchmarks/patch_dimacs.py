import sys

target = "/Users/ghostmesh/catalyst-mcp/catalyst-q-benchmarks/src/catalyst_q_benchmarks/official_corpora.py"
with open(target, "r") as f:
    content = f.read()

# 1. Add URL constants
new_urls = """TSPLIB95_URLS = [
    "https://raw.githubusercontent.com/mastqe/tsplib/master/ulysses16.tsp",
    "https://raw.githubusercontent.com/mastqe/tsplib/master/ulysses22.tsp",
    "https://raw.githubusercontent.com/mastqe/tsplib/master/att48.tsp",
]
DIMACS_GSET_URLS = [
    "https://web.stanford.edu/~yyye/yyye/Gset/G1",
    "https://web.stanford.edu/~yyye/yyye/Gset/G2",
    "https://web.stanford.edu/~yyye/yyye/Gset/G3",
]"""
content = content.replace("TSPLIB95_URLS = [\n    \"https://raw.githubusercontent.com/mastqe/tsplib/master/ulysses16.tsp\",\n    \"https://raw.githubusercontent.com/mastqe/tsplib/master/ulysses22.tsp\",\n    \"https://raw.githubusercontent.com/mastqe/tsplib/master/att48.tsp\",\n]", new_urls)

# 2. Add MaxCutProblem to _load_sdk if not there
if "MaxCutProblem" not in content.split("def _load_sdk")[1].split("return locals()")[0]:
    content = content.replace("from catalyst_q import CatalystQClient, MultidimensionalKnapsackProblem, RainProtocolKey, SATProblem, TSPProblem", "from catalyst_q import CatalystQClient, MultidimensionalKnapsackProblem, RainProtocolKey, SATProblem, TSPProblem, MaxCutProblem")
    content = content.replace("\"TSPProblem\": TSPProblem,", "\"TSPProblem\": TSPProblem,\n        \"MaxCutProblem\": MaxCutProblem,")

# 3. Add DIMACS runner code
dimacs_code = """
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

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
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
    return "\\n".join(lines) + "\\n"

def main("""

content = content.replace("def main(", dimacs_code)

# 4. Update main
old_main = """    parser.add_argument("--corpus", choices=["satlib-uf20", "orlib-mknap1", "tsplib95"], default="satlib-uf20")"""
new_main = """    parser.add_argument("--corpus", choices=["satlib-uf20", "orlib-mknap1", "tsplib95", "dimacs-maxcut"], default="satlib-uf20")"""
content = content.replace(old_main, new_main)

old_run = """    if args.corpus == "tsplib95":"""
new_run = """    if args.corpus == "dimacs-maxcut":
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
    elif args.corpus == "tsplib95":"""
content = content.replace(old_run, new_run)

with open(target, "w") as f:
    f.write(content)
print("DIMACS patch applied successfully.")
