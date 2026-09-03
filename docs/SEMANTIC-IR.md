# Candidate Semantic IR

This document describes the proposed intermediate representation between human-facing QSOL source and lower computational forms.

It is **non-normative until the core invariants are frozen**.

## Purpose

The Semantic IR should preserve information that ordinary compiler IRs often discard too early:

- research intent;
- epistemic class;
- units and types;
- explicit effects;
- capability requirements;
- dependencies;
- source provenance;
- result-determinism requirements;
- numeric-contract requirements;
- randomness/reproducibility requirements;
- extension-profile membership and version requirements;
- ordering constraints induced by effects and failure behavior.

The IR should be precise enough for machines while remaining inspectable by humans.

## Structural hierarchy

```text
Program
 └── Job[]
      └── Deck[]
           └── Card[]
```

A minimal conceptual `Card` shape is:

```text
Card {
    id
    verb
    noun
    operands[]
    result?
    value?
    type?
    unit?
    qualifiers{}
    semantic_class?
    effects[]
    capabilities[]
    result_determinism?
    numeric_contract?
    randomness_contract?
    extensions[]
    dependencies[]
    sequencing_constraints[]
    failure_behavior?
    source_location
}
```

These enforcement fields belong in the canonical semantic input. They must not be invented only after a backend has already chosen machinery.

A `NUMERIC` result-determinism request is incomplete without the numeric contract that defines the permitted tolerance, error metric, domain, precision rules, or other legal variation. The canonical model therefore needs to bind that contract before executable phases begin.

## Stable identity

Cards should be independently addressable.

A source-level identifier such as:

```text
@019 RUN PROJECTILE
```

may allow:

- AI proposals against a stable semantic unit;
- dependency references;
- provenance edges;
- localized diagnostics;
- deterministic diffs.

Whether identifiers are user-visible, generated, or both is not yet frozen.

## Typed values and units

Types and units should remain explicit in the semantic model.

Example:

```text
OBSERVE TEMPERATURE 294.3 K
```

may become conceptually:

```text
verb            OBSERVE
noun            TEMPERATURE
value           294.3
type            f64
unit            kelvin
semantic_class  OBSERVATION
```

The IR should not erase the unit merely because the selected backend ultimately receives a floating-point number.

## Epistemic metadata

Research-class information should survive lowering far enough to enforce non-promotion rules.

Example:

```text
DERIVE ENERGY = MASS * C * C
```

might carry:

```text
semantic_class = DERIVATION
```

while:

```text
PROVE CONSERVATION WITH LEAN
```

may carry a proof-class boundary and an explicit external verification dependency.

## Effects

Effects should be statically discoverable whenever practical.

Candidate effect classes include:

```text
READ_FILE
WRITE_FILE
NETWORK
PROCESS
CLOCK
RANDOM
AI_MODEL
EXTERNAL_TOOL
MUTATION
```

A card may be pure or effectful. A backend may not silently add an undeclared externally observable effect when the source contract forbids it.

GPU selection is intentionally not a Semantic-IR effect. Choosing CPU, SIMD, GPU, CUDA, or another accelerator is machinery selection and belongs in MORPH/execution metadata. GPU access may still require an explicit extension/capability contract.

## Capabilities

Effects describe what an operation does. Capabilities describe what the execution environment permits it to do.

Example:

```text
DENY NETWORK
```

should allow validation to reject any reachable card requiring network access.

Extension availability is separate. A deck may `USE QX-NET` because it needs that profile while still denying the `NETWORK` capability at execution time.

Capability authorization for a protected external effect must succeed before that effect begins. The canonical model must therefore preserve the required capability independently from later environment grant/deny decisions.

## Dependencies and sequencing

Dependencies should be explicit enough to support dataflow analysis and reproducibility.

Conceptually:

```text
@020 DERIVE ENERGY = MASS * C * C
```

may depend on the cards that established `MASS` and `C`.

A dependency graph can support:

- scheduling;
- fusion analysis;
- invalidation;
- trace explanations;
- provenance traversal;
- AI review.

