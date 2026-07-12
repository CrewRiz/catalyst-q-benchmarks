"""
quantum_generator.py
====================
Non-Autoregressive Holographic Generator (NAHG) — Phase 1 Prototype
Catalyst-Q / Strategic-Innovations AI, LLC
Travis Crew — July 2026

Demonstrates:
  1. Holographic Vocabulary: 100-concept CPHV Item Memory
  2. Prompt Encoding: variable-length prompt → fixed O(1) Prompt Hypervector (PHV)
  3. QUBO Construction: K output tokens × 100 concepts → Ising Hamiltonian
  4. Solver Dispatch: formats payload for /v3turbo/solve/qubo endpoint
  5. Decode: ground state → output token sequence

Vocabulary restriction rationale (from white_paper.md §4.6):
  Full 50k BPE vocab × K=10 → 500k binary variables → QUBO matrix ~2.5×10^11 entries.
  100-concept vocab × K=10 → 1,000 binary variables → 10^6 entries. Trivially solvable.
  Once the global-collapse generation paradigm is validated here, vocabulary tiling
  strategies extend this to full BPE in Phase 2.
"""

from __future__ import annotations

import os
import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import requests

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

HV_DIM = 10_000          # Hypervector dimensionality (complex polar)
CONCEPT_VOCAB_SIZE = 100  # Phase 1 restriction
DEFAULT_K = 10           # Number of output tokens to generate simultaneously
LAMBDA_CONSTRAINT = 5.0  # Penalty weight for one-hot constraint
ALPHA_SEMANTIC = 1.0     # Weight for prompt resonance energy
BETA_BINDING = 0.5       # Weight for grammatical binding energy

# Catalyst-Q solver endpoint — set via environment variable
QUBO_ENDPOINT = os.getenv(
    "CATALYSTQ_ENDPOINT",
    "https://api.strategic-innovations.ai/v3turbo/solve/qubo"
)
QUBO_API_KEY = os.getenv("CATALYSTQ_API_KEY", "")

# ---------------------------------------------------------------------------
# PHASE 1 CONCEPT VOCABULARY (100 semantic primitives)
# ---------------------------------------------------------------------------
# Drawn from WordNet supersenses: agents, actions, properties, relations,
# domain anchors. These serve as the generative alphabet for Phase 1.

CONCEPT_VOCAB: list[str] = [
    # Agents (0–14)
    "PERSON", "ORGANIZATION", "SYSTEM", "MODEL", "AGENT",
    "RESEARCHER", "MACHINE", "NETWORK", "PROCESSOR", "SOLVER",
    "COMPILER", "GENERATOR", "DECODER", "ENCODER", "OPTIMIZER",
    # Actions (15–34)
    "CREATE", "DESTROY", "MOVE", "COMMUNICATE", "COMPUTE",
    "SOLVE", "ENCODE", "DECODE", "COMPRESS", "EXPAND",
    "BIND", "UNBIND", "SUPERPOSE", "COLLAPSE", "ANNEAL",
    "PREDICT", "GENERATE", "SEARCH", "RETRIEVE", "MINIMIZE",
    # Properties (35–54)
    "LARGE", "SMALL", "FAST", "SLOW", "SAFE",
    "OPTIMAL", "COHERENT", "ORTHOGONAL", "SPARSE", "DENSE",
    "QUANTUM", "CLASSICAL", "HOLOGRAPHIC", "CAUSAL", "STOCHASTIC",
    "DETERMINISTIC", "PARALLEL", "SEQUENTIAL", "LINEAR", "NONLINEAR",
    # Relations (55–69)
    "CAUSE", "PREVENT", "ENABLE", "REQUIRE", "PRODUCE",
    "CONTAIN", "REPRESENT", "TRANSFORM", "APPROXIMATE", "CONVERGE",
    "DIVERGE", "BIND_TO", "SUPERPOSE_WITH", "RESONATE", "INTERFERE",
    # Domain anchors (70–84)
    "LANGUAGE", "MEMORY", "ENERGY", "PROBABILITY", "DISTRIBUTION",
    "VECTOR", "MATRIX", "HYPERVECTOR", "HAMILTONIAN", "QUBO",
    "TOKEN", "SEQUENCE", "CONTEXT", "EMBEDDING", "ATTENTION",
    # Structural / grammatical (85–99)
    "SUBJECT", "VERB", "OBJECT", "MODIFIER", "RELATION",
    "START", "END", "NULL", "UNKNOWN", "PADDING",
    "IS_A", "HAS", "PART_OF", "INSTANCE", "TYPE",
]

