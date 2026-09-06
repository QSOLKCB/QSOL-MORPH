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

Additional facets may be introduced for scheduling, external-service replay, failure/recovery policy, or other independent sources of nondeterminism or execution-path variation.

### STRICT result determinism

The same canonical program, immutable declared inputs, implementation identity, and required execution contract produce the same observable result bytes for the governed scope.

### NUMERIC result determinism

Results may differ at the bit level across legal implementations but remain within an explicitly declared numeric contract.

A `NUMERIC` declaration is incomplete without the numeric contract governing the relevant computation. Contracts may be attached at JOB, DECK, CARD, or another frozen scope, so provenance must preserve those bindings rather than assume one global numeric contract exists.

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

## Scoped source contracts

Result-determinism, numeric, randomness, and failure-behavior requirements remain attached to the canonical scope that owns them.

A JOB may establish a default/frozen requirement for its DECKs, a DECK may own a requirement for its CARDs, and a CARD may have its own explicit requirement where the normative semantic model permits that composition. The future specification must freeze inheritance/refinement rules before executable implementation.

No serializer, lowering, or backend may silently flatten a JOB/DECK contract into an arbitrary child or weaken a parent requirement merely because the target cannot satisfy it. Effective scope bindings and any permitted transition remain provenance-visible.

### Scoped failure-behavior provenance

Failure behavior affects the execution path and is therefore reproducibility-bearing.

Conceptually:

```text
failure_behavior_bindings[]:
    scope_kind
    scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
```

An explicit JOB/DECK/CARD recovery, continuation, compensation, or fail-stop policy remains attached to the source scope that owns it. When no explicit policy exists, the frozen default fail-stop behavior has a stable specification identity and may be recorded as the requested/effective behavior where it materially determines which later CARDs or DECKs execute.

A manifest must not infer effective failure policy merely from observed skipped CARDs. The policy that caused the execution path is itself part of the reproducibility record.

## Scoped requested versus effective result contracts

A trace preserves what was requested and what was actually provided **at the scope where the requirement applies**.

A DECK may contain one `STRICT` CARD and another `NUMERIC` CARD. One execution-wide requested/effective pair cannot represent that program without either weakening the strict requirement or overstating the numeric result.

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

A single execution-wide numeric scope is legal only when a frozen normalization rule proves that one contract and one material numeric mode govern the entire execution.

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
    machinery_authorization_record_ids[]?
```

Policy/tuning identity is material when selection is automatic, such as `ON BEST`.

A single execution-wide selection entry is valid only when one frozen machinery decision genuinely governs the whole run.

For a frozen experiment, replay may require the recorded backend rather than re-running an evolved selection policy.

## Protected machinery requirements and authorization

Selecting machinery does not itself authorize its use, and machinery selection is not an external Semantic-IR effect.

The run manifest carries the canonical requirement rows independently of authorization decisions:

```text
machinery_requirements[]:
    machinery_requirement_id
    scope_kind
    scope_id
    source_card_ids[]
    target_selector_or_class
    required_capabilities[]
```

Protected machinery access is then traced through identified authorization records:

```text
machinery_authorization_records[]:
    machinery_authorization_record_id
    backend_selection_scope_id
    source_card_ids[]
    machinery_requirement_ids[]
    required_capabilities[]
    granted_capabilities[]
    denied_capabilities[]
    capability_policy_id
    capability_policy_version
    authorization_status
```

The requirement rows answer **what permission the canonical program required**. Authorization records answer **what policy decided for this execution**. One cannot replace the other.

For `ON BEST`, the target may be resolved first so the applicable machinery requirement is known. All required capabilities must then be granted before protected machinery use starts. A denied accelerator authorization must not launch a kernel and must not be represented as a synthetic external effect.

Fallback from an unauthorized target to another target is legal only under a frozen pre-execution selection/fallback rule, and the selection plus authorization history remains provenance-visible.

## Generated artifact provenance

```text
generated_artifacts[]:
    generated_artifact_id
    artifact_kind
    artifact_hash
    backend_unit_id
    backend_selection_scope_id
    source_card_ids[]?
    artifact_location?
