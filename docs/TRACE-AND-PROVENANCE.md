# Trace and Provenance

QSOL-MORPH treats provenance as part of execution semantics for research workflows.

The goal is not merely to say that a program ran. The goal is to make it possible to answer:

- what source was executed;
- what semantic representation was produced;
- what backend was selected;
- what transformations were applied;
- what inputs and capabilities were used;
- what outputs were produced;
- what level of determinism was promised and observed.

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
numeric contract
```

### Execution trace

Potential fields:

```text
target architecture
device
runtime/compiler versions
seed and RNG identity
capabilities used
external tool versions
start/stop metadata where permitted
```

### Result trace

Potential fields:

```text
output hashes
validation status
error/tolerance contract
result semantic class
artifact locations
```

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

The result can retain edges back to the observations, parameters, derivation, and validation cards that produced it.

## External evidence

External evidence must remain explicit.

If a TEST compares against a file, external instrument, network service, benchmark, or formal tool, the trace should identify the relevant evidence boundary rather than treating the external result as native QSOL truth.

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

Not every execution needs every field. The active specification, determinism profile, and extensions should define the minimum trace required for a claim.

## Principle

> A result without enough provenance to support its claim should not be promoted beyond the evidence actually recorded.
