# Vector and Dataflow Model

QSOL-MORPH treats vector computation as a first-class architectural concept rather than a backend afterthought.

The goal is to express bulk scientific computation once, then map it onto scalar CPUs, SIMD units, GPUs, or future accelerators without forcing source code to encode one machine's physical width.

Because this IR is part of the mandatory end-to-end backend pipeline, it is **not a vector-only filter**. It must also preserve the complete supported QSOL-CORE semantic surface for operations that are not vectorizable.

The roadmap freezes a normative Vector/Dataflow IR specification before implementing the reference QSOL-CORE → Vector/Dataflow lowering. The reference lowering implements that contract; it does not define it.

## Role in the mandatory pipeline

The documented pipeline is singular:

```text
Canonical Semantic IR
    ↓
Semantic-to-QSOL-CORE Lowering
    ↓
QSOL-CORE
    ↓
Core-to-Vector/Dataflow Lowering
    ↓
Vector/Dataflow IR
    ↓
MORPH
    ↓
backend
```

Therefore every supported QSOL-CORE operation must have a semantics-preserving representation through the Vector/Dataflow IR stage.

The IR may represent vectorizable computation as dataflow graphs while carrying non-vector operations as defined scalar, control, call, effect, sequencing, or pass-through nodes/regions.

It must preserve, where applicable:

- scalar and vector data operations;
- result/data identities consumed by dependency edges;
- branches and control-flow regions;
- call/return boundaries and call state;
- explicit effects and their stable declared identities;
- complete required-capability sets for each protected effect;
- execution-relevant qualifiers not already consumed under a frozen lowering rule;
- explicit failure behavior not already lowered into core control semantics;
- source/effect/failure ordering constraints;
- result-determinism, scoped numeric, and randomness contracts;
- extension/profile identity required by execution;
- failure and totality classification;
- provenance links to QSOL-CORE and originating semantic CARDs;
- identities needed for runtime per-effect-attempt tracing, distinct from declared effect identities.

A backend must not bypass this IR merely because a QSOL-CORE operation is not vectorizable. If the IR cannot represent a supported core operation without semantic loss, that is an IR design/conformance failure rather than permission to invent a second backend path.

## Result and data identity

Dependency graphs require stable producer/consumer identity, not only raw values.

A source result binding may be renamed during lower representation, but the mapping must remain deterministic and provenance-bearing. The IR must preserve enough identity to establish:

```text
source result binding
    ↓
QSOL-CORE data identity
    ↓
Vector/Dataflow value/node identity
    ↓
dependent consumers
```

A lowering must not infer dependencies from incidental node order or numeric equality after discarding result identity.

## Abstract vectors

A QSOL vector is semantic data, not a promise about one hardware register.

Illustrative source:

```text
VECTOR A f32[1_000_000]
VECTOR B f32[1_000_000]
DERIVE C = A * B + 4.0
```

Candidate lower form:

```text
VLOAD A      -> V0
VLOAD B      -> V1
VMUL V0 V1   -> V2
VADD V2 4.0  -> V3
VSTORE V3    -> C
```

A backend may realize the same operations as:

- scalar loops;
- CPU SIMD;
- AVX-family instructions;
- LLVM vectors;
- CUDA threads/warps;
- other accelerator execution models.

## Vector width

Source programs should not encode physical vector width unless they explicitly request a target-specific extension.

The abstract execution model may process a semantic vector in target-natural chunks while preserving observable semantics.

## Dataflow graph

Dependencies are represented as a graph whenever useful.

For:

```text
DERIVE X = A * B
DERIVE Y = X + C
DERIVE Z = SQRT Y
```

the graph is conceptually:

```text
A ─┐
   MUL ── ADD ── SQRT ── Z
B ─┘      ↑
          C
```

This representation makes transformation opportunities explicit.

Source order remains semantically relevant for observable effects and for potentially failing operations under fail-stop execution. Only operations proven **pure and total** under the active contract may be freely scheduled from data dependencies.

A Vector/Dataflow lowering must preserve all result/dependency identity, control, call, effect-order, failure-order, capability, qualifier, failure-behavior, and contract constraints carried by QSOL-CORE and its preserved semantic metadata.

## Control flow and calls

Control operations must survive this mandatory IR stage without being flattened into ambiguous data dependencies.

A future frozen representation may use basic blocks, regions, explicit control edges, continuations, or another small model, but it must preserve the QSOL-CORE meaning of:

```text
BRANCH
JUMP
CALL
RETURN
STOP
```

and any frozen call/stack state semantics.

Vectorization may occur inside control regions when legal. It must not erase or speculate across a control boundary in a way that changes failure, effect, or result behavior.

## Effects and capabilities

Explicit effects remain explicit through this IR.

Conceptually, effect nodes/regions must retain enough information to preserve:

```text
declared_effect_id
effect_kind
required_capabilities[]
source/failure order
runtime effect-attempt provenance hook
```

`declared_effect_id` is the canonical semantic effect identity that survives lowering. A later `effect_attempt_id` identifies a concrete runtime attempt. The two identities must remain distinguishable so retries, duplicate attempts, or same-kind effects from one CARD can be audited.

A file write, process launch, network action, clock access, AI call, or other effect must not disappear merely because the surrounding numeric work becomes a vector graph.

Capability authorization remains an execution boundary. Every capability in the complete required set for an effect must be granted before the corresponding protected effect begins.

## Chaining and fusion

A backend may fuse a legal chain:

```text
X = A * B
Y = X + C
Z = sqrt(Y)
```

into an implementation equivalent to:

```text
Z[i] = sqrt(A[i] * B[i] + C[i])
```

