# Trace and Provenance

QSOL-MORPH treats provenance as part of execution semantics for research workflows.

The goal is not merely to say that a program ran. The goal is to make it possible to answer:

- what source was executed;
- what semantic representation was produced;
- how Semantic IR lowered into QSOL-CORE;
- how QSOL-CORE lowered into the mandatory Vector/Dataflow IR;
- how result bindings were preserved or renamed at each lowering boundary;
- what backend was selected for each governed execution unit;
- why each backend was selected;
- what transformations were applied;
- what exact immutable inputs and capabilities were required, granted, denied, and used;
- what identified outputs were produced and what semantic class/status belongs to each one;
- what result determinism was requested and actually provided for each governed scope;
- what numeric contract and material numeric mode governed each relevant execution scope;
- what randomness contract, RNG identity, and effective random stream governed each relevant execution scope;
- what extension versions/contracts were active;
- which declared effects produced which runtime attempts, which capability set governed each attempt, and what completion state each reached;
- whether execution failed and what effects were already observable.

## Trace layers

A future trace may contain several layers:

```text
SOURCE TRACE
SEMANTIC TRACE
SEMANTIC-TO-CORE TRACE
CORE-TO-VECTOR/DATAFLOW TRACE
MORPH TRACE
EXECUTION TRACE
RESULT TRACE
```

### Source trace

Potential fields:

```text
source_hash
spec_version
deck_id
job_id
source_location
```

### Semantic trace

Potential fields:

```text
semantic_ir_hash
card_ids
dependency_graph_hash
epistemic_classes
extension_requirements[]
result_determinism_bindings[]
numeric_contract_bindings[]
randomness_contract_bindings[]
required_capabilities[]
```

`result_determinism_bindings[]` represents the canonical scopes at which source result-determinism requirements are attached, including CARD-scoped requirements where present. A conceptual source binding may contain:

```text
scope_kind
scope_id
source_card_ids[]
requested_result_determinism
```

A trace must not collapse several distinct source result requirements into one execution-wide value unless a frozen normalization rule proves that the normalization preserves every source requirement.

`numeric_contract_bindings[]` similarly represents the canonical scopes in which numeric contracts are attached. A trace must not collapse several distinct source numeric contracts into one global identifier unless a frozen normalization rule proves that the collapse preserves meaning.

`randomness_contract_bindings[]` represents the canonical scopes in which randomness contracts are attached. Separate CARDs may require distinct seeded streams, RNG versions, entropy modes, or stream identities, so those source requirements must not be collapsed into one global randomness declaration unless a frozen normalization rule proves the collapse is lossless.

### Semantic-to-Core trace

The Semantic IR → QSOL-CORE transition is itself provenance-bearing.

Potential fields:

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

`result_binding_map[]` records any deterministic preservation or renaming of source result bindings into QSOL-CORE identities. A conceptual entry may contain:

```text
source_card_id
source_result_binding
lower_result_binding
mapping_rule_id?
```

If a binding is unchanged, an explicit identity mapping or a frozen rule permitting its deterministic reconstruction may be used. If a binding is renamed, the map must make that rename provenance-visible; IR hashes alone do not tell a consumer which lower name corresponds to a source result.

A backend should never be the first component to decide how semantic CARDs lower into QSOL-CORE.

### Core-to-Vector/Dataflow trace

The mandatory QSOL-CORE → Vector/Dataflow IR transition is a separate provenance-bearing transformation and must not disappear into MORPH bookkeeping.

Potential fields:

```text
core_ir_hash
vector_dataflow_spec_version
vector_dataflow_implementation_version
vector_dataflow_ir_hash
result_binding_map[]
vector_dataflow_lowering_diagnostics[]
```

This stage's `result_binding_map[]` links QSOL-CORE result bindings to their Vector/Dataflow identities when the lower IR preserves, splits, fuses, or renames bindings under a frozen rule. Both lowering boundaries therefore retain explicit name provenance rather than relying on consumers to reverse-engineer identity from graph structure.

