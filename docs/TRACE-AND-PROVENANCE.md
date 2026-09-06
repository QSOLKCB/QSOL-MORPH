# Trace and Provenance

QSOL-MORPH treats provenance as part of execution semantics for research workflows.

The goal is not merely to say that a program ran. The trace should make it possible to answer:

- what source and canonical Semantic IR were executed;
- which JOB, DECKs, and CARDs were selected and which actually executed;
- how Semantic IR lowered into QSOL-CORE;
- how QSOL-CORE lowered into the mandatory Vector/Dataflow IR;
- how result bindings and execution-contract scopes were preserved, renamed, split, fused, grouped, or otherwise mapped at each lowering boundary;
- which protected-machinery requirements survived each lowering and which authorization decisions governed their eventual use;
- which machinery-selection decisions were considered, denied, superseded, or finally used for each governed scope;
- why automatic machinery selection or fallback chose each target;
- whether protected machinery was authorized before use and what ordered trace evidence proves authorization completed before protected use began;
- whether each protected external effect was authorized before it began and what ordered trace evidence proves that relation;
- which typed control decision or identified failure record explains every untaken, skipped, or fail-stop-blocked execution path where such a cause is material;
- what exact immutable inputs were consumed and which material inputs contributed to each identified output;
- what result-determinism, numeric, randomness, and failure-behavior contracts governed each relevant scope;
- what extension contracts were resolved and how their owning scopes mapped through both mandatory lowerings;
- which external tools, services, models, provers, processes, or instruments materially contributed to each applicable attempt/output;
- what protected effects were declared, which capability sets belonged to them, which authorization decision governed each attempt, which runtime attempts occurred, and why any declaration had no attempt;
- which concrete effect attempts produced or exposed each applicable output;
- what generated artifacts were produced, which exact artifacts produced each applicable output, and which optimization provenance governed each optimized artifact;
- what optimizations actually ran and under which legality evidence;
- what identified outputs were produced, what semantic class/status belongs to each one, and what evidence-status claim is valid for each output;
- whether cache reuse occurred and what was reused;
- whether execution failed and what prior effects or artifacts were already observable.

## Trace layers

A future trace may contain several connected layers:

```text
SOURCE TRACE
SEMANTIC TRACE
SEMANTIC-TO-CORE TRACE
CORE-TO-VECTOR/DATAFLOW TRACE
MORPH TRACE
EXECUTION TRACE
RESULT TRACE
```

These layers describe different objects and must not be collapsed merely because one implementation stores them in one manifest.

## Source trace

Potential fields include:

```text
source_hash
spec_version
run_id?
job_id
deck_ids[]
source_location
```

Stable JOB/DECK/CARD identities originate in the canonical semantic model. A trace records them; it does not synthesize or renumber them.

## Semantic trace

Potential fields include:

```text
semantic_ir_hash
job_ids[]
deck_ids[]
card_ids[]
dependency_graph_hash
epistemic_class_bindings[]
extension_requirements[]
effect_requirements[]
machinery_requirements[]
result_determinism_bindings[]
numeric_contract_bindings[]
randomness_contract_bindings[]
failure_behavior_bindings[]
```

### Epistemic class bindings

The semantic trace binds epistemic meaning directly to stable CARD identity.

```text
epistemic_class_bindings[]:
    card_id
    semantic_class
```

Every applicable semantic class is paired with the canonical `card_id` that owns it. Separate `card_ids[]` and `epistemic_classes[]` arrays are not an acceptable positional association. Any class transition requires a frozen evidence-transition rule and provenance.

### Declared effect requirements

The semantic trace preserves the canonical effect-to-capability association.

```text
effect_requirements[]:
    declared_effect_id
    card_id
    effect_kind
    required_capabilities[]
```

`declared_effect_id` corresponds to canonical `EffectRequirement.effect_id`. The complete capability set belongs to that specific protected effect.

A CARD may declare several effects with different permission sets. An ambiguous CARD-wide capability union does not replace those associations.

### Protected machinery requirements

Protected machinery permission is represented separately from external effects.

```text
machinery_requirements[]:
    machinery_requirement_id
    scope_kind
    scope_id
    source_card_ids[]
    target_selector_or_class
    required_capabilities[]
```

A `GPU` machinery requirement does not turn GPU selection into a Semantic-IR effect. It says that if the governed computation resolves to that protected machinery class, the required machinery capabilities must be authorized before the machinery is used.

Every canonical machinery requirement that can affect target legality or authorization must remain traceable through both mandatory lowerings. A later authorization record references these stable requirement IDs rather than reconstructing requirements from target names.

