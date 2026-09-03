# Determinism and Reproducibility

QSOL-MORPH is intended for research computing, where performance is useful but reproducibility is part of the scientific contract.

This document describes the candidate determinism model. It is non-normative until the invariant freeze.

## Composable reproducibility contract

Determinism should not be represented as a single enum that mixes result guarantees with randomness configuration.

A future execution contract should instead compose at least two orthogonal facets:

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

Additional facets may be added if the specification needs to represent scheduling, external-service replay, or other independent sources of nondeterminism.

### STRICT result determinism

The same canonical program, declared inputs, implementation version, and required execution contract produce the same observable result bytes for the scope governed by the contract.

### NUMERIC result determinism

Results may differ at the bit level across legal implementations but remain within explicitly declared numeric contracts.

A `NUMERIC` declaration is incomplete without the numeric contract that governs the relevant computation. Contracts may be attached at CARD or other frozen scopes, so reproducibility must preserve those bindings rather than assume one global numeric contract exists for every execution.

Each contract must identify enough information to judge legal variation, such as tolerance/error metric, domain, precision behavior, or a referenced frozen numeric profile.

### DECLARED-NONDETERMINISTIC result behavior

The governed computation intentionally permits nondeterministic observable results. The source and trace must expose that fact.

### SEEDED randomness

Pseudorandom behavior is reproducible with respect to a recorded algorithm, algorithm version, seed, stream identity, partitioning/stream mapping, and relevant execution contract.

`SEEDED` is not a weaker or stronger result-determinism class. A computation may, for example, be both:

```text
result_determinism = STRICT
randomness = SEEDED
```

or:

```text
result_determinism = NUMERIC
randomness = SEEDED
```

Likewise, a computation with deterministic seeded RNG may still permit nondeterministic scheduling if its result contract explicitly allows it.

The exact names and complete facet set are not frozen.

## Scoped requested versus effective result contracts

A trace must preserve the distinction between what was requested and what was actually provided **at the scope where the requirement applies**.

The canonical model may attach different result-determinism requirements to different CARDs. A DECK may therefore contain, for example, one `STRICT` CARD and another `NUMERIC` CARD. One execution-wide requested/effective pair cannot represent that program without either weakening the strict requirement or overstating the numeric result.

Conceptually, provenance uses scoped entries:

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

`scope_kind` may eventually distinguish execution, CARD, region, kernel, or another frozen scope.

A single execution-wide entry is legal only when a frozen normalization rule proves that one requested/effective pair faithfully represents every source requirement. Otherwise the distinct source/effective scopes remain visible.

For example, if one governed scope requests:

```text
requested_result_determinism = STRICT
```

and an execution policy explicitly permits:

```text
effective_result_determinism = NUMERIC
```

then that scope's trace entry must retain both values and the rule/policy authorizing the transition.

A recorded transition is evidence of what happened. It is not itself authorization to weaken a source requirement.

The same requested/effective distinction applies independently to randomness, but randomness is also scoped to the CARD/region/kernel or other frozen scope it governs rather than being represented by one execution-wide singleton.

## Sources of nondeterminism

Potential sources include:

- random number generators;
- system entropy;
- wall-clock time;
- process scheduling;
- thread scheduling;
- unordered reductions;
- atomic update order;
- filesystem iteration order;
- network responses;
- external services;
- AI model sampling;
- GPU kernels and libraries;
- hardware-specific floating-point behavior;
- compiler optimization decisions.

QSOL-MORPH should treat these as explicit concerns rather than incidental runtime trivia.

## Randomness

Randomness should declare its source.

Illustrative seeded form:

```text
SEED RNG 18437
RUN MONTE_CARLO
```

A seeded RNG declaration establishes the randomness facet. It does not by itself establish the result-determinism facet.

Using the same integer seed is insufficient if the generator version or parallel stream mapping changes.

## Scoped randomness provenance

Randomness contracts may differ within one DECK or JOB because the canonical model permits CARD-scoped randomness requirements.

