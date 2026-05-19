#!/usr/bin/env python3
from __future__ import annotations

import argparse

from catalyst_q_benchmarks.high_qubit_exactness import write_high_qubit_exactness_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Catalyst-Q high-qubit exactness evidence campaign.")
    parser.add_argument("--output-dir", default="results/high_qubit_exactness")
    parser.add_argument("--case", action="append", default=None, help="Run only the named case. May be repeated.")
    args = parser.parse_args()
    artifacts = write_high_qubit_exactness_artifacts(args.output_dir, case_filter=args.case)
    for label, path in artifacts.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