### Source contract bindings

Result determinism, numeric behavior, randomness, and failure behavior remain scoped.

Conceptually:

```text
result_determinism_bindings[]:
    scope_kind
    scope_id
    source_card_ids[]
    requested_result_determinism

numeric_contract_bindings[]:
    scope_kind
    scope_id
    source_card_ids[]
    numeric_contract_id
    numeric_contract_hash

randomness_contract_bindings[]:
    scope_kind
    scope_id
    source_card_ids[]
    requested_randomness_mode

failure_behavior_bindings[]:
    scope_kind
    scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
```

The owning source scope may be a JOB, DECK, CARD, or another scope explicitly frozen by the semantic model.

When no explicit source failure policy exists, the frozen default fail-stop behavior has a stable specification identity and may be recorded as the requested/effective failure behavior when it materially governs the execution path. A trace must not leave default behavior implicit when doing so would prevent reconstruction of why later CARDs or DECKs did not execute.

A trace must not collapse distinct source requirements into one execution-wide declaration unless a frozen normalization rule proves that the collapse is lossless and provenance-visible.

## Semantic-to-Core trace

The Semantic IR → QSOL-CORE transition is independently provenance-bearing.

Potential fields include:

```text
semantic_ir_hash
semantic_to_core_spec_version
semantic_to_core_implementation_version
core_ir_hash
result_binding_map[]
resolved_extensions[]
extension_requirement_lowering_decisions[]
qualifier_lowering_decisions[]
machinery_requirement_lowering_decisions[]
result_determinism_lowering_decisions[]
numeric_contract_lowering_decisions[]
randomness_lowering_decisions[]
failure_behavior_lowering_decisions[]
lowering_diagnostics[]
```

The canonical identity field names are `semantic_to_core_spec_version` and `semantic_to_core_implementation_version`. Unprefixed aliases must not be invented unless a future frozen schema explicitly defines them.

### Cardinality-aware result-binding maps

A result-binding map must represent mapping cardinality explicitly.

One candidate conceptual shape is:

```text
result_binding_map[]:
    mapping_group_id
    source_bindings[]:
        source_card_id?
        binding_id
    lower_bindings[]:
        binding_id
    mapping_rule_id?
```

This supports:

- one source binding to one lower binding for preservation or rename;
- one source binding to several lower bindings for a split;
- several source bindings to one lower binding for a frozen legal fusion;
- several source bindings to several lower bindings only when a frozen rule explicitly permits that mapping.

`source_bindings[]` and `lower_bindings[]` must use deterministic canonical ordering. Positional parallel arrays are not sufficient. A consumer must be able to identify all lower identities originating from a source binding and all source identities contributing to a fused lower binding without guessing from array position or value equality.

A result-binding map is required whenever result identities are preserved or transformed unless a frozen rule permits deterministic reconstruction of the complete identity mapping. IR hashes alone do not establish binding correspondence.

### First-lowering contract decisions

Qualifier, machinery-requirement, result-determinism, numeric, randomness, failure-behavior, and extension decision records explain scope preservation, grouping, normalization, identity changes, and other frozen lowering choices.

A decision record should retain the source scope(s), resulting Core scope(s), source CARD identities, applicable frozen mapping/normalization rule, and any preauthorized transition identity when those details are material.

Extension requirements need their own scope-preserving mapping family because resolved extension identity alone does not establish ownership. A candidate record is:

```text
extension_requirement_lowering_decisions[]:
    source_scope_kind
    source_scope_id
    core_scope_ids[]
    source_card_ids[]
    profile_name
    resolved_version_or_content_identity
    contract_id_or_hash?
    mapping_rule_id
```

A JOB- or DECK-owned extension requirement must not be silently relocated to a CARD or detached from the lower Core scope(s) it governs. This mapping family may be omitted only when a frozen deterministic identity-scope reconstruction rule proves the source and Core extension scopes correspond without loss.

If a machinery requirement or failure behavior is preserved by identity, a decision record may be omitted only when a frozen deterministic reconstruction rule establishes that preservation. Generic metadata or IR hashes are not such a rule.

## Core-to-Vector/Dataflow trace

The mandatory QSOL-CORE → Vector/Dataflow IR transition is a separate provenance-bearing transformation.

Potential fields include:

```text
core_ir_hash
vector_dataflow_spec_version
vector_dataflow_implementation_version
vector_dataflow_ir_hash
result_binding_map[]
extension_requirement_mapping_decisions[]
machinery_requirement_mapping_decisions[]
core_to_vector_result_determinism_mapping_decisions[]
core_to_vector_numeric_contract_mapping_decisions[]
core_to_vector_randomness_mapping_decisions[]
failure_behavior_mapping_decisions[]
vector_dataflow_lowering_diagnostics[]
```

This stage uses the same frozen cardinality-aware `result_binding_map[]` semantics. A one-to-many lower split must appear as one mapping group containing multiple `lower_bindings[]`, not as a scalar field that can name only one lower result.

### Second-lowering contract mappings

The second lowering must preserve how QSOL-CORE execution-contract scopes correspond to lower Vector/Dataflow scopes.

Each mapping-decision family may conceptually contain:

```text
core_scope_ids[]
vector_dataflow_scope_ids[]
source_card_ids[]
mapping_rule_id
backend_unit_ids[]?
transition_authorized_by?
```

Use the applicable family for extension requirements, result determinism, numeric contracts/modes, randomness, protected-machinery requirements, and failure behavior.

For extension requirements, `extension_requirement_mapping_decisions[]` must additionally retain the applicable profile/version/content/contract identity so a lower region or backend unit cannot inherit an extension contract by positional or naming inference.

If a Core scope is split into multiple kernels, several Core scopes are fused into a region, or lower scope identity otherwise changes, the mapping must be provenance-visible.

The extension, result-determinism, numeric, and randomness mapping arrays may be omitted only when a frozen deterministic identity-scope reconstruction rule proves that the Core and Vector/Dataflow contract scopes correspond without loss. The same principle applies to machinery/failure mapping decisions. IR hashes alone are not a reconstruction rule.

If the Vector/Dataflow lowering implementation, specification, control representation, effect ordering, extension ownership, machinery requirements, capability metadata, binding mapping, failure behavior, or numeric/randomness structure changes, provenance must distinguish the resulting lower IR.

## MORPH trace

Potential fields include:

```text
vector_dataflow_ir_hash
morph_version
optimization_profile
optimization_provenance[]
backend_selection_scopes[]
backend_selection_decisions[]
machinery_authorization_records[]
machinery_use_records[]
generated_artifacts[]
vectorization_decisions[]
fusion_decisions[]
memory_placement_decisions[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
failure_behavior_bindings[]
```

## Scoped backend-selection provenance

Backend selection may differ across a JOB, and a governed scope may undergo more than one material selection decision when a frozen fallback rule applies.

The backend-selection scope record has its own stable identity, separate from the computation scope it governs. The governed computation is represented by `scope_kind` + `scope_id`; references from decisions, authorizations, generated artifacts, and outputs use `backend_selection_scope_id`:

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

`backend_selection_scope_id` is the stable record key referenced by `backend_selection_decisions[]`, `machinery_authorization_records[]`, `machinery_use_records[]`, `generated_artifacts[]`, and output `backend_selection_scope_ids[]`. `scope_id` identifies the source/Core/lower computation scope being governed and must not be treated as an implicit alias for the selection-scope record ID.

Each material decision is independently identified:

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

Selection-policy and tuning identity are material when selection is automatic, such as `ON BEST`.

A single execution-wide selection scope is valid only when one frozen machinery-selection process genuinely governs the whole execution. Explicit host targeting on one CARD and `ON BEST` on another remain separate scopes even if they eventually resolve to the same backend.

A denied protected target followed by an authorized fallback remains two ordered decisions. The first decision retains its authorization denial/status; the second references the predecessor and frozen fallback rule. `final_selection_decision_id` identifies which decision actually governed execution. A producer must not overwrite the denied decision with the fallback target.

Selecting a target is not equivalent to authorizing protected use of that target.

## Machinery authorization provenance

Protected machinery access has provenance separate from external effect attempts.

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

For an automatic target such as `ON BEST`, selection may occur first so the applicable machinery class is known. Every required machinery capability must then be authorized **before protected use of the selected machinery begins**.

When that ordering is material, protected use is represented explicitly:

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

`authorization_sequence_index` and `protected_use_start_sequence_index` are values in the same frozen monotonic event-order domain. Every protected machinery use references all applicable successful authorization records, and every required authorization must satisfy:

```text
authorization_sequence_index < protected_use_start_sequence_index
```

A record that merely says “authorized” without preserving an order relation to protected-use start is insufficient to prove the pre-use authorization invariant. If required ordering evidence cannot be established, execution/conformance fails closed for claims that require protected-machinery auditability.