If the Vector/Dataflow lowering implementation, specification, graph structure, control representation, effect ordering, capability metadata, result-binding mapping, or numeric/randomness structure changes, the trace must be able to identify the exact lower IR that MORPH received.

### Morph trace

Potential fields:

```text
vector_dataflow_ir_hash
morph_version
optimization_profile
backend_selection_scopes[]
vectorization decisions
fusion decisions
memory-placement decisions
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
```

Backend selection is scoped because one JOB may intentionally target different machinery for different CARDs, regions, kernels, or generated units. A conceptual entry may contain:

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

Selection-policy and tuning identity are material when selection is automatic, such as `ON BEST`. Recording only a selected backend says what ran but may not explain or reproduce why that machinery was chosen.

A single execution-wide backend-selection scope is valid only when a frozen rule establishes that one target decision governs the whole execution. Explicit host targeting on one CARD and `ON BEST` on another must remain separate entries even when both eventually resolve to the same backend.

## Scoped result-determinism provenance

Result-determinism requirements may differ within one DECK or JOB because the canonical model permits CARD-scoped contracts.

For example, one CARD may require `STRICT` while another permits `NUMERIC`. A trace therefore must not use one singular requested/effective result-determinism pair for the whole execution unless a frozen normalization rule proves that one pair faithfully represents every governed computation.

Conceptually:

```text
result_determinism_scopes[]:
    scope_kind              # EXECUTION / CARD / REGION / KERNEL / frozen equivalent
    scope_id
    source_card_ids[]
    requested_result_determinism
    effective_result_determinism
    transition_authorized_by?
    backend_unit_id?
```

A scope can be retained from a source CARD or introduced by a semantics-preserving lowering when several source CARDs are grouped into one lower region/kernel. Any grouping must preserve the strongest applicable source requirements or follow another frozen normalization rule that is provenance-visible.

If a scoped source requirement requests `STRICT` and an execution policy explicitly permits `NUMERIC` for that scope, the trace retains both values and the rule/policy authorizing the transition. Recording only the effective value would erase the source requirement; recording only the requested value would misstate what the backend delivered.

A transition record is evidence, not permission. A backend must fail closed if the requested scoped contract cannot be satisfied and no pre-execution rule authorizes a weaker scoped contract.

## Scoped numeric provenance

`numeric_execution_scopes[]` records contract/mode information at the scope where it is actually valid. A conceptual entry may contain:

```text
scope_kind              # EXECUTION / CARD / REGION / KERNEL / frozen equivalent
scope_id
source_card_ids[]
numeric_contract_id
numeric_contract_hash
material_numeric_mode
backend_unit_id?
```

A single execution-wide numeric scope is valid only when a frozen rule establishes that one contract and one material mode govern the whole execution. If separate CARDs, regions, or kernels use different contracts or contract-permitted modes, those must remain distinct entries.

## Scoped randomness provenance

Randomness requirements may also differ within one DECK or JOB because `randomness_contract` may be attached at CARD or another frozen scope.

A DECK can legally contain two seeded computations using different RNG algorithms, versions, seeds, streams, or parallel partitioning rules. A trace therefore must not represent randomness as one execution-wide singleton unless a frozen normalization rule proves that one entry faithfully represents every governed computation.

Conceptually:

```text
randomness_execution_scopes[]:
    scope_kind              # EXECUTION / CARD / REGION / KERNEL / frozen equivalent
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

Seeded replay requires more than a seed. When applicable, the RNG algorithm, version, seed, stream identity, and parallel partitioning/stream mapping are material inputs for the particular scope they govern.

If one CARD requires `SEEDED` with one stream and another CARD requires a distinct seeded stream, those remain separate scope entries. If a source requirement is weakened under an explicit pre-execution rule, the requested and effective modes plus the authorizing rule remain attached to that scope.

A transition record is evidence, not permission. A backend must fail closed if a scoped randomness requirement cannot be satisfied and no pre-execution rule authorizes a different mode.

### Execution trace

Potential fields:

```text
runtime/compiler versions
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
external tool versions
start/stop metadata where permitted
```

Each `backend_selection_scopes[]` entry records the selected machinery and, where applicable, the explicit target request or automatic-selection policy/tuning identity for the CARDs or lower execution unit it governs.

Each `numeric_execution_scopes[]` entry records the active numeric contract plus the **material numeric mode** used for that scope when contract-permitted choices can change legal result bytes. Material choices may include FMA behavior, denormal handling, effective precision, selected math-library mode, reduction strategy, or another frozen numeric-mode identity.

Each `result_determinism_scopes[]` entry records the requested and effective guarantee for the computation it governs. A DECK containing both `STRICT` and `NUMERIC` CARDs therefore retains those distinctions rather than weakening the strict CARD or overstating the numeric CARD.

Each `randomness_execution_scopes[]` entry records the requested/effective randomness contract and every replay-relevant RNG input for the computation it governs. Separate seeded computations must retain separate scope identities when their streams or RNG configuration differ.

## Identified input provenance

Every material runtime input must be traceable to the exact immutable value or artifact content actually consumed.

A conceptual input entry may contain:

```text
input_id
input_kind
canonical_value?
content_hash?
artifact_id_or_version?
location?
media_or_schema_type?
source_card_ids[]?
```

`input_id` is the stable provenance identity for this consumed input. Inline scalar/record inputs may bind a canonical value directly. Files, datasets, models, downloaded objects, or other mutable external resources require a content hash, immutable artifact/version identity, or equivalent frozen identity sufficient to distinguish the actual bytes/content consumed.

A path, URL, dataset name, model name, branch name, or other mutable locator is retrieval context only. It must not substitute for immutable input identity. If a material input contributes to a research result and its consumed identity cannot be established, the execution cannot claim reproducible provenance for that input and should fail closed where the active contract requires replay/auditability.

Capability provenance must distinguish requirement, authorization, and use. A failed execution denied `NETWORK` should be able to show:

```text
required_capabilities = [NETWORK]
granted_capabilities = []
denied_capabilities = [NETWORK]
capability_policy_id = ...
capability_policy_version = ...
capabilities_used = []
```

This records why the protected effect did not begin rather than merely showing that it was never used.

Global capability sets are not sufficient on their own when an individual effect attempt requires multiple permissions. The attempt itself must bind the full capability set that governed authorization for that external action.

Extensions are independently versionable. `resolved_extensions[]` should therefore bind, where material:

```text
profile_name
resolved_version
contract_id_or_hash
implementation/content identity where required
```

A profile name alone is insufficient provenance if different versions can change lowering, effects, or results.

## Per-effect-attempt provenance

Every protected external effect attempt should have its own runtime identity, a reference to its declared semantic effect identity, complete required-capability set, and completion state.

A conceptual entry may contain:

```text
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

`declared_effect_id` references the canonical `EffectRequirement.effect_id` from Semantic IR. It is distinct from `effect_attempt_id`: one identifies the declared semantic effect, while the other identifies this concrete runtime attempt. Preserving both lets provenance detect missing attempts, duplicate attempts, retries, or several same-kind effects originating from one CARD without guessing from `effect_kind` alone.

`required_capabilities[]` contains **every** capability that must be authorized before that attempt begins. For example, an AI-backed network request might require both `AI_MODEL` and `NETWORK`; recording only one would be insufficient to prove that the complete authorization boundary was satisfied.

The attempt must not begin unless every required capability in that set has been granted under the active capability policy. The global `granted_capabilities[]` / `denied_capabilities[]` fields describe the execution-wide decision space, while the per-attempt set identifies which permissions governed this specific effect.

`completion_state` is one of:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

or frozen equivalents.

The candidate states are mutually exclusive and evaluated with this precedence:

