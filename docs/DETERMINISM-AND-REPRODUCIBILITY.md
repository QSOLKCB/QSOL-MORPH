# Determinism and Reproducibility

QSOL-MORPH is intended for research computing, where performance is useful but reproducibility is part of the scientific contract.

This document describes the candidate determinism and reproducibility model. It is non-normative until the relevant invariants and contracts are frozen.

## Composable reproducibility contract

Determinism is not one enum that mixes result guarantees with randomness configuration.

A future execution contract composes at least these orthogonal facets:

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

Additional facets may cover scheduling, external-service replay, failure/recovery policy, or another independently frozen source of execution variation.

### STRICT result determinism

The same canonical program, immutable declared inputs, implementation identity, and required execution contract produce the same observable result bytes for the governed scope.

### NUMERIC result determinism

Results may differ at the bit level across legal implementations but remain within an explicitly declared numeric contract.

A `NUMERIC` declaration is incomplete without the numeric contract governing the relevant computation. Contracts may be attached at JOB, DECK, CARD, or another frozen scope.

### DECLARED-NONDETERMINISTIC result behavior

The governed computation intentionally permits nondeterministic observable results. The source and trace expose that fact.

### SEEDED randomness

Pseudorandom behavior is reproducible with respect to the recorded RNG algorithm, algorithm version, seed, stream identity, partitioning/stream mapping, and relevant execution contract.

`SEEDED` is not a result-determinism class. A computation may be `STRICT + SEEDED`, `NUMERIC + SEEDED`, or another explicitly frozen combination.

### EXTERNAL-ENTROPY randomness

Acquiring fresh entropy is an externally stateful operation. Any execution that obtains external entropy represents that acquisition as a canonical protected `RANDOM` effect with its own declared effect ID and complete `required_capabilities[]` including `RANDOM` or frozen equivalent.

The randomness mode permits fresh entropy but does not itself authorize entropy access. Each concrete acquisition uses the ordinary per-effect authorization and attempt provenance model.

A randomness scope using `EXTERNAL-ENTROPY` must additionally identify the exact acquisition attempt or attempts that supplied its entropy and, where material to audit or replay, the immutable input identity of the entropy actually consumed. Merely naming the source CARD or randomness mode is insufficient when one CARD can acquire entropy more than once.

## Scoped source contracts

Result-determinism, numeric, randomness, extension, machinery, and failure-behavior requirements remain attached to the canonical scope that owns them.

A JOB may establish a frozen requirement for its DECKs, a DECK may own a requirement for its CARDs, and a CARD may own its own explicit requirement where the normative model permits that composition. The future specification freezes inheritance/refinement rules before execution.

No serializer, lowering, or backend may silently flatten a JOB/DECK contract into an arbitrary child or weaken a parent requirement merely because a target cannot satisfy it.

### Failure-behavior provenance

```text
failure_behavior_bindings[]:
    failure_behavior_binding_id
    scope_kind
    scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
```

`failure_behavior_binding_id` is the stable provenance-record key. Outputs reference that record key through `failure_behavior_binding_ids[]`; the generic governed computation `scope_id` is not an alias for the binding record.

The frozen default fail-stop behavior has a stable identity when it materially governs execution. A manifest must not infer effective failure policy merely from skipped CARDs or DECKs.

## Stable execution-contract scope records

Execution scope records have their own stable type-specific keys. The key of the provenance record is distinct from the generic computation scope it governs.

### Result determinism

```text
result_determinism_scopes[]:
    result_determinism_scope_id
    scope_kind
    scope_id
    source_card_ids[]
    requested_result_determinism
    effective_result_determinism
    transition_authorized_by?
    backend_unit_id?
```

`result_determinism_scope_id` is referenced by output `result_determinism_scope_ids[]`.

### Randomness

```text
randomness_execution_scopes[]:
    randomness_scope_id
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
    entropy_effect_attempt_ids[]?
    entropy_input_ids[]?
    backend_unit_id?
```

