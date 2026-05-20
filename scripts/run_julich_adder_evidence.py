#!/usr/bin/env python3
from __future__ import annotations

import argparse

from catalyst_q_benchmarks.julich_adder import write_julich_adder_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Catalyst-Q Jülich adder evidence campaign.")
    parser.add_argument("--output-dir", default="results/julich_adder")
    parser.add_argument(
        "--register-bits",
        action="append",
        type=int,
        default=None,
        help="Register width to include. May be repeated. Defaults to 25, 32, 64, 128, 256, 512.",
    )
    args = parser.parse_args()
    widths = tuple(args.register_bits) if args.register_bits else (25, 32, 64, 128, 256, 512)
    artifacts = write_julich_adder_artifacts(args.output_dir, ladder_register_bits=widths)
    for label, path in artifacts.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
