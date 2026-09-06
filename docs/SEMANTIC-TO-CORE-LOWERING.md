# Semantic-to-QSOL-CORE Lowering

QSOL-MORPH requires an explicit boundary between the research-facing Semantic IR and QSOL-CORE.

This document describes the candidate architecture for that boundary. It is **non-normative until the relevant specification phase is frozen**.

## Why this boundary exists

QSOL source carries information that a conventional machine-oriented IR often does not:

- research intent;
- epistemic class;
- values, result bindings, types, and units;
- execution-relevant qualifiers;
- effects, stable declared effect IDs, and their complete required-capability sets;
- protected-machinery requirements and their complete required-capability sets;
- result-determinism requirements;
- scoped numeric contracts;
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
Core-to-Vector/Dataflow Lowering
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
    result_binding?
    core_operations[]
    preserved_qualifiers{}
    preserved_metadata
    effect_requirements[]
    machinery_requirements[]
    extension_requirements[]
    result_determinism_binding?
    numeric_contract_binding?
    randomness_contract_binding?
    sequencing_constraints[]
    failure_behavior
    provenance_edges
}
```

`sequencing_constraints[]` retains the canonical tagged Semantic-IR ordering field. Effect-order and failure-order may be deterministic projections of those tagged constraints, but they are not alternative lower fields and may not replace, flatten, or discard other sequencing kinds. If a future normative lower representation uses a different encoding, the conversion must be frozen, lossless, and provenance-visible.

`failure_behavior` retains the canonical Semantic-IR field name. If a future normative specification introduces a differently named lower representation, that conversion must itself be frozen and provenance-visible rather than being implied by an undocumented alias.

`machinery_requirements[]` retains the canonical protected-machinery requirements that may later govern MORPH target authorization. A generic `preserved_metadata` bucket is not a substitute for this explicit association.

`extension_requirements[]` retains the structured profile/version/contract association for extension-owned semantics at the CARD scope. JOB- or DECK-scoped extension requirements remain attached to their owning lower scope under the same preservation rule; they must not be copied onto an arbitrary CARD merely because lowering is expressed per CARD.

Some semantic CARDs may lower to multiple core operations.

Some semantic CARDs may establish metadata, evidence boundaries, orchestration, trace requirements, target-selection constraints, or adapter/tuning requirements rather than ordinary arithmetic instructions.

A CARD, its dependency-visible result binding, an execution-relevant qualifier, or an applicable machinery requirement must never disappear merely because a backend does not understand its semantic role.

## Result-binding preservation

A Semantic-IR `Card.result?` names the value produced for later dependency/reference use. It is not interchangeable with the value itself.

Lowering must preserve the identity relation:

```text
source CARD
    ↓ produces
result binding
    ↓ consumed by
dependent CARD(s)
```

A lower representation may rename, split, or fuse bindings only under a deterministic cardinality-aware mapping that is preserved in provenance and dependency edges. It must not discard the source binding and leave later stages to reconstruct dependencies from position, value equality, or backend-local naming.

A future frozen `result_binding_map[]` representation must be able to express one-to-one, one-to-many, many-to-one, and where permitted many-to-many mappings without positional inference. Identified mapping groups with plural source/lower binding sets are one candidate representation.

Conformance fixtures must include multiple producer/consumer chains plus preserved, renamed, split, and fused result mappings, and must detect missing, duplicated, or incorrectly rebound result identities.

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

The canonical `effect_id` must remain identifiable through lowering. Runtime attempts later acquire distinct `effect_attempt_id` values; a backend or runtime must not replace the declared identity with only the attempt identity.

Capability authorization must complete successfully for **every capability in the set** before that protected effect begins.

A lowering may not collapse multiple effect-specific requirement sets into an ambiguous CARD-level union if doing so loses which permissions govern which attempt.

A lowering may not replace an explicit local operation with a network-backed helper unless the semantic and capability contracts explicitly permit that effect.

## Protected machinery requirements

Protected machinery permission is distinct from an external effect and must survive this lowering boundary explicitly.

A canonical requirement such as:

```text
machinery_requirement_id = gpu_1
target_selector_or_class = GPU
required_capabilities = [GPU]
```

must remain associated with the JOB/DECK/CARD scope that owns it until MORPH can resolve the applicable target and authorize its protected use.

Semantic-to-Core lowering therefore must either:

1. preserve `machinery_requirements[]` directly in QSOL-CORE/preserved lower metadata; or
2. transform them into a separately frozen lower representation with a deterministic, provenance-visible mapping back to every canonical `machinery_requirement_id`.

A target-selection qualifier does not replace the machinery requirement, and an effect requirement does not replace it either. Selecting GPU/CUDA remains machinery selection; the separate machinery requirement states what authorization is required before that machinery may actually be used.

If lowering consumes, groups, scopes, or otherwise transforms machinery requirements, provenance must record the mapping/decision. Dropping an applicable machinery requirement before MORPH is a conformance failure.

Each first-boundary machinery mapping is an identified cardinality-aware group:

```text
machinery_requirement_lowering_decisions[]:
    mapping_group_id
    source_scope_refs[]:
        scope_kind
        scope_id
    core_scope_refs[]:
        scope_kind
        scope_id
    source_machinery_requirement_ids[]
    lower_machinery_requirement_ids[]
    source_card_ids[]
    mapping_rule_id
