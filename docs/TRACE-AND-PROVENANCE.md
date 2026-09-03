# Trace and Provenance

QSOL-MORPH treats provenance as part of execution semantics for research workflows.

The goal is not merely to say that a program ran. The goal is to make it possible to answer:

- what source was executed;
- what semantic representation was produced;
- how Semantic IR lowered into QSOL-CORE;
- how QSOL-CORE lowered into the mandatory Vector/Dataflow IR;
- what backend was selected;
- why that backend was selected;
- what transformations were applied;
- what inputs and capabilities were required, granted, denied, and used;
- what outputs were produced;
- what result determinism was requested and actually provided;
- what numeric contract and material numeric mode governed each relevant execution scope;
- what randomness was requested and actually used;
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
requested_result_determinism
numeric_contract_bindings[]
requested_randomness_contract
required_capabilities[]
```

`numeric_contract_bindings[]` represents the canonical scopes in which numeric contracts are attached, including CARD-scoped contracts where present. A trace must not collapse several distinct source contracts into one global identifier unless a frozen normalization rule proves that the collapse preserves meaning.

### Semantic-to-Core trace

The Semantic IR → QSOL-CORE transition is itself provenance-bearing.

Potential fields:

```text
semantic_ir_hash
semantic_to_core_spec_version
semantic_to_core_implementation_version
core_ir_hash
resolved_extensions[]
qualifier_lowering_decisions[]
numeric_contract_lowering_decisions[]
lowering_diagnostics[]
```

A backend should never be the first component to decide how semantic CARDs lower into QSOL-CORE.

### Core-to-Vector/Dataflow trace

The mandatory QSOL-CORE → Vector/Dataflow IR transition is a separate provenance-bearing transformation and must not disappear into MORPH bookkeeping.

Potential fields:

```text
core_ir_hash
vector_dataflow_spec_version
vector_dataflow_implementation_version
vector_dataflow_ir_hash
vector_dataflow_lowering_diagnostics[]
```

If the Vector/Dataflow lowering implementation, specification, graph structure, control representation, effect ordering, capability metadata, or numeric structure changes, the trace must be able to identify the exact lower IR that MORPH received.

### Morph trace

Potential fields:

```text
vector_dataflow_ir_hash
morph_version
optimization_profile
selected_backend
backend_selection_policy_id
backend_selection_policy_version
backend_selection_tuning_id
backend_selection_tuning_hash
vectorization decisions
fusion decisions
memory-placement decisions
numeric_execution_scopes[]
```

`backend_selection_policy_*` and tuning identity are material when selection is automatic, such as `ON BEST`. Recording only the backend says what ran but may not explain or reproduce why that machinery was chosen.

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

### Execution trace

Potential fields:

```text
target architecture
device
runtime/compiler versions
requested_result_determinism
effective_result_determinism
determinism_transition_authorized_by
numeric_execution_scopes[]
requested_randomness_mode
effective_randomness_mode
randomness_transition_authorized_by
rng_algorithm
rng_version
seed
stream_id
parallel_partitioning
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

Each `numeric_execution_scopes[]` entry records the active numeric contract plus the **material numeric mode** used for that scope when contract-permitted choices can change legal result bytes. Material choices may include FMA behavior, denormal handling, effective precision, selected math-library mode, reduction strategy, or another frozen numeric-mode identity.

`requested_result_determinism` and `effective_result_determinism` are intentionally distinct. If source requests `STRICT` but an execution policy explicitly permits `NUMERIC`, the trace must retain both contracts and the rule or policy that authorized the transition. Recording only the final class would erase the original requirement; recording only the requested class would misstate the guarantee actually delivered.

Randomness uses the same separation. If source requests `SEEDED` and an explicit policy permits another mode, the trace must retain:

```text
requested_randomness_mode
effective_randomness_mode
randomness_transition_authorized_by
```

A policy-authorized transition is still a semantic event and must not be reconstructed from the effective mode alone.

Seeded replay requires more than a seed. The RNG algorithm, version, stream identity, and parallel partitioning/stream mapping are material reproducibility inputs when applicable.

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

### Result trace

Potential fields:

```text
output hashes
test status
validation status where an explicit VALIDATION transition occurred
numeric_execution_scopes[]
result semantic class
artifact locations
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
card_id
failure_class
failure_stage
backend_detail?
prior_committed_effects[]
completed_decks[]
effect_attempts[]
observable_artifacts[]
```

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
- extension/contract identity;
- result identity.

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

## Cache provenance

A cached result may be valid reuse without proving that a cold reconstruction still succeeds.

A trace should distinguish at least conceptually between:

```text
COLD EXECUTION
VERIFIED CACHE REUSE
UNVERIFIED CACHE HIT
```

The exact categories are not frozen.

Cache provenance should bind the material cache identity, including specification/compiler/backend/target/numeric/randomness/extension and lower-IR inputs required to justify reuse. Where numeric behavior is scoped, the cache identity must bind the relevant scoped contract/mode entries rather than one ambiguous global pair.

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

Not every execution needs every field. The active specification, determinism profile, scoped numeric contracts, randomness contract, capability policy, extension set, semantic-to-core lowering contract, Vector/Dataflow lowering contract, and backend-selection policy should define the minimum trace required for a claim.

The roadmap requires a trace/failure/provenance foundation before the first executable QSOL reference machine. Later phases may enrich the trace, but executable research results must not begin life without source/IR/execution-contract/policy binding.

## Principle

> A result without enough provenance to support its claim should not be promoted beyond the evidence actually recorded.
