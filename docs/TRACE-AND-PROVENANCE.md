# Trace and Provenance

QSOL-MORPH treats provenance as part of execution semantics for research workflows.

This document is architectural and non-normative until the relevant contracts are frozen. Its purpose is to ensure that later implementations can explain not only what bytes were produced, but which semantic units, concrete executions, lowerings, machinery decisions, authorization decisions, execution paths, entropy acquisitions, external tools, toolchain invocations, and evidence transitions produced them.

## Trace questions

A complete trace should be able to answer:

- what source and canonical Semantic IR were executed;
- which stable JOB, DECK, and CARD identities were selected;
- which concrete DECK and CARD executions actually occurred;
- which typed control decision or identified failure record caused an untaken or blocked path;
- how Semantic IR lowered into QSOL-CORE;
- how QSOL-CORE lowered into the mandatory Vector/Dataflow IR;
- how result bindings were preserved, renamed, split, fused, or otherwise mapped;
- how extension, machinery, result-determinism, numeric, randomness, and failure-behavior scopes mapped through both mandatory lowerings;
- which machinery-selection decisions were considered, denied, superseded, or finally used;
- which protected machinery requirements applied and whether authorization completed before protected use began;
- which protected effects were declared for each concrete CARD execution, authorized, attempted, completed, aborted, partially observed, or legitimately not attempted;
- which external-entropy acquisition attempt(s) and immutable entropy input(s) governed every applicable EXTERNAL-ENTROPY randomness scope;
- what exact immutable inputs were consumed and which ones materially contributed to each output;
- which concrete CARD executions, effect attempts, tools, generated artifacts, optimization records, direct toolchain producers, transitive toolchain ancestry, and execution-contract scopes produced each output;
- whether cache reuse occurred and under what legality evidence;
- what epistemic class and evidence status belongs to each output;
- whether execution failed, at what typed scope, and what had already become observable.

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

These layers describe different objects. A flat manifest may serialize them together, but it must not erase their identities or joins.

## Stable source identities

Stable JOB/DECK/CARD identities originate in the canonical semantic model. A trace records them; it does not synthesize, renumber, or infer them from array position.

```text
source_trace:
    source_hash
    spec_version
    run_id?
    job_id
    deck_ids[]
    card_ids[]
    source_location?
```

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

```text
epistemic_class_bindings[]:
    card_id
    semantic_class
```

Separate `card_ids[]` and `epistemic_classes[]` arrays are not an acceptable positional association. Epistemic class is bound directly to canonical CARD identity.

### Declared effect requirements

```text
effect_requirements[]:
    declared_effect_id
    card_id
    effect_kind
    required_capabilities[]
```

The complete capability set belongs to that specific effect. A CARD-wide capability union may be useful for preflight but cannot replace the per-effect association.

A canonical declaration is source identity. Runtime accounting is performed against each applicable concrete `card_execution_id`, because the same canonical CARD may execute more than once.

### Protected machinery requirements

```text
machinery_requirements[]:
    machinery_requirement_id
    scope_kind
    scope_id
    source_card_ids[]
    target_selector_or_class
    required_capabilities[]
```

A GPU requirement does not turn GPU selection into an external effect. It is a separate protected-machinery authorization boundary.

### Source contract bindings

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
    failure_behavior_binding_id
    scope_kind
    scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
```

`failure_behavior_binding_id` is the stable record identity used by result and failure provenance. It is distinct from the generic computation `scope_id` and remains resolvable even when several bindings or policy transitions concern one governed computation.

The owning scope may be a JOB, DECK, CARD, or another scope frozen by the semantic model. Distinct source requirements may not be collapsed into one execution-wide declaration unless a frozen normalization proves that collapse is lossless.

## Semantic-to-Core trace

The Semantic IR to QSOL-CORE transition is independently provenance-bearing.

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

The canonical identity field names are `semantic_to_core_spec_version` and `semantic_to_core_implementation_version`.

### Cardinality-aware result-binding maps

Result-binding maps are identified mapping groups:

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

This model supports:

- one-to-one preservation or rename;
- one-to-many split;
- many-to-one frozen legal fusion;
- many-to-many only when an explicit frozen rule permits it.

`source_bindings[]` and `lower_bindings[]` use deterministic canonical ordering. Positional inference is not sufficient. A map is required whenever result identities are preserved or transformed unless a frozen rule permits deterministic reconstruction of the complete mapping.

### First-lowering scope mappings

Every decision family that maps a scoped semantic requirement identifies both ends with typed scope references rather than untyped IDs.

```text
scope_ref:
    scope_kind
    scope_id