A denied GPU authorization must not launch a GPU kernel, must not have a corresponding protected-use start record, and must not be represented as a fake external effect attempt. A fallback to another target is legal only under a frozen pre-execution selection/fallback rule and appears as a later backend-selection decision with its own authorization where applicable.

## Generated artifact provenance

Generated kernels, binaries, object files, bytecode, or equivalent target artifacts are identified records.

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
    artifact_location?
```

`backend_unit_id` identifies the lower execution/code-generation unit that produced the artifact. `backend_selection_scope_id` identifies the governed machinery-selection scope. `backend_selection_decision_id`, when material, identifies the final concrete decision whose target produced the artifact, which is required to disambiguate fallback histories.

When an artifact is generated from optimized IR, `optimized_ir_hash` and `optimization_record_ids[]` bind that concrete artifact to the actual transformation sequence and legality evidence that produced it. The referenced optimization records reciprocally list the applicable `generated_artifact_ids[]`. A reference/no-transform artifact may omit optimization links only under a frozen deterministic rule proving that no material optimization decision intervened.

A mixed-backend JOB may produce several same-kind artifacts. Their hashes alone do not establish which target decision or optimization history produced which artifact.

A backend-selection scope may govern several generated artifacts, including reference and optimized variants. Output provenance therefore records applicable `generated_artifact_ids[]` so an output identifies the exact generated artifact that actually produced or supplied it, and the artifact in turn identifies the optimization provenance that governed it.

## Scoped result-determinism provenance

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

`result_determinism_scope_id` is the stable record key referenced by output `result_determinism_scope_ids[]`. `scope_kind` + `scope_id` identify the governed computation and are not an implicit alias for this record key. Multiple execution records may govern the same computation scope only when each remains independently identified and the frozen composition rule is traceable.

A scope may be retained from source or introduced by a semantics-preserving lowering. Grouping must preserve the strongest applicable requirements or follow another frozen normalization rule that is provenance-visible.

A recorded transition is evidence, not authorization. If a requested guarantee cannot be satisfied and no pre-execution rule authorizes a weaker guarantee, execution fails closed.

## Scoped numeric provenance

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

`numeric_scope_id` is the stable record key referenced by output `numeric_scope_ids[]`; it is separate from the governed computation `scope_id`.

Material numeric choices may include FMA behavior, denormal handling, effective precision, reduction strategy, selected math-library mode, or another frozen numeric-mode identity.

A single execution-wide numeric scope is valid only when a frozen rule establishes that one contract and one material mode govern the entire execution.

## Scoped randomness provenance

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
    backend_unit_id?
```

`randomness_scope_id` is the stable record key referenced by output `randomness_scope_ids[]`; it is separate from the governed computation `scope_id`.

Seeded replay requires more than an integer seed. Where applicable, RNG algorithm, version, seed, stream identity, and parallel partitioning/stream mapping are material inputs.

A single execution-wide randomness scope is valid only under a frozen lossless normalization rule.

For `EXTERNAL-ENTROPY`, the randomness scope records the permitted/effective randomness mode, while the entropy acquisition itself remains a declared protected `RANDOM` effect with contextual capability authorization and concrete attempt provenance. The scope record is not authorization to access an entropy source.

## Execution trace

Potential fields include:

```text
run_id
job_id
deck_executions[]
card_executions[]
control_decisions[]
failure_records[]
runtime_compiler_versions[]
backend_selection_scopes[]
backend_selection_decisions[]
machinery_requirements[]
machinery_authorization_records[]
machinery_use_records[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
failure_behavior_bindings[]
inputs[]
required_capabilities[]
granted_capabilities[]
denied_capabilities[]
capability_policy_id
capability_policy_version
capabilities_used[]
resolved_extensions[]
effect_requirements[]
effect_authorization_records[]
effect_attempts[]
effect_non_attempt_records[]
cache_reuse_records[]
external_tool_versions[]
start_stop_metadata?
```

Global capability sets describe the execution-wide decision space, but they do not replace per-effect or per-machinery requirement/authorization records.

## Per-DECK and per-CARD execution provenance

Membership in the canonical program does not prove that a semantic unit executed.

```text
deck_executions[]:
    deck_execution_id
    deck_id
    deck_status
    card_execution_ids[]
    execution_order_index?
    failure_record_id?
    failure_card_id?
    failure_class?
    failure_stage?
```

A DECK prevented from starting by prior fail-stop remains visible with an explicit non-started/skipped status or frozen equivalent. `failure_record_id`, when present, identifies the structured failure event that caused or summarizes the DECK outcome; the aggregate failure fields may be retained as convenient summaries but do not replace the identified record.

