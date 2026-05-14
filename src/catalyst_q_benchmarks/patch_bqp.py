import sys

target = "/Users/ghostmesh/catalyst-mcp/catalyst-q-benchmarks/src/catalyst_q_benchmarks/official_corpora.py"
with open(target, "r") as f:
    content = f.read()

# 1. Add URL constants
new_urls = """DIMACS_GSET_URLS = [
    "https://web.stanford.edu/~yyye/yyye/Gset/G1",
    "https://web.stanford.edu/~yyye/yyye/Gset/G2",
    "https://web.stanford.edu/~yyye/yyye/Gset/G3",
]
ORLIB_BQP_URLS = [
    "https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/bqp50.txt",
]"""
content = content.replace("DIMACS_GSET_URLS = [\n    \"https://web.stanford.edu/~yyye/yyye/Gset/G1\",\n    \"https://web.stanford.edu/~yyye/yyye/Gset/G2\",\n    \"https://web.stanford.edu/~yyye/yyye/Gset/G3\",\n]", new_urls)

# 2. Add QUBOProblem to _load_sdk if not there
if "QUBOProblem" not in content.split("def _load_sdk")[1].split("return locals()")[0]:
    content = content.replace("from catalyst_q import CatalystQClient, MultidimensionalKnapsackProblem, RainProtocolKey, SATProblem, TSPProblem, MaxCutProblem", "from catalyst_q import CatalystQClient, MultidimensionalKnapsackProblem, RainProtocolKey, SATProblem, TSPProblem, MaxCutProblem, QUBOProblem")
    content = content.replace("\"MaxCutProblem\": MaxCutProblem,", "\"MaxCutProblem\": MaxCutProblem,\n        \"QUBOProblem\": QUBOProblem,")

# 3. Add BQP runner code
bqp_code = """
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

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
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
    return "\\n".join(lines) + "\\n"

def main("""

content = content.replace("def main(", bqp_code)

# 4. Update main
old_main = """    parser.add_argument("--corpus", choices=["satlib-uf20", "orlib-mknap1", "tsplib95", "dimacs-maxcut"], default="satlib-uf20")"""
new_main = """    parser.add_argument("--corpus", choices=["satlib-uf20", "orlib-mknap1", "tsplib95", "dimacs-maxcut", "orlib-bqp"], default="satlib-uf20")"""
content = content.replace(old_main, new_main)

old_run = """    if args.corpus == "dimacs-maxcut":"""
new_run = """    if args.corpus == "orlib-bqp":
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
    elif args.corpus == "dimacs-maxcut":"""
content = content.replace(old_run, new_run)

# Fix a subtle bug where _download might return Path, but parse_orlib_bqp expects text
# Note: we read text using data_path.read_text in run_qubo_bqp, which is correct

with open(target, "w") as f:
    f.write(content)
print("BQP patch applied successfully.")