```

For example:

```text
extension_requirement_lowering_decisions[]:
    source_scope_ref
    core_scope_refs[]
    source_card_ids[]
    profile_name
    resolved_version_or_content_identity
    contract_id_or_hash?
    mapping_rule_id
```

The same typed-endpoint principle applies to machinery-requirement, result-determinism, numeric-contract, randomness, and failure-behavior lowering decisions. A JOB-owned requirement must not be silently relocated to a CARD or detached from the Core scope that inherits it.

Machinery requirements additionally need an explicit requirement-level association at this first boundary:

```text
machinery_requirement_lowering_decisions[]:
    mapping_group_id
    source_scope_refs[]
    core_scope_refs[]
    source_machinery_requirement_ids[]
    lower_machinery_requirement_ids[]
    source_card_ids[]
    mapping_rule_id
```

Both scope arrays contain typed `scope_ref` values. Source requirement IDs resolve in the input Semantic IR and lower requirement IDs in the resulting Core IR, qualified by the corresponding IR hashes and owning scopes. Both requirement-ID sets are nonempty, deterministic, and duplicate-free. Unrelated requirements sharing a scope use separate mapping groups. Splits or frozen legal fusions must identify every source/lower requirement and a frozen rule defining the exact relation, including the target selector and complete capability set for each lower requirement. Neither shared scope IDs nor list position can substitute for that association.

A mapping family may be omitted only when a frozen deterministic reconstruction rule proves both scope correspondence and every applicable requirement-ID association without loss. Generic metadata or IR hashes alone are not such a rule. See [Semantic-to-Core machinery preservation](SEMANTIC-TO-CORE-LOWERING.md#protected-machinery-requirements).

## Core-to-Vector/Dataflow trace

The mandatory QSOL-CORE to Vector/Dataflow IR transition is a separate provenance-bearing transformation.

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

This boundary uses the same cardinality-aware result-binding map semantics.

### Typed second-lowering contract mappings

The second lowering preserves exactly which typed Core scope maps to which typed Vector/Dataflow scope. Bare arrays such as `core_scope_ids[]` and `vector_dataflow_scope_ids[]` are not sufficient because JOB, DECK, CARD, region, kernel, and generated-unit namespaces may overlap.

```text
core_scope_refs[]:
    scope_kind
    scope_id

vector_dataflow_scope_refs[]:
    scope_kind
    scope_id
```

A generic mapping record may contain:

```text
core_scope_refs[]
vector_dataflow_scope_refs[]
source_card_ids[]
mapping_rule_id
backend_unit_ids[]?
transition_authorized_by?
```

Use the applicable mapping family for:

- extension requirements;
- protected-machinery requirements;
- result determinism;
- numeric contracts and material numeric modes;
- randomness contracts;
- failure behavior.

`machinery_requirement_mapping_decisions[]` additionally identifies the stable machinery-requirement records on both sides of the lowering boundary:

```text
machinery_requirement_mapping_decisions[]:
    core_scope_refs[]
    vector_dataflow_scope_refs[]
    source_machinery_requirement_ids[]
    lower_machinery_requirement_ids[]
    source_card_ids[]
    mapping_rule_id
    backend_unit_ids[]?
```

The source/lower requirement-ID arrays are cardinality-aware. Scope correspondence and source CARD identity do not identify which requirement was mapped when one Core scope owns several machinery requirements. Each lower requirement must preserve the source target selector/class and complete capability set or identify the frozen rule that transformed them.

`extension_requirement_mapping_decisions[]` additionally retains the applicable profile/version/content/contract identity.

If a Core scope splits into multiple kernels, several Core scopes fuse into one lower region, or scope identity otherwise changes, that mapping is provenance-visible. Each mapping family may be omitted only under a frozen deterministic identity-scope reconstruction rule that covers that family. IR hashes alone do not establish scope correspondence.

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
toolchain_invocations[]
vectorization_decisions[]
fusion_decisions[]
memory_placement_decisions[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
failure_behavior_bindings[]
rule_records[]
validation_evidence[]
```

## Backend-selection provenance

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

`backend_selection_scope_id` is the stable selection-record key. `scope_kind` plus `scope_id` identify the governed computation and are not aliases for the selection-scope record identity.

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

A denied protected target followed by an authorized fallback remains two ordered decisions. The denied decision is never overwritten by the fallback.

## Machinery authorization and use provenance

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

Protected use is independently identified:

