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

`SEEDED` is not a result-determinism class. A computation may be `STRICT + SEEDED`, `NUMERIC + SEEDED`, or another explicitly frozen combination.

## Scoped source contracts

Result-determinism, numeric, randomness, and failure-behavior requirements remain attached to the canonical scope that owns them.

A JOB may establish a default/frozen requirement for its DECKs, a DECK may own a requirement for its CARDs, and a CARD may have its own explicit requirement where the normative semantic model permits that composition. The future specification must freeze inheritance/refinement rules before executable implementation.

No serializer, lowering, or backend may silently flatten a JOB/DECK contract into an arbitrary child or weaken a parent requirement merely because the target cannot satisfy it.

### Scoped failure-behavior provenance

Failure behavior affects the execution path and is therefore reproducibility-bearing.

```text
failure_behavior_bindings[]:
    scope_kind
    scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
```

An explicit JOB/DECK/CARD recovery, continuation, compensation, or fail-stop policy remains attached to the source scope that owns it. When no explicit policy exists, the frozen default fail-stop behavior has a stable specification identity and may be recorded where it materially determines which later CARDs or DECKs execute.

A manifest must not infer effective failure policy merely from observed skipped CARDs. The policy that caused the path is part of the reproducibility record.

## Scoped result-determinism provenance

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

A single execution-wide entry is legal only when a frozen normalization rule proves that it faithfully represents every governed source requirement.

A recorded transition is evidence, not authorization. If a source requirement cannot be satisfied and no pre-execution rule authorizes a weaker guarantee, execution fails closed.

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

Seeded replay requires algorithm, algorithm version, seed, stream identity, and parallel partitioning/stream mapping wherever those inputs can affect the generated sequence.

## Time

Wall-clock time is an external input. A deterministic computation must not silently read it. Any clock access belongs behind explicit semantics/effect boundaries and must be traced according to the active contract.

## Floating point

Floating-point reproducibility is sensitive to fused multiply-add, reassociation, reduction-tree shape, denormal handling, precision contraction/expansion, transcendental-library implementation, and target-specific instructions.

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

Parallel execution is not inherently nondeterministic, but deterministic parallel execution may require race-free dataflow, deterministic partitioning, deterministic reductions, controlled atomics, and stable synchronization semantics.

When those requirements cannot be met for a governed scope, the implementation must reject the requested result contract unless a weaker contract was explicitly permitted before execution.

For seeded parallel execution, partitioning/stream mapping is part of the scoped replay contract.

## Scoped backend selection and fallback

Automatic and explicit machinery choices are provenance-bearing decisions. A governed computation and the ordered decisions made for it are separate objects.

```text
backend_selection_scopes[]:
    scope_kind
    scope_id
    source_card_ids[]
    backend_unit_id?
    selection_decision_ids[]
    final_selection_decision_id?
```

Each material selection attempt is independently identified:

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

Policy/tuning identity is material when selection is automatic, such as `ON BEST`.

A denied protected target followed by an authorized fallback remains two ordered decisions. The first decision retains its authorization denial and status; the second references the predecessor and frozen fallback rule. `final_selection_decision_id` identifies the decision whose target actually governed execution. A manifest must not overwrite the denied decision with the fallback target.

A single execution-wide selection scope is valid only when one frozen machinery-selection process genuinely governs the whole run.

For a frozen experiment, replay may require the previously final selected target rather than re-running an evolved policy.

## Protected machinery requirements and authorization

Selecting machinery does not itself authorize its use, and machinery selection is not an external Semantic-IR effect.

Canonical requirement rows remain present independently of runtime authorization:

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
```

The requirement rows answer **what the canonical program required**. Authorization records answer **what policy decided for this particular machinery decision**. One cannot replace the other.

For `ON BEST`, target selection may occur first so the applicable machinery requirement is known. All required capabilities must then be granted before protected machinery use starts.

A denied accelerator authorization must not launch a kernel or be represented as a synthetic external effect. Fallback is legal only under a frozen pre-execution rule and remains visible as a later backend-selection decision.

## Generated artifact provenance

Generated kernels, binaries, objects, bytecode, or equivalent artifacts are identified records:

```text
generated_artifacts[]:
    generated_artifact_id
    artifact_kind
    artifact_hash
    backend_unit_id
    backend_selection_scope_id
    backend_selection_decision_id?
    source_card_ids[]?
    artifact_location?
