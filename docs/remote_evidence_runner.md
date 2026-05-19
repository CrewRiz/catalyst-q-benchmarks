# Remote Evidence Runner

The full benchmark/evidence stack should not live on a small laptop. The local
machine should run the lean harness and trigger remote campaigns.

## Worker Role

Cloudflare Workers are the primary Catalyst-Q execution fabric. RainProtocol
state-in-payload requests can be split into deterministic nonlinear shards,
routed across Workers and Durable Objects, tracked through Workflows/Queues, and
recombined without putting the transient solver state in a database.

The only part that should stay outside a single monolithic Worker is the
competitor baseline stack: native SCIP/Gurobi/Concorde/Qiskit/D-Wave-style
campaigns used for third-party evidence. Those runs are heavy, license-sensitive,
and are better handled by GitHub Actions, Cloudflare Containers, or dedicated
runners, with their artifacts published back to R2.

## Recommended Split

- Local laptop: use `requirements/benchmark-core.txt` for tests, manifests,
  validators, and API smoke evidence.
- Catalyst-Q API: run on Cloudflare Workers at
  `https://api.strategic-innovations.ai/v3turbo` using RainProtocol nonlinear
  sharding, Durable Objects, Queues, Workflows, Analytics Engine, and R2.
- GitHub Actions, Cloudflare Containers, or a rented runner: use
  `environment.benchmark.yml` for the external competitor solver stack and
  scheduled evidence refreshes.
- Cloudflare R2: store generated JSON, Markdown, SVG charts, raw logs, and
  compressed benchmark artifacts.
- Cloudflare Worker: serve `https://catalyst-q-sdk.strategic-innovations.ai`,
  `/benchmarks/public/*`, docs, pricing pages, SDK packages, and API metadata
  from R2 without exposing proprietary internals.
- Cloudflare Workflows or Queues: orchestrate multi-step evidence jobs, record
  state, and trigger external runners.
- Cloudflare Containers: future option for hosted benchmark workers when the
  account has Containers enabled and the campaign needs native binaries.

## Cloudflare References

- Workers limits: https://developers.cloudflare.com/workers/platform/limits/
- R2 storage and pricing: https://developers.cloudflare.com/r2/pricing/
- Containers overview: https://developers.cloudflare.com/containers/
- Workflows overview: https://www.cloudflare.com/developer-platform/products/workflows/

## Local Setup

```bash
python3 -m venv .venv-core
.venv-core/bin/python -m pip install -U pip
.venv-core/bin/python -m pip install -e . -r requirements/benchmark-core.txt
.venv-core/bin/python -m pytest tests -q
```

## Remote Setup

Run the `Catalyst-Q full evidence` GitHub Actions workflow manually, or let the
weekly schedule refresh the artifact. The workflow installs the remote profile,
runs the harness, uploads a GitHub artifact, and publishes the latest evidence
files to R2 when these repository settings exist:

- Secret `CATALYST_Q_API_KEY`, optional for paid/live API checks.
- Secret `CLOUDFLARE_API_TOKEN`, required for R2 upload.
- Secret `CLOUDFLARE_ACCOUNT_ID`, required for R2 upload.
- Variable `CATALYST_Q_R2_BUCKET`, the bucket that serves public evidence.

## Claim Discipline

Remote execution does not change the claims policy. Public claims still require
raw solver outputs, checksums, solver versions, hardware metadata, validators,
and generated charts from the same artifacts.
