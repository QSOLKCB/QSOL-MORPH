# Determinism and Reproducibility

QSOL-MORPH is intended for research computing, where performance is useful but reproducibility is part of the scientific contract.

This document describes the candidate determinism and reproducibility model. It is non-normative until the relevant invariants and contracts are frozen.

## Composable reproducibility contract

Determinism should not be represented as one enum that mixes result guarantees with randomness configuration.

A future execution contract should compose at least these orthogonal facets:

```text
RESULT DETERMINISM
    STRICT
    NUMERIC
    DECLARED-NONDETERMINISTIC

RANDOMNESS
    NONE
    SEEDED
    EXTERNAL-ENTROPY
    DECLARED-NONDETERMINISTIC
```

Additional facets may be introduced for scheduling, external-service replay, or other independent sources of nondeterminism.

### STRICT result determinism

The same canonical program, immutable declared inputs, implementation identity, and required execution contract produce the same observable result bytes for the governed scope.

### NUMERIC result determinism

Results may differ at the bit level across legal implementations but remain within an explicitly declared numeric contract.

A `NUMERIC` declaration is incomplete without the numeric contract governing the relevant computation. Contracts may be attached at CARD or other frozen scopes, so provenance must preserve those bindings rather than assume one global numeric contract exists.

### DECLARED-NONDETERMINISTIC result behavior

The governed computation intentionally permits nondeterministic observable results. The source and trace must expose that fact.

### SEEDED randomness

Pseudorandom behavior is reproducible with respect to the recorded RNG algorithm, algorithm version, seed, stream identity, partitioning/stream mapping, and relevant execution contract.

`SEEDED` is not a result-determinism class. A computation may be:

```text
result_determinism = STRICT
randomness = SEEDED
```

or:

```text
result_determinism = NUMERIC
randomness = SEEDED
```

The exact names and complete facet set remain provisional.

## Scoped requested versus effective result contracts

A trace preserves what was requested and what was actually provided **at the scope where the requirement applies**.

A DECK may contain one `STRICT` CARD and another `NUMERIC` CARD. One execution-wide requested/effective pair cannot represent that program without either weakening the strict requirement or overstating the numeric result.

Conceptually:

```text
result_determinism_scopes[]:
    scope_kind
    scope_id
    source_card_ids[]
    requested_result_determinism
    effective_result_determinism
    transition_authorized_by?
    backend_unit_id?
```

A single execution-wide entry is legal only when a frozen normalization rule proves that one requested/effective pair faithfully represents every governed source requirement.

A recorded transition is evidence, not authorization. If a source requirement cannot be satisfied and no pre-execution rule authorizes a weaker guarantee, execution fails closed.

The same requested/effective distinction applies independently to randomness.

## Sources of nondeterminism

Potential sources include:

- random number generators;
- system entropy;
- wall-clock time;
- process/thread scheduling;
- unordered reductions;
- atomic update order;
- filesystem iteration order;
- network responses;
- external services;
- AI model sampling;
- GPU kernels and libraries;
- hardware-specific floating-point behavior;
- compiler and backend selection decisions.

QSOL-MORPH treats these as explicit concerns rather than incidental runtime trivia.

## Scoped randomness provenance

Randomness contracts may differ within one DECK or JOB.

Conceptually:

```text
randomness_execution_scopes[]:
    scope_kind
    scope_id
    source_card_ids[]
    requested_randomness_mode
    effective_randomness_mode
    transition_authorized_by?
    rng_algorithm?
    rng_version?
    seed?
    stream_id?
    parallel_partitioning?
    backend_unit_id?
```

A single execution-wide randomness entry is legal only when a frozen lossless normalization rule proves that one randomness contract and replay configuration faithfully govern every affected source computation.

Seeded replay requires the algorithm, algorithm version, seed, stream identity, and parallel partitioning/stream mapping wherever those inputs can affect the generated sequence.

## Time

Wall-clock time is an external input.

A deterministic computation must not silently read it. Any clock access belongs behind explicit semantics/effect boundaries and must be traced according to the active contract.

## Floating point

Floating-point reproducibility is sensitive to:

- fused multiply-add;
- reassociation;
- reduction-tree shape;
- denormal handling;
- precision contraction/expansion;
- transcendental-library implementation;
- target-specific instructions.

QSOL-MORPH must not call a transformation semantically identical under a strict numeric contract merely because the real-number algebra looks equivalent.

## Scoped numeric provenance

Numeric contracts and effective material modes may differ within one execution.

