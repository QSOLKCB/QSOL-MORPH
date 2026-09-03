# Vector and Dataflow Model

QSOL-MORPH treats vector computation as a first-class architectural concept rather than a backend afterthought.

The goal is to express bulk scientific computation once, then map it onto scalar CPUs, SIMD units, GPUs, or future accelerators without forcing source code to encode one machine's physical width.

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

Source order remains semantically relevant for observable effects even when pure vector operations are scheduled from data dependencies. A vector/dataflow lowering must preserve effect-order constraints carried by the Semantic IR.

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

provided the active numeric and semantic contract permits the transformation.

Fusion must not be justified solely by performance. It must be semantically legal.

## Masks

Masks allow data-parallel conditional execution without requiring source-level scalar branching for every element.

Illustrative form:

```text
MASK ACTIVE WHERE ENERGY > 0
ADD ENERGY DELTA WHERE ACTIVE
```

A target may lower masks into vector predicates, branchless scalar operations, GPU predicates, or another equivalent representation.

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

Floating-point reductions require special care because reassociation can alter results. A deterministic/numeric profile must define when alternate reduction trees are legal.

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

## Determinism

Parallel execution can create nondeterminism through:

- race conditions;
- unordered reductions;
- atomic update order;
- backend library choices;
- varying launch/scheduling behavior.

The dataflow IR must carry enough information for QSOL-MORPH to determine whether a requested result-determinism contract can be satisfied while independently preserving any randomness/reproducibility contract.

If the requested result-determinism contract cannot be satisfied, the backend must fail closed unless the source or execution policy explicitly permitted the weaker result contract before execution. Reporting a weaker class in the trace is required when such a permitted downgrade occurs, but reporting alone is not authorization to downgrade.

Likewise, a backend must not replace a required seeded random stream with an unseeded or external-entropy source merely because it can report that change afterward.

## Performance principle

> Move data as little as possible. Express parallelism semantically. Let MORPH choose the physical execution strategy.

The architecture is inspired by vector and chaining traditions, but it is target-independent by design.