`randomness_scope_id` is referenced by output `randomness_scope_ids[]`.

Seeded replay binds algorithm, algorithm version, seed, stream identity, and parallel partitioning/stream mapping wherever they affect the generated sequence.

When `effective_randomness_mode = EXTERNAL-ENTROPY`, `entropy_effect_attempt_ids[]` identifies every protected `RANDOM` acquisition attempt that materially supplied this randomness scope. Each attempt must resolve to a successful contextual authorization record and explicit effect-begin provenance. If the entropy value itself is a material input, `entropy_input_ids[]` identifies the immutable input record(s) actually consumed.

An audit identity or content hash may identify an entropy acquisition without preserving raw secret/random bytes, but such a record does not establish byte-for-byte replayability unless the consumed entropy is reconstructable. The manifest must state the strongest guarantee actually supported.

### Numeric behavior

```text
numeric_execution_scopes[]:
    numeric_scope_id
    scope_kind
    scope_id
    source_card_ids[]
    numeric_contract_id
    numeric_contract_hash
    material_numeric_mode
    backend_unit_id?
```

`numeric_scope_id` is referenced by output `numeric_scope_ids[]`.

`material_numeric_mode` records contract-permitted choices that can change legal result bytes, including FMA behavior, denormal handling, effective precision, reduction strategy, or selected math-library mode.

The three record keys above are type-specific on purpose. Overlapping JOB/CARD/region/kernel computation IDs must not make output references ambiguous.

A single execution-wide scope record is legal only when a frozen normalization proves it faithfully represents every governed source requirement.

## Time and floating point

Wall-clock time is an external input. A deterministic computation must not silently read it.

Floating-point reproducibility is sensitive to fused multiply-add, reassociation, reduction-tree shape, denormal handling, precision contraction/expansion, transcendental-library implementation, and target-specific instructions.

QSOL-MORPH must not call a transformation semantically identical under a strict numeric contract merely because the real-number algebra looks equivalent.

## Parallelism

Parallel execution is not inherently nondeterministic, but deterministic parallel execution may require race-free dataflow, deterministic partitioning, deterministic reductions, controlled atomics, and stable synchronization semantics.

When those requirements cannot be met, execution fails closed unless a weaker contract was explicitly permitted before execution.

## Backend selection and fallback

A governed computation and the ordered machinery decisions made for it are separate objects.

```text
backend_selection_scopes[]:
    backend_selection_scope_id
    scope_kind
    scope_id
    source_card_ids[]
    backend_unit_id?
    selection_decision_ids[]
    final_selection_decision_id?
```

`backend_selection_scope_id` is the stable selection-scope record key. `scope_kind` plus `scope_id` identify the computation being governed and are not aliases for that record key.

```text
backend_selection_decisions[]:
    backend_selection_decision_id
    backend_selection_scope_id
    decision_sequence_index
    requested_target
    selected_backend
    selected_backend_version?
    target_architecture?
    device?
    selection_policy_id?
    selection_policy_version?
    selection_tuning_id?
    selection_tuning_hash?
    predecessor_selection_decision_id?
    fallback_rule_id?
    machinery_authorization_record_ids[]?
    decision_status
```

A denied protected target followed by an authorized fallback remains two ordered decisions. The first decision is not overwritten by the fallback.

## Protected machinery requirements, authorization, and use

Canonical requirements remain present independently of runtime authorization:

```text
machinery_requirements[]:
    machinery_requirement_id
    scope_kind
    scope_id
    source_card_ids[]
    target_selector_or_class
    required_capabilities[]
```

Runtime authorization is separately identified:

```text
machinery_authorization_records[]:
    machinery_authorization_record_id
    backend_selection_scope_id
    backend_selection_decision_id
    source_card_ids[]
    machinery_requirement_ids[]
    required_capabilities[]
    granted_capabilities[]
    denied_capabilities[]
    capability_policy_id
    capability_policy_version
    authorization_status
    authorization_sequence_index?
```

Protected machinery use is also independently identified:

```text
machinery_use_records[]:
    machinery_use_record_id
    backend_selection_scope_id
    backend_selection_decision_id
    backend_unit_id?
    source_card_ids[]
    machinery_authorization_record_ids[]
    protected_use_start_sequence_index
    protected_use_stop_sequence_index?
```

Authorization and protected-use indices belong to one frozen monotonic event-order domain. Every protected use references all applicable successful authorization records, each satisfying:

```text
authorization_sequence_index < protected_use_start_sequence_index
```

Denied machinery has no protected-use start record.

## Generated artifact provenance

```text
generated_artifacts[]:
    generated_artifact_id
    artifact_kind
    artifact_hash
    backend_unit_id
    backend_selection_scope_id
    backend_selection_decision_id?
    source_card_ids[]?
    optimized_ir_hash?
    optimization_record_ids[]?
    toolchain_invocation_ids[]
    artifact_location?
```

A bare hash list is insufficient. When an artifact is generated from optimized IR, its `optimized_ir_hash` and `optimization_record_ids[]` identify the transformation history that produced it. `toolchain_invocation_ids[]` records the ordered exact compiler/assembler/linker/code-generation invocations that materially produced its bytes.

## Toolchain invocation provenance

```text
toolchain_invocations[]:
    toolchain_invocation_id
    invocation_sequence_index
    invocation_kind
    tool_name
    material_tool_identity
    target_or_architecture?
    abi?
    flags[]
    environment_or_config_hash?
    input_ir_hashes[]?
    input_generated_artifact_ids[]?
    output_generated_artifact_ids[]
    backend_unit_id?
    backend_selection_scope_id?
```

`material_tool_identity` must be an immutable/versioned identity adequate to distinguish the actual tool used for the active reproducibility claim, such as version plus executable/content hash, immutable tool artifact ID, or frozen equivalent.

Generated artifacts and toolchain invocations are reciprocally linked. If multiple stages materially produce an artifact, its `toolchain_invocation_ids[]` are ordered so compile/assemble/link or equivalent chains remain reconstructable. A run-wide compiler-version list is summary metadata only and cannot substitute for artifact-specific invocation identity, flags, target/ABI, or configuration.

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
    generated_artifact_ids[]
```

An optimization profile is configuration, not evidence of what actually ran.

Every optimized generated artifact links to its applicable optimization record(s), and those records reciprocally list the generated artifacts. The required join is:

```text
output -> generated_artifact -> optimization_provenance
                         \-> toolchain_invocations
```

## Lowering provenance

Reproducibility binds both mandatory lowering stages.

```text
semantic_to_core_spec_version
semantic_to_core_implementation_version
core_ir_hash
semantic_to_core_result_binding_map[]
extension_requirement_lowering_decisions[]
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
extension_requirement_mapping_decisions[]
machinery_requirement_mapping_decisions[]
core_to_vector_result_determinism_mapping_decisions[]
core_to_vector_numeric_contract_mapping_decisions[]
core_to_vector_randomness_mapping_decisions[]
failure_behavior_mapping_decisions[]
```

Result-binding maps are cardinality-aware identified mapping groups capable of one-to-one preservation/rename, one-to-many split, many-to-one frozen legal fusion, and many-to-many only under an explicit frozen rule.

Binding maps are required whenever result identities are preserved or transformed unless a frozen deterministic rule reconstructs the complete mapping.

Lowering decision records identify both endpoints with typed scope references:

```text
scope_ref:
    scope_kind
    scope_id
```

At the second boundary, every applicable mapping family uses typed `core_scope_refs[]` and `vector_dataflow_scope_refs[]`. Bare scope-ID arrays are not sufficient where namespaces can overlap.

This typed-endpoint rule applies to extension requirements, machinery requirements, result determinism, numeric contracts/modes, randomness, and failure behavior. Mapping families may be omitted only under a frozen deterministic identity-scope reconstruction rule covering that family.

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

Every material input requires a stable `input_id` plus a canonical value or immutable content/artifact identity sufficient to distinguish what was actually consumed.

Paths, URLs, dataset names, and model names are retrieval context, not immutable identity by themselves.

## DECK and CARD execution provenance

Canonical membership alone does not establish execution.

```text
deck_executions[]:
    deck_execution_id
    deck_id
    deck_status
    card_execution_ids[]
    execution_order_index?
    failure_record_id?