```

`backend_selection_scope_id` identifies the governed selection scope. `backend_selection_decision_id`, where material, identifies the concrete final selection decision that produced the artifact, which is necessary when fallback history exists.

A bare hash list is insufficient provenance. Outputs carry applicable `generated_artifact_ids[]` so reference and optimized executables under the same selection scope remain distinguishable.

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

Result-binding maps use a frozen cardinality-aware representation capable of one-to-one preservation/rename, one-to-many split, many-to-one fusion, and explicitly permitted many-to-many mapping without positional inference.

Binding maps are required whenever result identities are preserved or transformed, except under a frozen deterministic rule that reconstructs the complete mapping.

The Semantic→Core decision records identify how qualifiers, machinery requirements, failure behavior, and determinism/numeric/randomness contracts became QSOL-CORE contracts or preserved metadata.

The Core→Vector/Dataflow mapping records do the same for lower regions/kernels/units. IR hashes identify representations but do not establish binding or contract-scope correspondence by themselves.

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
    external_tool_ids[]?
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

`evidence_class` must be compatible with the output's `semantic_class` and the explicit evidence transition that produced it. The candidate model does not provide independent `test_status`, `validation_status`, and `proof_status` fields because those fields admit contradictory epistemic claims.

Generic output `status` describes result/artifact execution or availability state. It does not promote epistemic class.

`effect_attempt_ids[]`, where applicable, identifies the concrete attempts that produced, published, exposed, or materially supplied the output. Each corresponding attempt reciprocally names the output in `observable_output_ids[]`.

`external_tool_ids[]`, where applicable, identifies the exact tools/services/models/provers that supplied the output, not merely the source CARD or adapter profile.

The execution-scope references identify the exact machinery, determinism, numeric, and randomness context governing each output. `generated_artifact_ids[]` identifies the exact generated artifact that ran where applicable.

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

Paths, URLs, dataset names, model names, and similar locators are retrieval context, not reproducibility evidence by themselves.

## External-tool provenance

Extension resolution identifies the QSOL adapter/profile contract; it does not identify the external tool, service, model, prover, process, or instrument that supplied evidence or data.

```text
external_tool_versions[]:
    external_tool_id
    tool_kind
    tool_name_or_service
    version?
    content_hash_or_model_id?
    endpoint_or_location?
    source_card_ids[]?
    effect_attempt_ids[]?
    output_ids[]?
```

The record must contain enough immutable version/content/model/service identity to distinguish a material change in the external evidence producer.

When one CARD invokes several tools or retries against different versions, `source_card_ids[]` alone is not sufficient attribution. Material tool records therefore link to concrete effect attempts and/or outputs, with reciprocal `external_tool_ids[]` on those records where applicable.

## Cache reuse provenance

Cache legality and cache provenance are distinct.

Ordinary result substitution is conservative and effect-free by default. Effectful reuse requires a separately frozen replay/cache semantic preserving declared effects, contextual authorization, ordering, failure behavior, attempt provenance, and output attribution.

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

Verified cache reuse does not prove cold reconstructability. That claim needs separate cold-execution or equivalent evidence.

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

## Per-effect authorization provenance

Execution-wide capability sets are summaries, not proof that a particular effect attempt was authorized.

Each identified protected effect attempt therefore links to an authorization decision:

```text
effect_authorization_records[]:
    effect_authorization_record_id
    effect_attempt_id
    declared_effect_id
    card_id
    required_capabilities[]
    granted_capabilities[]
    denied_capabilities[]
    capability_policy_id
    capability_policy_version
    authorization_status
    authorization_sequence_index?
```

Every required capability must be granted by the authorization record for that attempt before the protected effect begins. If an attempt has been created but authorization is denied, its completion state remains `NOT_STARTED` and the denial record remains provenance-visible.

## Effect declaration and attempt accounting

A declared protected effect does not necessarily produce a runtime attempt. Its CARD may be on an untaken branch, may never be reached after prior fail-stop failure, or may be explicitly skipped by a frozen execution rule.

Every declaration is accounted for by either one or more `effect_attempts[]` records or an explicit `effect_non_attempt_records[]` entry.

```text
effect_non_attempt_records[]:
    declared_effect_id
    card_id
    effect_kind
    non_attempt_reason
    governing_control_or_failure_id?
    backend_detail?
```

Legitimate candidate reasons include `UNTAKEN_BRANCH`, `PRIOR_FAIL_STOP`, `CARD_NOT_REACHED`, and `EXPLICIT_SKIP` or frozen equivalents.

`BACKEND_OMISSION_DETECTED` (or frozen equivalent) means a reachable required effect was omitted by the implementation. It is not a successful non-attempt classification: it forces structured execution/conformance failure and cannot coexist with successful enclosing execution status.

Runtime attempts carry contextual authorization and concrete result/tool attribution:

```text
effect_attempts[]:
    effect_attempt_id
    declared_effect_id
    card_id
    effect_kind
    required_capabilities[]
    effect_authorization_record_id
    sequence_index
    completion_state
    backend_detail?
    observable_output_ids[]
    external_tool_ids[]?
