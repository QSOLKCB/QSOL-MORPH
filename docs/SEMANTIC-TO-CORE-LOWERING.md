# Semantic-to-QSOL-CORE Lowering

QSOL-MORPH requires an explicit boundary between the research-facing Semantic IR and QSOL-CORE.

This document describes the candidate architecture for that boundary. It is **non-normative until the relevant specification phase is frozen**.

## Why this boundary exists

QSOL source carries information that a conventional machine-oriented IR often does not:

- research intent;
- epistemic class;
- values, types, and units;
- execution-relevant qualifiers;
- effects and their complete required-capability sets;
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
    preserved_qualifiers{}
    preserved_metadata
    effect_requirements[]
    ordering_constraints
    failure_contract
    provenance_edges
}
```

Some semantic CARDs may lower to multiple core operations.

Some semantic CARDs may establish metadata, evidence boundaries, orchestration, trace requirements, target-selection constraints, or adapter/tuning requirements rather than ordinary arithmetic instructions.

A CARD or execution-relevant qualifier must never disappear merely because a backend does not understand its semantic role.

## Qualifier preservation

`qualifiers{}` is part of the lowering contract.

Execution-relevant qualifiers may include, where frozen by the active specification or extension contract:

```text
target selection
adapter selection
tuning controls
extension-specific controls
placement constraints
other machine-selection or lowering modifiers
```

A lowering must either:

1. preserve the qualifier explicitly into QSOL-CORE/lower metadata for later MORPH interpretation; or
2. consume it under a frozen rule whose validated effect is represented in the lowered result and provenance.

It may not silently erase or default a qualifier that can change machinery, legality, authorization, or behavior.

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

Semantic effect requirements survive lowering as explicit per-effect associations.

For example, a semantic file write may lower into one or more core effect operations while retaining:

```text
effect_id = write_1
effect_kind = WRITE_FILE
required_capabilities = [FILESYSTEM_WRITE]
```

A remote AI effect may instead retain:

```text
effect_id = ai_call_1
effect_kind = AI_MODEL
required_capabilities = [AI_MODEL, NETWORK]
```

Capability authorization must complete successfully for **every capability in the set** before that protected effect begins.

A lowering may not collapse multiple effect-specific requirement sets into an ambiguous CARD-level union if doing so loses which permissions govern which attempt.

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

Effectful CARDs retain their effect-order constraints and per-effect capability bindings.

The lower representation must preserve enough information for QSOL-CORE to reproduce CARD → DECK → JOB failure propagation, explicit `failure_behavior`, and per-effect-attempt completion state.

## Unsupported semantic constructs

If a semantic construct or execution-relevant qualifier has no legal QSOL-CORE lowering, the lowering phase must fail explicitly.

It must not:

- drop the construct or qualifier;
- replace it with a no-op without a frozen rule;
- silently weaken an execution contract;
- translate an unknown epistemic class into ordinary data;
- defer semantic invention to a backend.

Failing closed is preferable to emitting a program with changed meaning.

## Extensions

Extensions may define additional lowering rules behind explicit versioned contracts.

A lowering trace should bind the resolved extension identity used to interpret extension-owned constructs and qualifiers.

An extension may add lowering functionality. It may not silently redefine frozen core meaning.

## Conformance fixtures

The future normative lowering specification should publish fixtures pairing canonical Semantic IR inputs with expected QSOL-CORE outputs and preserved metadata.

Fixtures should cover at least:

- scalar data and arithmetic;
- XOR and other logic;
- units/types;
- observations and assumptions;
- TEST / VALIDATION / PROOF boundaries;
- execution-relevant qualifiers, including target/adapter/tuning/extension-control qualifiers;
- single and multiple effects with distinct complete capability sets;
- seeded randomness;
- numeric contracts;
- explicit failure behavior and ordering constraints;
- extension-owned constructs and qualifiers;
- unsupported construct/qualifier rejection.

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
qualifier_lowering_decisions[]
lowering_diagnostics[]
```

This allows a result to be traced through the first representational change rather than beginning provenance only after QSOL-CORE already exists.

## Principle

> The first lowering arrow is part of the language contract, not backend plumbing.