```text
machinery_use_records[]:
    machinery_use_record_id
    backend_selection_scope_id
    backend_selection_decision_id
    backend_unit_id?
    source_card_ids[]
    card_execution_ids[]
    initiating_scope_ref?
    machinery_authorization_record_ids[]
    protected_use_start_sequence_index
    protected_use_stop_sequence_index?
```

`card_execution_ids[]` identifies the concrete CARD invocations participating in this use, not all invocations of the source CARD or backend unit. It is nonempty for CARD-governed work, and every ID resolves through `card_executions[]` to the corresponding canonical CARD and DECK execution in this run. A repeated launch, retry, or loop iteration receives a distinct use record with the correct concrete invocation IDs; an event index alone is not this join.

For genuine pre-CARD machinery setup only, the CARD-execution array may be empty and `initiating_scope_ref` is required instead. This is a typed `{ scope_kind, scope_id }` reference to the actual aggregate RUN or DECK_EXECUTION that initiated setup, resolving to `run_id` or `deck_execution_id`. It must not invent a CARD execution. A use serving several CARD executions must list the actual participating executions under the frozen lowering/execution mapping.

Authorization and use indices live in one frozen monotonic event-order domain. Every applicable successful machinery authorization satisfies:

```text
authorization_sequence_index < protected_use_start_sequence_index
```

Denied machinery has no use-start record.

## Generated artifact provenance

```text
generated_artifacts[]:
    generated_artifact_id
    artifact_kind
    artifact_hash
    backend_unit_id
    backend_selection_scope_id
    backend_selection_decision_id
    source_card_ids[]?
    optimized_ir_hash?
    optimization_record_ids[]?
    direct_producer_toolchain_invocation_id
    toolchain_invocation_chain_ids[]
    artifact_location?
```

`backend_selection_decision_id` is required and resolves to the exact decision that governed production of this artifact. That decision must belong to the recorded `backend_selection_scope_id` and match its target context. The scope's final decision is not a substitute: an artifact produced for a rejected candidate remains attributed to that candidate even when another decision ultimately executes. Artifact existence does not authorize protected use.

Generated artifacts link concrete target output to the machinery decision that produced them. When an artifact comes from optimized IR, `optimization_record_ids[]` and `optimized_ir_hash` identify the actual transformation history.

`direct_producer_toolchain_invocation_id` names the one invocation that directly emitted this artifact. `toolchain_invocation_chain_ids[]` is the ordered material ancestry of compiler/assembler/linker/code-generation invocations whose outputs contributed transitively to the artifact bytes. The chain includes the direct producer but chain membership does **not** mean that every ancestor directly emitted the final artifact.

## Toolchain invocation provenance

Run-wide compiler/tool versions are useful summaries, but they cannot identify the exact build path for one artifact when different backend units or stages use different versions, flags, targets, linkers, or generated-code options.

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
    input_ids[]
    input_generated_artifact_ids[]?
    output_generated_artifact_ids[]
    backend_unit_id?
    backend_selection_scope_id?
```

`material_tool_identity` is immutable/versioned identity sufficient to distinguish the actual compiler, assembler, linker, code generator, or frozen equivalent used by that invocation. It may be represented by a version plus binary/content hash, immutable tool artifact ID, or another frozen identity adequate for the reproducibility claim.

`input_ids[]` resolves to identified immutable `inputs[]` records for every material input not generated in this run, including prebuilt objects, static libraries, headers, startup files, sysroots, and implicit toolchain dependencies. It is empty only when no such inputs were consumed. A path, library name, search flag, or tool version is not the identity of the bytes read. A composite dependency input must content-bind the complete material dependency set through a frozen manifest representation. Missing material input identity invalidates a complete/reproducible build-provenance claim.

`input_generated_artifact_ids[]` and `output_generated_artifact_ids[]` are **direct edges** in the build graph. If invocation `link-1` consumes `obj-1` and emits `exe-1`, then `obj-1` appears in `link-1.input_generated_artifact_ids[]` and `exe-1` appears in `link-1.output_generated_artifact_ids[]`. A prebuilt library consumed by the same linker instead appears in `link-1.input_ids[]`; it must not be fabricated as an artifact generated by this run.

The reciprocal direct-producer invariant is therefore narrow and exact: a generated artifact's `direct_producer_toolchain_invocation_id` must resolve to an invocation whose `output_generated_artifact_ids[]` contains that artifact. An invocation listed only in `toolchain_invocation_chain_ids[]` is not required to list the final artifact as a direct output.

For example:

```text
compile-1: source/IR -> obj-1
link-1:    obj-1 + prebuilt-lib-1 -> exe-1
link-1.input_generated_artifact_ids = [obj-1]
link-1.input_ids = [prebuilt-lib-1]