```text
card_executions[]:
    card_execution_id
    deck_execution_id
    card_id
    card_status
    execution_order_index?
    governing_control_decision_id?
    governing_failure_record_id?
    failure_class?
    failure_stage?
```

Candidate `card_status` values may include `EXECUTED_SUCCESS`, `EXECUTED_FAILED`, `UNTAKEN_BRANCH`, `PRIOR_FAIL_STOP`, `CARD_NOT_REACHED`, `EXPLICIT_SKIP`, or frozen equivalents.

This matters even for pure CARDs. A TEST on an untaken branch may have no output, effect, or failure record, but it must still be distinguishable from a TEST that executed successfully.

### Typed execution-path causes

Execution-path causes use typed, resolvable references rather than one untyped ID namespace.

A candidate control-decision ledger is:

```text
control_decisions[]:
    control_decision_id
    deck_execution_id
    control_card_id
    control_kind
    decision_outcome
    selected_successor_or_scope_id?
    decision_sequence_index?
    backend_detail?
```

`control_decision_id` identifies the concrete branch/jump/mask/dispatch or frozen equivalent decision that governed an execution path. An `UNTAKEN_BRANCH` CARD or effect declaration should reference the applicable `governing_control_decision_id` when that cause is known and material.

Failures use a separate identified namespace:

```text
failure_records[]:
    failure_record_id
    deck_execution_id?
    card_execution_id?
    failure_card_id
    failure_class
    failure_stage
    failure_sequence_index?
    backend_detail?
```

`failure_record_id` identifies the structured failure event. `failure_card_id` retains the canonical meaning of the CARD whose unhandled failure produced that record. `PRIOR_FAIL_STOP` or `CARD_NOT_REACHED` caused by failure should reference the applicable `governing_failure_record_id`.

A producer must not put a control-decision ID into a failure field, put a failure-record ID into a control field, or rely on identifier-string shape to infer the target namespace. If both control and failure materially contribute to one path, the frozen composition rule must define whether both typed references are present and how their precedence is interpreted.

## Identified input provenance

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

A path, URL, dataset name, model name, branch name, or other mutable locator is retrieval context only. It must not substitute for immutable input identity.

If a material input contributes to a research result and the required immutable identity cannot be established, replay/provenance validation fails closed where the active contract requires auditability.

Identified inputs are execution-wide records, but output attribution is not inferred from mere availability. Each applicable `outputs[]` record references the exact materially contributing inputs through `input_ids[]` under the frozen provenance-dependency rule.

## Capability provenance

Capability provenance distinguishes requirement, authorization, and use.

Execution-wide summaries may record:

```text
required_capabilities = [NETWORK]
granted_capabilities = []
denied_capabilities = [NETWORK]
capability_policy_id = ...
capability_policy_version = ...
capabilities_used = []
```

These summaries are not sufficient to prove authorization for an individual protected effect attempt.

### Per-effect authorization provenance

Every identified protected external effect attempt has a contextual authorization record.

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

The authorization record establishes exactly which policy evaluated this attempt and what complete capability set was granted or denied in that context. An implementation must not infer per-attempt authorization from execution-wide capability unions because the same capability may be permitted for one scope/effect and denied for another.

Authorization must complete successfully before the protected effect begins. `authorization_sequence_index` and the attempt's `effect_begin_sequence_index` are values in the same frozen monotonic event-order domain whenever effect-order auditability is required. Every protected effect known to have begun must satisfy:

```text
authorization_sequence_index < effect_begin_sequence_index
```

A denied authorization must not have a corresponding effect-begin event. If an attempt object has already been created and authorization is denied, that attempt remains `NOT_STARTED`, carries no `effect_begin_sequence_index`, and links to the denial record. A generic attempt `sequence_index` is not a substitute for this authorization-before-begin proof unless a future frozen schema explicitly defines it in the same event-order domain.

Protected machinery authorization remains separate through `machinery_authorization_records[]` and ordered `machinery_use_records[]`; machinery selection is not an external effect.

External entropy acquisition, however, is an externally stateful operation and therefore uses the protected-effect model: it must be declared as a `RANDOM` effect, require the `RANDOM` capability or frozen equivalent, and link each concrete acquisition attempt to its authorization record before acquisition begins.

## Resolved extension provenance

```text
resolved_extensions[]:
    profile_name
    resolved_version
    contract_id_or_hash
    implementation_or_content_identity?
```

A profile name alone is insufficient if different versions can change lowering, effects, or results. Resolved identity also does not replace the scope-mapping records required when an extension requirement is JOB-, DECK-, CARD-, Core-, or lower-region-scoped.

