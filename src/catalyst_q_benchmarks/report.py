from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .manifest import load_manifest


def build_readiness_report(manifest: Optional[Dict[str, Any]] = None) -> str:
    data = manifest or load_manifest()
    suites = data["suites"]
    tier_1 = [suite for suite in suites if suite["priority"] == "tier_1"]
    tier_2 = [suite for suite in suites if suite["priority"] == "tier_2"]

    lines = [
        "# Catalyst-Q Evidence Readiness",
        "",
        "This report is generated from `benchmarks/suites.json`. It is a readiness report, not a solver superiority claim.",
        "",
        "## Summary",
        "",
        f"- Suites tracked: {len(suites)}",
        f"- Tier-one suites: {len(tier_1)}",
        f"- Tier-two suites: {len(tier_2)}",
        f"- Claim policy: {data['claim_policy']}",
        "",
        "## Suites",
        "",
        "| Suite | Domain | Priority | Baselines | Claim target |",
        "|---|---|---:|---|---|",
    ]
    for suite in suites:
        lines.append(
            "| {source} | {domain} | {priority} | {baselines} | {claim_target} |".format(
                source=suite["source"],
                domain=suite["domain"],
                priority=suite["priority"],
                baselines=", ".join(suite["baselines"]),
                claim_target=suite["claim_target"],
            )
        )

    lines.extend(
        [
            "",
            "## Next Evidence Required",
            "",
            "- Add raw JSONL runs for Catalyst-Q and every baseline.",
            "- Commit validator outputs and instance checksums.",
            "- Generate objective, gap, runtime, and cost charts from raw artifacts.",
            "- Promote claims only through the claims ladder in `docs/claims_policy.md`.",
            "",
        ]
    )
    return "\n".join(lines)


def build_readiness_svg(manifest: Optional[Dict[str, Any]] = None) -> str:
    data = manifest or load_manifest()
    counts: Dict[str, int] = {}
    for suite in data["suites"]:
        counts[suite["domain"]] = counts.get(suite["domain"], 0) + 1

    width = 900
    row_height = 34
    height = 80 + row_height * len(counts)
    max_count = max(counts.values())
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#111827">Catalyst-Q Evidence Coverage</text>',
    ]
    y = 68
    for domain, count in sorted(counts.items()):
        bar_width = int(560 * count / max_count)
        lines.append(f'<text x="24" y="{y + 20}" font-family="Arial, sans-serif" font-size="14" fill="#111827">{_escape(domain)}</text>')
        lines.append(f'<rect x="250" y="{y + 5}" width="{bar_width}" height="22" fill="#2563eb"/>')
        lines.append(f'<text x="{260 + bar_width}" y="{y + 21}" font-family="Arial, sans-serif" font-size="13" fill="#111827">{count}</text>')
        y += row_height
    lines.append("</svg>")
    return "\n".join(lines)


def write_report(output: Path, chart: Optional[Path] = None) -> None:
    manifest = load_manifest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_readiness_report(manifest), encoding="utf-8")
    if chart is not None:
        chart.parent.mkdir(parents=True, exist_ok=True)
        chart.write_text(build_readiness_svg(manifest), encoding="utf-8")


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Catalyst-Q public evidence readiness reports.")
    parser.add_argument("--output", default="results/evidence_index.md", help="Markdown output path.")
    parser.add_argument("--chart", default="assets/charts/evidence_coverage.svg", help="SVG chart output path.")
    args = parser.parse_args(argv)
    write_report(Path(args.output), Path(args.chart))
    print(f"Wrote {args.output}")
    print(f"Wrote {args.chart}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