```

Every selected DECK remains represented, including a DECK prevented from starting by prior fail-stop.

```text
card_executions[]:
    card_execution_id
    deck_execution_id
    card_id
    card_status
    execution_order_index?
    governing_control_decision_id?
    governing_failure_record_id?
    failure_record_id?
```

`card_id` identifies the canonical semantic CARD. `card_execution_id` identifies one concrete runtime execution. This distinction is material for loops, retries, calls, repeated DECK execution, or another construct that can execute the same CARD more than once.

Candidate statuses include executed success/failure, untaken branch, prior fail-stop, CARD not reached, and explicit frozen skip.

## Typed execution-path causality and failure identity

Control decisions and failures are separate identified namespaces:

```text
control_decisions[]:
    control_decision_id
    card_execution_id
    control_kind
    decision
    sequence_index?
    backend_detail?

failure_records[]:
    failure_record_id
    failing_scope_kind
    failing_scope_id
    failure_class
    failure_stage
    failure_card_id?
    failure_card_execution_id?
    deck_execution_id?
    sequence_index?
    backend_detail?
```

`failing_scope_kind` plus `failing_scope_id` is always present. It identifies the typed runtime or pre-runtime scope where the failure occurred.

For a CARD-caused failure, `failure_card_id` and `failure_card_execution_id` are required and must resolve consistently through `card_executions[]`. For a legitimate pre-CARD failure, such as JOB-scoped contract rejection or protected-machinery denial before CARD execution, those CARD fields are absent rather than fabricated.

An untaken branch references `governing_control_decision_id`. Prior fail-stop or another failure-caused non-reach references `governing_failure_record_id`.

A catch-all `governing_control_or_failure_id` is invalid because it erases the target namespace.

## Per-effect authorization provenance

```text
effect_authorization_records[]:
    effect_authorization_record_id
    effect_attempt_id
    declared_effect_id
    card_id
    card_execution_id
    required_capabilities[]
    granted_capabilities[]
    denied_capabilities[]
    capability_policy_id
    capability_policy_version
    authorization_status
    authorization_sequence_index?
```

Execution-wide capability sets are summaries, not proof that one attempt was authorized.

## Effect declaration and attempt accounting

Runtime attempts carry contextual authorization, explicit begin/end ordering, concrete CARD-execution identity, and output/tool attribution:

```text
effect_attempts[]:
    effect_attempt_id
    declared_effect_id
    card_id
    card_execution_id
    effect_kind
    required_capabilities[]
    effect_authorization_record_id
    sequence_index
    effect_begin_sequence_index?
    effect_end_sequence_index?
    completion_state
    backend_detail?
    observable_output_ids[]
    external_tool_ids[]?
```

Authorization and effect-begin indices live in one frozen monotonic event-order domain. Every protected attempt known to begin satisfies:

```text
authorization_sequence_index < effect_begin_sequence_index
```

Denied authorization has no effect-begin event. Generic `sequence_index` is not authorization-order proof.

A declared effect may legitimately have no runtime attempt for a specific concrete CARD execution:

```text
effect_non_attempt_records[]:
    effect_non_attempt_record_id
    declared_effect_id
    card_id
    card_execution_id
    effect_kind
    non_attempt_reason
    governing_control_decision_id?
    governing_failure_record_id?
    backend_detail?