## External-tool provenance

The QSOL extension/profile used to invoke a tool is not the same object as the external tool, service, model, prover, process, or instrument that actually produced evidence or data.

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

The record must preserve enough immutable version/content/model/service identity to distinguish material changes in the external evidence producer.

When one source CARD invokes multiple tools, retries against different model/prover versions, or receives distinct evidence from different services, `source_card_ids[]` alone is not sufficient attribution. Material tool records therefore link to the concrete effect attempts and/or outputs they served. The corresponding attempts/outputs carry reciprocal `external_tool_ids[]` where material.

## Per-effect-attempt provenance

Every protected external effect attempt has its own runtime identity and a reference to the declared semantic effect that produced it.

```text
effect_attempts[]:
    effect_attempt_id
    declared_effect_id
    card_id
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

`declared_effect_id` references canonical `EffectRequirement.effect_id`. `effect_attempt_id` identifies the concrete runtime attempt. They are not interchangeable.

`effect_authorization_record_id` identifies the contextual decision that granted or denied this attempt's complete required capability set. A successful effect attempt cannot exist without a successful applicable authorization record under the frozen authorization contract.

`effect_begin_sequence_index` is the ordered event proving when protected effect execution actually began. `effect_end_sequence_index`, when known and material, records the completion/abort/stop event in the same frozen event-order domain. `NOT_STARTED` attempts have no begin event. Every attempt known to have begun carries a begin event when the active auditability contract requires ordering proof.

`observable_output_ids[]` contains stable output IDs this attempt actually produced, published, exposed, or materially supplied. An output produced by an external effect carries the reciprocal `effect_attempt_ids[]` reference.

`external_tool_ids[]`, when present, identifies the concrete tools/services/models/provers used by this attempt rather than merely the extension adapter or source CARD.

### Declared effects with no runtime attempt

Every declared effect is accounted for by either one or more `effect_attempts[]` records or an explicit non-attempt record when no runtime attempt object exists.

```text
effect_non_attempt_records[]:
    declared_effect_id
    card_id
    effect_kind
    non_attempt_reason
    governing_control_decision_id?
    governing_failure_record_id?
    backend_detail?
```

Legitimate candidate reasons may include `UNTAKEN_BRANCH`, `PRIOR_FAIL_STOP`, `CARD_NOT_REACHED`, `EXPLICIT_SKIP`, or frozen equivalents.

`UNTAKEN_BRANCH` should resolve to an applicable `control_decisions[]` record when the cause is available. `PRIOR_FAIL_STOP` and failure-caused `CARD_NOT_REACHED` should resolve to an applicable `failure_records[]` record. An explicit skip may use a separate frozen policy/rule identity if it is not caused by control flow or failure. Typed references prevent a consumer from guessing whether an opaque ID names a branch decision or a failure event.

`BACKEND_OMISSION_DETECTED` (or a frozen equivalent) is qualitatively different: it means a reachable required effect was not attempted because the implementation/backend failed to honor the semantic program. Recording that reason **must force structured execution/conformance failure**. It cannot be treated as an ordinary successful non-attempt path and cannot coexist with a successful enclosing execution status. The resulting structured omission failure should itself have an identified `failure_record_id` when the frozen failure schema requires complete causal linkage.

An effect declaration with neither an attempt nor an explicit non-attempt reason is incomplete provenance when declaration-completeness auditing is required.

Capability denial after an attempt has been identified but before the effect begins remains an `effect_attempts[]` record with `completion_state = NOT_STARTED` plus an identified denial authorization record; it is not silently converted into a non-attempt record.

### Completion states

`completion_state` is one of:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

or frozen equivalents.

The candidate states are mutually exclusive and evaluated in this order:

```text
1. NOT_STARTED
   The protected effect never began.

2. COMPLETED
   The effect reached its defined completion boundary.

3. If the effect began and is known not to have completed:
   ABORTED_CLEAN  no externally observable change occurred
   PARTIAL        some incomplete portion became observable
   UNKNOWN        clean-vs-partial observability cannot be established

4. UNKNOWN
   Whether the effect reached its completion boundary cannot be established.
```

Known completion takes precedence over uncertainty about broader consequences. Successful executions record completed effect attempts too.

## Result trace

Results are identified records rather than bare hashes plus one shared semantic class.

```text
outputs[]:
    output_id
    result_binding?
    artifact_hash
    artifact_location?
    semantic_class
    status
    producer_card_ids[]
    input_ids[]
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

