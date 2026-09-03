# Optimization and CI Evidence Model

QSOL-MORPH treats optimization as a semantics-preserving activity, not a synonym for speed.

This document adapts optimization principles already formalized in QSOL's OPT work for use in the future QSOL-MORPH compiler and CI architecture.

## Primary rule

> A faster semantics-breaking change is not an optimization.

Speed is subordinate to correctness, determinism requirements, validation boundaries, provenance, and public semantic contracts.

## Admissible optimization

A candidate optimization is admissible only when the required contract is preserved.

Candidate preserved dimensions include:

```text
semantics
named invariants
determinism class
validation behavior
provenance/evidence boundaries
public API / serialized contract
resource assumptions
```

A backend-specific optimization may add an implementation strategy. It may not silently alter one of these dimensions.

## Reference equivalence

Where practical, optimized implementations should be checked against a reference implementation.

For early QSOL-MORPH this makes the conservative C backend especially valuable:

```text
semantic program
   ├── reference C path
   └── optimized backend path
```

The optimized path should demonstrate the equivalence required by the active semantic/numeric contract.

## Deterministic parallelism

Parallel execution is acceptable when the required result contract is preserved.

A useful CI pattern is:

```text
scalar/reference result
        ==
deterministic parallel result
```

when exact equivalence is required and a suitable witness/test exists.

For tolerance-bounded numeric profiles, the comparison must use the declared numeric contract rather than silently substituting byte equality or vague closeness.

## Approximation boundary

Approximation is not ordinary optimization when it changes results beyond exact semantics.

An approximation requires an explicit contract containing enough information to judge it, potentially including:

```text
reference
error metric
tolerance/domain
validation dataset
failure policy
```

Without an error contract, CI should not promote an approximation as a semantics-preserving optimization.

## Cache boundary

Verified cache reuse does not prove cold reconstruction.

CI should distinguish:

- cache hit correctness;
- cache key correctness;
- cold build/reconstruction correctness.

A pipeline that always reuses a valid cache may still hide a broken clean-build path.

Periodic or gated cold-path validation should exist for claims that depend on reconstructability.

## Combined resource model

Two independently valid optimizations may be invalid when composed if their combined resource demands conflict.

Examples:

- GPU shared-memory pressure;
- register pressure;
- RAM limits;
- disk/cache capacity;
- CI timeout budgets;
- concurrency limits.

Composition checks should consider the combined resource model rather than assuming local validity composes automatically.

## Benchmark evidence

Historical timings are observations, not portable performance targets.

A CI or documentation claim that an optimization is faster on a target environment should bind:

```text
target context
measurement
correctness validation
provenance
workload identity
```

No evidence label by itself turns an old benchmark number into a transferable target claim.

## CI optimization strategy

The future QSOL-MORPH CI should optimize cost without weakening evidence.

Candidate techniques:

### Path-scoped checks

Run expensive suites only when their governed surface changes, while retaining at least one integration path capable of detecting cross-boundary breakage.

### Content-addressed caches

Cache toolchains, generated IR, test fixtures, and build products using keys tied to the real semantic inputs.

### Reference/optimized split

Keep a small trusted reference lane and compare faster/parallel lanes against it.

### Deterministic sharding

Partition test vectors deterministically so failures are reproducible and shard assignment is inspectable.

### Frozen fixtures

Use hash-bound semantic fixtures for compatibility and regression testing.

### Exact-head validation

When a PR is being reviewed, final evidence should correspond to the current PR head rather than an obsolete commit.

### Pinned toolchains

Critical compiler/formalization lanes should pin toolchain identity and verify downloaded artifacts where practical.

### Explicit trust boundaries

CI should state which claims come from:

- source/static analysis;
- generated artifacts;
- execution tests;
- external toolchains;
- formal proofs;
- repository history/provenance.

No one layer should claim to prove another layer's external facts.

## Lean/formalization CI

If QSOL-MORPH later formalizes frozen contracts, the formal CI should borrow the strongest applicable patterns from OPT:

- dependency-minimal formal packages where practical;
- pinned compiler/toolchain versions;
- source placeholder rejection;
- audit-root completeness checks;
- declaration-level axiom audits;
- frozen release/artifact binding outside the proof language;
- explicit separation between what Lean proves and what Git/CI establishes.

Formal proof does not prove benchmark timing, external measurement authenticity, or Git immutability merely because those values are mentioned in a theorem context.

## Fail closed

If CI cannot establish the evidence required by a release claim, the claim should fail rather than be silently weakened.

## Principle

> Optimize the pipeline, not the evidence away.