Data dependencies are not the only ordering constraints.

Under fail-stop semantics, source order can be observable through both **effects** and **failure**. A pure CARD that may fail can determine whether an earlier or later external effect occurs. Therefore the candidate canonical model must derive or preserve sequencing constraints sufficient to keep this distinction.

Example:

```text
@010 WRITE A
@011 DIV X 0
@012 WRITE B
```

The source-order meaning is:

1. `WRITE A` may complete;
2. `DIV X 0` fails;
3. `WRITE B` does not start.

A backend must not move `@011` before `@010` merely because the division is pure and data-independent.

The default rule is therefore:

- effectful CARDs preserve source order where observable;
- potentially failing CARDs preserve source order relative to observable effects and other failure-observable boundaries where reordering could change the outcome;
- only CARDs proven **pure and total** under the active contract may be freely scheduled by dependency edges alone;
- a future explicit parallel/commutative/recovery construct may relax these constraints only if frozen semantics define its legality and observability.

## Failure boundary

Execution failure is part of semantics, not an implementation accident.

The Semantic IR need not encode operating-system-specific error numbers in the core schema, but it must preserve enough information for lower layers to apply one frozen failure model. In particular:

- failed evaluation must not manufacture an ordinary result value;
- pure operations must not leave committed semantic state after failure;
- potentially failing pure operations remain ordering-relevant under fail-stop execution;
- effectful operations must expose whether an effect was not started, completed, partial, or of unknown completion state;
- an unhandled DECK failure propagates to the enclosing JOB by default unless an explicit frozen JOB-level handler says otherwise;
- later backends must not choose incompatible trap/continue/rollback behavior for the same semantic program.

Explicit recovery syntax, if introduced later, belongs in the semantic model rather than being an implicit backend policy.

## Canonical form

The semantic model should support a deterministic canonical representation.

Canonicalization may include:

- stable field order;
- normalized numeric forms;
- normalized unit identifiers;
- normalized keyword case;
- deterministic ordering for unordered metadata;
- explicit schema/specification version;
- deterministic escaping and encoding;
- deterministic derivation of effect-order and failure-order constraints;
- canonical identity for numeric/reproducibility contracts;
- canonical extension/version requirements.

This enables stable hashing and reproducible comparison.

## Hashing

A canonical card, deck, or job may be hashable independently.

Potential uses:

- provenance;
- frozen research artifacts;
- cache keys;
- transformation verification;
- backend comparison.

Hash identity must be defined over canonical semantic content rather than incidental formatting if source formatting is not itself part of the semantic contract.

## Lowering

Semantic lowering should be staged.

Illustratively:

```text
Semantic Card
    ↓
Typed semantic operation
    ↓
QSOL-CORE operation(s)
    ↓
Vector/Dataflow IR
    ↓
Backend IR
```

Not every semantic card must lower directly into one core instruction. Some cards are metadata, orchestration, validation, provenance, authorization, or failure boundaries.

## Example

Source-like form:

```text
@011 OBSERVE MASS 4.2 kg
@012 SET C 299792458 m/s
@013 DERIVE ENERGY = MASS * C * C
@014 TRACE ENERGY
```

Conceptual semantic structure:

```text
@011:
  verb: OBSERVE
  noun: MASS
  semantic_class: OBSERVATION
  value: 4.2
  unit: kg

@012:
  verb: SET
  noun: C
  semantic_class: PARAMETER
  value: 299792458
  unit: m/s

@013:
  verb: DERIVE
  noun: ENERGY
  semantic_class: DERIVATION
  depends_on: [@011, @012]

@014:
  verb: TRACE
  noun: ENERGY
  depends_on: [@013]
```

A lower backend may manipulate raw numeric values, but the trace system should still be able to relate those values to the semantic cards and contracts that produced them.

## What the IR must not become

The Semantic IR should not become:

- a vendor GPU ISA;
- an LLVM clone;
- a serialized Python AST;
- an untyped bag of strings;
- a place where every backend deposits private fields into the core schema.

Target-specific metadata belongs behind explicit extension boundaries.