When present, `evidence_status` is one class-discriminated record rather than several independent booleans/statuses:

```text
evidence_status:
    evidence_class      # TEST / VALIDATION / PROOF / frozen equivalent
    status
    evidence_rule_id?
```

`evidence_class` must be compatible with the output's `semantic_class` and the explicit evidence transition that produced it. One output must not simultaneously claim incompatible TEST, VALIDATION, and PROOF statuses merely because several optional fields can be populated.

The generic output `status` describes the result/artifact execution or availability state under the frozen result schema. It is not an epistemic promotion field and cannot by itself convert TEST into VALIDATION or VALIDATION into PROOF.

A future frozen composition rule may permit an output to reference multiple separately identified evidence records, but that must be an explicit model. Independent `test_status`, `validation_status`, and `proof_status` fields are not the candidate default because they admit contradictory combinations.

Each output owns its own epistemic class and status. One validated output must not promote another simulation or TEST output produced by the same JOB.

`input_ids[]` identifies the exact immutable `inputs[]` records that materially contributed to this output. It is not a list of every input visible to or available during the run. The frozen provenance-dependency rule defines whether direct and/or transitive material dependencies must be included. When output-level input attribution is required but cannot be established, provenance validation fails closed rather than guessing from the execution-wide input set.

`effect_attempt_ids[]`, when applicable, identifies the concrete effect attempts that produced, exposed, or materially supplied this output. Each referenced attempt reciprocally names the output in `observable_output_ids[]`. This lets provenance attribute authorization, completion state, backend detail, and partial-effect history to the exact result rather than only to its producing CARD.

`external_tool_ids[]`, when applicable, identifies the concrete external evidence/data producers that materially supplied this output. Those tool records reciprocally reference the output and/or the effect attempts through which they contributed.

`backend_selection_scope_ids[]` identifies machinery-selection scopes governing the output. `generated_artifact_ids[]`, when applicable, identifies the exact generated executable, kernel, bytecode image, or equivalent artifact that actually produced or supplied it. `result_determinism_scope_ids[]`, `numeric_scope_ids[]`, and `randomness_scope_ids[]` resolve directly to the stable type-specific record keys defined by their respective execution-scope arrays, not to the generic computation `scope_id`. The cache references identify legal reuse that contributed to the output.

## Failure and partial-effect provenance

A failed execution remains a provenance-bearing execution event.

Capability denial occurs before the protected effect begins and records an already identified attempt as `NOT_STARTED` with its denial authorization record. A declared effect that was never reached is represented by its explicit non-attempt record.

A detected omission of a reachable required effect is itself a structured execution/conformance failure; it is not merely explanatory provenance.

An unhandled CARD failure stops its DECK by default. An unhandled DECK failure fails the enclosing JOB by default, and no later DECK begins. Dependent consumers or comparisons must not execute against missing or partial failed outputs as though they were complete.

Useful failure fields include:

```text
run_id
execution_status
job_id
job_status
deck_executions[]
card_executions[]
control_decisions[]
failure_records[]
failure_card_id
failure_class
failure_stage
backend_detail?
failure_behavior_bindings[]
backend_selection_scopes[]
backend_selection_decisions[]
effect_requirements[]
effect_authorization_records[]
effect_attempts[]
effect_non_attempt_records[]
machinery_requirements[]
machinery_authorization_records[]
machinery_use_records[]
observable_output_ids[]
```

`failure_records[]` is the resolvable source of failure-event identity. Aggregate `failure_card_id`, `failure_class`, and `failure_stage` may summarize the primary/enclosing failure, but causal references from CARD or non-attempt records use `governing_failure_record_id` and therefore resolve to an actual identified failure record.

The canonical field for the CARD whose unhandled failure produced a failure record is `failure_card_id`. `card_id` remains appropriate inside effect-attempt/authorization/non-attempt records that identify the CARD owning that effect declaration.

## Hash identities

A trace should distinguish at least:

- source-text identity;
- canonical Semantic-IR identity;
- lowered QSOL-CORE identity;
- mandatory Vector/Dataflow IR identity;
- generated target identity;
- resolved extension/contract identities;
- external-tool/service/model identities where material;
- immutable material input identities;
- optimization reference/optimized IR identities where material;
- cache identities where reuse occurs;
- each identified output/result identity.

These are different objects and should not be collapsed into one digest.

## Provenance graph and epistemic boundaries

CARD dependencies naturally form a provenance graph.

```text
@011 OBSERVE MASS 4.2 kg
@012 SET C 299792458 m/s
@013 DERIVE ENERGY = MASS * C * C
@014 TEST ENERGY
@015 SAVE ENERGY
```