```

The source requirement IDs resolve in the input Semantic IR; the lower requirement IDs resolve in the resulting QSOL-CORE representation. The two IR hashes and typed owning scopes qualify those identities. Both ID sets are nonempty, deterministic, and duplicate-free. Unrelated requirements sharing an owning scope use separate mapping groups; they must not be paired by array position or inferred from shared source CARDs.

One-to-one preservation/rename, one-to-many split, and frozen legal fusion retain the exact source-to-lower requirement relation. A multi-source or multi-target group is valid only when its frozen `mapping_rule_id` defines that relation unambiguously, including which source target selector and complete capability set governs each lower requirement. Ambiguous grouping, swapped requirements, missing endpoints, and unauthorized capability weakening fail conformance. Omission is allowed only under a frozen deterministic reconstruction rule that recovers both the owning scopes and every requirement-ID association, not merely the scope correspondence.

## Determinism, numeric, and randomness contracts

Lowering must carry execution contracts forward rather than re-infer them later.

Material contracts include, where applicable:

```text
requested_result_determinism
numeric_contract binding + scope
requested_randomness_contract
RNG identity / stream requirements
```

Numeric contracts may be attached to individual CARDs or another frozen scope. Lowering must preserve the scope-to-contract association. It may normalize multiple contracts into one lower/global contract only under a frozen rule that proves the normalization preserves each source contract and records the mapping.

The same rule applies independently to result determinism and randomness. If lowering groups source CARDs into a Core scope, changes scope identity, or applies a frozen normalization, the transformation must preserve which source requirements govern the resulting Core contract and record the decision in provenance.

A transformation that changes the legal numeric behavior or randomness requirements is not merely a representation change.

## Units and types

A backend may eventually operate on raw machine numbers, but unit and type checks required by the semantic contract must occur before information is discarded.

A lowering must either:

1. encode the required checks/normalization into QSOL-CORE operations; or
2. establish a validated premise that permits safe erasure of the higher-level metadata.

Silent unit loss is not valid lowering.

## Ordering and failure

Lowering must preserve source-observable ordering constraints through the canonical tagged `sequencing_constraints[]` representation or a separately frozen lossless equivalent.

Only CARDs proven **pure and total** under the active contract may be freely reordered solely from dependency information.

Potentially failing pure CARDs remain ordering-relevant under fail-stop semantics when moving them could change which external effects commit.

Effectful CARDs retain their effect-order constraints and per-effect capability bindings. Effect-order and failure-order views are derived from the full tagged sequencing relation and must not be used to truncate it.

The lower representation must preserve enough information for QSOL-CORE to reproduce CARD → DECK → JOB failure propagation, explicit `failure_behavior`, and per-effect-attempt completion state.

If explicit JOB/DECK/CARD failure behavior is normalized, grouped, or mapped into lower control semantics, the responsible frozen rule and source-to-lower scope relation must remain provenance-visible.

## Unsupported semantic constructs

If a semantic construct or execution-relevant qualifier has no legal QSOL-CORE lowering, the lowering phase must fail explicitly.

It must not:

- drop the construct, result binding, qualifier, machinery requirement, extension requirement, or tagged sequencing constraint;
- replace it with a no-op without a frozen rule;
- silently weaken an execution or scoped numeric contract;
- translate an unknown epistemic class into ordinary data;
- defer semantic invention to a backend.

Failing closed is preferable to emitting a program with changed meaning.

## Extensions

Extensions may define additional lowering rules behind explicit versioned contracts.

A lowering trace should bind the resolved extension identity used to interpret extension-owned constructs and qualifiers **and** preserve which source scope owned that requirement.

If lowering preserves an extension requirement by identity, the source-to-Core scope relation may be omitted only when a frozen deterministic identity-scope reconstruction rule makes the ownership relation losslessly reconstructible. If lowering groups, relocates, splits, fuses, or otherwise transforms the owning scope, `extension_requirement_lowering_decisions[]` records that mapping together with the resolved profile/version/content/contract identity and frozen mapping rule.

An extension may add lowering functionality. It may not silently redefine frozen core meaning or detach a versioned profile requirement from the scope whose syntax, effects, qualifiers, or hooks it interprets.

## Conformance fixtures

The future normative lowering specification should publish fixtures pairing canonical Semantic IR inputs with expected QSOL-CORE outputs and preserved metadata.

Fixtures should cover at least:

- scalar data and arithmetic;
- producer/consumer result bindings and dependency identity, including preserved, renamed, split, and fused mappings;
- XOR and other logic;
- units/types;
- observations and assumptions;
- TEST / VALIDATION / PROOF boundaries;
- execution-relevant qualifiers, including target/adapter/tuning/extension-control qualifiers;
- single and multiple effects with distinct stable effect IDs and complete capability sets;
- protected machinery requirements at CARD/DECK/JOB scopes and explicit preservation into the lower representation;
- multiple machinery requirements sharing one source scope but reaching different Core scopes, plus missing, swapped, ambiguous, split, and frozen-fusion requirement-ID mappings;
- seeded randomness;
- multiple scoped numeric contracts and legal normalization/rejection cases;
- explicit failure behavior and tagged sequencing constraints, including non-effect/failure sequencing kinds;
- extension-owned constructs and qualifiers, including JOB/DECK/CARD scoped extension requirements where permitted and scope-preserving/remapped extension provenance;
- unsupported construct/qualifier/machinery-requirement/sequencing-constraint rejection.

A reference lowering implementation should pass those fixtures before backend code generation is considered conforming.

## Provenance

Lowering is itself a provenance-bearing transformation.

Useful trace material includes:

```text
semantic_ir_hash
semantic_to_core_spec_version
semantic_to_core_implementation_version
core_ir_hash
result_binding_map[]
resolved_extensions[]
extension_requirement_lowering_decisions[]
qualifier_lowering_decisions[]
machinery_requirement_lowering_decisions[]
result_determinism_lowering_decisions[]
numeric_contract_lowering_decisions[]
randomness_lowering_decisions[]
failure_behavior_lowering_decisions[]
lowering_diagnostics[]
```

The canonical identity fields are `semantic_to_core_spec_version` and `semantic_to_core_implementation_version`, matching the flattened trace and run-manifest schemas. Lowering producers and consumers must not substitute unprefixed aliases unless a future frozen schema explicitly defines that alias mapping.

`extension_requirement_lowering_decisions[]` binds each materially transformed source extension requirement to the Core scope(s) that inherit it, retaining source scope identity, source CARD provenance, resolved profile/version/content/contract identity, and the frozen mapping rule. It may be omitted only under a frozen deterministic identity-scope reconstruction rule that actually covers extension ownership.

`machinery_requirement_lowering_decisions[]` uses the identified mapping groups defined in [Protected machinery requirements](#protected-machinery-requirements), including mandatory `source_machinery_requirement_ids[]` and `lower_machinery_requirement_ids[]` independently of the typed source/Core scope endpoints. A frozen reconstruction exception must recover every requirement association as well as scope ownership.

`result_determinism_lowering_decisions[]`, `randomness_lowering_decisions[]`, and `failure_behavior_lowering_decisions[]` record scope preservation, grouping, identity changes, frozen normalizations, and any permitted transitions needed to explain how source requirements became Core contracts. IR hashes alone cannot establish that correspondence.

This allows a result to be traced through the first representational change rather than beginning provenance only after QSOL-CORE already exists.

## Principle

> The first lowering arrow is part of the language contract, not backend plumbing.
