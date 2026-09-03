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
- determinism requirements;
- randomness/reproducibility requirements;
- extension-profile membership.

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
    randomness_contract?
    dependencies[]
    source_location
}
```

These enforcement fields belong in the canonical semantic input. They must not be invented only after a backend has already chosen machinery.

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

## Dependencies and effect ordering

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

Source order and dependency order are not interchangeable for effects. The candidate model treats effectful CARDs in a DECK as source-ordered by default: canonicalization should derive sequencing constraints between effectful cards so backends cannot reorder two writes, process launches, network calls, or other observable effects merely because no data edge exists between them.

Independent pure cards may be scheduled according to dependencies. A future explicit parallel/commutative-effects construct may relax effect ordering only if the frozen specification defines its legality and observability rules.

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
- deterministic derivation of effect-order constraints.

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

Not every semantic card must lower directly into one core instruction. Some cards are metadata, orchestration, validation, or provenance boundaries.

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

A lower backend may manipulate raw numeric values, but the trace system should still be able to relate those values to the semantic cards that produced them.

## What the IR must not become

The Semantic IR should not become:

- a vendor GPU ISA;
- an LLVM clone;
- a serialized Python AST;
- an untyped bag of strings;
- a place where every backend deposits private fields into the core schema.

Target-specific metadata belongs behind explicit extension boundaries.