The result may retain edges back to the observation, parameter, derivation, TEST, and save operation.

`@014 TEST ENERGY` remains a TEST. It must not be serialized or described as VALIDATION merely because it checks a result. Any stronger epistemic transition requires a distinct frozen rule or CARD semantics.

External instruments, network services, benchmarks, AI systems, and formal tools remain explicit evidence boundaries.

## Cache provenance and legality

Cache provenance and cache legality are separate questions.

A cached result may be valid reuse without proving that a cold reconstruction still succeeds. Merely finding a matching cache entry does not authorize semantic substitution.

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

A verified reuse record does not prove cold reconstructability. A separate cold execution or equivalent evidence is needed for that claim.

### Effectful cache restriction

Ordinary result/value substitution from cache is legal only for computations proven safe for reuse under the active contract. The conservative default is effect-free reuse.

An effectful CARD must not be satisfied merely by returning a prior cached value if that would skip a declared external effect.

Effectful reuse requires a separately frozen cache/replay semantic that preserves or explicitly defines:

- declared effect identity and whether the effect executes again;
- complete per-attempt capability authorization boundaries;
- source/effect/failure ordering;
- effect-attempt identity and completion-state provenance;
- output-to-effect-attempt attribution;
- externally observable artifacts/state;
- randomness and external-input replay rules;
- CARD/DECK/JOB failure behavior;
- per-output semantic class/status/evidence claim and execution-scope links.

Absent such a frozen rule, the implementation executes the effect normally or fails closed.

## Optimization provenance

An optimization profile names requested/configured policy; it is not a record of the transformations that actually occurred.

```text
optimization_provenance[]:
    optimization_record_id
    source_card_ids[]
    backend_unit_id?
    reference_ir_hash
    optimized_ir_hash
    transformation_sequence[]
    legality_witnesses[]
    generated_artifact_ids[]?
    vectorization_decisions[]?
    fusion_decisions[]?
    memory_placement_decisions[]?
    target_context_measurements[]?
    resource_model_assumptions[]?
```

A target-adaptive implementation must preserve the actual transformation sequence and legality evidence rather than only the profile name. A stable content identity for a complete MORPH trace may substitute only when it is sufficient to retrieve and verify the complete decision record.

When optimized IR is code-generated, every resulting artifact must be joined to the applicable optimization record(s), and those records reciprocally identify the generated artifacts. `backend_unit_id` alone is insufficient when one unit has reference and optimized variants. The chain `output → generated_artifact → optimization_provenance` must resolve without guessing from hashes or array position.

A faster semantics-breaking change is not an optimization.

## Benchmark provenance

Historical benchmark observations must not silently become universal performance claims.

A transferable target claim should identify:

- target machine/context;
- measured workload;
- correctness validation;
- provenance binding;
- measurement method.

Correctness and evidence boundaries outrank attractive speed numbers.

## Trace policy

Not every execution requires every optional field. The active specification, execution contracts, capability policy, extension set, lowering contracts, backend-selection/fallback policy, machinery-authorization policy, effect-authorization policy, and cache/replay rules define the minimum trace required for the claim being made.

However, executable research results must not begin life without enough provenance to bind identified outputs to:

- their canonical program and per-DECK/per-CARD execution path, including typed control/failure cause references where those causes explain skipped or untaken execution;
- the exact immutable material inputs that contributed to each output;
- semantic class/status and a mutually consistent evidence-status claim;
- scoped machinery-selection decision history plus resolvable determinism/numeric/randomness/failure-behavior decisions;
- exact generated artifact identities and their governing optimization provenance where applicable;
- concrete effect attempts and their contextual authorization decisions plus authorization-before-begin ordering evidence where external effects produced or exposed the result;
- extension set, extension-scope mappings through both mandatory lowerings, and concrete material external-tool identities;
- machinery authorization decisions plus ordered protected-use evidence where protected machinery was actually used;
- optimization decisions where material;
- cache/reuse context where relevant;
- execution/failure history.

Every declared protected effect must also be accounted for by an attempt or explicit non-attempt reason when declaration-completeness auditing is required. A detected omission of a reachable declared effect fails execution/conformance. Every protected machinery requirement that governs an executed scope must remain traceable to the selection decision, authorization record, and where material the ordered machinery-use record proving authorization preceded protected use.

The roadmap therefore places the trace/failure/provenance foundation before the first executable QSOL reference machine.

## Principle

> A result without enough provenance to support its claim should not be promoted beyond the evidence actually recorded.