```

`backend_unit_id` identifies the lower execution/code-generation unit that produced the artifact. `backend_selection_scope_id` links that artifact to the exact machinery-selection record containing the selected backend, version, architecture, device, and automatic-selection policy/tuning identity where applicable.

For a mixed-backend JOB, two artifacts may have identical artifact kinds while remaining attributable to different machinery scopes. A bare hash list is insufficient provenance.

A single backend-selection scope may govern more than one generated artifact. Outputs therefore carry applicable `generated_artifact_ids[]` so reference and optimized executables, alternate kernels, or multiple generated units under the same scope cannot be confused.

## Lowering provenance

Reproducibility binds both mandatory lowering stages.

Material identities include:

```text
semantic_to_core_spec_version
semantic_to_core_implementation_version
core_ir_hash
semantic_to_core_result_binding_map[]
qualifier_lowering_decisions[]
machinery_requirement_lowering_decisions[]
result_determinism_lowering_decisions[]
numeric_contract_lowering_decisions[]
randomness_lowering_decisions[]
failure_behavior_lowering_decisions[]
vector_dataflow_spec_version
vector_dataflow_implementation_version
vector_dataflow_ir_hash
core_to_vector_result_binding_map[]
machinery_requirement_mapping_decisions[]
core_to_vector_result_determinism_mapping_decisions[]
core_to_vector_numeric_contract_mapping_decisions[]
core_to_vector_randomness_mapping_decisions[]
failure_behavior_mapping_decisions[]
```

Result-binding maps use a frozen cardinality-aware representation. They must be able to express one-to-one preservation/rename, one-to-many split, many-to-one fusion, and any explicitly permitted many-to-many transformation without positional inference.

Binding maps are required whenever result identities are preserved or transformed, except under a frozen deterministic reconstruction rule that recovers the complete mapping.

The Semantic→Core lowering-decision records identify the frozen rules, scope mappings, normalizations, and transition authorities that explain how execution-relevant qualifiers, machinery requirements, failure behavior, and source determinism/numeric/randomness contracts became QSOL-CORE contracts or preserved metadata.

The Core→Vector/Dataflow mapping records perform the same job for the second mandatory lowering. If a Core contract scope is split across kernels, fused into a region, or otherwise changes lower identity, the corresponding mapping must be recorded. Mapping records may be omitted only when a frozen deterministic identity-scope reconstruction rule proves the mapping is lossless.

IR hashes identify representations but do not establish binding or contract-scope correspondence by themselves.

## Result provenance

A run may produce several outputs with different epistemic classes and statuses.

```text
outputs[]:
    output_id
    result_binding?
    artifact_hash
    artifact_location?
    semantic_class
    status
    producer_card_ids[]
    effect_attempt_ids[]?
    backend_selection_scope_ids[]
    generated_artifact_ids[]?
    result_determinism_scope_ids[]
    numeric_scope_ids[]
    randomness_scope_ids[]
    cache_reuse_record_ids[]?
    evidence_status?
```

When present, evidence status is class-discriminated:

```text
evidence_status:
    evidence_class      # TEST / VALIDATION / PROOF / frozen equivalent
    status
    evidence_rule_id?
```

`evidence_class` must be compatible with the output's `semantic_class` and with the explicit evidence-transition rule that produced it. The candidate model does not provide independent `test_status`, `validation_status`, and `proof_status` fields because those fields permit one output to carry contradictory epistemic claims.

The generic output `status` describes the frozen result/artifact execution or availability state. It does not promote epistemic class.

A simulation output and a separately validated output remain distinct records. The validation/proof status of one output must not promote another result from the same JOB.

`effect_attempt_ids[]`, when applicable, identifies the concrete effect attempts that produced, published, exposed, or materially supplied the output. Each corresponding effect-attempt record reciprocally names the output through `observable_output_ids[]`. This makes effect authorization and completion state attributable to the exact output.

The scope-reference arrays identify the exact machinery, result guarantee, numeric behavior, and RNG configuration that governed each output. `generated_artifact_ids[]` identifies the exact generated artifact that actually produced or supplied the output when generated code applies.

## Input provenance

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

## External-tool provenance

Extension resolution identifies the QSOL adapter/profile contract; it does not identify the external tool, service, model, prover, process, or instrument that actually supplied evidence or data.

```text
external_tool_versions[]:
    external_tool_id
    tool_kind
    tool_name_or_service
    version?
    content_hash_or_model_id?
    endpoint_or_location?
    source_card_ids[]?
```

The record must contain enough immutable version/content/model/service identity to distinguish a material change in the external evidence producer.

## Cache reuse provenance

Cache legality and cache provenance are distinct.

Ordinary result substitution is conservative and effect-free by default. Effectful reuse requires a separately frozen replay/cache semantic that preserves the declared effect, authorization, ordering, failure, and per-attempt provenance boundaries.

```text
cache_reuse_records[]:
    cache_reuse_record_id
    classification
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

Candidate classifications include `COLD_EXECUTION`, `VERIFIED_CACHE_REUSE`, and `UNVERIFIED_CACHE_HIT` or frozen equivalents.

