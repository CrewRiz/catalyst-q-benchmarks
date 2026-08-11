# Founder Benchmark Playbook

Date: 2026-06-18

This playbook turns the Catalyst-Q quantum benchmark evidence into a founder
operating plan. It is written for public-safe use: measured benchmark evidence
is in scope; implementation details are out of scope.

## Positioning

Use this sentence first:

> Catalyst-Q is a virtual quantum execution backend/simulator with public
> benchmark evidence under review on Metriq, plus QED-C and SuperMarQ
> reproduction artifacts.

Avoid stronger public claims until independent reviewers and upstream
maintainers have accepted the relevant artifacts.

## Current Evidence Anchor

- Metriq: canonical submission under review in unitaryfoundation/metriq-data#459.
- QED-C: Level 1-3 reproduction packet with four families at 1.000000 mean
  fidelity and Grover's Search at 0.998869.
- SuperMarQ: GHZ-4 at 0.999600, GHZ-6 at 0.998975, Mermin-Bell-4 at 1.000000,
  and Mermin-Bell-6 at 1.000000.
- Repository: this benchmark evidence repo contains public-safe artifacts and
  tests that guard the packet's claim boundary.

## 72-Hour Plan

1. Freeze the public evidence.
   - Keep Metriq #459 as the canonical public review thread.
   - Keep the evidence packet PR narrow and conservative.
   - Do not add implementation details to public review comments.

2. Prepare diligence conversations.
   - Use `docs/technical_diligence_packet_2026_06_18.md` as the one-page
     reviewer brief.
   - Ask reviewers to evaluate benchmark validity, category fit, and scoring
     interpretation.
   - Do not ask reviewers to validate private architecture from public material.

3. Start private outreach.
   - Target quantum benchmarking researchers, quantum software leads, and
     simulation/HPC skeptics.
   - Ask for a 30-minute technical review, not an endorsement.
   - Offer the public evidence packet first; reserve deeper details for a
     private review process.

## 30-Day Plan

| Week | Objective | Output |
|---|---|---|
| 1 | Defend the evidence | Respond to Metriq review, keep labels/source metadata tidy, and capture reviewer questions. |
| 2 | Reproduce across benchmark families | Add clean QED-C, SuperMarQ, and MQT Bench runs where practical. |
| 3 | Convert interest into diligence | Run private technical reviews with labs, platform teams, and investors. |
| 4 | Turn signal into design partners | Secure 2-3 scoped pilot conversations around simulation, benchmark execution, or optimization workloads. |

## Outreach Ask

Use a narrow ask:

> We have public benchmark evidence for Catalyst-Q as a virtual quantum execution
> backend/simulator. I am looking for technical reviewers who can pressure-test
> the benchmark interpretation and help identify the next reproduction targets.

Do not ask for blanket validation of the company. Ask for review of specific
benchmark artifacts.

## Founder Guardrails

- Be loud about the evidence, quiet about the mechanism.
- Say "under review" until upstream acceptance.
- Say "virtual backend/simulator" unless a reviewer explicitly asks about
  taxonomy.
- Do not introduce alternate public taxonomy labels until category-fit review
  supports them.
- Lead with reproducible artifacts, not theory.
- Keep all charts backed by committed source data.
- Treat every skeptical question as useful diligence input.

## June 2026 Reporting Basis

The operating posture in this playbook follows current public benchmark norms:

- Metriq's 2026 platform is built around reproducible execution, transparent
  provenance, public dataset review, and constructive community review.
- Metriq encourages direct result contributions through the metriq-gym upload
  workflow, with ibm_torino used as a normalization anchor for the score scale.
- Mature benchmark organizations separate submitted or estimated results from
  accepted/compliant results, require clear comparison basis, and require enough
  context for readers to understand category fit.

Public references:

- Metriq 2026 platform release: https://unitary.foundation/posts/2026_metriq_platform/
- Metriq site and FAQ: https://metriq.info/
- Metriq-gym benchmark docs: https://unitaryfoundation.github.io/metriq-gym/benchmarks/overview/
- SPEC Fair Use Rules: https://www.spec.org/products/fairuse/
- MLCommons inference submission guide: https://docs.mlcommons.org/inference/submission/

## Escalation Trigger

Move from quiet technical outreach to broader public distribution only after at
least one of the following happens:

- Metriq maintainers accept or materially engage the canonical submission.
- An independent reviewer reproduces or validates the benchmark interpretation.
- A design partner requests a private benchmark evaluation against their own
  workload.

Keep the public announcement draft unpublished until one of those triggers is
met or the founder explicitly approves a lower-key "request for review" post.
