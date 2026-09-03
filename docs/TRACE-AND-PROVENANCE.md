# Trace and Provenance

QSOL-MORPH treats provenance as part of execution semantics for research workflows.

The goal is not merely to say that a program ran. The goal is to make it possible to answer:

- what source was executed;
- what semantic representation was produced;
- what backend was selected;
- what transformations were applied;
- what inputs and capabilities were used;
- what outputs were produced;
- what result determinism was requested and actually provided;
- what numeric contract governed legal result variation;
- what randomness configuration generated any pseudorandom stream;
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
extension_profiles
requested_result_determinism
numeric_contract_id
randomness_contract
```

### Morph trace

Potential fields:

```text
morph_version
optimization_profile
selected_backend
vectorization decisions
fusion decisions
memory-placement decisions
numeric_contract_id
numeric_contract_hash
```

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
randomness_mode
rng_algorithm
rng_version
seed
stream_id
parallel_partitioning
capabilities used
external tool versions
start/stop metadata where permitted
```

`requested_result_determinism` and `effective_result_determinism` are intentionally distinct. If source requests `STRICT` but an execution policy explicitly permits `NUMERIC`, the trace must retain both contracts and the rule or policy that authorized the transition. Recording only the final class would erase the original requirement; recording only the requested class would misstate the guarantee actually delivered.

Seeded replay requires more than a seed. The RNG algorithm, version, stream identity, and parallel partitioning/stream mapping are material reproducibility inputs when applicable.

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

A precondition or capability rejection should occur before the effect begins where practical and therefore record `NOT_STARTED`. If an external operation has already become observable before failing, the trace must not imply rollback that did not happen.

Useful failure fields may include:

```text
card_id
failure_class
failure_stage
backend_detail?
prior_committed_effects[]
partial_effect_state
observable_artifacts[]
```

An unhandled execution failure should not silently emit an ordinary successful research result.

## Hashes

Hashes should bind canonical semantic content where possible.

A trace should distinguish:

- source-text identity;
- canonical semantic identity;
- generated target identity;
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

Not every execution needs every field. The active specification, determinism profile, numeric contract, randomness contract, and extensions should define the minimum trace required for a claim.

The roadmap requires a minimal trace/failure/provenance foundation before the first executable QSOL reference machine. Later phases may enrich the trace, but executable research results must not begin life without source/IR/execution-contract binding.

## Principle

> A result without enough provenance to support its claim should not be promoted beyond the evidence actually recorded.