A verified cache reuse does not prove cold reconstructability. That claim needs separate cold-execution or equivalent evidence.

## Optimization provenance

```text
optimization_provenance[]:
    optimization_record_id
    source_card_ids[]
    backend_unit_id?
    reference_ir_hash
    optimized_ir_hash
    transformation_sequence[]
    legality_witnesses[]
    vectorization_decisions[]?
    fusion_decisions[]?
    memory_placement_decisions[]?
    target_context_measurements[]?
    resource_model_assumptions[]?
```

An optimization profile names requested/configured policy; it is not a record of transformations that actually occurred.

Target-adaptive executions must preserve the actual transformation sequence and legality evidence. A stable content identity for a complete MORPH trace may substitute only when that trace is retrievable and verifiable.

## Effect declaration and attempt accounting

A declared protected effect does not necessarily produce a runtime attempt. Its CARD may be on an untaken branch, may never be reached after a prior fail-stop failure, or may be explicitly skipped by a frozen execution rule.

Every declaration is therefore accounted for by either one or more `effect_attempts[]` records or an explicit `effect_non_attempt_records[]` entry:

```text
effect_non_attempt_records[]:
    declared_effect_id
    card_id
    effect_kind
    non_attempt_reason
    governing_control_or_failure_id?
    backend_detail?
```

Candidate reasons include `UNTAKEN_BRANCH`, `PRIOR_FAIL_STOP`, `CARD_NOT_REACHED`, `EXPLICIT_SKIP`, `BACKEND_OMISSION_DETECTED`, or frozen equivalents.

Runtime attempts carry concrete result attribution where applicable:

```text
effect_attempts[]:
    effect_attempt_id
    declared_effect_id
    card_id
    effect_kind
    required_capabilities[]
    sequence_index
    completion_state
    backend_detail?
    observable_output_ids[]
```

`observable_output_ids[]` links the effect attempt to the stable output records it actually produced, published, exposed, or materially supplied. The reciprocal `outputs[].effect_attempt_ids[]` relation prevents a result from being attributed only to a broad producer CARD when several effect attempts occurred.

An effect declaration with neither an attempt nor a non-attempt reason is incomplete provenance when declaration-completeness auditing is required.

## Per-CARD execution provenance

Canonical membership alone does not establish execution.

```text
card_executions[]:
    card_execution_id
    deck_execution_id
    card_id
    card_status
    execution_order_index?
    governing_control_or_failure_id?
    failure_class?
    failure_stage?
```

Candidate statuses include `EXECUTED_SUCCESS`, `EXECUTED_FAILED`, `UNTAKEN_BRANCH`, `PRIOR_FAIL_STOP`, `CARD_NOT_REACHED`, `EXPLICIT_SKIP`, or frozen equivalents.

This is material even for pure CARDs. A TEST that sits on an untaken branch may produce no output, effect, or failure, but it is semantically different from a TEST that executed successfully.

## Multi-DECK JOB execution provenance

```text
deck_executions[]:
    deck_execution_id
    deck_id
    deck_status
    card_execution_ids[]
    execution_order_index?
    failure_card_id?
    failure_class?
    failure_stage?
```

Every DECK selected for that JOB execution remains represented. A later DECK prevented from starting by fail-stop behavior records an explicit non-started/skipped status or frozen equivalent rather than disappearing.

## Reproducibility manifest

A future run manifest may include:

```text
spec_version
run_id
source_hash
semantic_ir_hash
job_id
deck_executions[]
card_ids[]
card_executions[]
execution_status
job_status
failure_card_id?
failure_class?
failure_stage?
failure_behavior_bindings[]
semantic_to_core_spec_version
semantic_to_core_implementation_version
core_ir_hash
semantic_to_core_result_binding_map[]
qualifier_lowering_decisions[]
machinery_requirement_lowering_decisions[]
result_determinism_lowering_decisions[]
numeric_contract_lowering_decisions[]
randomness_lowering_decisions[]
failure_behavior_lowering_decisions[]
vector_dataflow_spec_version
vector_dataflow_implementation_version
vector_dataflow_ir_hash
core_to_vector_result_binding_map[]
machinery_requirement_mapping_decisions[]
core_to_vector_result_determinism_mapping_decisions[]
core_to_vector_numeric_contract_mapping_decisions[]
core_to_vector_randomness_mapping_decisions[]
failure_behavior_mapping_decisions[]
morph_version
backend_selection_scopes[]
machinery_requirements[]
machinery_authorization_records[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
inputs[]
outputs[]
cache_reuse_records[]
resolved_extensions[]
external_tool_versions[]
effect_requirements[]
required_capabilities[]
granted_capabilities[]
denied_capabilities[]
capability_policy_id
capability_policy_version
capabilities_used[]
effect_attempts[]
effect_non_attempt_records[]
optimization_profile
optimization_provenance[]
generated_artifacts[]
```

