# Candidate Semantic IR

This document describes the proposed intermediate representation between human-facing QSOL source and lower computational forms.

It is **non-normative until the core invariants are frozen**.

## Purpose

The Semantic IR should preserve information that ordinary compiler IRs often discard too early:

- research intent;
- epistemic class;
- units and types;
- explicit effects;
- effect-to-capability requirements;
- protected-machinery capability requirements without misclassifying machinery selection as an external effect;
- dependencies;
- source provenance;
- result-determinism requirements at the JOB, DECK, CARD, or other frozen scope that owns them;
- numeric-contract requirements at their governing scope;
- randomness/reproducibility requirements at their governing scope;
- extension-profile membership, version, and contract requirements;
- ordering constraints induced by effects and failure behavior.

The IR should be precise enough for machines while remaining inspectable by humans.

## Structural hierarchy

```text
Program
 └── Job[]
      └── Deck[]
           └── Card[]
```

The hierarchy itself carries stable identity. A conceptual shape is:

```text
Program {
    jobs[]
}

Job {
    id
    decks[]
    result_determinism?
    numeric_contract?
    randomness_contract?
    machinery_requirements[]
    failure_behavior?
    source_location?
}

Deck {
    id
    cards[]
    result_determinism?
    numeric_contract?
    randomness_contract?
    machinery_requirements[]
    failure_behavior?
    source_location?
}

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
    effect_requirements[]
    machinery_requirements[]
    result_determinism?
    numeric_contract?
    randomness_contract?
    extension_requirements[]
    dependencies[]
    sequencing_constraints[]
    failure_behavior?
    source_location
}

EffectRequirement {
    effect_id
    effect_kind
    required_capabilities[]
}

MachineryRequirement {
    machinery_requirement_id
    target_selector_or_class
    required_capabilities[]
}

ExtensionRequirement {
    profile_name
    required_version_or_range
    contract_id_or_hash?
}
```

`Job.id`, `Deck.id`, and `Card.id` are canonical identities, not serialization-only labels. They must survive canonicalization, lossless transport, lowering provenance, and trace production without being synthesized or renumbered merely because a representation changes.

`result_determinism?`, `numeric_contract?`, and `randomness_contract?` may be attached at JOB, DECK, CARD, or another scope only where the frozen semantic model permits that scope. A scope-level requirement must remain attached to the canonical object that owns it. It must not be flattened into an arbitrary CARD, lost during serialization, or reconstructed from execution output.

The normative model must freeze composition/inheritance rules before executable implementation. In particular, a child scope must not silently weaken a parent result-determinism, numeric, or randomness requirement merely because a backend prefers a weaker contract. Effective scope bindings and any permitted transitions remain provenance-visible.

`failure_behavior?` may exist at JOB, DECK, or CARD scope only where the frozen semantic model defines a policy at that scope. A higher-scope recovery, continuation, compensation, or other failure policy must be represented on the corresponding canonical `Job` or `Deck`; it must not be inferred from CARD fields or invented during serialization, lowering, or execution. In the absence of an explicit scoped policy, the frozen default failure semantics apply.

`effect_requirements[]` is the canonical association between a protected external effect and the complete capability set that must authorize that specific effect. A CARD may have zero, one, or multiple effect requirements. Separate unassociated `effects[]` and `capabilities[]` arrays are insufficient once one CARD can initiate multiple effects with different authorization requirements.

`machinery_requirements[]` is separate canonical state for permission to use a class of protected machinery. A machinery requirement has its own stable identity, names the target selector/class it governs, and binds the complete capability set required before that machinery is actually used. Machinery requirements may be attached to JOB, DECK, or CARD only where the frozen target-selection model permits that scope.

A derived CARD-level or execution-wide union of capabilities may be useful for preflight or summaries, but such a union does not replace either the per-effect mapping or the per-machinery requirement mapping.

`extension_requirements[]` is the canonical association between an extension profile and the version/contract required to interpret extension-owned syntax, qualifiers, effects, adapters, or lowering hooks. A serializer or lowering stage must not split profile names from their version/contract requirements and later reconstruct the association by position or guesswork.

These enforcement fields belong in the canonical semantic input. They must not be invented only after a backend has already begun execution on selected machinery.

A `NUMERIC` result-determinism request is incomplete without the numeric contract that defines the permitted tolerance, error metric, domain, precision rules, or other legal variation. The canonical model therefore needs to bind that contract at its governing scope before executable phases begin.

## Stable identity

Jobs, decks, and cards should be independently addressable.

A source-level card identifier such as:

```text
@019 RUN PROJECTILE
```

may allow:

- AI proposals against a stable semantic unit;
- dependency references;
- provenance edges;
- localized diagnostics;
- deterministic diffs.