```

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

Candidate statuses include `EXECUTED_SUCCESS`, `EXECUTED_FAILED`, `UNTAKEN_BRANCH`, `PRIOR_FAIL_STOP`, `CARD_NOT_REACHED`, and `EXPLICIT_SKIP` or frozen equivalents.

This is material even for pure CARDs. A TEST on an untaken branch may produce no output, effect, or failure but is semantically different from a TEST that executed successfully.

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

Every DECK selected for the JOB execution remains represented. A later DECK prevented from starting by fail-stop records an explicit non-started/skipped status or frozen equivalent rather than disappearing.

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
backend_selection_decisions[]
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
```

`run_id` identifies the aggregate execution event. `job_id` identifies the stable canonical JOB selected for that run. `deck_executions[]` identifies each selected DECK and its individual outcome. `card_executions[]` records the actual path/outcome of every CARD in those selected DECK executions. `card_ids[]` remains an identity/reference inventory, not proof of execution.

`execution_status` and `job_status` record the aggregate outcome even when no output exists. Per-DECK status/failure context lives in `deck_executions[]`; per-CARD path/outcome lives in `card_executions[]`. `failure_behavior_bindings[]` identifies the source/effective failure policies governing those paths.

Each `backend_selection_scopes[]` entry identifies a governed source/lower unit and its ordered selection-decision IDs. `backend_selection_decisions[]` preserves each target decision, denial/fallback transition, selection-policy/tuning identity, and final decision rather than overwriting the history.

Each canonical `machinery_requirements[]` row independently records the stable requirement and required capabilities. `machinery_authorization_records[]` bind those requirements to specific backend-selection decisions and policy outcomes.

Each `result_determinism_scopes[]`, `numeric_execution_scopes[]`, and `randomness_execution_scopes[]` entry binds its own scope identity and effective execution contract.

Each `inputs[]` entry binds a declared material input to the exact immutable value/content/artifact identity consumed.

Each `outputs[]` entry binds its identity to semantic class, generic result status, compatible class-discriminated evidence status, producer CARDs, concrete effect attempts and external tools where applicable, governing execution scopes, exact generated artifacts, and relevant cache-reuse records.

Each `cache_reuse_records[]` entry makes cold versus reused execution auditable.

Each `effect_requirements[]` entry carries the source CARD ID, declared effect ID, effect kind, and complete capability set. Every declaration must be accounted for by attempts or an explicit legitimate non-attempt reason; a detected reachable-effect omission is itself failure.

Each `effect_authorization_records[]` entry proves which policy evaluated one concrete attempt and which complete capability set was granted or denied.

Each Semantic→Core lowering-decision record preserves the rule/scope/transition evidence needed to explain consumed qualifiers, machinery requirements, failure behavior, and determinism/numeric/randomness mappings.

Each Core→Vector/Dataflow mapping record preserves the scope correspondence required to explain how Core machinery/failure/determinism/numeric/randomness contracts became lower execution regions or units.

Each `external_tool_versions[]` entry binds a material external evidence/data producer to stable version/content/model/service identity and, where material, to the concrete attempts/outputs it served.

Each `optimization_provenance[]` entry records what transformations actually ran and their legality/evidence context. `optimization_profile` alone is insufficient.

Each `generated_artifacts[]` entry binds an artifact to its backend unit, selection scope, and concrete selection decision where fallback history makes that identity material. Applicable outputs link to the exact generated artifacts that actually executed.

Not every optional field applies to every execution, but no material reproducibility decision may disappear merely because another run could have reached the same bytes by a different path.

## Reproducibility versus portability

Portable source does not imply bit-identical execution across every target.

QSOL-MORPH should state the strongest reproducibility guarantee actually provided by a source/backend/contract combination, including the scopes and outputs to which that guarantee applies.

## Failure behavior

An implementation fails closed when a required scoped determinism, numeric, randomness, effect capability, machinery capability, failure behavior, or other frozen execution contract cannot be satisfied.

Silently weakening `STRICT` to nondeterministic behavior, substituting external entropy for a required seeded stream, changing fail-stop into continuation, dropping an explicit recovery policy, or omitting a reachable required effect is invalid unless a frozen pre-execution contract explicitly permits the applicable transition. A reachable-effect omission is not a permitted transition and produces structured failure.

General execution failure and effect-attempt completion semantics are documented separately in [Failure and Partial-Effect Semantics](FAILURE-AND-PARTIAL-EFFECTS.md).

## Design principle

> Nondeterminism, failure policy, machinery-selection history, authorization, cache reuse, external tools, optimization decisions, generated-artifact identity, execution path, and external inputs are scientific inputs, not invisible implementation details.