```

Legitimate candidate reasons include untaken branch, prior fail-stop, CARD not reached, and explicit frozen skip.

`BACKEND_OMISSION_DETECTED` or frozen equivalent means a reachable required effect was omitted. It forces structured execution/conformance failure and cannot coexist with successful enclosing execution.

### Unconditional declaration completeness

For every selected concrete `card_execution_id`, every applicable canonical effect declaration owned by its `card_id` must resolve to:

- one or more identified attempts for that `card_execution_id`; or
- exactly one identified legitimate non-attempt record for that `card_execution_id`; or
- structured failure if accounting cannot be completed or a reachable required effect was omitted.

This is unconditional. There is no profile, backend, optimization, or deployment mode in which declaration-completeness accounting may be silently disabled.

Candidate completion states remain mutually exclusive:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

Known completion takes precedence over uncertainty about broader external consequences.

## External-tool provenance

```text
external_tool_versions[]:
    external_tool_id
    tool_kind
    tool_name_or_service
    material_identity_status
    material_identity_kind?
    material_identity_value?
    endpoint_or_location?
    source_card_ids[]?
    effect_attempt_ids[]?
    output_ids[]?
```

A material external tool, service, model, prover, process, or instrument must not be identified only by a display name or mutable endpoint. `material_identity_status = IDENTIFIED` requires an immutable or versioned `material_identity_value`, such as an executable/content hash, tool version adequate for the active claim, model/version ID, immutable artifact ID, or frozen equivalent.

If material identity cannot be established, record `material_identity_status = UNAVAILABLE` (or frozen equivalent). Replay/evidence claims that depend on exact identity must then be weakened or rejected according to frozen policy rather than silently claiming full reproducibility.

Extension resolution identifies the adapter/profile contract. It does not substitute for the actual tool, service, model, prover, process, or instrument identity.

## Cache reuse provenance

Ordinary result substitution is conservative and effect-free by default. Effectful reuse requires a separately frozen replay/cache semantic preserving declared effects, contextual authorization, ordering, failure behavior, attempt provenance, output attribution, and relevant external state.

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

Verified cache reuse does not prove cold reconstructability.

## Result provenance

```text
outputs[]:
    output_id
    result_binding?
    artifact_hash
    artifact_location?
    semantic_class
    status
    producer_card_ids[]
    producer_card_execution_ids[]
    input_ids[]
    effect_attempt_ids[]?
    external_tool_ids[]?
    backend_selection_scope_ids[]
    generated_artifact_ids[]?
    result_determinism_scope_ids[]
    numeric_scope_ids[]
    randomness_scope_ids[]
    failure_behavior_binding_ids[]
    cache_reuse_record_ids[]?
    evidence_status?
```

`producer_card_ids[]` records canonical semantic producers. `producer_card_execution_ids[]` records the concrete CARD execution(s) that actually produced, materially supplied, or published the output. Each concrete producer ID resolves to `card_executions[]`, which identifies its DECK execution and canonical CARD.

A canonical CARD ID alone is insufficient when a CARD can execute more than once.

`input_ids[]` identifies the exact immutable inputs materially contributing to this output. Execution-wide input availability is not a substitute.

`effect_attempt_ids[]`, where applicable, identifies concrete effect attempts that produced or exposed the output. Each attempt reciprocally lists the output in `observable_output_ids[]`.

`external_tool_ids[]`, where applicable, identifies exact material external tools/services/models/provers.

`generated_artifact_ids[]` identifies the exact generated artifact that executed where applicable and thereby links the output to optimization and toolchain provenance.

`failure_behavior_binding_ids[]` identifies the exact failure-policy provenance records that governed the producer path.

The result-determinism, numeric, randomness, and failure-policy arrays resolve directly to stable record keys defined above.

### Evidence status

```text
evidence_status:
    evidence_class      # TEST / VALIDATION / PROOF / frozen equivalent
    status
    evidence_rule_id?
