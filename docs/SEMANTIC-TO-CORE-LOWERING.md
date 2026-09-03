# Semantic-to-QSOL-CORE Lowering

QSOL-MORPH requires an explicit boundary between the research-facing Semantic IR and QSOL-CORE.

This document describes the candidate architecture for that boundary. It is **non-normative until the relevant specification phase is frozen**.

## Why this boundary exists

QSOL source carries information that a conventional machine-oriented IR often does not:

- research intent;
- epistemic class;
- values, types, and units;
- effects and required capabilities;
- result-determinism requirements;
- numeric contracts;
- randomness contracts;
- extension requirements;
- source, data, effect, and failure ordering;
- JOB / DECK / CARD identity and provenance.

QSOL-CORE provides a deliberately smaller operational machine.

The mapping between those layers is therefore part of QSOL semantics. It must not be invented opportunistically by a C, LLVM, CUDA, or other backend.

## Pipeline position

The intended pipeline is:

```text
QSOL source
    ↓
Canonical Semantic IR
    ↓
Semantic-to-Core Lowering
    ↓
QSOL-CORE
    ↓
Vector/Dataflow IR
    ↓
MORPH
    ↓
backend
```

Each arrow is an explicit contract boundary.

## Lowering result

A semantic CARD does not necessarily map one-to-one onto one QSOL-CORE instruction.

A lowering may produce conceptually:

```text
LoweredCard {
    source_card_id
    core_operations[]
    preserved_metadata
    effect_and_capability_requirements
    ordering_constraints
    failure_contract
    provenance_edges
}
```

Some semantic CARDs may lower to multiple core operations.

Some semantic CARDs may establish metadata, evidence boundaries, orchestration, or trace requirements rather than ordinary arithmetic instructions.

A CARD must never disappear merely because a backend does not understand its semantic role.

## Epistemic preservation

Lowering must preserve the epistemic meaning necessary to prevent silent promotion.

For example:

```text
OBSERVE MASS 4.2 kg
```

may lower its numeric payload into ordinary data operations, but the association with `OBSERVATION` must remain available to validation and provenance layers.

Likewise:

```text
TEST RESULT
```

must not become `VALIDATION`, and:

```text
PROVE PROPERTY WITH LEAN
```

must retain its explicit external proof/evidence boundary.

Lowering changes representation. It does not upgrade claims.

## Effects and capabilities

Semantic effects and capability requirements survive lowering as distinct concepts.

For example, a semantic file write may lower into one or more core effect operations while retaining:

```text
effect = WRITE_FILE
required_capability = FILESYSTEM_WRITE
```

Capability authorization must still complete successfully before the protected effect begins.

A lowering may not replace an explicit local operation with a network-backed helper unless the semantic and capability contracts explicitly permit that effect.

## Determinism, numeric, and randomness contracts

Lowering must carry execution contracts forward rather than re-infer them later.

Material contracts include, where applicable:

```text
requested_result_determinism
numeric_contract
requested_randomness_contract
RNG identity / stream requirements
```

A transformation that changes the legal numeric behavior or randomness requirements is not merely a representation change.

## Units and types

A backend may eventually operate on raw machine numbers, but unit and type checks required by the semantic contract must occur before information is discarded.

A lowering must either:

1. encode the required checks/normalization into QSOL-CORE operations; or
2. establish a validated premise that permits safe erasure of the higher-level metadata.

Silent unit loss is not valid lowering.

## Ordering and failure

Lowering must preserve source-observable ordering constraints.

Only CARDs proven **pure and total** under the active contract may be freely reordered solely from dependency information.

Potentially failing pure CARDs remain ordering-relevant under fail-stop semantics when moving them could change which external effects commit.

Effectful CARDs retain their effect-order constraints.

The lower representation must preserve enough information for QSOL-CORE to reproduce CARD → DECK → JOB failure propagation and per-effect-attempt completion state.

## Unsupported semantic constructs

If a semantic construct has no legal QSOL-CORE lowering, the lowering phase must fail explicitly.

It must not:

- drop the construct;
- replace it with a no-op without a frozen rule;
- silently weaken an execution contract;
- translate an unknown epistemic class into ordinary data;
- defer semantic invention to a backend.

Failing closed is preferable to emitting a program with changed meaning.

## Extensions

Extensions may define additional lowering rules behind explicit versioned contracts.

A lowering trace should bind the resolved extension identity used to interpret extension-owned constructs.

An extension may add lowering capability. It may not silently redefine frozen core meaning.

## Conformance fixtures

The future normative lowering specification should publish fixtures pairing canonical Semantic IR inputs with expected QSOL-CORE outputs and preserved metadata.

Fixtures should cover at least:

- scalar data and arithmetic;
- XOR and other logic;
- units/types;
- observations and assumptions;
- TEST / VALIDATION / PROOF boundaries;
- effects and capability requirements;
- seeded randomness;
- numeric contracts;
- failure and ordering constraints;
- extension-owned constructs;
- unsupported construct rejection.

A reference lowering implementation should pass those fixtures before backend code generation is considered conforming.

## Provenance

Lowering is itself a provenance-bearing transformation.

Useful trace material includes:

```text
semantic_ir_hash
lowering_spec_version
lowering_implementation_version
core_ir_hash
resolved_extensions[]
lowering_diagnostics[]
```

This allows a result to be traced through the first representational change rather than beginning provenance only after QSOL-CORE already exists.

## Principle

> The first lowering arrow is part of the language contract, not backend plumbing.