assert len(CONCEPT_VOCAB) == CONCEPT_VOCAB_SIZE, (
    f"Vocab size mismatch: {len(CONCEPT_VOCAB)} != {CONCEPT_VOCAB_SIZE}"
)

CONCEPT_INDEX: dict[str, int] = {c: i for i, c in enumerate(CONCEPT_VOCAB)}


# ---------------------------------------------------------------------------
# 1. HOLOGRAPHIC VOCABULARY — CPHV Item Memory
# ---------------------------------------------------------------------------

class ItemMemory:
    """
    Static holographic vocabulary: each concept → fixed orthogonal CPHV.
    Phase angles are seeded deterministically from the concept string, ensuring
    reproducibility across sessions without training.
    """

    def __init__(self, vocab: list[str], dim: int = HV_DIM) -> None:
        self.vocab = vocab
        self.dim = dim
        self._hv: np.ndarray = self._generate_item_memory()

    def _generate_item_memory(self) -> np.ndarray:
        """
        Returns shape (|V|, D) complex128 array.
        Each row is a unit-magnitude complex hypervector (phase-only).
        Seeded by SHA-256 hash of concept string for deterministic reproducibility.
        """
        hv = np.zeros((len(self.vocab), self.dim), dtype=np.complex128)
        for i, concept in enumerate(self.vocab):
            seed = int(hashlib.sha256(concept.encode()).hexdigest(), 16) % (2**32)
            rng = np.random.default_rng(seed)
            phases = rng.uniform(-np.pi, np.pi, self.dim)
            hv[i] = np.exp(1j * phases)
        return hv

    def get(self, concept: str) -> np.ndarray:
        """Return the CPHV for a concept name."""
        idx = CONCEPT_INDEX[concept]
        return self._hv[idx]

    def get_by_idx(self, idx: int) -> np.ndarray:
        return self._hv[idx]

    def nearest(self, query: np.ndarray) -> tuple[str, float]:
        """
        Return the concept with highest phase-coherence to the query vector.
        Similarity = Re(query · hv*) / D  (real part of normalized inner product)
        """
        sims = np.real(self._hv @ query.conj()) / self.dim
        idx = int(np.argmax(sims))
        return self.vocab[idx], float(sims[idx])

    def all_similarities(self, query: np.ndarray) -> np.ndarray:
        """Return similarity of query to all concepts. Shape: (|V|,)"""
        return np.real(self._hv @ query.conj()) / self.dim


# ---------------------------------------------------------------------------
# 2. POSITIONAL HYPERVECTORS
# ---------------------------------------------------------------------------

def make_pos_hv(pos: int, dim: int = HV_DIM, delta: float = 0.01) -> np.ndarray:
    """
    Deterministic positional CPHV using linear phase rotation.
    HV_pos[j] = exp(i * pos * j * delta)
    Distinct positions are approximately orthogonal for large dim.
    """
    j = np.arange(dim, dtype=np.float64)
    phases = pos * j * delta
    return np.exp(1j * phases)


# ---------------------------------------------------------------------------
# 3. PROMPT ENCODING — O(1) Prompt Hypervector
# ---------------------------------------------------------------------------