Stable JOB and DECK identities similarly allow multi-job/multi-deck workflows, failure propagation, output provenance, and cross-deck dependencies to refer to the same semantic objects before and after serialization or lowering.

Whether identifiers are user-visible, generated, or both is not yet frozen. What is not optional for a lossless canonical model is that once an identity exists, representation changes must not silently replace or renumber it.

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

## Effects and capability bindings

Effects describe what an operation does. Capabilities describe what the execution environment must authorize before a protected effect begins or before protected machinery is used.

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

Each protected effect carries its own complete capability set through `effect_requirements[]`. For example, a remote AI operation might conceptually require:

```text
effect_id = ai_call_1
effect_kind = AI_MODEL
required_capabilities = [AI_MODEL, NETWORK]
```

while another effect on the same CARD may require a different set.

All capabilities in the set for a specific effect must be authorized before that effect begins. Lowering and tracing must preserve the effect-to-capability association rather than guessing from a CARD-level union.

## Protected machinery authorization

GPU selection is intentionally **not** a Semantic-IR effect. Choosing CPU, SIMD, GPU, CUDA, or another accelerator is machinery selection and belongs in MORPH/execution metadata.

Protected machinery access may nevertheless require runtime permission. That authorization uses `machinery_requirements[]`, not `effect_requirements[]`.

Conceptually:

```text
machinery_requirement_id = gpu_access_1
target_selector_or_class = GPU
required_capabilities = [GPU]
```

The actual machinery may need to be resolved before the applicable requirement is known. For example, `ON BEST` may select a GPU-backed scope. Selection and authorization are therefore distinct steps:

```text
resolve machinery scope
    ↓
resolve applicable machinery requirement(s)
    ↓
authorize every required machinery capability
    ↓
only then begin protected machinery use
```

A target may be selected for planning/provenance without being authorized for execution. If a required machinery capability is denied or cannot be established, protected use of that machinery must not begin.

A policy must not silently fall back from a denied GPU target to another target unless a frozen pre-execution fallback/selection rule explicitly permits that transition and records it. Likewise, selecting GPU machinery must not create a synthetic external effect merely to obtain a capability-check hook.

Machinery authorization and effect authorization may both apply to one CARD. For example, a GPU computation may require `GPU` machinery permission while a separate network effect on that CARD requires `NETWORK`. These are different semantic boundaries and must remain separately traceable.

## Capabilities

Example:

```text
DENY NETWORK
```

should allow validation to reject any reachable protected effect whose `required_capabilities[]` includes `NETWORK`.

Likewise, if a selected machinery scope requires `GPU` and policy denies that capability, the protected GPU execution must not begin.

Extension availability is separate. A deck may `USE QX-NET` because it needs that profile while still denying the `NETWORK` capability at execution time. A deck may understand QX-GPU/QX-CUDA while policy still denies protected accelerator access.

Capability authorization for a protected external effect must succeed before that effect begins. Capability authorization for protected machinery must succeed before that machinery is used. The canonical model therefore preserves per-effect and per-machinery requirement sets independently from later environment grant/deny decisions.

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
- effectful operations must expose the completion state of every identified effect attempt;
- an effect attempt that begins but is proven to have produced no externally observable change must be distinguishable from both `NOT_STARTED` and `PARTIAL`;
- an unhandled DECK failure propagates to the enclosing JOB by default unless an explicit frozen JOB-level handler says otherwise;
- explicit JOB/DECK/CARD failure policies must remain attached to the canonical scope that owns them;
- later backends must not choose incompatible trap/continue/rollback behavior for the same semantic program.

Explicit recovery syntax, if introduced later, belongs in the semantic model rather than being an implicit backend policy.

## Canonical form

The semantic model should support a deterministic canonical representation.

Canonicalization may include:

- stable field order;
- stable JOB / DECK / CARD identities;
- normalized numeric forms;
- normalized unit identifiers;
- normalized keyword case;
- deterministic ordering for unordered metadata;
- deterministic ordering of `required_capabilities[]` within each effect or machinery requirement;
- explicit schema/specification version;
- deterministic escaping and encoding;
- deterministic derivation of effect-order and failure-order constraints;
- canonical identity for scoped determinism/numeric/randomness contracts;
- canonical machinery-requirement identities;
- canonical structured extension requirements.

This enables stable hashing and reproducible comparison.

## Hashing

A canonical card, deck, or job may be hashable independently.

Potential uses:

- provenance;
- frozen research artifacts;
- cache keys;
- transformation verification;
- backend comparison.

Hash identity must be defined over canonical semantic content rather than incidental formatting if source formatting is not itself part of the semantic contract. Stable hierarchy IDs, execution-relevant qualifiers, effect requirements, machinery requirements, scoped result-determinism/numeric/randomness contracts, per-requirement capability sets, scoped failure behavior, and extension requirements contribute to semantic identity according to the frozen canonicalization rules.

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