provided the active scoped numeric, failure, ordering, and semantic contracts permit the transformation.

Fusion must not be justified solely by performance. It must be semantically legal.

Fusion may not swallow an effect, control boundary, result/dependency identity, or potentially failing operation in a way that changes observable ordering or failure behavior.

## Masks

Masks allow data-parallel conditional execution without requiring source-level scalar branching for every element.

Illustrative form:

```text
MASK ACTIVE WHERE ENERGY > 0
ADD ENERGY DELTA WHERE ACTIVE
```

A target may lower masks into vector predicates, branchless scalar operations, GPU predicates, or another equivalent representation.

A data-parallel mask is not automatically equivalent to arbitrary QSOL-CORE control flow; lowering must preserve the distinction where observable semantics differ.

## Reductions

Candidate reductions include:

```text
SUM
PRODUCT
MIN
MAX
ALL
ANY
```

Floating-point reductions require special care because reassociation can alter results. The scoped numeric contract governing the reduction must define when alternate reduction trees are legal.

## XOR and vector logic

XOR is expected to be available both for scalar logical/integer domains and vectorized matching domains.

Examples:

```text
XOR FLAGS MASK
VXOR V0 V1 -> V2
```

Type coercion should not make XOR ambiguous. Boolean XOR and bitwise integer XOR are related operations over explicitly typed domains.

## Aliasing

Optimization legality depends on whether two names may refer to overlapping storage.

The vector/dataflow model should make aliasing rules explicit rather than forcing every optimization pass to guess.

Potential strategies include:

- immutable-by-default values;
- explicit mutable buffers;
- declared views/slices;
- conservative alias analysis when uncertainty remains.

The final model is not frozen.

## Memory locality

QSOL-MORPH should minimize unnecessary movement.

A backend may keep intermediate values resident:

- in registers;
- in caches;
- in GPU device memory;
- in shared/local accelerator memory;

provided residency choices do not violate observable source semantics.

For accelerator execution, avoiding repeated host/device transfers is a primary optimization opportunity.

## Abstract memory classes

A future GPU/accelerator profile may expose concepts such as:

```text
AUTO
HOST
DEVICE
SHARED
LOCAL
CONSTANT
```

Normal research source should prefer `AUTO` or omit placement where automatic placement is sufficient.

Explicit placement is an expert control and should remain visible in the trace when material.

## Failure and totality

The IR must retain whether an operation is:

```text
pure + total
pure + potentially failing
effectful
```

or the frozen equivalent classification.

An unused result does not make a potentially failing operation unobservable under fail-stop execution. An optimizer operating on this IR must not delete such an operation unless it preserves the original failure at the same observable point.

Only operations proven pure and total may be removed solely because their results are dead.

Per-effect completion semantics must also remain representable, including a cleanly aborted begun effect that is proven to have produced no external change and the precedence rule under which known completion is `COMPLETED` rather than `UNKNOWN`.

## Scoped numeric contracts

The IR must preserve which numeric contract governs which CARD-derived operation, region, reduction, or kernel candidate.

A lower representation may group operations under a common contract only when that grouping is semantically valid. If separate source contracts remain distinct, the IR must carry enough scope identity to later produce provenance entries such as:

```text
scope_kind
scope_id
source_card_ids[]
numeric_contract_id
numeric_contract_hash
material_numeric_mode
backend_unit_id?
```

The material numeric mode may be selected only within the legal choices of that scope's contract. Different kernels may therefore legitimately have different modes, and provenance must not collapse them into one false execution-wide pair.

## Determinism

Parallel execution can create nondeterminism through:

- race conditions;
- unordered reductions;
- atomic update order;
- backend library choices;
- varying launch/scheduling behavior.

The IR must carry enough information for QSOL-MORPH to determine whether a requested result-determinism contract can be satisfied while independently preserving any randomness/reproducibility contract and all scoped numeric contracts.

If the requested result-determinism contract cannot be satisfied, the backend must fail closed unless the source or execution policy explicitly permitted the weaker result contract before execution. Reporting a weaker class in the trace is required when such a permitted downgrade occurs, but reporting alone is not authorization to downgrade.

Likewise, a backend must not replace a required seeded random stream with an unseeded or external-entropy source merely because it can report that change afterward.

## Lowering provenance

The QSOL-CORE → Vector/Dataflow transition is independently provenance-bearing.

A conforming trace should bind, where material:

```text
core_ir_hash
vector_dataflow_spec_version
vector_dataflow_implementation_version
vector_dataflow_ir_hash
result_binding_map[]
vector_dataflow_lowering_diagnostics[]
```

MORPH must receive a specific identifiable Vector/Dataflow IR. It must not be possible for a changed lower graph to hide behind the same Semantic IR/Core IR/MORPH identities.

## Conformance requirement

Vector/Dataflow specification and reference-lowering conformance should include fixtures covering more than arithmetic.

Representative tests should include:

- scalar-only QSOL-CORE programs;
- producer/consumer result-binding preservation;
- branches and calls;
- multiple same-kind declared effects with distinct `declared_effect_id` values;
- effectful operations with single and multiple capability requirements;
- execution-relevant qualifiers and explicit failure behavior;
- failing pure operations ordered around effects;
- mixed scalar/vector regions;
- multiple scoped numeric contracts and modes;
- determinism/randomness contract preservation;
- declared-effect/runtime-attempt provenance identity and completion states;
- unsupported constructs failing closed rather than bypassing the IR.

## Performance principle

> Move data as little as possible. Preserve the whole program. Expose vectorizable structure. Let MORPH choose the physical execution strategy.

The architecture is inspired by vector and chaining traditions, but it is target-independent by design.