class PromptEncoder:
    """
    Encodes a variable-length list of concept tokens into a fixed-dimension
    Prompt Hypervector (PHV) via positional binding and superposition.
    Memory footprint: O(1) regardless of prompt length.
    """

    def __init__(self, item_memory: ItemMemory) -> None:
        self.im = item_memory

    def encode(self, prompt_concepts: list[str]) -> np.ndarray:
        """
        prompt_concepts: list of concept names (from CONCEPT_VOCAB)
        Returns: PHV of shape (D,) complex128

        PHV = Σ_p  HV_token_p ⊗ HV_pos_p
        where ⊗ is component-wise complex multiplication (phase binding)
        """
        phv = np.zeros(self.im.dim, dtype=np.complex128)
        for p, concept in enumerate(prompt_concepts):
            hv_tok = self.im.get(concept)
            hv_pos = make_pos_hv(p, self.im.dim)
            phv += hv_tok * hv_pos  # phase binding + superposition
        # Normalize to unit magnitude per component
        mag = np.abs(phv)
        mag[mag == 0] = 1.0
        phv = phv / mag
        return phv

    def decode_at_position(self, phv: np.ndarray, pos: int) -> tuple[str, float]:
        """
        Recover the concept at position `pos` from the PHV via conjugate unbinding.
        Query = PHV ⊗ HV_pos_p*
        """
        hv_pos_conj = make_pos_hv(pos, self.im.dim).conj()
        query = phv * hv_pos_conj
        return self.im.nearest(query)


# ---------------------------------------------------------------------------
# 4. QUBO CONSTRUCTION
# ---------------------------------------------------------------------------

@dataclass
class QUBOPayload:
    """Structured payload for the /v3turbo/solve/qubo endpoint."""
    num_variables: int
    Q: dict[tuple[int, int], float]  # sparse upper-triangular QUBO matrix
    variable_map: dict[int, tuple[int, int]]  # var_idx → (position, concept_idx)
    metadata: dict = field(default_factory=dict)

    def to_api_dict(self) -> dict:
        """Serialize to the format expected by the Catalyst-Q QUBO endpoint."""
        return {
            "num_variables": self.num_variables,
            "Q": [
                {"i": i, "j": j, "value": v}
                for (i, j), v in self.Q.items()
            ],
            "metadata": self.metadata,
        }


