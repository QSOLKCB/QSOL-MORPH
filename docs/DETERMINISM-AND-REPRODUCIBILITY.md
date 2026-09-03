# Determinism and Reproducibility

QSOL-MORPH is intended for research computing, where performance is useful but reproducibility is part of the scientific contract.

This document describes the candidate determinism model. It is non-normative until the invariant freeze.

## Determinism classes

A future specification may distinguish several execution classes rather than treating determinism as a single boolean.

Candidate classes:

```text
STRICT
NUMERIC
SEEDED
DECLARED-NONDETERMINISTIC
```

### STRICT

The same canonical program, declared inputs, implementation version, and required execution contract produce the same observable result bytes.

### NUMERIC

Results may differ at the bit level across legal implementations but remain within an explicitly declared numeric contract.

### SEEDED

Pseudorandom behavior is deterministic with respect to a recorded algorithm, seed, stream identity, and relevant execution contract.

### DECLARED-NONDETERMINISTIC

The program intentionally permits nondeterministic behavior. The source and trace must expose that fact.

The exact names and semantics of these classes are not frozen.

## Sources of nondeterminism

Potential sources include:

- random number generators;
- system entropy;
- wall-clock time;
- process scheduling;
- thread scheduling;
- unordered reductions;
- atomic update order;
- filesystem iteration order;
- network responses;
- external services;
- AI model sampling;
- GPU kernels and libraries;
- hardware-specific floating-point behavior;
- compiler optimization decisions.

QSOL-MORPH should treat these as explicit concerns rather than incidental runtime trivia.

## Randomness

Randomness should declare its source.

Illustrative seeded form:

```text
SEED RNG 18437
RUN MONTE_CARLO
```

A reproducible trace may need to record:

```text
rng_algorithm
rng_version
seed
stream_id
parallel_partitioning
```

Using the same integer seed is insufficient if the generator or parallel stream mapping changes.

## Time

Wall-clock time is an external input.

A deterministic computation should not silently read it.

Possible explicit forms may distinguish:

```text
CLOCK MONOTONIC
CLOCK WALL
```

or a capability/effect declaration.

## Floating point

Floating-point reproducibility is especially sensitive to:

- fused multiply-add;
- reassociation;
- reduction tree shape;
- denormal handling;
- precision contraction/expansion;
- transcendental library implementation;
- target-specific instructions.

QSOL-MORPH must not label a transformation semantically identical under a strict numeric contract merely because the real-number algebra looks equivalent.

The active numeric contract determines which transformations are legal.

## Parallelism

Parallel execution is not inherently nondeterministic, but it often exposes order-sensitive behavior.

A deterministic parallel backend may require:

- race-free dataflow;
- deterministic partitioning;
- deterministic reduction algorithms;
- controlled atomics;
- stable synchronization semantics.

When those requirements cannot be met, the backend should reject a strict contract or explicitly record a weaker one.

## Backend selection

Automatic backend selection must be traceable.

If a source requests:

```text
RUN MODEL ON BEST
```

then the trace should identify what `BEST` resolved to and under which selection policy.

For a frozen experiment, a later replay may choose to require the recorded backend rather than re-run target selection.

## Reproducibility manifest

A future run manifest may include:

```text
spec_version
source_hash
semantic_ir_hash
morph_version
backend
backend_version
target_architecture
device
numeric_contract
determinism_class
rng_algorithm
seed
inputs[]
outputs[]
extensions[]
capabilities[]
optimization_profile
kernel_or_binary_hashes[]
```

Not every field is required for every execution.

## Reproducibility versus portability

Portable source does not imply bit-identical execution across every target.

QSOL-MORPH should state the strongest reproducibility guarantee actually provided by a given source/backend/numeric-contract combination.

## Failure behavior

A backend should fail closed when a required determinism contract cannot be satisfied.

Silently downgrading:

```text
STRICT -> DECLARED-NONDETERMINISTIC
```

would make the trace accurate only after violating the user's declared execution requirement.

A downgrade is acceptable only when the source or execution policy explicitly permits it.

## Design principle

> Nondeterminism is an input to the scientific method, not an invisible implementation detail.