obj-1.direct_producer_toolchain_invocation_id = compile-1
obj-1.toolchain_invocation_chain_ids = [compile-1]

exe-1.direct_producer_toolchain_invocation_id = link-1
exe-1.toolchain_invocation_chain_ids = [compile-1, link-1]
```

`compile-1.output_generated_artifact_ids[]` contains `obj-1`, not `exe-1`; `link-1.output_generated_artifact_ids[]` contains `exe-1`. `prebuilt-lib-1` resolves to its consumed immutable identity in `inputs[]`. This preserves the truthful direct-output relation, external build dependencies, and exact transitive build ancestry.

Where every intermediate generated artifact is retained, `toolchain_invocation_chain_ids[]` must be consistent with the graph reachable through direct input/output artifact edges. If a future frozen profile permits omission of intermediate artifacts, it must define how the transitive chain remains content-bound and verifiable rather than fabricating direct-output edges.

A generated artifact cannot claim reproducible byte provenance from a run-wide compiler list alone.

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

An optimization profile is configuration, not evidence of what actually ran. The required join for an optimized result is resolvable as:

```text
output
  -> generated_artifact
      -> optimization_provenance
      -> direct toolchain producer
      -> ordered toolchain ancestry
```

`backend_unit_id` alone is not sufficient when one unit produces reference and optimized variants.

## Referenced rules and validation evidence

A rule name or a producer's success label is not evidence of permission. Contract transitions, explicit skips, and verified cache substitutions use shared, resolvable rule and evidence records:

```text
rule_records[]:
    rule_id
    rule_kind
    authority_kind
    authority_id
    authority_version_or_hash
    rule_content_hash
    rule_content?
    rule_location?

validation_evidence[]:
    validation_evidence_id
    rule_id
    subject_kind
    subject_id
    evaluated_context_hash
    verifier_identity
    outcome
    validation_sequence_index
    application_sequence_index?
    evidence_hash
    evidence_content?
    evidence_location?
```

Candidate `rule_kind` values include `CONTRACT_TRANSITION`, `EFFECT_SKIP`, and `CACHE_SUBSTITUTION`. `authority_kind` distinguishes a frozen source/specification authority from an execution policy. The authority ID and version/content identity must resolve to the authority actually accepted for this run; a backend cannot authorize itself by inventing a rule record. Rule content must be embedded or retrievable through a content-bound location, and its hash must verify. The rule definition includes its permitted operation, scope, and applicability conditions.

`subject_kind` defines the target namespace: `RESULT_DETERMINISM_SCOPE`, `RANDOMNESS_SCOPE`, `CARD_EXECUTION`, `EFFECT_NON_ATTEMPT_RECORD`, or `CACHE_REUSE_RECORD` resolves to that ledger's stable record key. The evidence must name the same rule as the subject's rule reference and bind the exact subject and evaluated context, not another run, invocation, contract, or cache entry. `verifier_identity` identifies the verification method and its immutable/versioned implementation.

Evidence content must likewise be embedded or retrievable and hash-verifiable. It contains the evaluated context and checks needed to establish applicability; `evaluated_context_hash` binds that context canonically. An `outcome = PASS` string alone is insufficient. Validation must establish that the evidence supports the rule under the current source, policy, inputs, and execution contracts. Unknown IDs, unavailable definitions, wrong kinds, stale versions, mismatched context, and failed or unverifiable evidence fail closed.

For an applied transition, skip, or cache substitution, `application_sequence_index` is required and denotes the actual subject's contract activation, skip, or substitution event. It shares the frozen monotonic event-order domain with `validation_sequence_index`, which must precede it. A rejected decision has no application event. Reporting a rule or validating it after application cannot retroactively authorize behavior.

These records are provenance about operational permission and checks, not TEST/VALIDATION/PROOF research outputs and not capability grants. Referencing them never bypasses effect or protected-machinery authorization.

## Stable execution-contract scope records

Execution scope records have type-specific stable keys distinct from the generic computation scope they govern.

```text
result_determinism_scopes[]:
    result_determinism_scope_id
    scope_kind
    scope_id
    source_card_ids[]
    requested_result_determinism
    effective_result_determinism
    transition_authorized_by?
    transition_evidence_id?
    backend_unit_id?

numeric_execution_scopes[]:
    numeric_scope_id
    scope_kind
    scope_id
    source_card_ids[]
    numeric_contract_id
    numeric_contract_hash
    material_numeric_mode
    backend_unit_id?

