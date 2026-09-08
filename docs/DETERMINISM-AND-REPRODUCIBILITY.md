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
    governed_scope_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
    transition_evidence_id?
```

`failure_behavior_binding_id` is the stable provenance-record key. Outputs and failure records reference that record key through `failure_behavior_binding_ids[]`; the generic governed computation `scope_id` is not an alias for the binding record.

The frozen default fail-stop behavior has a stable identity when it materially governs execution. A manifest must not infer effective failure policy merely from skipped CARDs or DECKs. When requested and effective failure semantics differ, the rule must resolve to accepted content-bound `CONTRACT_TRANSITION` authority and `transition_evidence_id` must resolve to passing evidence for this exact binding, validated before the effective policy is applied. A representation-only mapping cannot authorize fail-stop becoming continue, retry, or compensate.

## Stable execution-contract scope records

Execution scope records have their own stable type-specific keys. The key of the provenance record is distinct from the generic computation scope it governs.

### Result determinism

```text
result_determinism_scopes[]:
    result_determinism_scope_id
    governed_scope_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
    source_card_ids[]
    requested_result_determinism
    effective_result_determinism
    transition_authorized_by?
    transition_evidence_id?
    backend_unit_id?
```

`result_determinism_scope_id` is referenced by output `result_determinism_scope_ids[]`.

### Randomness

```text
randomness_execution_scopes[]:
    randomness_scope_id
    governed_scope_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
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
```

`randomness_scope_id` is referenced by output `randomness_scope_ids[]`.

Seeded replay binds algorithm, algorithm version, seed, stream identity, and parallel partitioning/stream mapping wherever they affect the generated sequence.

When `effective_randomness_mode = EXTERNAL-ENTROPY`, `entropy_effect_attempt_ids[]` identifies every protected `RANDOM` acquisition attempt that materially supplied this randomness scope. Each attempt must resolve to a successful contextual authorization record and explicit effect-begin provenance. If the entropy value itself is a material input, `entropy_input_ids[]` identifies the immutable input record(s) actually consumed.

An audit identity or content hash may identify an entropy acquisition without preserving raw secret/random bytes, but such a record does not establish byte-for-byte replayability unless the consumed entropy is reconstructable. The manifest must state the strongest guarantee actually supported.

### Numeric behavior

```text
numeric_execution_scopes[]:
    numeric_scope_id
    governed_scope_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
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

The three record keys above are type-specific on purpose. Every execution-contract record also carries the fully qualified `governed_scope_ref` containing representation identity and complete representation-relative `owner_scope_path[]`. Overlapping JOB/DECK/CARD/region/kernel local IDs therefore remain distinguishable. Stable ledger IDs and `source_card_ids[]` do not substitute for canonical ownership.

A single execution-wide scope record is legal only when a frozen normalization proves it faithfully represents every governed source requirement.

### Resolvable transition authority and evidence