```text
1. NOT_STARTED   if the protected effect never began.
2. COMPLETED     if the effect reached its defined completion boundary.
3. If the effect began and is known not to have completed:
   a. ABORTED_CLEAN if no externally observable change occurred.
   b. PARTIAL       if some externally observable portion occurred.
   c. UNKNOWN       if clean-vs-partial observability cannot be established.
4. UNKNOWN       if whether the effect reached its completion boundary cannot be established.
```

Known completion therefore takes precedence over uncertainty about the extent of side effects outside the effect's completion contract. For example, a process known to have exited is `COMPLETED` even if the wider external consequences of that process cannot be fully enumerated.

`ABORTED_CLEAN` prevents a cleanly aborted buffered/atomic operation from being falsely described as either `PARTIAL` or `UNKNOWN`. It is distinct from `NOT_STARTED` because the protected operation did begin.

This is an array because a DECK may contain many effectful CARDs and a single CARD may eventually initiate more than one external effect. A single aggregate `partial_effect_state` cannot explain which write, process launch, network operation, or external tool invocation became observable.

Successful executions record completed effect attempts too. Effect-attempt provenance is not only a failure-reporting mechanism.

## Result trace

Results are represented as identified output records rather than parallel plural fields plus one shared semantic class.

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
    test_status?
    validation_status?       # only for explicit VALIDATION semantics
    proof_status?            # only for explicit PROOF semantics
