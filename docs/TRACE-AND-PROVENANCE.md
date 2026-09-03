# Trace and Provenance

QSOL-MORPH treats provenance as part of execution semantics for research workflows.

The goal is not merely to say that a program ran. The goal is to make it possible to answer:

- what source was executed;
- what semantic representation was produced;
- what backend was selected;
- why that backend was selected;
- what transformations were applied;
- what inputs and capabilities were required, granted, denied, and used;
- what outputs were produced;
- what result determinism was requested and actually provided;
- what numeric contract governed legal result variation;
- what randomness was requested and actually used;
- what extension versions/contracts were active;
- whether execution failed and what effects were already observable.

## Trace layers

A future trace may contain several layers:

```text
SOURCE TRACE
SEMANTIC TRACE
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
numeric_contract_id
requested_randomness_contract
required_capabilities[]
```

### Morph trace

Potential fields:

```text
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
numeric_contract_id
numeric_contract_hash
```

`backend_selection_policy_*` and tuning identity are material when selection is automatic, such as `ON BEST`. Recording only the backend says what ran but may not explain or reproduce why that machinery was chosen.

### Execution trace

Potential fields:

```text
target architecture
device
runtime/compiler versions
requested_result_determinism
effective_result_determinism
determinism_transition_authorized_by
numeric_contract_id
numeric_contract_hash
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
external tool versions
start/stop metadata where permitted
```

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

Extensions are independently versionable. `resolved_extensions[]` should therefore bind, where material:

```text
profile_name
resolved_version
contract_id_or_hash
implementation/content identity where required
```

A profile name alone is insufficient provenance if different versions can change lowering, effects, or results.

### Result trace

Potential fields:

```text
output hashes
test status
validation status where an explicit VALIDATION transition occurred
error/tolerance contract
result semantic class
artifact locations
execution_status
job_status
deck_status
failure_card_id
failure_class
failure_stage
partial_effect_state
```

## Failure and partial-effect provenance

A failed execution remains a provenance-bearing execution event.

The trace should distinguish whether an effect was:

```text
NOT_STARTED
COMPLETED
PARTIAL
UNKNOWN
```

or frozen semantic equivalents.

Capability denial must occur before the protected effect begins and therefore records `NOT_STARTED`. Other precondition failures should occur before the effect where possible; if an external operation has already become observable before failing, the trace must not imply rollback that did not happen.

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
partial_effect_state
observable_artifacts[]
```

An unhandled CARD failure stops its DECK by default, and an unhandled DECK failure fails its enclosing JOB by default. The trace must not imply that dependent DECKs or comparisons successfully consumed a missing or partial failed result.

An unhandled execution failure should not silently emit an ordinary successful research result.

## Hashes

Hashes should bind canonical semantic content where possible.

A trace should distinguish:

- source-text identity;
- canonical semantic identity;
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

Cache provenance should bind the material cache identity, including specification/compiler/backend/target/numeric/randomness/extension inputs required to justify reuse.

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

Not every execution needs every field. The active specification, determinism profile, numeric contract, randomness contract, capability policy, extension set, and backend-selection policy should define the minimum trace required for a claim.

The roadmap requires a trace/failure/provenance foundation before the first executable QSOL reference machine. Later phases may enrich the trace, but executable research results must not begin life without source/IR/execution-contract/policy binding.

## Principle

> A result without enough provenance to support its claim should not be promoted beyond the evidence actually recorded.