randomness_execution_scopes[]:
    randomness_scope_id
    scope_kind
    scope_id
    source_card_ids[]
    requested_randomness_mode
    effective_randomness_mode
    transition_authorized_by?
    transition_evidence_id?
    rng_algorithm?
    rng_version?
    seed?
    stream_id?
    parallel_partitioning?
    entropy_effect_attempt_ids[]?
    entropy_input_ids[]?
    backend_unit_id?

failure_behavior_bindings[]:
    failure_behavior_binding_id
    scope_kind
    scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
```

Output references resolve directly to `result_determinism_scope_id`, `numeric_scope_id`, `randomness_scope_id`, and `failure_behavior_binding_id`. They never infer those records from a generic `scope_id`.

Whenever requested and effective result-determinism or randomness contracts differ, both `transition_authorized_by` and `transition_evidence_id` are required. The former resolves to `rule_records[].rule_id` of kind `CONTRACT_TRANSITION`; the latter resolves to `validation_evidence[].validation_evidence_id` for that exact execution-scope record. Evidence binds the requested/effective contracts, accepted source/policy authority, and governing numeric/randomness context, and must establish authorization before the effective contract is activated or used. A missing, unknown, inapplicable, or post-execution authority is an unauthorized transition and fails closed. The optional notation permits absence only when no transition occurred; it does not permit an undocumented downgrade. Lowering that applies a transition must preserve this authorization/evidence relation into the governed execution scope.

### External-entropy attribution

When `effective_randomness_mode = EXTERNAL-ENTROPY`, the randomness scope must identify the exact protected `RANDOM` acquisition attempt or attempts that supplied entropy through `entropy_effect_attempt_ids[]`. Each referenced attempt must resolve to the ordinary effect authorization/attempt ledger and therefore prove authorization completed before acquisition began.

Where the acquired entropy becomes a material runtime input, `entropy_input_ids[]` identifies the immutable input record(s), such as a canonical captured value, content hash, immutable artifact identity, or another frozen identity sufficient to distinguish what was actually consumed. If raw entropy is intentionally not retained, a frozen audit identity may establish what acquisition was used, but the manifest must not claim byte-for-byte replayability unless the consumed entropy value is actually reconstructable.

The randomness mode itself never authorizes entropy access and never substitutes for the protected `RANDOM` effect attempt.

A single execution-wide scope record is valid only when a frozen normalization proves it faithfully represents every governed source requirement.

## Execution trace

Potential fields include:

```text
run_id
job_id
deck_executions[]
card_executions[]
control_decisions[]
failure_records[]
execution_status
job_status
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
rule_records[]
validation_evidence[]
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
generated_artifacts[]
toolchain_invocations[]
start_stop_metadata?
```

Execution-wide capability arrays and `runtime_compiler_versions[]` are summaries only. Contextual authorization records prove per-boundary authorization, and `toolchain_invocations[]` plus generated-artifact direct/ancestry links prove the exact artifact-producing build graph.

## DECK and CARD execution ledgers

Every selected DECK remains identified even when fail-stop prevents it from starting:

```text
deck_executions[]:
    deck_execution_id
    deck_id
    deck_status
    card_execution_ids[]
    execution_order_index?
    failure_record_id?
```

Every CARD execution is a distinct runtime object:

```text
card_executions[]:
    card_execution_id
    deck_execution_id
    card_id
    card_status
    execution_order_index?
    governing_control_decision_id?
    governing_failure_record_id?
    governing_skip_rule_id?
    skip_verification_evidence_id?
    failure_record_id?
```

Canonical `card_id` identifies the semantic CARD. `card_execution_id` identifies one concrete execution of that CARD. The distinction matters for loops, retries, calls, repeated DECK execution, or any future construct that can execute one canonical CARD more than once.

Membership in `card_ids[]` is not proof that a CARD ran. An explicitly skipped CARD uses the rule/evidence requirements in [Effect non-attempt records](#effect-non-attempt-records), with evidence bound to its `CARD_EXECUTION` subject. Skipping the parent CARD cannot evade the accounting and rule validation for its effects.

## Typed execution-path causality and failures

Control decisions and failures have distinct identified namespaces:

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
    failure_behavior_binding_ids[]
    failure_class
    failure_stage
    failure_card_id?
    failure_card_execution_id?
    deck_execution_id?
    sequence_index?
    backend_detail?
```

`failing_scope_kind` plus `failing_scope_id` is the always-present typed identity of the scope where the failure occurred. Frozen scope kinds may include JOB, DECK_EXECUTION, CARD_EXECUTION, BACKEND_SELECTION_SCOPE, LOWERING, or another explicitly specified execution scope.