For example, separate computations may use different RNG algorithms, versions, seeds, streams, or partitioning rules. Reproducibility therefore uses scoped entries rather than one execution-wide RNG tuple.

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

If a scoped source requirement requests `SEEDED` and an execution policy explicitly permits another mode, that scope's record retains both requested and effective modes plus the pre-execution rule authorizing the transition.

Seeded replay requires the algorithm, algorithm version, seed, stream identity, and parallel partitioning/stream mapping wherever those inputs can affect the generated sequence.

## Time

Wall-clock time is an external input.

A deterministic computation should not silently read it.

Possible explicit forms may distinguish:

```text
CLOCK MONOTONIC
CLOCK WALL
```

or a capability/effect declaration.

## Floating point

Floating-point reproducibility is especially sensitive to:

- fused multiply-add;
- reassociation;
- reduction tree shape;
- denormal handling;
- precision contraction/expansion;
- transcendental library implementation;
- target-specific instructions.

QSOL-MORPH must not label a transformation semantically identical under a strict numeric contract merely because the real-number algebra looks equivalent.

The numeric contract governing a CARD, region, kernel, or other frozen scope determines which transformations are legal there.

The execution trace must also bind the **material numeric mode** used within each relevant scope when choices such as FMA behavior, denormal handling, effective precision, reduction strategy, or math-library mode can change otherwise legal result bytes.

## Scoped numeric provenance

Numeric contracts and effective numeric modes may differ within one execution.

For example, two CARDs may bind different tolerance contracts, or a backend may legally choose different contract-permitted modes for separate kernels. A reproducibility record therefore uses scoped entries rather than one singular global contract/mode pair.

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

`scope_kind` may eventually distinguish execution, CARD, region, kernel, or another frozen scope.

A single execution-wide entry is legal only when a frozen normalization rule proves that one numeric contract and one material numeric mode govern the whole execution. Otherwise the source and effective scopes remain distinct.

## Parallelism

Parallel execution is not inherently nondeterministic, but it often exposes order-sensitive behavior.

A deterministic parallel backend may require:

- race-free dataflow;
- deterministic partitioning;
- deterministic reduction algorithms;
- controlled atomics;
- stable synchronization semantics.

When those requirements cannot be met for a governed scope, the backend must reject that scope's requested result-determinism contract unless the source or execution policy explicitly permits a weaker result contract. Merely reporting a downgrade after execution is not sufficient permission.

For seeded parallel execution, the partitioning/stream-mapping scheme is part of the scoped reproducibility input and must be recorded when it can change the generated sequence.

## Scoped backend selection

Backend selection must be traceable at the scope where the target decision actually applies.

A JOB may contain, for example, one CARD explicitly targeting a host backend and another using:

```text
RUN MODEL ON BEST
```

One execution-wide `backend` field cannot represent both decisions. Reproducibility therefore uses scoped machinery-selection entries.

Conceptually:

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

Automatic-selection policy and tuning identity are material for scopes using policies such as `ON BEST`. Explicitly targeted scopes can leave those policy fields absent while still recording their requested and effective target.

A single execution-wide backend-selection scope is legal only when a frozen rule establishes that one machinery decision governs the entire execution. Separate source target qualifiers must remain separately attributable even when they happen to resolve to the same backend.

For a frozen experiment, a later replay may require the recorded selected backend for each governed scope rather than re-run an evolved selection policy.

## Lowering provenance

Reproducibility must bind both mandatory lowering stages, not only the semantic source and final MORPH/backend.

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

The binding maps are material whenever a lowering preserves, renames, splits, or otherwise maps result identities. IR hashes identify the representations but do not by themselves tell a provenance consumer which lower result name corresponds to a source binding.

If the QSOL-CORE → Vector/Dataflow lowering changes its control-flow graph, effect ordering, capability metadata, result-binding mapping, vector structure, or numeric representation while Semantic IR and MORPH remain unchanged, the manifest must still distinguish the run.

## Result provenance

A run may produce several outputs with different epistemic classes and statuses.

Reproducibility therefore treats `outputs[]` as identified records rather than a list of hashes paired with one execution-wide semantic class.