Whenever requested and effective result-determinism or randomness contracts differ, `transition_authorized_by` and `transition_evidence_id` are mandatory. They resolve respectively to `rule_records[].rule_id` of kind `CONTRACT_TRANSITION` and `validation_evidence[].validation_evidence_id` for this exact type-specific execution-scope record. These ledgers use the complete shared [rule and evidence schemas](TRACE-AND-PROVENANCE.md#referenced-rules-and-validation-evidence), not opaque IDs or separately abbreviated definitions.

The rule is bound to the accepted source/specification or execution-policy authority, its version/content identity, and verifiable rule content. Passing evidence binds the exact requested/effective contracts, governing numeric/randomness context, and actual policy conditions. It must establish authorization before effective-contract activation or use, with same-domain `validation_sequence_index < application_sequence_index`. Missing, unknown, wrong-kind, stale, mismatched, unavailable, or post-execution authority/evidence fails closed. Optional notation permits omission only when there is no transition, not an undocumented downgrade. A transition recorded by a lowering retains this relation into the governed execution scope.

Rule/evidence records neither grant effect or machinery capabilities nor promote research evidence status. A producer's `PASS` label alone is not verification. The manifest retains the referenced definitions, evaluated context, and verification evidence inline or through retrievable content-bound records.

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
    governed_scope_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
    source_card_ids[]
    backend_unit_id?
    selection_decision_ids[]
    final_selection_decision_id?
```

`backend_selection_scope_id` is the stable selection-scope record key. `governed_scope_ref` resolves the exact computation through representation identity plus its complete owner path; source CARD summaries and local scope IDs cannot replace that identity.

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
    fallback_evidence_id?
    machinery_authorization_record_ids[]?
    decision_status
```

A denied protected target followed by an authorized fallback remains two ordered decisions. The first decision is not overwritten by the fallback. A fallback requires both an accepted content-bound `BACKEND_FALLBACK` rule and passing `fallback_evidence_id` bound to this exact decision, predecessor, target context, and active policy/contracts, with validation preceding fallback selection/application.

## Protected machinery requirements, authorization, and use

Canonical requirements remain present independently of runtime authorization:

```text
machinery_requirements[]:
    machinery_requirement_id
    owner_scope_path[]:
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
    machinery_requirement_refs[]:
        owner_scope_path[]:
            scope_kind
            scope_id
        machinery_requirement_id
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
    generated_artifact_ids[]
    execution_subject_refs[]:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    source_card_ids[]?
    card_execution_ids[]?
    initiating_scope_ref?
    machinery_authorization_record_ids[]
    output_ids[]
    protected_use_start_sequence_index
    protected_use_stop_sequence_index?
```

`execution_subject_refs[]` is the canonical execution-governed identity for protected machinery use. Semantic CARD use records resolve those references to `card_executions[]`; direct QSOL-CORE use records resolve them to the exact `CORE_OPERATION` / `operation_execution_id` in `operation_executions[]`. `source_card_ids[]` and `card_execution_ids[]`, when present, are verified Semantic-lineage projections of the CARD-backed subset and must agree with the subject references; they are absent on a direct Core run with no Semantic lineage. Repeated uses under one backend scope/decision cannot collapse retries, iterations, or repeated Core-operation invocations into canonical source IDs.

Genuine pre-execution RUN/DECK setup that is not governed by any CARD or lower operation may use an empty `execution_subject_refs[]` only with `initiating_scope_ref`, a typed `{ scope_kind, scope_id }` reference to the actual RUN or DECK_EXECUTION, resolving to `run_id` or `deck_execution_id`. A direct Core operation is not pre-CARD setup and must use its actual operation execution subject. Shared uses list every concrete participating execution subject under the frozen execution mapping. `generated_artifact_ids[]` names the exact generated code artifact(s) actually executed by the use and remains populated even when the use fails before producing an output; every ID must match the use's backend scope/decision/unit. `output_ids[]` names every output materially produced or exposed by this exact protected-use occurrence and is reciprocal with `outputs[].machinery_use_record_ids[]`; matching CARD/operation identity, backend scope, or generated artifact is not an occurrence-level substitute.

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
    backend_selection_decision_id
    source_card_ids[]?
    optimized_ir_hash?
    optimization_record_ids[]?
    direct_producer_toolchain_invocation_id
    toolchain_invocation_chain_ids[]
    artifact_location?
```

`backend_selection_decision_id` is required and resolves to the exact production decision in the recorded selection scope, with matching target context. A rejected candidate's artifact remains attributed to that candidate, never implicitly to the scope's final fallback decision. Artifact existence is not machinery-use authorization.

A bare hash list is insufficient. When an artifact is generated from optimized IR, its `optimized_ir_hash` and `optimization_record_ids[]` identify the transformation history that produced it.

`direct_producer_toolchain_invocation_id` identifies the invocation that directly emitted this artifact. `toolchain_invocation_chain_ids[]` records the ordered material ancestry of compiler/assembler/linker/code-generation invocations that contributed transitively to its bytes. Chain membership does not mean every ancestor directly emitted the final artifact.

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
    input_ir_hashes[]
    input_ids[]
    input_generated_artifact_ids[]?
    output_generated_artifact_ids[]
    backend_unit_id?
    backend_selection_scope_id?
```

`material_tool_identity` must be an immutable/versioned identity adequate to distinguish the actual tool used for the active reproducibility claim, such as version plus executable/content hash, immutable tool artifact ID, or frozen equivalent.

`input_ir_hashes[]` is explicit and must contain every exact IR snapshot directly consumed by the invocation. It is nonempty for any compilation/code-generation step that consumes IR, optimized or not, and empty only for a step that consumes no IR. Tool, flags, target, backend-unit, source summaries, or output hashes cannot reconstruct this direct input identity.

`input_ids[]` resolves to immutable `inputs[]` records for every material input not generated in this run, including prebuilt objects, static libraries, headers, startup files, sysroots, and implicit toolchain dependencies. It is empty only when no such inputs were consumed. A composite input must bind the complete material dependency set through a frozen content-manifest representation. Mutable paths, library names, flags, and tool versions alone do not identify the actual dependency bytes; missing material input identity invalidates a complete/reproducible build-provenance claim.

`input_generated_artifact_ids[]` and `output_generated_artifact_ids[]` are direct build-graph edges. A generated artifact's `direct_producer_toolchain_invocation_id` must resolve to an invocation whose `output_generated_artifact_ids[]` contains that artifact. Other invocations in `toolchain_invocation_chain_ids[]` are transitive ancestors and are not required to claim the final artifact as a direct output.

For a normal compile/link chain:

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

The compiler directly outputs `obj-1`; the linker directly outputs `exe-1`. `prebuilt-lib-1` resolves to its consumed immutable identity in `inputs[]`, not a fabricated generated artifact. The executable still retains the complete ordered material chain without falsely claiming the compiler directly emitted it.

Where intermediate generated artifacts are retained, the ordered chain must be consistent with the direct input/output artifact graph. Any future frozen representation that omits intermediates must define how the transitive chain remains content-bound and verifiable.

A run-wide compiler-version list is summary metadata only and cannot substitute for artifact-specific invocation identity, flags, target/ABI, configuration, immutable material inputs, direct producer, or transitive chain.

## Optimization provenance

```text
optimization_provenance[]:
    optimization_record_id
    source_card_ids[]
    backend_unit_id?
    reference_ir_hash
    optimized_ir_hash
    transformation_sequence[]
    legality_witnesses[]:
        legality_witness_id
        witness_kind
        validation_evidence_id
    vectorization_decisions[]?
    fusion_decisions[]?
    memory_placement_decisions[]?
    target_context_measurements[]?
    resource_model_assumptions[]?
    generated_artifact_ids[]
```

Each legality witness is an identified, typed, verifiable record rather than an opaque label. `validation_evidence_id` resolves to passing content-bound evidence for this exact optimization record, binding the reference/optimized IR pair, ordered transformation sequence, active numeric/determinism/randomness/failure contracts, material effects/sequencing/extensions/machinery/inputs/target context, accepted `OPTIMIZATION_LEGALITY` rule, and immutable/versioned verifier identity. A witness for another IR pair or context is invalid.

An optimization profile is configuration, not evidence of what actually ran.

Every optimized generated artifact links to its applicable optimization record(s), and those records reciprocally list the generated artifacts. The required join is:

```text
output -> generated_artifact -> optimization_provenance
                         \-> direct toolchain producer + ordered ancestry
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
    owner_scope_path[]:
        scope_kind
        scope_id
```

Every first-boundary scope reference uses the complete ordered absolute containment path in its own representation. Semantic endpoints carry all JOB/DECK/CARD ancestors as applicable; Core endpoints carry all enclosing Core scopes needed to distinguish locally repeated IDs. Bare kind/local-ID pairs are insufficient.

At the first boundary, `machinery_requirement_lowering_decisions[]` uses identified mapping groups with complete-path `source_scope_refs[]` and `core_scope_refs[]`, plus nonempty deterministic owner-qualified `source_machinery_requirement_refs[]` and `lower_machinery_requirement_refs[]`. Each machinery reference structurally pairs `owner_scope_path[]` with its local requirement ID and resolves in the hash-bound source Semantic IR or resulting Core IR. Separate same-named requirements must not be inferred from source CARD IDs or paired by position; a frozen rule defines any split/fusion relation unambiguously. The complete shape and rejection rules are shared with [Semantic-to-Core machinery preservation](SEMANTIC-TO-CORE-LOWERING.md#protected-machinery-requirements).

At the second boundary, every applicable mapping family uses `core_scope_refs[]` and `vector_dataflow_scope_refs[]` whose entries carry complete representation-relative `owner_scope_path[]` values. Bare IDs and one-level kind/local-ID pairs are insufficient when enclosing Core/Vector scopes can reuse local IDs.

For `machinery_requirement_mapping_decisions[]`, complete scope paths are necessary but not sufficient: each mapping also carries owner-qualified `source_machinery_requirement_refs[]` and `lower_machinery_requirement_refs[]`, structurally pairing every local machinery requirement ID with its complete owning path. This preserves exact requirement/capability-set correspondence through preservation, split, or frozen legal fusion without positional inference.

This typed-endpoint rule applies to extension requirements, machinery requirements, result determinism, numeric contracts/modes, randomness, and failure behavior. Mapping families may be omitted only under a frozen deterministic reconstruction rule covering that family; for machinery it must reconstruct every requirement-ID association as well as the owning scopes.

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
    consumer_execution_refs[]:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    consumer_card_execution_ids[]?
    consumer_scope_refs[]?
    effect_attempt_ids[]
```

Every material input requires a stable `input_id` plus a canonical value or immutable content/artifact identity sufficient to distinguish what was actually consumed.

Paths, URLs, dataset names, and model names are retrieval context, not immutable identity by themselves. `consumer_execution_refs[]` identifies the exact current-run execution subjects that consumed the value and resolves to CARD or operation executions as applicable, including failed/output-free invocations. `consumer_card_execution_ids[]`, when present, is the verified Semantic projection of the CARD-backed subset and reciprocates `card_executions[].input_ids[]`; it is absent or empty for a direct Core run with no CARD consumers. Direct Core consumers reciprocate through `operation_executions[].input_ids[]`. `effect_attempt_ids[]` identifies concrete effect acquisitions and reciprocates `effect_attempts[].acquired_input_ids[]`. Genuine run/DECK setup uses typed `consumer_scope_refs[]`; canonical `source_card_ids[]` is summary context only and never substitutes for runtime subject identity.

## DECK, CARD, and lower-operation execution provenance

Canonical membership alone does not establish execution.

```text
deck_executions[]:
    deck_execution_id
    deck_id
    deck_status
    card_execution_ids[]
    execution_order_index?
    governing_failure_record_id?
    failure_record_id?
```

Every selected DECK remains represented, including a DECK prevented from starting by prior fail-stop. A non-started/skipped DECK caused by an earlier failure requires `governing_failure_record_id` resolving to that blocking failure; `failure_record_id` remains reserved for a failure caused by this DECK execution itself.

```text
card_executions[]:
    card_execution_id
    deck_execution_id
    card_id
    card_status
    input_ids[]
    cache_reuse_record_ids[]?
    execution_order_index?
    governing_control_decision_id?
    governing_failure_record_id?
    governing_skip_rule_id?
    skip_verification_evidence_id?
    failure_record_id?
```

`card_id` identifies the canonical semantic CARD. `card_execution_id` identifies one concrete runtime execution. This distinction is material for loops, retries, calls, repeated DECK execution, or another construct that can execute the same CARD more than once. `input_ids[]` reciprocally identifies the material inputs consumed by this invocation, while `cache_reuse_record_ids[]` reciprocally identifies cache decisions applying to this current-run invocation.

For lower-representation entry, concrete operation execution is identified independently rather than synthesized as a CARD execution:

```text
operation_executions[]:
    operation_execution_id
    operation_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        operation_id
    operation_kind
    operation_status
    input_ids[]
    execution_order_index?
    failure_record_id?
    source_card_ids[]?
    source_card_execution_ids[]?
```

For direct `QSOL_CORE`, `operation_ref.representation_kind = QSOL_CORE` and `representation_identity = core_ir_hash`. `source_card_ids[]` / `source_card_execution_ids[]` are optional verified lineage only; they are absent when no Semantic lineage exists.

Candidate statuses include executed success/failure, untaken branch, prior fail-stop, CARD not reached, and explicit frozen skip. Explicit CARD skips require the same resolvable skip rule and passing applicability evidence as effect skips, with evidence bound to the exact `CARD_EXECUTION` subject. A parent skip cannot evade accounting for its effects.

## Typed execution-path causality and failure identity

Control decisions and failures are separate identified namespaces:

```text
control_decisions[]:
    control_decision_id
    card_execution_id?
    operation_execution_id?
    control_kind
    decision
    sequence_index?
    backend_detail?

failure_records[]:
    failure_record_id
    failing_scope_kind
    failing_scope_id
    failure_behavior_binding_ids[]
    result_determinism_scope_ids[]
    numeric_scope_ids[]
    randomness_scope_ids[]
    failure_class
    failure_stage
    failure_card_id?
    failure_card_execution_id?
    operation_execution_id?
    deck_execution_id?
    sequence_index?
    backend_detail?
```

`failing_scope_kind` plus `failing_scope_id` is always present. It identifies the typed runtime or pre-runtime scope where the failure occurred.

`failure_behavior_binding_ids[]` is required and resolves to the exact stable policy bindings active for this failure and its propagation/handling, including the applicable frozen default fail-stop binding. Policies sharing a computation scope or different transitions must not be inferred from observed control flow. A rejected requested policy is not an effective handling policy; pre-CARD/lower-entry rejections retain the applicable setup/rejection-handling binding. Missing or incompatible bindings make the failure trace incomplete.

Each failure also carries the complete applicable `result_determinism_scope_ids[]`, `numeric_scope_ids[]`, and `randomness_scope_ids[]`. Derive the exact sets independently from the typed failing scope, the concrete execution subject when one exists, and validated lowering/contract mappings; require the recorded arrays to match those complete applicable ledgers. An empty array is valid only when no scope in that family governs the failure. Output absence does not waive failure-to-contract attribution.

For a CARD-caused failure, `failure_card_id` and `failure_card_execution_id` are required and must resolve consistently through `card_executions[]`. For a legitimate pre-CARD or direct lower-operation failure, those CARD fields are absent rather than fabricated; `operation_execution_id`, where applicable, identifies the actual lower execution subject.

An untaken branch references `governing_control_decision_id`. Prior fail-stop or another failure-caused non-reach references `governing_failure_record_id`.

A catch-all `governing_control_or_failure_id` is invalid because it erases the target namespace.

## Declared effect requirement identity

```text
effect_requirements[]:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
    declared_effect_id
    card_id?
    operation_id?
    effect_kind
    required_capabilities[]
```

Every declaration resolves by `(representation_kind, representation_identity, owner_scope_path[], declared_effect_id)` against the hash-bound representation that actually owns it. Semantic declarations may retain `card_id`; direct Core declarations identify their Core operation without inventing a CARD. Missing, mismatched, ambiguous, or cross-representation ownership fails closed before authorization or attempt accounting.

## Per-effect authorization provenance

```text
effect_authorization_records[]:
    effect_authorization_record_id
    effect_attempt_id
    effect_requirement_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        declared_effect_id
    execution_subject_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    card_id?
    card_execution_id?
    required_capabilities[]
    granted_capabilities[]
    denied_capabilities[]
    capability_policy_id
    capability_policy_version
    authorization_status
    authorization_sequence_index?
```

Execution-wide capability sets are summaries, not proof that one attempt was authorized. `effect_requirement_ref` identifies the exact declared effect in the representation that owns it; `execution_subject_ref` identifies the concrete CARD or lower-operation invocation governed by the decision. Semantic CARD attempts require matching `card_id` / `card_execution_id`; direct Core attempts resolve to `CORE_OPERATION` / `operation_execution_id`, with CARD fields absent unless verified Semantic lineage exists.

## Effect declaration and attempt accounting

Runtime attempts carry contextual authorization, explicit begin/end ordering, concrete execution-subject identity, and output/tool attribution:

```text
effect_attempts[]:
    effect_attempt_id
    effect_requirement_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        declared_effect_id
    execution_subject_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    card_id?
    card_execution_id?
    effect_kind
    required_capabilities[]
    effect_authorization_record_id
    sequence_index
    effect_begin_sequence_index?
    effect_end_sequence_index?
    completion_state
    backend_detail?
    acquired_input_ids[]
    observable_output_ids[]
    external_tool_ids[]
```

Authorization and effect-begin indices live in one frozen monotonic event-order domain. Every protected attempt known to begin satisfies:

```text
authorization_sequence_index < effect_begin_sequence_index
```

Denied authorization has no effect-begin event. Generic `sequence_index` is not authorization-order proof. For `completion_state = NOT_STARTED`, `effect_begin_sequence_index` and `effect_end_sequence_index` are absent and `acquired_input_ids[]`, `observable_output_ids[]`, and `external_tool_ids[]` are all empty. No output may reference a `NOT_STARTED` attempt through `effect_attempt_ids[]`; that contradiction fails closed.

A declared effect may legitimately have no runtime attempt for a specific concrete execution subject:

```text
effect_non_attempt_records[]:
    effect_non_attempt_record_id
    effect_requirement_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        declared_effect_id
    execution_subject_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    card_id?
    card_execution_id?
    effect_kind
    non_attempt_reason
    governing_control_decision_id?
    governing_failure_record_id?
    governing_skip_rule_id?
    skip_verification_evidence_id?
    backend_detail?
```

Legitimate candidate reasons include untaken branch, prior fail-stop, subject not reached, and explicit frozen skip.

An explicit frozen skip requires `governing_skip_rule_id` resolving to `rule_records[].rule_id` of kind `EFFECT_SKIP`, plus `skip_verification_evidence_id` resolving to passing `validation_evidence[]` for this exact non-attempt record, effect declaration, concrete execution subject, and active semantic/policy context. The frozen rule must permit the skip and its applicability must be verified before application. Free-text reasons and optional control/failure references are not substitute authorization. Missing, unresolved, inapplicable, or unverifiable rule/evidence forces conformance failure, not successful omission.

`BACKEND_OMISSION_DETECTED` or frozen equivalent means a reachable required effect was omitted. It forces structured execution/conformance failure and cannot coexist with successful enclosing execution.

### Unconditional declaration completeness

For every selected concrete `execution_subject_ref`, every applicable declared effect owned by that subject's representation/context must resolve to:

- one or more identified attempts for that execution subject; or
- exactly one identified legitimate non-attempt record for that execution subject; or
- structured failure if accounting cannot be completed or a reachable required effect was omitted.

This is unconditional. There is no profile, backend, optimization, or deployment mode in which declaration-completeness accounting may be silently disabled. Semantic runs may additionally project the relation through `card_execution_id`; direct Core runs must not fabricate that projection.

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
    effect_attempt_ids[]
    output_ids[]
```

A material external tool, service, model, prover, process, or instrument must not be identified only by a display name or mutable endpoint. `material_identity_status = IDENTIFIED` requires an immutable or versioned `material_identity_value`, such as an executable/content hash, tool version adequate for the active claim, model/version ID, immutable artifact ID, or frozen equivalent.

If material identity cannot be established, record `material_identity_status = UNAVAILABLE` (or frozen equivalent). Replay/evidence claims that depend on exact identity must then be weakened or rejected according to frozen policy rather than silently claiming full reproducibility. Every material external-tool record carries explicit `effect_attempt_ids[]` and `output_ids[]` arrays with at least one concrete subject across them, and attempt/output `external_tool_ids[]` links are reciprocal. Empty subject arrays are allowed only for a non-material/non-participating record that is not being used as provenance for an execution result.

Extension resolution identifies the adapter/profile contract. It does not substitute for the actual tool, service, model, prover, process, or instrument identity.

## Cache reuse provenance

Ordinary result substitution is conservative and effect-free by default. Effectful reuse requires a separately frozen replay/cache semantic preserving declared effects, contextual authorization, ordering, failure behavior, attempt provenance, output attribution, and relevant external state.

```text
cache_reuse_records[]:
    cache_reuse_record_id
    classification
    source_card_ids[]
    card_execution_ids[]
    reused_computation_id?
    cache_key_hash?
    cached_artifact_hash?
    cached_output_id?
    cache_producer_run_id?
    legality_rule_id?
    verification_evidence_id?
    material_cache_identity_hash
```

Candidate classifications are `COLD_EXECUTION`, `VERIFIED_REUSE`, and `UNVERIFIED_HIT`, or frozen equivalents. `card_execution_ids[]` identifies the exact current-run invocation(s) governed by the cache decision and reciprocates `card_executions[].cache_reuse_record_ids[]`; canonical CARD identity alone is not a runtime substitution join. For `VERIFIED_REUSE`, both `legality_rule_id` and `verification_evidence_id` are mandatory and resolve to the shared rule/evidence ledgers. The rule has kind `CACHE_SUBSTITUTION`; passing evidence binds this exact reuse record, reused computation/artifact, checked cache key/artifact content, and current inputs/contracts/context before substitution. Immutable cached-output/producer provenance may supply content identity, but unknown IDs, stale evidence, a hash alone, or the classification label cannot establish verified reuse.

For effectful substitution, the referenced rule must specifically be the applicable separately frozen replay/cache semantic; a generic cache rule is insufficient. An `UNVERIFIED_HIT` cannot satisfy a CARD or produce a verified-reuse output: verify successfully before reuse, execute cold, or fail closed. The optional notation used by other classifications does not waive verified-reuse conditions. See the complete [cache validation contract](TRACE-AND-PROVENANCE.md#cache-reuse-provenance).

Verified cache reuse does not prove cold reconstructability.

## Result provenance

```text
outputs[]:
    output_id
    result_binding_ref?:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        binding_id
    artifact_hash
    artifact_location?
    semantic_class
    status
    producer_execution_refs[]:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    producer_card_ids[]?
    producer_card_execution_ids[]?
    input_ids[]
    effect_attempt_ids[]?
    external_tool_ids[]
    backend_selection_scope_ids[]
    machinery_use_record_ids[]
    generated_artifact_ids[]?
    result_determinism_scope_ids[]
    numeric_scope_ids[]
    randomness_scope_ids[]
    failure_behavior_binding_ids[]
    cache_reuse_record_ids[]?
    evidence_status?
```

`result_binding_ref?` is the representation- and owner-qualified result identity defined by the canonical trace contract: representation kind/content identity, complete binding-owner path, and local binding ID. It resolves through the applicable cardinality-aware result-binding maps when the producer and named output binding live in different representations; local binding text or producer-array position is never sufficient, including after fusion.

`producer_execution_refs[]` is the canonical nonempty concrete-producer relation. Semantic producers resolve through `card_executions[]`; direct QSOL-CORE producers resolve through `operation_executions[]` and the hash-bound Core operation. `producer_card_ids[]` / `producer_card_execution_ids[]`, when present, are verified Semantic-lineage projections of the applicable producer refs and must agree exactly; they are absent on a legitimate direct Core entry with no Semantic ancestry. A canonical CARD ID alone is insufficient when a CARD can execute more than once, and no CARD identity may be invented merely to satisfy an output projection.

`input_ids[]` identifies the exact immutable inputs materially contributing to this output. Execution-wide input availability is not a substitute.

`effect_attempt_ids[]`, where applicable, identifies concrete effect attempts that produced or exposed the output. Each attempt reciprocally lists the output in `observable_output_ids[]`, and every referenced attempt must have begun; `NOT_STARTED` is forbidden in this relation.

`external_tool_ids[]` is always an explicit array. It identifies exact material external tools/services/models/provers and reciprocally resolves to `external_tool_versions[].output_ids[]`; it is empty when no material external tool supplied the output.

`machinery_use_record_ids[]` identifies the exact protected-use occurrence(s) that materially produced or exposed the output and is reciprocal with `machinery_use_records[].output_ids[]`. Backend scope, execution subject, artifact identity, or authorization records cannot substitute when one invocation performs several protected launches.

`generated_artifact_ids[]` identifies the exact generated artifact that executed where applicable and thereby links the output to optimization provenance, its direct toolchain producer, and its ordered transitive toolchain ancestry.

`failure_behavior_binding_ids[]` identifies the exact failure-policy provenance records that governed the producer path.

The result-determinism, numeric, randomness, and failure-policy arrays resolve directly to stable record keys defined above. Their complete applicable sets are derived from `producer_execution_refs[]` and validated lowering/contract mappings; CARD projections are never required to derive scope attribution for a lower-entry producer.

### Evidence status

```text
evidence_status:
    evidence_class      # TEST / VALIDATION / PROOF / frozen equivalent
    status
    evidence_rule_id?
    evidence_validation_id?
```

`evidence_class` must be compatible with the output's `semantic_class` and explicit evidence transition. Generic output `status` is non-epistemic and cannot promote TEST into VALIDATION or PROOF. Any non-class-preserving transition requires both `evidence_rule_id` resolving to accepted content-bound `EPISTEMIC_TRANSITION` authority and `evidence_validation_id` resolving to passing evidence for this exact output, artifact hash, original source classes, concrete producers, contributing evidence/inputs, target evidence class, and claim-publication event.

## Reproducibility manifest

A future run manifest may include:

```text
spec_version
run_id
input_representation:
    representation_kind
    representation_identity
source_hash?
semantic_ir_hash?
job_id?
deck_executions[]?
card_ids[]?
card_executions[]?
operation_executions[]?
control_decisions[]
failure_records[]
primary_failure_record_id?
execution_status
job_status
failure_behavior_bindings[]
rule_records[]
validation_evidence[]
semantic_to_core_spec_version?
semantic_to_core_implementation_version?
core_ir_hash?
semantic_to_core_result_binding_map[]?
extension_requirement_lowering_decisions[]?
qualifier_lowering_decisions[]?
machinery_requirement_lowering_decisions[]?
result_determinism_lowering_decisions[]?
numeric_contract_lowering_decisions[]?
randomness_lowering_decisions[]?
failure_behavior_lowering_decisions[]?
vector_dataflow_spec_version?
vector_dataflow_implementation_version?
vector_dataflow_ir_hash?
core_to_vector_result_binding_map[]?
extension_requirement_mapping_decisions[]?
machinery_requirement_mapping_decisions[]?
core_to_vector_result_determinism_mapping_decisions[]?
core_to_vector_numeric_contract_mapping_decisions[]?
core_to_vector_randomness_mapping_decisions[]?
failure_behavior_mapping_decisions[]?
morph_version?
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

`run_id` identifies the aggregate execution. `input_representation` is mandatory and identifies the representation that actually entered this execution plus its content-bound identity. The corresponding named layer hash, when present, must agree with that identity. Layer-specific manifest fields are conditionally required exactly when this execution traversed that layer; an untraversed layer is absent, not synthesized.

For a Semantic-IR entry that lowers to Core, `semantic_ir_hash`, the Semantic→Core specification/implementation identities, `core_ir_hash`, and every applicable first-lowering map/decision record are mandatory. For a legitimate `QSOL_CORE` entry, `core_ir_hash` identifies the input Core snapshot and the Semantic-IR/first-lowering fields are absent; the run must not fabricate `semantic_ir_hash`, a lowering implementation, or mapping history. Likewise, a direct PR #7 Core reference-machine execution that does not traverse Core→Vector/Dataflow or MORPH leaves those later layer fields absent. Entry at any other frozen representation follows the same rule: preserve actual downstream traversal and do not invent upstream history.

`source_hash`, `job_id`, `deck_executions[]`, `card_ids[]`, and `card_executions[]` are present only when that source/semantic lineage or execution structure exists for the entered representation or is explicitly retained as verifiable provenance. `operation_executions[]` carries concrete lower-operation execution for direct Core or another lower-representation entry when applicable. Their absence/presence must follow actual execution structure; no lower-entry run may fabricate Semantic CARD identities. Conversely, once a present downstream record references semantic, lowering, Core, Vector/Dataflow, or MORPH provenance, the referenced layer and its complete transitive validation closure become mandatory.

`control_decisions[]` and `failure_records[]` provide typed resolvable causes for untaken or blocked execution subjects and effect non-attempts. A failure record always identifies its typed failing scope, exact `failure_behavior_binding_ids[]`, and complete applicable result-determinism/numeric/randomness scope IDs; CARD identity is present only when a CARD execution actually caused that failure, while direct lower-operation failure uses its operation execution identity.

Failure manifests retain `backend_selection_scopes[]` and `backend_selection_decisions[]`, including denied candidates and fallback predecessors referenced by machinery records. They preserve the complete transitive reference closure, including policy bindings, requirements, rules, evidence, execution-contract scope ledgers, and observable outputs, inline or through retrievable content-bound trace records. Dangling IDs do not constitute complete failure provenance.

Every protected machinery use links to all applicable successful authorization records, its representation-qualified `execution_subject_refs[]` when execution-governed, or a genuine pre-execution RUN/DECK initiating scope only when no CARD/lower operation governs the use, and preserves authorization-before-use ordering. Semantic CARD IDs are conditional verified lineage projections, not the primary subject identity.

Every begun protected effect preserves authorization-before-begin ordering and carries its representation-qualified `effect_requirement_ref` and `execution_subject_ref`. Semantic `card_id` / `card_execution_id` are required only for CARD-backed attempts and are absent on legitimate direct Core operation attempts without Semantic lineage.

Every declared effect is unconditionally accounted for per selected concrete execution subject by attempt, legitimate identified non-attempt, or structured failure. Explicit frozen skips require a resolvable skip rule and passing invocation-bound applicability evidence.

Every changed requested/effective result-determinism or randomness contract requires resolvable versioned transition authority and passing evidence established before effective-contract activation or use.

Every EXTERNAL-ENTROPY randomness scope links to the exact protected RANDOM acquisition attempt(s) and immutable entropy input identity where material.

Every output binds nonempty representation-qualified `producer_execution_refs[]`, exact material input IDs, applicable effect attempts/tools, exact generated artifacts, stable execution-contract/failure-policy records, cache reuse, and compatible evidence status. CARD producer arrays are retained only as verified Semantic-lineage projections.

Every generated artifact identifies its exact production backend-selection decision, direct producer invocation, and exact ordered transitive toolchain ancestry. Direct invocation input/output artifact edges remain truthful, and immutable `input_ids[]` identify all material non-generated toolchain dependencies. Run-wide compiler/version summaries are not a substitute.

Every material external tool either has an immutable/versioned identity adequate for the active claim or an explicit identity-unavailable status that weakens that claim.

Every machinery mapping at both mandatory lowerings identifies the exact source and lower machinery requirement IDs in addition to typed scope endpoints, so multiple requirements owned by one scope cannot be swapped or detached.

Every Core-to-Vector/Dataflow contract mapping uses typed scope endpoints so overlapping scope namespaces cannot make source/lower ownership ambiguous.

Every optimized generated artifact links reciprocally to the optimization records that produced it. Every `VERIFIED_REUSE` record resolves its applicable legality rule and passing context-bound verification evidence; unverified hits do not supply results.

Not every optional field applies to every execution, but no material reproducibility decision may disappear merely because another execution path could have produced the same bytes. Conditional requirements stated above remain mandatory whenever their condition holds.

## Reproducibility versus portability

Portable source does not imply bit-identical execution across every target.

QSOL-MORPH states the strongest reproducibility guarantee actually provided by a source/backend/contract combination, including the scopes and outputs to which that guarantee applies.

## Failure behavior

An implementation fails closed when a required determinism, numeric, randomness, effect capability, machinery capability, failure behavior, extension, effect-accounting, material-tool identity, toolchain-build provenance, or other frozen execution contract cannot be satisfied.

A permitted weakening of a determinism, randomness, or replay guarantee requires the resolvable frozen pre-execution authority and verification evidence defined above. Recording a weaker effective value is not itself permission. Effect and machinery authorization, declared-effect accounting, truthful failure attribution, and reference integrity remain mandatory: a transition cannot authorize hidden entropy acquisition, work begun before authorization, an omitted reachable required effect, fabricated provenance, or a dangling evidence reference. Such violations produce structured failure. Unavailable material-tool identity or incomplete build-input provenance cannot support a full reproducibility claim.

General execution failure and effect-attempt completion semantics are documented separately in [Failure and Partial-Effect Semantics](FAILURE-AND-PARTIAL-EFFECTS.md).

## Design principle

> Nondeterminism, failure policy, typed execution path, concrete representation-qualified execution-subject identity, machinery-selection history, authorization order, cache reuse, external tools, optimization decisions, direct toolchain production, transitive toolchain ancestry, generated-artifact identity, immutable inputs, and entropy acquisition are scientific inputs, not invisible implementation details.