`failure_behavior_binding_ids[]` is required and resolves to the exact `failure_behavior_bindings[]` records governing this failure and its propagation or handling. It includes the applicable frozen default fail-stop binding, not just explicit recovery policies. When several policies or transitions concern one computation, the failure references those actually active at that event; it must not infer policy from the resulting path or a generic scope ID. A rejected requested policy is not an effective handling policy. Pre-CARD rejection records retain the applicable setup/rejection-handling binding without inventing a CARD culprit. Missing or incompatible governing bindings make the failure trace incomplete.

`failure_card_id` remains the canonical source-CARD identity **when a CARD's unhandled failure caused the record**. `failure_card_execution_id` identifies the corresponding concrete runtime CARD execution. For a CARD-caused failure, both are required and must resolve consistently through `card_executions[]`.

A failure that occurs before any CARD execution, such as JOB-scoped contract rejection, DECK setup failure, protected-machinery denial before CARD use, or another pre-CARD execution failure, must not invent a CARD identity. In that case the typed failing scope is authoritative and `failure_card_id` / `failure_card_execution_id` are absent.

An untaken branch references `governing_control_decision_id`. Prior fail-stop or another failure-caused non-reach references `governing_failure_record_id`. A catch-all control-or-failure ID is invalid because it erases the target namespace.

## Inputs

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

Every material input requires a stable `input_id` plus a canonical value or immutable content/artifact identity sufficient to identify what was actually consumed. Paths, URLs, dataset names, and model names are retrieval context, not immutable identity by themselves.

## Effect authorization

Every protected effect attempt has a contextual authorization decision:

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

## Effect attempts

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

`card_id` identifies the canonical declaration owner. `card_execution_id` identifies the concrete runtime invocation in which this attempt occurred. Attempts from different retries, loop iterations, calls, or repeated DECK executions must never collapse merely because they share one canonical CARD ID.

Authorization and effect-begin indices share one frozen monotonic event-order domain. Every protected attempt known to begin satisfies:

```text
authorization_sequence_index < effect_begin_sequence_index
```

Denied authorization has no effect-begin event. Generic attempt `sequence_index` is not authorization-order proof.

### Effect completion states

The candidate states are mutually exclusive:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

Known completion takes precedence over uncertainty about broader external consequences. Completion belongs to the effect attempt, not to the enclosing CARD outcome.

## Effect non-attempt records

A declared effect may legitimately have no runtime attempt for a particular concrete CARD execution when control flow, prior failure, or another frozen rule prevents the effect from being attempted.

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
    governing_skip_rule_id?
    skip_verification_evidence_id?
    backend_detail?
