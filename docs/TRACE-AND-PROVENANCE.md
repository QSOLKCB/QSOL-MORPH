# Trace and Provenance

QSOL-MORPH treats provenance as part of execution semantics for research workflows.

The goal is not merely to say that a program ran. The trace should make it possible to answer:

- what source and canonical Semantic IR were executed;
- how Semantic IR lowered into QSOL-CORE;
- how QSOL-CORE lowered into the mandatory Vector/Dataflow IR;
- how result bindings were preserved, mapped, split, fused, or renamed at each lowering boundary;
- which machinery governed each CARD, region, kernel, or generated execution unit;
- why automatic machinery selection chose that target;
- what exact immutable inputs were consumed;
- what result-determinism, numeric, and randomness contracts governed each relevant scope;
- what extension contracts were resolved;
- what protected effects were declared, which capability sets belonged to those effects, and which runtime attempts occurred;
- what identified outputs were produced and what semantic class/status belongs to each one;
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
job_id
deck_id
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
epistemic_classes[]
extension_requirements[]
effect_requirements[]
result_determinism_bindings[]
numeric_contract_bindings[]
randomness_contract_bindings[]
```

### Declared effect requirements

The semantic trace preserves the canonical effect-to-capability association rather than replacing it with one execution-wide or CARD-wide capability union.

A conceptual entry is:

```text
effect_requirements[]:
    declared_effect_id
    card_id
    effect_kind
    required_capabilities[]
```

`declared_effect_id` corresponds to canonical `EffectRequirement.effect_id`. The complete `required_capabilities[]` set belongs to that specific protected effect.

A CARD may declare several effects with different permission sets. For example:

```text
CARD @050
    AI_MODEL effect  -> [AI_MODEL, NETWORK]
    WRITE_FILE effect -> [FILESYSTEM_WRITE]
```

An ambiguous union such as `[AI_MODEL, NETWORK, FILESYSTEM_WRITE]` does not replace those two associations. Runtime authorization and runtime attempt provenance must remain checkable against the declared effect that actually owns each capability set.

### Source contract bindings

`result_determinism_bindings[]`, `numeric_contract_bindings[]`, and `randomness_contract_bindings[]` represent the canonical source scopes at which those requirements are attached.

A conceptual result-determinism source binding may contain:

```text
scope_kind
scope_id
source_card_ids[]
requested_result_determinism
```

Numeric and randomness source bindings follow the same scoping principle. A trace must not collapse distinct source requirements into one execution-wide declaration unless a frozen normalization rule proves that the collapse is lossless and provenance-visible.

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
qualifier_lowering_decisions[]
result_determinism_lowering_decisions[]
numeric_contract_lowering_decisions[]
randomness_lowering_decisions[]
lowering_diagnostics[]
```

### Result binding map

A conceptual entry may contain:

```text
source_card_id
source_result_binding
lower_result_binding
mapping_rule_id?
```

A result binding map is required whenever result identities are preserved or transformed unless a frozen rule permits deterministic reconstruction of the identity mapping. This requirement applies to preserved names as well as renamed, split, or fused names.

IR hashes identify representations; they do not by themselves establish which lower value corresponds to a source result binding.

### Contract lowering decisions

The determinism, numeric, randomness, qualifier, and extension decision records explain scope preservation, grouping, normalization, identity changes, and other frozen lowering choices. A backend must never be the first component to decide how semantic CARD contracts acquire QSOL-CORE meaning.

## Core-to-Vector/Dataflow trace

The mandatory QSOL-CORE → Vector/Dataflow IR transition is a separate provenance-bearing transformation.

Potential fields include:

```text
core_ir_hash
vector_dataflow_spec_version
vector_dataflow_implementation_version
vector_dataflow_ir_hash
result_binding_map[]
vector_dataflow_lowering_diagnostics[]
```

This stage's `result_binding_map[]` links QSOL-CORE result bindings to their Vector/Dataflow identities when bindings are preserved, renamed, split, fused, or otherwise transformed under a frozen rule. Omission is permitted only when a frozen deterministic reconstruction rule applies.

If the Vector/Dataflow lowering implementation, specification, control representation, effect ordering, capability metadata, binding mapping, or numeric/randomness structure changes, provenance must distinguish the resulting lower IR.

## MORPH trace

Potential fields include:

```text
vector_dataflow_ir_hash
morph_version
optimization_profile
backend_selection_scopes[]
vectorization_decisions[]
fusion_decisions[]
memory_placement_decisions[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
```

## Scoped backend-selection provenance

Backend selection may differ across a JOB. Provenance therefore uses scoped records.

Conceptually:

```text
backend_selection_scopes[]:
    scope_kind              # EXECUTION / CARD / REGION / KERNEL / GENERATED_UNIT / frozen equivalent
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

Selection-policy and tuning identity are material when selection is automatic, such as `ON BEST`.

A single execution-wide entry is valid only when one frozen machinery decision genuinely governs the whole execution. Explicit host targeting on one CARD and `ON BEST` on another remain separate scopes even if they eventually resolve to the same backend.

## Scoped result-determinism provenance

Result guarantees may differ within one DECK or JOB.

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

A scope may be retained from source or introduced by a semantics-preserving lowering that groups source CARDs. Grouping must preserve the strongest applicable source requirements or follow another frozen normalization rule that is provenance-visible.

A recorded transition is evidence, not authorization. If a requested scoped guarantee cannot be satisfied and no pre-execution rule authorizes a weaker guarantee, execution fails closed.

## Scoped numeric provenance

Numeric contracts and effective material modes may differ across CARDs, regions, or kernels.

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

Material numeric choices may include FMA behavior, denormal handling, effective precision, reduction strategy, selected math-library mode, or another frozen numeric-mode identity.

A single execution-wide numeric scope is valid only when a frozen rule establishes that one contract and one material mode govern the entire execution.

## Scoped randomness provenance

Randomness requirements may also differ within one DECK or JOB.

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

Seeded replay requires more than an integer seed. Where applicable, RNG algorithm, version, seed, stream identity, and parallel partitioning/stream mapping are material inputs.

A single execution-wide randomness scope is valid only under a frozen lossless normalization rule.

## Execution trace

Potential fields include:

```text
runtime_compiler_versions[]
backend_selection_scopes[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
inputs[]
required_capabilities[]
granted_capabilities[]
denied_capabilities[]
capability_policy_id
capability_policy_version
capabilities_used[]
resolved_extensions[]
effect_attempts[]
cache_reuse_records[]
external_tool_versions[]
start_stop_metadata?
```

Global capability sets describe the execution-wide decision space, but they do not replace the per-effect requirement and per-attempt capability sets.

## Identified input provenance

Every material runtime input is bound to the exact immutable value or artifact content actually consumed.

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

A path, URL, dataset name, model name, branch name, or other mutable locator is retrieval context only. It must not substitute for immutable input identity.

If a material input contributes to a research result and the required immutable identity cannot be established, replay/provenance validation fails closed where the active contract requires auditability.

## Capability provenance

Capability provenance distinguishes requirement, authorization, and use.

For a denied network execution, a trace may record:

```text
required_capabilities = [NETWORK]
granted_capabilities = []
denied_capabilities = [NETWORK]
capability_policy_id = ...
capability_policy_version = ...
capabilities_used = []
```

This explains why a protected effect did not begin.

The complete required capability set is also carried by the declared effect and by each corresponding runtime attempt. An attempt must not begin until every required capability is granted.

## Resolved extension provenance

Extensions are independently versionable.

`resolved_extensions[]` should bind, where material:

```text
profile_name
resolved_version
contract_id_or_hash
implementation_or_content_identity?
```

A profile name alone is insufficient if different versions can change lowering, effects, or results.

## Per-effect-attempt provenance

Every protected external effect attempt has its own runtime identity and a reference to the declared semantic effect that produced it.

Conceptually:

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
    observable_artifacts[]
```

`declared_effect_id` references canonical `EffectRequirement.effect_id`. `effect_attempt_id` identifies this concrete runtime attempt. They are not interchangeable.

Preserving both identities lets provenance detect missing attempts, duplicate attempts, retries, or several same-kind effects originating from one CARD.

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

Known completion takes precedence over uncertainty about broader consequences. A process known to have exited is `COMPLETED` even if the trace cannot enumerate every external consequence of that process.

Successful executions record completed effect attempts too. Per-attempt provenance is not merely a failure-reporting mechanism.

## Result trace

Results are identified records rather than bare hashes plus one shared semantic class.

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

Each output owns its own epistemic class and status. One validated output must not promote another simulation or TEST output produced by the same JOB.

`backend_selection_scope_ids[]` identifies the machinery that produced the output. The determinism/numeric/randomness scope references identify the execution contracts that governed it. `cache_reuse_record_ids[]`, when present, identifies legal cache reuse that contributed to producing or supplying that output.

Execution-wide failure fields may include:

```text
execution_status
job_status
deck_status
failure_card_id
failure_class
failure_stage
effect_attempts[]
```

## Failure and partial-effect provenance

A failed execution remains a provenance-bearing execution event.

Capability denial occurs before the protected effect begins and therefore records the identified attempt as `NOT_STARTED`.

An unhandled CARD failure stops its DECK by default. An unhandled DECK failure fails the enclosing JOB by default, and no later DECK begins. Dependent consumers or comparisons must not execute against missing or partial failed outputs as though they were complete.

Useful failure fields include:

```text
execution_status
job_status
deck_status
failure_card_id
failure_class
failure_stage
backend_detail?
completed_decks[]
effect_attempts[]
observable_artifacts[]
```

The canonical field for the CARD whose unhandled failure produced the enclosing failure record is `failure_card_id`. `card_id` remains appropriate inside an effect-attempt record that identifies the CARD that initiated that attempt.

## Hash identities

A trace should distinguish at least:

- source-text identity;
- canonical Semantic-IR identity;
- lowered QSOL-CORE identity;
- mandatory Vector/Dataflow IR identity;
- generated target identity;
- resolved extension/contract identities;
- immutable material input identities;
- cache identities where reuse occurs;
- each identified output/result identity.

These are different objects and should not be collapsed into one digest.

## Provenance graph and epistemic boundaries

CARD dependencies naturally form a provenance graph.

For example:

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

A cached result may be valid reuse without proving that a cold reconstruction still succeeds. Conversely, merely finding a matching cache entry does not authorize semantic substitution.

A trace should distinguish reuse classifications conceptually such as:

```text
COLD_EXECUTION
VERIFIED_CACHE_REUSE
UNVERIFIED_CACHE_HIT
```

The exact names are not frozen.

### Identified cache-reuse records

When cache lookup or reuse is material, provenance should record identified entries such as:

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

The record identifies **whether** work was executed cold or reused, **what** computation/artifact was reused, **which material cache identity justified the lookup**, and **which legality/verification rule authorized substitution** when reuse occurred.

A verified reuse record does not prove cold reconstructability. A separate cold execution or equivalent evidence is needed for that claim.

### Effectful cache restriction

Ordinary result/value substitution from cache is legal only for computations proven safe for reuse under the active contract. The conservative default is effect-free reuse.

An effectful CARD must not be satisfied merely by returning a prior cached value if that would skip a declared external effect. A cached file write, process launch, network request, AI call, clock read, or other protected effect cannot silently stand in for a new required effect attempt.

Effectful reuse requires a separately frozen cache/replay semantic that preserves or explicitly defines:

- declared effect identity and whether the effect executes again;
- complete capability authorization boundaries;
- source/effect/failure ordering;
- effect-attempt identity and completion-state provenance;
- externally observable artifacts/state;
- randomness and external-input replay rules;
- CARD/DECK/JOB failure behavior;
- per-output semantic class/status and execution-scope links.

Absent such a frozen rule, the implementation executes the effect normally or fails closed; it must not relabel skipped work as verified reuse.

A cached artifact may still be used as an explicit declared input or reference fixture when the semantic contract says so. In that case the cached artifact itself is bound by immutable input provenance.

## Optimization provenance

An optimized implementation remains connected to its reference semantics.

Useful records may include:

```text
reference_ir_hash
optimized_ir_hash
transformation_sequence[]
legality_witnesses[]
target_context_measurements[]
resource_model_assumptions[]
```

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

Not every execution requires every optional field. The active specification, execution contracts, capability policy, extension set, lowering contracts, backend-selection policy, and cache/replay rules define the minimum trace required for the claim being made.

However, executable research results must not begin life without enough provenance to bind identified outputs to their canonical program, immutable inputs, semantic class/status, scoped machinery/determinism/numeric/randomness decisions, extension set, authorization decisions, cache/reuse context where relevant, and execution/failure history.

The roadmap therefore places the trace/failure/provenance foundation before the first executable QSOL reference machine.

## Principle

> A result without enough provenance to support its claim should not be promoted beyond the evidence actually recorded.