A conceptual output record may include:

```text
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
test_status?
validation_status?
proof_status?
```

A simulation output and a separately validated output remain distinct records. The validation status of one output must not promote another output merely because both were produced in the same JOB.

`backend_selection_scope_ids[]` identifies the machinery-selection decisions that governed the output. `randomness_scope_ids[]` identifies the exact randomness contracts/streams that governed an output when randomness contributed to that result.

## Input provenance

Declared runtime inputs must be bound to the actual immutable value or content consumed, not merely to a mutable path, URL, dataset name, model name, or other locator.

A conceptual material input record may include:

```text
input_id
input_kind
canonical_value?          # for inline scalar/record inputs
content_hash?             # required for material external byte/artifact inputs
artifact_id_or_version?
location?
media_or_schema_type?
source_card_ids[]?
```

Every material input requires a stable `input_id` plus either its canonical value or an immutable content/artifact identity sufficient to distinguish the exact input consumed. For a file, dataset, model, downloaded object, or other mutable external resource, a location alone is not reproducibility evidence; the consumed bytes or immutable artifact/version must be hash-bound.

A location remains useful retrieval context, but replay and audit must not infer content identity from a mutable locator.

## Reproducibility manifest

A future run manifest may include:

```text
spec_version
source_hash
semantic_ir_hash
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

Each `backend_selection_scopes[]` entry binds the source CARDs/lower execution unit to its requested target where applicable, selected backend/version, target/device identity, and automatic-selection policy/tuning identity when automatic selection was used.

Each `result_determinism_scopes[]` entry binds the scope identity, source CARD provenance, requested and effective guarantees, any preauthorized transition, and backend execution-unit identity when useful.

Each `numeric_execution_scopes[]` entry binds the scope identity, source CARD provenance where applicable, numeric-contract identity/hash, effective material numeric mode, and backend execution-unit identity when useful.

Each `randomness_execution_scopes[]` entry binds the scope identity, source CARD provenance, requested/effective randomness mode, transition authority, and replay-relevant RNG algorithm/version/seed/stream/partitioning plus backend execution-unit identity where useful.

Each `inputs[]` entry binds the declared material input to a stable input ID and the exact canonical value, content hash, immutable artifact/version identity, or equivalent frozen identity actually consumed.

Each `outputs[]` entry binds its artifact/result identity to its own semantic class, status, producer provenance, and governing backend-selection/determinism/numeric/randomness scopes.

Not every field is required for every execution. Backend-selection policy/tuning fields are material within scopes where the backend was chosen automatically; scoped seeded-RNG fields are material when seeded randomness is used; effect-attempt entries are material whenever protected external effects are attempted; binding maps are material when result identities are transformed; Vector/Dataflow identities are material whenever the mandatory lower IR participates in execution or code generation; scoped machinery/determinism/numeric/randomness entries are material whenever their decisions or contracts affect legal results; immutable input identity is material whenever an external or mutable input contributes to a result.

The manifest should represent independent reproducibility facets independently rather than collapsing them into ambiguous labels or false execution-wide singletons.

## Reproducibility versus portability

Portable source does not imply bit-identical execution across every target.

QSOL-MORPH should state the strongest reproducibility guarantee actually provided by a given source/backend/contract combination, including the scopes and outputs to which that guarantee applies.

## Failure behavior

A backend should fail closed when a required scoped determinism or numeric contract cannot be satisfied.

Silently downgrading:

```text
STRICT -> DECLARED-NONDETERMINISTIC
```

for a scope that did not authorize that transition would make the trace accurate only after violating the user's declared execution requirement.

A downgrade is acceptable only when the source or execution policy explicitly permits it before execution for the affected scope.

The same rule applies independently to randomness and other reproducibility facets: an implementation may not substitute external entropy for a required seeded stream merely because it records that substitution afterward.

General execution failure and effect-attempt completion semantics are documented separately in [Failure and Partial-Effect Semantics](FAILURE-AND-PARTIAL-EFFECTS.md).

## Design principle

> Nondeterminism is an input to the scientific method, not an invisible implementation detail.