```

`evidence_class` must be compatible with the output's `semantic_class` and explicit evidence transition. Generic output `status` is non-epistemic and cannot promote TEST into VALIDATION or PROOF.

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
control_decisions[]
failure_records[]
primary_failure_record_id?
execution_status
job_status
failure_behavior_bindings[]
semantic_to_core_spec_version
semantic_to_core_implementation_version
core_ir_hash
semantic_to_core_result_binding_map[]
extension_requirement_lowering_decisions[]
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
extension_requirement_mapping_decisions[]
machinery_requirement_mapping_decisions[]
core_to_vector_result_determinism_mapping_decisions[]
core_to_vector_numeric_contract_mapping_decisions[]
core_to_vector_randomness_mapping_decisions[]
failure_behavior_mapping_decisions[]
morph_version
backend_selection_scopes[]
backend_selection_decisions[]
machinery_requirements[]
machinery_authorization_records[]
machinery_use_records[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
inputs[]
outputs[]
cache_reuse_records[]
resolved_extensions[]
external_tool_versions[]
effect_requirements[]
effect_authorization_records[]
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
toolchain_invocations[]
```

`run_id` identifies the aggregate execution. `job_id` identifies the canonical JOB. `deck_executions[]` and `card_executions[]` identify the concrete runtime path.

`control_decisions[]` and `failure_records[]` provide typed resolvable causes for untaken or blocked CARDs and effect non-attempts. A failure record always identifies its typed failing scope; CARD identity is present only when a CARD execution actually caused that failure.

Every protected machinery use links to all applicable successful authorization records and preserves authorization-before-use ordering.

Every begun protected effect preserves authorization-before-begin ordering and carries its concrete `card_execution_id`.

Every declared effect is unconditionally accounted for per selected concrete CARD execution by attempt, legitimate identified non-attempt, or structured failure.

Every EXTERNAL-ENTROPY randomness scope links to the exact protected RANDOM acquisition attempt(s) and immutable entropy input identity where material.

Every output binds canonical producers **and** concrete CARD execution producers, exact material input IDs, applicable effect attempts/tools, exact generated artifacts, stable execution-contract/failure-policy records, cache reuse, and compatible evidence status.

Every generated artifact binds the exact ordered toolchain invocation chain that materially produced its bytes; run-wide compiler/version summaries are not a substitute.

Every material external tool either has an immutable/versioned identity adequate for the active claim or an explicit identity-unavailable status that weakens that claim.

Every Core-to-Vector/Dataflow contract mapping uses typed scope endpoints so overlapping scope namespaces cannot make source/lower ownership ambiguous.

Every optimized generated artifact links reciprocally to the optimization records that produced it.

Not every optional field applies to every execution, but no material reproducibility decision may disappear merely because another execution path could have produced the same bytes.

## Reproducibility versus portability

Portable source does not imply bit-identical execution across every target.

QSOL-MORPH states the strongest reproducibility guarantee actually provided by a source/backend/contract combination, including the scopes and outputs to which that guarantee applies.

## Failure behavior

An implementation fails closed when a required determinism, numeric, randomness, effect capability, machinery capability, failure behavior, extension, effect-accounting, material-tool identity, toolchain-build provenance, or other frozen execution contract cannot be satisfied.

Silently weakening `STRICT`, substituting external entropy for required seeded replay, acquiring external entropy without a declared/authorized `RANDOM` effect, failing to attribute external entropy to its concrete acquisition attempt, changing fail-stop into continuation, dropping explicit recovery policy, beginning protected work before authorization, losing typed path causality, fabricating a failing CARD for a pre-CARD failure, omitting a reachable required effect, claiming full replay with unavailable material external-tool identity, or claiming reproducible artifact bytes without the material toolchain invocation chain is invalid unless a frozen pre-execution contract explicitly permits the applicable weakening. A reachable-effect omission is not such a permitted transition and produces structured failure.

General execution failure and effect-attempt completion semantics are documented separately in [Failure and Partial-Effect Semantics](FAILURE-AND-PARTIAL-EFFECTS.md).

## Design principle

> Nondeterminism, failure policy, typed execution path, concrete CARD execution identity, machinery-selection history, authorization order, cache reuse, external tools, optimization decisions, toolchain invocations, generated-artifact identity, immutable inputs, and entropy acquisition are scientific inputs, not invisible implementation details.