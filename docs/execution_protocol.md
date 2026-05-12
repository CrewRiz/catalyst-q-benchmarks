# Execution Protocol

## Raw Result Envelope

Every benchmark run should append one JSON object per line to `results/raw/<campaign>.jsonl`.

Required fields:

- `suite_id`: suite id from `benchmarks/suites.json`.
- `instance_id`: stable instance name.
- `instance_sha256`: checksum of the exact input file or generated instance descriptor.
- `solver_id`: `catalyst-q`, `gurobi`, `scip`, `ortools-cpsat`, `kissat`, `open-wbo`, etc.
- `solver_version`: exact version or commit.
- `command`: command or API request descriptor with secrets removed.
- `seed`: integer seed or null.
- `timeout_s`: configured timeout.
- `runtime_s`: measured wall-clock runtime.
- `status`: `optimal`, `feasible`, `infeasible`, `unknown`, `timeout`, or `error`.
- `objective`: numeric objective where applicable.
- `hardware`: CPU, memory, operating system, and cloud instance metadata.
- `validator`: suite-specific validation result.

## Benchmark Budgets

Use fixed budgets so charts are interpretable:

- Smoke: 10 seconds per instance.
- Interactive developer: 60 seconds per instance.
- Production quick pass: 10 minutes per instance.
- Research pass: 1 hour per instance.

## Reporting

Publish three views:

- Developer view: install, run, validate, cost.
- Researcher view: raw data, validators, exact protocol.
- Investor view: cost per valid solution, time-to-good-enough, market workflow mapping.