`run_id` identifies the aggregate execution event. `job_id` identifies the stable canonical JOB selected for that run. `deck_executions[]` identifies each selected DECK and its individual per-run outcome. `card_executions[]` records the actual path/outcome of every CARD in those selected DECK executions. `card_ids[]` remains a stable identity/reference inventory, not proof that every CARD executed.

`execution_status` and `job_status` record the aggregate run outcome even when no output exists. Per-DECK status/failure context lives in `deck_executions[]`; per-CARD path/outcome lives in `card_executions[]`. `failure_behavior_bindings[]` identifies the source/effective failure policies that governed those paths, including the stable frozen default when materially applicable.

Each `backend_selection_scopes[]` entry binds source CARDs/lower execution units to requested and selected machinery plus automatic-selection policy/tuning identity where applicable. Applicable protected machinery authorization is linked through `machinery_authorization_records[]`.

Each canonical `machinery_requirements[]` row independently records the stable requirement ID, owning source scope/CARD provenance, target selector/class, and complete capability set. Authorization records reference these requirement IDs; a manifest containing only authorization decisions is incomplete when protected machinery requirements are material.

Each `result_determinism_scopes[]`, `numeric_execution_scopes[]`, and `randomness_execution_scopes[]` entry binds its scope identity, source provenance, effective contract/mode, and backend execution-unit identity where useful.

Each `inputs[]` entry binds a declared material input to the exact immutable value/content/artifact identity consumed.

Each `outputs[]` entry binds its artifact/result identity to its own semantic class, result status, mutually consistent evidence status, producer provenance, concrete effect-attempt IDs where applicable, governing execution scopes, exact generated artifacts where applicable, and relevant cache-reuse records.

Each `cache_reuse_records[]` entry makes cold versus reused execution auditable and binds the material cache identity plus any legality/verification evidence supporting substitution.

Each `effect_requirements[]` entry carries source CARD ID, canonical declared effect ID, effect kind, and complete capability set. Every declaration must be accounted for by attempts or an explicit non-attempt reason.

Each Semantic→Core lowering-decision record preserves the rule/scope/transition evidence needed to explain consumed qualifiers, machinery requirements, failure behavior, and determinism/numeric/randomness mappings.

Each Core→Vector/Dataflow mapping record preserves the scope correspondence required to explain how Core machinery/failure/determinism/numeric/randomness contracts became lower execution regions or units.

Each `external_tool_versions[]` entry binds a material external evidence/data producer to stable version/content/model/service identity independently of the QSOL extension profile used to invoke it.

Each `optimization_provenance[]` entry records what transformations actually ran and their legality/evidence context. `optimization_profile` alone is insufficient.

Each `generated_artifacts[]` entry binds a generated kernel/binary or equivalent artifact hash to its backend unit and governing backend-selection scope. Applicable output records link to the exact generated artifact IDs that actually executed.

Not every optional field applies to every execution, but stable JOB, per-DECK, and per-CARD execution identity plus the enclosing execution outcome are material even when a failed or skipped path produces no outputs. No material reproducibility decision may disappear merely because another run would have reached the same bytes by a different path.

The manifest should represent independent reproducibility facets independently rather than collapsing them into false execution-wide singletons.

## Reproducibility versus portability

Portable source does not imply bit-identical execution across every target.

QSOL-MORPH should state the strongest reproducibility guarantee actually provided by a source/backend/contract combination, including the scopes and outputs to which that guarantee applies.

## Failure behavior

An implementation fails closed when a required scoped determinism, numeric, randomness, effect capability, machinery capability, failure behavior, or other frozen execution contract cannot be satisfied.

Silently weakening:

```text
STRICT -> DECLARED-NONDETERMINISTIC
```

or substituting external entropy for a required seeded stream is invalid unless an explicit pre-execution rule authorizes that transition for the affected scope.

Likewise, silently changing fail-stop into continuation/retry or dropping an explicit recovery policy is invalid. Any legal mapping or transition of failure behavior is frozen and provenance-visible.

General execution failure and effect-attempt completion semantics are documented separately in [Failure and Partial-Effect Semantics](FAILURE-AND-PARTIAL-EFFECTS.md).

## Design principle

> Nondeterminism, failure policy, machinery choice and authorization, cache reuse, external tools, optimization decisions, generated-artifact identity, execution path, and external inputs are scientific inputs, not invisible implementation details.
