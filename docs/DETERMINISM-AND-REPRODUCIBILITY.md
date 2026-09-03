# Determinism and Reproducibility

QSOL-MORPH is intended for research computing, where performance is useful but reproducibility is part of the scientific contract.

This document describes the candidate determinism model. It is non-normative until the invariant freeze.

## Composable reproducibility contract

Determinism should not be represented as a single enum that mixes result guarantees with randomness configuration.

A future execution contract should instead compose at least two orthogonal facets:

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

Additional facets may be added if the specification needs to represent scheduling, external-service replay, or other independent sources of nondeterminism.

### STRICT result determinism

The same canonical program, declared inputs, implementation version, and required execution contract produce the same observable result bytes.

### NUMERIC result determinism

Results may differ at the bit level across legal implementations but remain within an explicitly declared numeric contract.

### DECLARED-NONDETERMINISTIC result behavior

The program intentionally permits nondeterministic observable results. The source and trace must expose that fact.

### SEEDED randomness

Pseudorandom behavior is reproducible with respect to a recorded algorithm, seed, stream identity, partitioning, and relevant execution contract.

`SEEDED` is not a weaker or stronger result-determinism class. A computation may, for example, be both:

```text
result_determinism = STRICT
randomness = SEEDED
```

or:

```text
result_determinism = NUMERIC
randomness = SEEDED
```

Likewise, a computation with deterministic seeded RNG may still permit nondeterministic scheduling if the result contract explicitly allows it.

The exact names and complete facet set are not frozen.

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
rng_mode
rng_algorithm
rng_version
seed
stream_id
parallel_partitioning
```

Using the same integer seed is insufficient if the generator or parallel stream mapping changes.

A seeded RNG declaration establishes the randomness facet. It does not by itself establish the result-determinism facet.

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

When those requirements cannot be met, the backend must reject the requested result-determinism contract unless the source or execution policy explicitly permits a weaker result contract. Merely reporting a downgrade after execution is not sufficient permission.

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
result_determinism
randomness_mode
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

The manifest should represent independent reproducibility facets independently rather than collapsing them into one ambiguous label.

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

A downgrade is acceptable only when the source or execution policy explicitly permits it before execution.

The same rule applies independently to randomness and other reproducibility facets: an implementation may not substitute external entropy for a required seeded stream merely because it records that substitution afterward.

## Design principle

> Nondeterminism is an input to the scientific method, not an invisible implementation detail.