def build_qubo(
    phv: np.ndarray,
    item_memory: ItemMemory,
    K: int = DEFAULT_K,
    alpha: float = ALPHA_SEMANTIC,
    beta: float = BETA_BINDING,
    lam: float = LAMBDA_CONSTRAINT,
    affinity_matrix: Optional[np.ndarray] = None,
) -> QUBOPayload:
    """
    Build the QUBO Hamiltonian for generating K output tokens simultaneously.

    Variable encoding:
      var_idx(k, c) = k * CONCEPT_VOCAB_SIZE + c
      x_{k,c} = 1 → concept c selected at output position k

    Energy terms:
      H_semantic  = -alpha * Σ_{k,c} Resonance(k,c) * x_{k,c}
      H_binding   = -beta  * Σ_k Σ_{c1,c2} G[c1,c2] * x_{k,c1} * x_{k+1,c2}
      H_constraint = lambda * Σ_k (1 - Σ_c x_{k,c})²
                   = lambda * Σ_k [ Σ_c x_{k,c}^2 + 2*Σ_{c1<c2} x_{k,c1}*x_{k,c2} - 2*Σ_c x_{k,c} + 1 ]
                   (dropping the constant +1 term, absorbed into offset)
    """
    C = CONCEPT_VOCAB_SIZE
    N = K * C  # total binary variables

    Q: dict[tuple[int, int], float] = {}

    def var(k: int, c: int) -> int:
        return k * C + c

    def add_Q(i: int, j: int, val: float):
        if val == 0.0:
            return
        i, j = (i, j) if i <= j else (j, i)  # upper triangular
        Q[(i, j)] = Q.get((i, j), 0.0) + val

    # --- Precompute resonance scores ---
    # Resonance(k, c) = Re[ PHV · (HV_c ⊗ HV_pos_{K+k})* ] / D
    # We use output positions starting at K (continuing the prompt positions)
    resonance = np.zeros((K, C), dtype=np.float64)
    for k in range(K):
        hv_pos = make_pos_hv(K + k, item_memory.dim)  # output position in sequence
        for c in range(C):
            bound = item_memory.get_by_idx(c) * hv_pos
            resonance[k, c] = float(np.real(np.dot(phv, bound.conj())) / item_memory.dim)

    # --- H_semantic: linear terms (diagonal of Q) ---
    for k in range(K):
        for c in range(C):
            v = var(k, c)
            add_Q(v, v, -alpha * resonance[k, c])

    # --- H_binding: quadratic terms between adjacent positions ---
    if affinity_matrix is None:
        # Default: use HDC cosine similarity between concept hypervectors as proxy
        # G[c1, c2] = cosine_similarity(HV_c1, HV_c2) — semantically related concepts
        # attract each other. This is corpus-free and purely hypervector-derived.
        hv_matrix = np.array([item_memory.get_by_idx(c) for c in range(C)])
        # Gram matrix of cosine similarities
        norms = np.linalg.norm(hv_matrix, axis=1)  # all 1.0 for unit CPHVs
        G = np.real(hv_matrix @ hv_matrix.conj().T) / item_memory.dim  # (C, C)
        # Zero out self-similarity (diagonal) to avoid self-reinforcement
        np.fill_diagonal(G, 0.0)
    else:
        G = affinity_matrix
        assert G.shape == (C, C), f"Affinity matrix must be ({C},{C})"

    for k in range(K - 1):
        for c1 in range(C):
            for c2 in range(C):
                val = -beta * G[c1, c2]
                if abs(val) > 1e-6:  # sparse threshold
                    add_Q(var(k, c1), var(k + 1, c2), val)

    # --- H_constraint: one-hot penalty ---
    # Expansion of lambda * (1 - Σ_c x_{k,c})^2:
    # = lambda * [Σ_c x_{k,c}^2 + 2*Σ_{c1<c2} x_{k,c1}*x_{k,c2} - 2*Σ_c x_{k,c}]
    for k in range(K):
        for c in range(C):
            v = var(k, c)
            # x^2 = x for binary vars; diagonal contribution: +lambda - 2*lambda = -lambda
            add_Q(v, v, lam - 2 * lam)
        for c1 in range(C):
            for c2 in range(c1 + 1, C):
                # Cross terms: +2*lambda
                add_Q(var(k, c1), var(k, c2), 2.0 * lam)

    # Build variable map for decoding
    variable_map = {
        var(k, c): (k, c)
        for k in range(K)
        for c in range(C)
    }

    return QUBOPayload(
        num_variables=N,
        Q=Q,
        variable_map=variable_map,
        metadata={
            "K": K,
            "vocab_size": C,
            "alpha": alpha,
            "beta": beta,
            "lambda": lam,
            "corpus_free_affinity": affinity_matrix is None,
            "generator_version": "NAHG-Phase1-v0.1.0",
        },
    )


# ---------------------------------------------------------------------------
# 5. SOLVER DISPATCH
# ---------------------------------------------------------------------------

def solve_qubo_local_simulated_annealing(
    payload: QUBOPayload,
    num_reads: int = 100,
    num_sweeps: int = 1000,
    seed: int = 42,
) -> np.ndarray:
    """
    Local simulated annealing fallback (no API key required).
    Demonstrates the QUBO minimization principle on CPU.
    Returns binary solution array of shape (N,).
    """
    N = payload.num_variables
    rng = np.random.default_rng(seed)

    # Convert sparse Q dict to dense matrix for SA
    Q_dense = np.zeros((N, N), dtype=np.float64)
    for (i, j), v in payload.Q.items():
        Q_dense[i, j] += v
        if i != j:
            Q_dense[j, i] += v  # symmetrize for energy computation

    def energy(x: np.ndarray) -> float:
        return float(x @ Q_dense @ x)

    best_x = None
    best_e = float("inf")

    for _ in range(num_reads):
        x = rng.integers(0, 2, N).astype(np.float64)
        T = 2.0
        for sweep in range(num_sweeps):
            T *= 0.995  # geometric cooling
            flip_idx = rng.integers(0, N)
            x_new = x.copy()
            x_new[flip_idx] = 1.0 - x_new[flip_idx]
            dE = energy(x_new) - energy(x)
            if dE < 0 or rng.random() < np.exp(-dE / max(T, 1e-10)):
                x = x_new
        e = energy(x)
        if e < best_e:
            best_e = e
            best_x = x.copy()

    return best_x