Conceptually:

```text
numeric_execution_scopes[]:
    scope_kind
    scope_id
    source_card_ids[]
    numeric_contract_id
    numeric_contract_hash
    material_numeric_mode
    backend_unit_id?
```

`material_numeric_mode` records contract-permitted choices that can change legal result bytes, such as FMA behavior, denormal handling, effective precision, reduction strategy, or selected math-library mode.

A single execution-wide numeric scope is legal only when a frozen normalization rule proves that one contract and one material mode govern the entire execution.

## Parallelism

Parallel execution is not inherently nondeterministic, but it often exposes order-sensitive behavior.

A deterministic parallel implementation may require:

- race-free dataflow;
- deterministic partitioning;
- deterministic reduction algorithms;
- controlled atomics;
- stable synchronization semantics.

When those requirements cannot be met for a governed scope, the implementation must reject the requested result contract unless a weaker contract was explicitly permitted before execution.

For seeded parallel execution, partitioning/stream mapping is part of the scoped replay contract.

## Scoped backend selection

Automatic and explicit machinery choices are provenance-bearing decisions.

A source may request:

```text
RUN MODEL ON HOST
RUN MODEL ON BEST
```

Different source computations may legally resolve to different machinery, so provenance uses scoped records:

```text
backend_selection_scopes[]:
    scope_kind
    scope_id
    source_card_ids[]
    backend_unit_id?
    requested_target?
    selected_backend
    selected_backend_version?
    target_architecture?
    device?
    selection_policy_id?
    selection_policy_version?
    selection_tuning_id?
    selection_tuning_hash?
```

Policy/tuning identity is material when selection is automatic, such as `ON BEST`.

A single execution-wide selection entry is valid only when one frozen machinery decision genuinely governs the whole run.

For a frozen experiment, replay may require the recorded backend rather than re-running an evolved selection policy.

## Lowering provenance

Reproducibility binds both mandatory lowering stages.

Material identities include:

```text
semantic_to_core_spec_version
semantic_to_core_implementation_version
core_ir_hash
semantic_to_core_result_binding_map[]
vector_dataflow_spec_version
vector_dataflow_implementation_version
vector_dataflow_ir_hash
core_to_vector_result_binding_map[]
```

Binding maps are required whenever result identities are preserved or transformed, except under a frozen deterministic identity-map reconstruction rule.

IR hashes identify representations but do not themselves establish correspondence between source and lower result names.

## Result provenance

A run may produce several outputs with different epistemic classes and statuses.

Conceptually:

```text
outputs[]:
    output_id
    result_binding?
    artifact_hash
    artifact_location?
    semantic_class
    status
    producer_card_ids[]
    backend_selection_scope_ids[]
    result_determinism_scope_ids[]
    numeric_scope_ids[]
    randomness_scope_ids[]
    cache_reuse_record_ids[]?
    test_status?
    validation_status?
    proof_status?
```

A simulation output and a separately validated output remain distinct records. The validation/proof status of one output must not promote another result from the same JOB.

The scope-reference arrays identify the exact machinery, result guarantee, numeric behavior, and RNG configuration that governed each output.

## Input provenance

Declared runtime inputs are bound to the actual immutable value or content consumed, not merely to a mutable locator.

Conceptually:

```text
inputs[]:
    input_id
    input_kind
    canonical_value?
    content_hash?
    artifact_id_or_version?
    location?
    media_or_schema_type?
    source_card_ids[]?
```

Every material input requires a stable `input_id` plus either its canonical value or an immutable content/artifact identity sufficient to distinguish what was actually consumed.

Paths, URLs, dataset names, model names, and similar locators remain useful retrieval context but are not reproducibility evidence by themselves.

## Cache reuse provenance

Cache legality and cache provenance are distinct.

Ordinary result substitution is conservative and effect-free by default. Effectful reuse requires a separately frozen replay/cache semantic that preserves the declared effect, authorization, ordering, failure, and per-attempt provenance boundaries.

Even when reuse is legal, the run manifest must record that reuse occurred. Otherwise a cold execution and a cache-substituted execution can become indistinguishable despite having different reconstruction evidence.

Conceptually:

```text
cache_reuse_records[]:
    cache_reuse_record_id
    classification              # COLD_EXECUTION / VERIFIED_CACHE_REUSE / UNVERIFIED_CACHE_HIT / frozen equivalent
    source_card_ids[]
    reused_computation_id?
    cache_key_hash?
    cached_artifact_hash?
    cached_output_id?
    cache_producer_run_id?
    legality_rule_id?
    verification_evidence_id?
    material_cache_identity_hash
```