```

The stable `effect_non_attempt_record_id` distinguishes separate non-attempt facts even when the same canonical CARD/effect declaration is encountered more than once. `card_execution_id` binds each non-attempt to the exact runtime invocation/path being accounted for.

Candidate legitimate reasons include untaken branch, prior fail-stop, CARD not reached, and explicit frozen skip. Untaken control flow resolves to a `control_decision_id`; failure-caused non-reach resolves to a `failure_record_id`.

An explicit frozen skip requires both `governing_skip_rule_id` and `skip_verification_evidence_id`. They resolve to a `rule_records[]` entry of kind `EFFECT_SKIP` and passing `validation_evidence[]` for this exact non-attempt record, declaration, CARD execution, and active semantic/policy context. The rule must explicitly permit this skip and its applicability must be verified before the skip is applied. Optional control/failure references, a free-text reason, or a rule valid only for another invocation cannot substitute for these records. An unknown, missing, inapplicable, or unverifiable skip rule forces structured conformance failure; a reachable required effect omitted without a valid skip rule is a backend omission, not success.

`BACKEND_OMISSION_DETECTED` or frozen equivalent means a reachable required effect was omitted. It forces structured execution/conformance failure and cannot coexist with successful enclosing execution.

### Unconditional declaration accounting

Declaration completeness is not an optional audit mode.

For every selected concrete `card_execution_id`, every applicable canonical `effect_requirement` owned by that CARD must resolve to exactly one of these provenance outcomes:

1. one or more identified `effect_attempts[]` records for that `card_execution_id` when execution/retry semantics produce attempts;
2. exactly one identified legitimate `effect_non_attempt_records[]` record for that `card_execution_id` when no attempt occurred; or
3. a structured execution/conformance failure if complete accounting itself cannot be established or a reachable required effect was omitted.

A declared effect with neither an attempt nor a legitimate non-attempt record is always incomplete provenance and fails closed. Profiles, backends, optimization modes, or deployment settings may not disable this requirement.

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

For a material external tool, service, model, prover, process, or instrument, `tool_name_or_service` and a mutable endpoint are labels/locators only. `material_identity_status = IDENTIFIED` requires an immutable or versioned `material_identity_value`, such as an executable/content hash, tool version bound strongly enough for the active claim, model/version ID, immutable artifact ID, or frozen equivalent.

If exact material identity cannot be established, record `material_identity_status = UNAVAILABLE` (or a frozen equivalent) and the strongest replay/evidence claim must be weakened or rejected according to the frozen policy. Identity unavailability may never be silently treated as full reproducibility.

Extension resolution identifies the adapter/profile contract. It does not substitute for the actual tool, service, model, prover, process, or instrument identity.

## Cache reuse provenance

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

Candidate classifications are `COLD_EXECUTION`, `VERIFIED_REUSE`, and `UNVERIFIED_HIT`, or frozen equivalents.

For `VERIFIED_REUSE`, `legality_rule_id` and `verification_evidence_id` are mandatory. They resolve to a `rule_records[]` entry of kind `CACHE_SUBSTITUTION` and passing, content-bound `validation_evidence[]` for this exact cache-reuse record. The record must identify the reused computation/artifact and the checked cache key/artifact content, either directly through the corresponding hash fields or through resolvable immutable cached-output/producer provenance. Evidence verifies the material cache identity and substitution legality against the current inputs, contracts, and execution context before substitution is applied. A matching hash or a producer's `VERIFIED_REUSE` label alone is not verification evidence.

Ordinary result substitution is effect-free by default. Effectful reuse additionally requires that the referenced rule is the separately frozen replay/cache semantic covering this operation's declared effects, contextual authorization, ordering, failure, attempt provenance, output attribution, and external state behavior. A generic cache rule does not permit effectful substitution.

An `UNVERIFIED_HIT` remains diagnostic and cannot satisfy a CARD or produce a verified-reuse output. It must undergo successful verification before reuse, trigger cold execution, or fail closed. Missing, stale, mismatched, failed, or unavailable verification evidence invalidates `VERIFIED_REUSE`; optional notation for other classifications never waives its conditions.

Verified cache reuse does not prove cold reconstructability.

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

`producer_card_ids[]` records the canonical semantic producers. `producer_card_execution_ids[]` records the concrete runtime CARD execution(s) that actually produced, materially supplied, or published the output. Every concrete producer resolves through `card_executions[]` to its `deck_execution_id` and canonical `card_id`.

The concrete producer-execution relation is required whenever runtime producer attribution is part of the trace contract, including whenever the same canonical CARD can execute more than once. A canonical CARD ID alone is insufficient for loops, retries, repeated calls, or repeated DECK execution.

`input_ids[]` identifies the exact immutable inputs materially contributing to the output. Execution-wide input availability is not a substitute.

`effect_attempt_ids[]`, where applicable, identifies concrete effect attempts that produced or exposed the output. Those attempts reciprocally list the output in `observable_output_ids[]`.

`external_tool_ids[]`, where applicable, identifies the exact material tools/services/models/provers that supplied the output.

`generated_artifact_ids[]` identifies the exact executable/kernel/bytecode artifact that ran where applicable. The artifact links onward to its optimization provenance, its direct toolchain producer, and its ordered transitive toolchain ancestry.

`failure_behavior_binding_ids[]` resolves to the exact identified failure-policy records that governed the producer path. A generic computation `scope_id` cannot substitute for this record-level join.

The execution-contract scope arrays resolve directly to the stable type-specific scope-record keys described above.

### Evidence status

When present, evidence status is class-discriminated:

```text
evidence_status:
    evidence_class      # TEST / VALIDATION / PROOF / frozen equivalent
    status
    evidence_rule_id?