def solve_qubo_api(payload: QUBOPayload, timeout: float = 30.0) -> Optional[np.ndarray]:
    """
    Dispatch QUBO to the Catalyst-Q /v3turbo/solve/qubo endpoint.
    Returns binary solution array or None if the call fails.
    """
    if not QUBO_API_KEY:
        print("[WARN] CATALYSTQ_API_KEY not set — skipping API dispatch.")
        return None

    headers = {
        "Authorization": f"Bearer {QUBO_API_KEY}",
        "Content-Type": "application/json",
    }
    body = payload.to_api_dict()

    try:
        resp = requests.post(QUBO_ENDPOINT, json=body, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        solution = np.array(data["solution"], dtype=np.float64)
        return solution
    except requests.RequestException as e:
        print(f"[ERROR] QUBO API call failed: {e}")
        return None


# ---------------------------------------------------------------------------
# 6. DECODE GROUND STATE → TOKEN SEQUENCE
# ---------------------------------------------------------------------------

def decode_solution(
    solution: np.ndarray,
    payload: QUBOPayload,
    K: int = DEFAULT_K,
) -> list[str]:
    """
    Convert binary solution vector → K output concept tokens.
    For each position k, select the concept c with x_{k,c} = 1.
    If multiple are 1 (constraint violated), take the one with highest value
    (fractional relaxation fallback).
    If none are 1, take the one closest to 1.
    """
    C = CONCEPT_VOCAB_SIZE
    output_tokens: list[str] = []

    for k in range(K):
        slot = solution[k * C : (k + 1) * C]
        chosen_c = int(np.argmax(slot))
        output_tokens.append(CONCEPT_VOCAB[chosen_c])

    return output_tokens


# ---------------------------------------------------------------------------
# 7. END-TO-END GENERATION PIPELINE
# ---------------------------------------------------------------------------

def generate(
    prompt: list[str],
    K: int = DEFAULT_K,
    use_api: bool = True,
    verbose: bool = True,
) -> list[str]:
    """
    Full Non-Autoregressive Holographic Generation pipeline.

    Args:
        prompt:   List of concept tokens from CONCEPT_VOCAB (the prompt context)
        K:        Number of output tokens to generate simultaneously
        use_api:  If True, dispatch to Catalyst-Q API; else use local SA
        verbose:  Print progress

    Returns:
        List of K generated concept tokens
    """
    t0 = time.perf_counter()

    # Step 1: Build Item Memory
    if verbose:
        print("[1/5] Instantiating Holographic Vocabulary (CPHV Item Memory)...")
    im = ItemMemory(CONCEPT_VOCAB, dim=HV_DIM)

    # Step 2: Encode prompt → PHV
    if verbose:
        print(f"[2/5] Encoding prompt of {len(prompt)} tokens → O(1) Prompt Hypervector...")
    encoder = PromptEncoder(im)
    phv = encoder.encode(prompt)

    # Step 3: Build QUBO Hamiltonian
    if verbose:
        print(f"[3/5] Building QUBO Hamiltonian ({K} positions × {CONCEPT_VOCAB_SIZE} concepts = {K*CONCEPT_VOCAB_SIZE} variables)...")
    payload = build_qubo(phv, im, K=K)
    if verbose:
        print(f"      Sparse Q entries: {len(payload.Q):,}")

    # Step 4: Solve
    if verbose:
        solver_name = "Catalyst-Q API" if (use_api and QUBO_API_KEY) else "Local Simulated Annealing"
        print(f"[4/5] Solving Hamiltonian via {solver_name}...")

    solution = None
    if use_api:
        solution = solve_qubo_api(payload)
    if solution is None:
        if verbose:
            print("      Falling back to local simulated annealing...")
        solution = solve_qubo_local_simulated_annealing(payload)

    # Step 5: Decode
    if verbose:
        print("[5/5] Decoding ground state → token sequence...")
    tokens = decode_solution(solution, payload, K=K)

    t1 = time.perf_counter()

    if verbose:
        print(f"\n{'='*60}")
        print(f"NAHG Generation Complete — {t1-t0:.3f}s")
        print(f"Prompt  : {' → '.join(prompt)}")
        print(f"Output  : {' → '.join(tokens)}")
        print(f"='*60}")

    return tokens


# ---------------------------------------------------------------------------
# DEMO / SELF-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Non-Autoregressive Holographic Generator (NAHG) — Phase 1 Prototype")
    print("Strategic-Innovations AI, LLC | Catalyst-Q Platform")
    print("=" * 60)

    # --- Demo 1: Encode/Decode roundtrip test ---
    print("\n[TEST 1] HDC Roundtrip: encode prompt → PHV → decode each position")
    im = ItemMemory(CONCEPT_VOCAB, dim=HV_DIM)
    enc = PromptEncoder(im)
    test_prompt = ["QUANTUM", "SYSTEM", "GENERATE", "SEQUENCE", "FAST"]
    phv = enc.encode(test_prompt)
    print(f"  Prompt PHV shape: {phv.shape}, dtype: {phv.dtype}")
    print(f"  Mean |component| = {np.abs(phv).mean():.4f} (expect ~1.0 after norm)")
    for p, expected in enumerate(test_prompt):
        recovered, sim = enc.decode_at_position(phv, p)
        status = "✓" if recovered == expected else "✗"
        print(f"  pos={p}: expected={expected:20s} recovered={recovered:20s} sim={sim:.4f} {status}")

    # --- Demo 2: QUBO construction ---
    print("\n[TEST 2] QUBO Hamiltonian construction")
    payload = build_qubo(phv, im, K=5)
    N = payload.num_variables
    nnz = len(payload.Q)
    density = nnz / (N * (N + 1) / 2) * 100
    print(f"  Variables: {N} ({5} positions × {CONCEPT_VOCAB_SIZE} concepts)")
    print(f"  Non-zero Q entries: {nnz:,} ({density:.2f}% of upper triangle)")
    print(f"  API payload size: ~{len(json.dumps(payload.to_api_dict())) / 1024:.1f} KB")

    # --- Demo 3: Full generation pipeline (local SA) ---
    print("\n[TEST 3] Full NAHG pipeline — generating 8 tokens from prompt")
    prompt = ["QUANTUM", "SYSTEM", "MINIMIZE", "HAMILTONIAN"]
    output = generate(prompt, K=8, use_api=False, verbose=True)

    # --- Demo 4: Orthogonality verification ---
    print("\n[TEST 4] CPHV Orthogonality verification (random sample)")
    rng = np.random.default_rng(0)
    indices = rng.choice(CONCEPT_VOCAB_SIZE, size=10, replace=False)
    sims = []
    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):
            ci, cj = indices[i], indices[j]
            hv_i = im.get_by_idx(ci)
            hv_j = im.get_by_idx(cj)
            sim = float(np.real(np.dot(hv_i, hv_j.conj())) / HV_DIM)
            sims.append(abs(sim))
    print(f"  Mean |cross-similarity| (expect ~0.0): {np.mean(sims):.5f}")
    print(f"  Max  |cross-similarity| (expect <0.05): {np.max(sims):.5f}")
    print(f"  All pairs near-orthogonal: {'✓' if np.max(sims) < 0.05 else '✗'}")

    print("\nNAHG prototype self-test complete.")