The record states whether work executed cold or was reused, what computation/artifact was reused, which cache identity justified the lookup, and which rule/evidence authorized substitution.

`VERIFIED_CACHE_REUSE` does **not** prove that a cold reconstruction still succeeds. That claim needs separate cold-execution or equivalent evidence.

An `UNVERIFIED_CACHE_HIT` may be useful diagnostic evidence, but it must not be promoted into verified reuse merely because the bytes appear plausible.

## Reproducibility manifest

A future run manifest may include:

```text
spec_version
source_hash
semantic_ir_hash
job_id
deck_id
card_ids[]
execution_status
job_status
deck_status
failure_card_id?
failure_class?
failure_stage?
semantic_to_core_spec_version
semantic_to_core_implementation_version
core_ir_hash
semantic_to_core_result_binding_map[]
vector_dataflow_spec_version
vector_dataflow_implementation_version
vector_dataflow_ir_hash
core_to_vector_result_binding_map[]
morph_version
backend_selection_scopes[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
inputs[]
outputs[]
cache_reuse_records[]
resolved_extensions[]
required_capabilities[]
granted_capabilities[]
denied_capabilities[]
capability_policy_id
capability_policy_version
capabilities_used[]
effect_attempts[]
optimization_profile
kernel_or_binary_hashes[]
```

`job_id` and `deck_id` identify the stable canonical hierarchy member represented by this execution. `card_ids[]` identifies the stable CARD identities that the manifest's producer, output, failure, scope, effect-attempt, and cache-reuse references may name. A whole-source hash is not a substitute for the selected JOB/DECK execution identity.

`execution_status`, `job_status`, and `deck_status` record the enclosing run outcome even when no output exists. When a failure occurs, `failure_card_id`, `failure_class`, and `failure_stage` identify the canonical failing CARD and stable semantic failure context. Effect completion alone cannot stand in for the enclosing CARD/DECK/JOB outcome: a process effect may be `COMPLETED` while its CARD and JOB fail because the completed process returned a non-success exit status.

Each `backend_selection_scopes[]` entry binds source CARDs/lower execution units to their requested and selected machinery plus automatic-selection policy/tuning identity where applicable.

Each `result_determinism_scopes[]` entry binds the scope identity, source CARD provenance, requested/effective guarantees, any preauthorized transition, and backend execution-unit identity where useful.

Each `numeric_execution_scopes[]` entry binds the scope identity, source CARD provenance, numeric-contract identity/hash, material numeric mode, and backend execution-unit identity where useful.

Each `randomness_execution_scopes[]` entry binds the scope identity, source CARD provenance, requested/effective randomness mode, transition authority, replay-relevant RNG algorithm/version/seed/stream/partitioning, and backend execution-unit identity where useful.

Each `inputs[]` entry binds a declared material input to the exact immutable value/content/artifact identity consumed.

Each `outputs[]` entry binds its artifact/result identity to its own semantic class, status, producer provenance, governing execution scopes, and any relevant cache-reuse records.

Each `cache_reuse_records[]` entry makes cold versus reused execution auditable and binds the material cache identity plus any legality/verification evidence supporting substitution.

Not every optional field applies to every execution, but stable JOB/DECK identity and the enclosing execution outcome are material even when a failed run produces no outputs, and no material reproducibility decision may disappear merely because another run would have reached the same bytes by a different path.

The manifest should represent independent reproducibility facets independently rather than collapsing them into false execution-wide singletons.

## Reproducibility versus portability

Portable source does not imply bit-identical execution across every target.

QSOL-MORPH should state the strongest reproducibility guarantee actually provided by a source/backend/contract combination, including the scopes and outputs to which that guarantee applies.

## Failure behavior

An implementation fails closed when a required scoped determinism, numeric, randomness, capability, or other frozen execution contract cannot be satisfied.

Silently weakening:

```text
STRICT -> DECLARED-NONDETERMINISTIC
```

or substituting external entropy for a required seeded stream is invalid unless an explicit pre-execution rule authorizes that transition for the affected scope.

General execution failure and effect-attempt completion semantics are documented separately in [Failure and Partial-Effect Semantics](FAILURE-AND-PARTIAL-EFFECTS.md).

## Design principle

> Nondeterminism, machinery choice, cache reuse, and external inputs are scientific inputs, not invisible implementation details.