```

Each output record binds the artifact/result identity to **its own** epistemic `semantic_class` and execution/status information. A JOB that emits both a simulation artifact and a separately validated artifact therefore cannot serialize both under one shared class.

`result_binding` links the output to the canonical or mapped binding that produced it where applicable. `producer_card_ids[]` preserves the semantic provenance edge back to its producer(s), while the backend-selection/determinism/numeric/randomness scope references identify the machinery and execution contracts that governed that particular output.

An output must not acquire `VALIDATION` or `PROOF` status merely because another output in the same JOB has that status.

Execution-wide fields may still include:

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

Capability denial must occur before the protected effect begins and therefore records that identified attempt as `NOT_STARTED`. Other precondition failures should occur before the effect where possible. If an operation began and is known not to have completed, it records `ABORTED_CLEAN` when no observable external change occurred, `PARTIAL` when some incomplete portion became observable, and `UNKNOWN` only when that distinction cannot be established. If completion itself cannot be established, the attempt is also `UNKNOWN`. A known-completed attempt remains `COMPLETED` regardless of uncertainty about broader external consequences.

Useful failure fields may include:

```text
job_status
deck_status
failure_card_id
failure_class
failure_stage
backend_detail?
prior_committed_effects[]
completed_decks[]
effect_attempts[]
observable_artifacts[]
```

`failure_card_id` is the canonical field name for the CARD whose unhandled failure produced the enclosing failure record. Failure schemas must not alternate between `card_id` and `failure_card_id` for this meaning.

An unhandled CARD failure stops its DECK by default, and an unhandled DECK failure fails its enclosing JOB by default. The trace must not imply that dependent DECKs or comparisons successfully consumed a missing or partial failed result.

An unhandled execution failure should not silently emit an ordinary successful research result.

## Hashes

Hashes should bind canonical semantic content where possible.

A trace should distinguish:

- source-text identity;
- canonical semantic identity;
- lowered QSOL-CORE identity;
- mandatory Vector/Dataflow IR identity;
- generated target identity;
- immutable material input identities;
- extension/contract identity;
- each identified output/result identity.

Those are different objects and should not be collapsed into one digest.

## Provenance graph

CARD dependencies naturally create a provenance graph.

Example:

```text
@011 OBSERVE MASS 4.2 kg
@012 SET C 299792458 m/s
@013 DERIVE ENERGY = MASS * C * C
@014 TEST ENERGY
@015 SAVE ENERGY
```

The result can retain edges back to the observation, parameter, derivation, TEST card, and save operation that produced or checked it.

`@014 TEST ENERGY` remains a `TEST`. It must not be described or serialized as `VALIDATION` merely because it participates in checking a result. If the language later supports an epistemically stronger `VALIDATION` class, promotion to that class requires a distinct CARD or explicit evidence-transition rule defined by the frozen specification.

## External evidence

External evidence must remain explicit.

If a TEST compares against a file, external instrument, network service, benchmark, or formal tool, the trace should identify the relevant evidence boundary rather than treating the external result as native QSOL truth.

A successful TEST against external evidence still does not silently become VALIDATION or PROOF.

## Cache provenance and legality

A cached result may be valid reuse without proving that a cold reconstruction still succeeds, but cache provenance alone does **not** authorize semantic substitution.

A trace should distinguish at least conceptually between:

```text
COLD EXECUTION
VERIFIED CACHE REUSE
UNVERIFIED CACHE HIT
```

The exact categories are not frozen.

Ordinary result/value substitution from cache is legal only for computations proven safe for reuse under the active contract. In the conservative default, that means the reused computation is effect-free and substitution preserves result determinism, numeric behavior, randomness/replay requirements, failure behavior, ordering, epistemic class, dependencies, input identities, machinery-selection provenance, and output provenance.

An effectful CARD must **not** be satisfied merely by returning a prior cached value if doing so skips a declared external effect. A cached file write, process launch, network request, AI call, clock read, or other protected effect cannot silently stand in for a new required effect attempt, because that would bypass capability authorization, effect ordering, failure behavior, and per-attempt provenance.

Effectful reuse requires an explicit frozen cache/replay semantic that defines what is being replayed or reused and proves preservation of every affected contract, including:

- the declared effect identity and whether the effect must execute again;
- the complete capability authorization boundary;
- source/effect/failure ordering;
- effect-attempt identity and completion-state provenance;
- externally observable artifacts/state;
- randomness/external-input replay rules;
- failure behavior and JOB/DECK propagation;
- per-output semantic class/status and execution-scope links.

Absent such a frozen rule, the implementation must execute the effect normally or fail closed; it must not relabel skipped work as `VERIFIED CACHE REUSE`.

A cached artifact may still be used as an explicit declared input, reference fixture, or optimization artifact when the semantic contract says so. That is different from silently replacing an effectful CARD evaluation.

Cache provenance should bind the material cache identity, including specification/compiler/backend-selection scopes/target/determinism/numeric/randomness/extension, immutable input identities, and lower-IR inputs required to justify reuse. Where machinery selection, result determinism, numeric behavior, or randomness is scoped, the cache identity must bind the relevant scoped entries rather than ambiguous global singletons.

## Optimization provenance

An optimized implementation must remain connected to its reference semantics.

Useful trace information may include:

- reference IR hash;
- optimized IR hash;
- transformation sequence;
- legality witnesses/checks;
- target-context measurements;
- resource-model assumptions.

## Benchmark provenance

Historical benchmark observations must not silently become universal performance claims.

A transferable target claim should identify:

- target machine/context;
- measured workload;
- correctness validation;
- provenance binding;
- measurement method.

This distinction is intentionally aligned with the optimization discipline developed in QSOL's OPT work: correctness and evidence boundaries outrank attractive speed numbers.

## Trace policy

Not every execution needs every field. The active specification, backend-selection scopes, scoped result-determinism requirements, scoped numeric contracts, scoped randomness contracts, immutable input requirements, capability policy, extension set, semantic-to-core lowering contract, Vector/Dataflow lowering contract, and cache/replay legality rules should define the minimum trace required for a claim.

The roadmap requires a trace/failure/provenance foundation before the first executable QSOL reference machine. Later phases may enrich the trace, but executable research results must not begin life without source/IR/input/execution-contract/machinery/policy binding.

## Principle

> A result without enough provenance to support its claim should not be promoted beyond the evidence actually recorded.