```

The evidence class must be compatible with the output's `semantic_class` and explicit evidence transition. Generic output `status` is an execution/artifact state and cannot promote epistemic class.

## Failure trace

A failed execution retains enough information to distinguish the enclosing outcome from prior completed effects or machinery use without inventing a CARD culprit.

```text
run_id
execution_status
job_id
job_status
deck_executions[]
card_executions[]
control_decisions[]
failure_records[]
failure_behavior_bindings[]
primary_failure_record_id?
backend_selection_scopes[]
backend_selection_decisions[]
machinery_requirements[]
effect_requirements[]
effect_authorization_records[]
effect_attempts[]
effect_non_attempt_records[]
machinery_authorization_records[]
machinery_use_records[]
rule_records[]
validation_evidence[]
observable_output_ids[]
```

A failure trace includes the backend-selection scope and decision ledgers referenced by its machinery authorization/use records, including denied candidates and fallback predecessors, not just the final target. Every `failure_behavior_binding_ids[]` reference resolves to the retained governing policy bindings. A standalone failure manifest must preserve the complete transitive closure of its references, including applicable rules, evidence, requirements, and observable outputs, either inline or through retrievable content-bound trace records. An unresolvable ID or an unbound mutable external trace link is incomplete provenance.

The primary failure resolves through `failure_records[]` to an always-present typed failing scope. `failure_card_id` is canonical only for CARD-caused failures and is absent for legitimate pre-CARD failures.

Effect-attempt completion is independent of CARD success. A completed process effect may coexist with a failed CARD if the process completed and returned a non-success status under the active contract.

Protected machinery authorization outcomes are not enough by themselves. If protected machinery actually began, `machinery_use_records[]` preserve the concrete use, its CARD-execution or pre-CARD initiating-scope relation, and ordering evidence.

## Provenance validation rules

At minimum, a future validator should reject or fail closed when:

- stable JOB/DECK/CARD identities are missing or silently renumbered;
- an epistemic class becomes detached from its CARD;
- a declared effect loses its per-effect capability binding;
- a protected machinery requirement disappears before MORPH;
- a machinery-requirement mapping cannot identify the exact source and lower requirement records at either lowering boundary when multiple requirements share a scope;
- a result-binding map cannot represent the actual split/fusion cardinality;
- a lowering scope mapping uses ambiguous untyped endpoints where namespaces can overlap;
- a required extension ownership mapping becomes positional or implicit;
- a requested execution contract differs from its effective contract without resolvable, versioned, applicable pre-execution authority and passing context-bound evidence;
- a rule/evidence reference has the wrong kind, subject, context, content hash, or order;
- output scope IDs do not resolve to stable type-specific scope records;
- an output or failure's failure-behavior reference does not resolve to the exact applicable stable `failure_behavior_binding_id`;
- a concrete output cannot be joined to the CARD execution that produced it;
- a CARD-governed machinery use cannot be joined to its concrete participating CARD executions;
- a genuine pre-CARD machinery use fabricates CARD executions or omits its typed initiating runtime scope;
- an EXTERNAL-ENTROPY randomness scope cannot resolve to the exact protected RANDOM acquisition attempt(s), and to immutable entropy input identity where required by the audit/replay contract;
- an effect attempt or non-attempt cannot be joined to its concrete `card_execution_id`;
- a non-attempt record has no stable identity;
- an explicit skip lacks a resolvable frozen skip rule and passing applicability evidence for that invocation;
- any applicable declared effect lacks both attempt and legitimate non-attempt accounting for a selected concrete CARD execution;
- an effect begins before its authorization completed;
- protected machinery begins before every applicable authorization completed;
- denied protected machinery nevertheless has a use-start record;
- a reachable required effect is omitted;
- an effect non-attempt record points to an untyped or unresolved cause;
- a failure lacks a typed failing-scope identity;
- a failure trace omits referenced backend-selection scopes, decisions, or other records needed to resolve its provenance;
- a pre-CARD failure fabricates `failure_card_id`, or a CARD-caused failure omits the matching canonical/concrete CARD identities;
- cold execution and cache reuse become indistinguishable;
- `VERIFIED_REUSE` lacks a matching frozen legality rule, checked cache identity, or passing verification evidence, or an unverified hit supplies an output;
- an optimized artifact cannot be joined to its optimization record;
- a generated artifact omits its exact production `backend_selection_decision_id` or is attributed to the final fallback decision instead;
- a generated artifact cannot resolve its direct producer toolchain invocation;
- a generated artifact's ordered toolchain ancestry is inconsistent with the direct generated-artifact input/output graph under the active profile;
- a transitive toolchain ancestor is falsely recorded as directly outputting a final artifact merely to satisfy chain membership;
- a toolchain invocation omits material tool identity, immutable non-generated `input_ids[]`, or material build flags/configuration required by the active reproducibility claim;
- output evidence status contradicts semantic class;
- a mutable input locator substitutes for immutable input identity;
- a material external tool has neither immutable/versioned material identity nor an explicit identity-unavailable state that weakens the claim.

## Principle

> Trace meaning, not just bytes. Preserve stable semantic identity, typed scope correspondence, concrete execution identity, unconditional declared-effect accounting, authorization-before-use ordering, truthful direct build edges, transitive toolchain ancestry, and the exact evidence chain from immutable inputs through lowerings, optimization, toolchain invocations, and machinery to each output or failure.
