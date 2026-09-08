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

`sequencing_constraints[]` retains the canonical tagged Semantic-IR ordering field. Effect-order and failure-order may be deterministic projections of those tagged constraints, but they are not alternative lower fields and may not replace, flatten, or discard other sequencing kinds.

If every sequencing edge and both of its typed endpoints remain source-qualified and unchanged under a frozen deterministic reconstruction rule, the lower representation may preserve that relation directly. If lowering renames, splits, fuses, relocates, or otherwise changes an endpoint or edge encoding, it must emit `sequencing_constraint_lowering_decisions[]` identifying the exact source edge(s), exact lower edge(s), direction, endpoint kinds, complete owner paths, and the frozen rule/evidence that validates that mapping. Retaining only the original edge text while changing the containing representation is not sufficient provenance.

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

When QSOL-CORE retains an epistemic class, that class is a representation-qualified lower-IR binding, not an informal comment or inherited assumption. The Core binding must resolve to the exact Core owner/operation or value scope and retain the validated source class relation through the lowering trace. If a hand-built or direct-entry Core representation has no such binding, downstream outputs from that representation are `UNCLASSIFIED`/no-claim unless a later explicit evidence-bearing contract creates a valid class binding; they must never invent `TEST`, `VALIDATION`, or `PROOF` merely because an output exists.

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
        owner_scope_path[]:
            scope_kind
            scope_id
    core_scope_refs[]:
        owner_scope_path[]:
            scope_kind
            scope_id
    source_machinery_requirement_refs[]:
        owner_scope_path[]:
            scope_kind
            scope_id
        machinery_requirement_id
    lower_machinery_requirement_refs[]:
        owner_scope_path[]:
            scope_kind
            scope_id
        machinery_requirement_id
    source_card_ids[]
    mapping_rule_id
```

Every source/Core endpoint carries its complete representation-relative `owner_scope_path[]`. Source and lower machinery requirements are owner-qualified composite references, so repeated local requirement IDs such as `gpu` remain distinct across sibling scopes. The source references resolve in the input Semantic IR and the lower references in the resulting QSOL-CORE representation. Both reference sets are nonempty, deterministic, duplicate-free by complete qualified identity, and never paired by array position or inferred from shared source CARDs.

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

First-lowering decision families that can change execution-contract semantics carry a stable transition-decision identity plus explicit authority and subject-bound evidence:

```text
transition_decision_id?
transition_authorized_by?
transition_evidence_id?
```

For `result_determinism_lowering_decisions[]`, `numeric_contract_lowering_decisions[]`, `randomness_lowering_decisions[]`, and `failure_behavior_lowering_decisions[]`, all three fields are mandatory whenever the source/requested semantics differ from the effective Core semantics. A semantics-changing numeric decision additionally records exact content-bound `requested_numeric_contract_ref` and `effective_numeric_contract_ref` values containing the numeric contract ID and hash on each side. `transition_decision_id` identifies that exact first-lowering semantic-transition decision. `transition_authorized_by` resolves to accepted versioned/content-bound `CONTRACT_TRANSITION` authority. `transition_evidence_id` resolves to passing validation evidence whose subject is that exact lowering transition decision, including the requested/effective contract pair, complete owner-qualified Semantic/Core scope endpoints, and active context. Numeric transition evidence also binds both numeric contract IDs/hashes and the exact legal arithmetic/value-set change being authorized, including tolerance/fast-math, reassociation/FMA, precision, rounding, or denormal changes where applicable. The validation event must precede activation or application of the changed Core contract in the shared monotonic event-order domain. Missing, stale, wrong-kind, context-mismatched, unverifiable, self-authorized, or late authority/evidence fails closed. A generic numeric mapping rule, backend flag, or IR hash cannot authorize a semantic numeric weakening. These transition fields may be absent only for semantics-preserving mapping where no transition occurred.

The resulting execution-contract record preserves the same transition authority and provenance without reusing one singular evidence record for a different subject. Each materialized result-determinism scope, randomness scope, or failure-behavior binding affected by the transition receives its own `transition_evidence_id`, bound to that exact execution-scope record. Numeric execution scopes retain the effective content-bound numeric contract and material numeric mode, while the trace closure retains the numeric lowering decision and its pre-application transition authority/evidence through the owner-qualified mapping path. Result-determinism, randomness, and failure behavior retain their subject-bound target evidence; one-to-many lowering therefore produces distinct target-scope evidence records that may all reference the same lowering-decision evidence. A target formed from several authorized lowering decisions cites every applicable lowering evidence record. Identical evidence IDs must not be reused across different singular subjects. A later runtime success label, IR hash, generic mapping rule, or post-application validation cannot substitute for the required pre-application evidence chain.

## Units and types

A backend may eventually operate on raw machine numbers, but unit and type checks required by the semantic contract must occur before information is discarded.

Preservation or erasure is itself a provenance-bearing lowering decision. A lowering that does not encode the required unit/type checks and normalization explicitly into QSOL-CORE operations uses an identified record:

```text
type_unit_lowering_decisions[]:
    type_unit_lowering_decision_id
    source_fact_refs[]:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        fact_kind              # TYPE | UNIT | frozen equivalent
        fact_key_or_id
        fact_value_hash
    core_fact_refs[]:
        owner_scope_path[]:
            scope_kind
            scope_id
        fact_kind
        fact_key_or_id
        fact_value_hash?
    disposition               # PRESERVED | NORMALIZED | ERASED
    lowering_rule_id?
    validation_evidence_id?
```

Every source fact resolves in the hash-bound Semantic IR through its complete owner path and content identity. `core_fact_refs[]` identifies the exact Core facts/checks/normalized representation that remain after lowering. A bare type name, unit text, source CARD summary, or Core IR hash is not a source-to-lower relation.

For `PRESERVED`, a decision may be omitted only under a frozen deterministic identity reconstruction rule that proves the exact fact survives unchanged. For `NORMALIZED` or `ERASED`, both `lowering_rule_id` and `validation_evidence_id` are mandatory. The rule resolves to accepted, versioned, content-bound `TYPE_UNIT_LOWERING` authority, and the evidence resolves to passing validation whose singular subject is this exact `type_unit_lowering_decision_id`. The evaluated context binds the exact source type/unit facts, conversion or normalization semantics, range/domain premises, resulting Core facts/operations, active numeric/failure contracts, and every material dependency needed to justify erasure.

Validation must complete **before** the source metadata is discarded or the normalized Core value is made available. Post-erasure success, a generic “validated premise” label, equal output bytes, or an IR hash cannot substitute for that subject-bound pre-erasure evidence. If the source-to-Core relation cannot be proven under an accepted rule, the higher-level type/unit metadata remains explicit or lowering fails closed.

Silent unit loss is not valid lowering.

## Ordering and failure

Lowering must preserve source-observable ordering constraints through the canonical tagged `sequencing_constraints[]` representation or a separately frozen lossless equivalent.

When endpoint identity changes, preservation is represented explicitly:

```text
sequencing_constraint_lowering_decisions[]:
    sequencing_mapping_id
    source_edge_refs[]:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        constraint_kind
        predecessor_endpoint_ref
        successor_endpoint_ref
        edge_hash
    lower_edge_refs[]:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        constraint_kind
        predecessor_endpoint_ref
        successor_endpoint_ref
        edge_hash
    mapping_rule_id?
    validation_evidence_id?
```

Each endpoint reference uses the shared typed sequencing-endpoint contract: endpoint kind, complete owner path, and stable local ID in the named representation. Direction is part of edge identity; predecessor and successor are never interchangeable. `edge_hash` content-binds the tagged constraint plus both directed qualified endpoints.

If the edge and endpoints are unchanged and remain source-qualified under a frozen deterministic reconstruction rule, the explicit mapping record may be omitted. Any rename, split, fusion, relocation, retargeting, direction change, or alternative lower encoding requires a nonempty mapping group plus accepted `SEQUENCING_LOWERING` rule and passing `validation_evidence_id` bound to this exact mapping before the lower edge becomes operative. A mapping that drops an edge, reverses direction, changes endpoint kind, or cannot account for every resulting edge fails conformance.

Only CARDs proven **pure and total** under the active contract may be freely reordered solely from dependency information.

Potentially failing pure CARDs remain ordering-relevant under fail-stop semantics when moving them could change which external effects commit.

Effectful CARDs retain their effect-order constraints and per-effect capability bindings. Effect-order and failure-order views are derived from the full tagged sequencing relation and must not be used to truncate it.

The lower representation must preserve enough information for QSOL-CORE to reproduce CARD → DECK → JOB failure propagation, explicit `failure_behavior`, and per-effect-attempt completion state.

If explicit JOB/DECK/CARD failure behavior is normalized, grouped, or mapped into lower control semantics, the responsible frozen rule and source-to-lower scope relation must remain provenance-visible.

## Unsupported semantic constructs

If a semantic construct or execution-relevant qualifier has no legal QSOL-CORE lowering, the lowering phase must fail explicitly.

It must not:

- drop the construct, result binding, qualifier, machinery requirement, extension requirement, tagged sequencing constraint, type, or unit;
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
- units/types, including verified normalization/erasure and rejection when the pre-erasure premise cannot be proven;
- observations and assumptions;
- TEST / VALIDATION / PROOF boundaries;
- execution-relevant qualifiers, including target/adapter/tuning/extension-control qualifiers;
- single and multiple effects with distinct stable effect IDs and complete capability sets;
- protected machinery requirements at CARD/DECK/JOB scopes and explicit preservation into the lower representation;
- multiple machinery requirements sharing one source scope but reaching different Core scopes, plus missing, swapped, ambiguous, split, and frozen-fusion requirement-ID mappings;
- seeded randomness;
- multiple scoped numeric contracts and legal normalization/rejection cases;
- explicit failure behavior and tagged sequencing constraints, including non-effect/failure sequencing kinds and owner-qualified endpoint rename/split/fusion mappings;
- extension-owned constructs and qualifiers, including JOB/DECK/CARD scoped extension requirements where permitted and scope-preserving/remapped extension provenance;
- unsupported construct/qualifier/machinery-requirement/sequencing-constraint/type/unit rejection.

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
type_unit_lowering_decisions[]
sequencing_constraint_lowering_decisions[]
machinery_requirement_lowering_decisions[]
result_determinism_lowering_decisions[]
numeric_contract_lowering_decisions[]
randomness_lowering_decisions[]
failure_behavior_lowering_decisions[]
lowering_diagnostics[]
```

The canonical identity fields are `semantic_to_core_spec_version` and `semantic_to_core_implementation_version`, matching the flattened trace and run-manifest schemas. Lowering producers and consumers must not substitute unprefixed aliases unless a future frozen schema explicitly defines that alias mapping.

`extension_requirement_lowering_decisions[]` binds each materially transformed source extension requirement to the Core scope(s) that inherit it. Every source/Core scope endpoint is represented by its complete ordered absolute containment path in that representation, not only a kind/local-ID pair; source Semantic paths include JOB/DECK/CARD ancestors as applicable. The record also retains source CARD provenance, resolved profile/version/content/contract identity, and the frozen mapping rule. It may be omitted only under a frozen deterministic identity-scope reconstruction rule that actually covers extension ownership.

`machinery_requirement_lowering_decisions[]` uses the identified mapping groups defined in [Protected machinery requirements](#protected-machinery-requirements), including mandatory `source_machinery_requirement_refs[]` and `lower_machinery_requirement_refs[]`. Each reference pairs the complete representation-relative `owner_scope_path[]` with its local `machinery_requirement_id`; separate ID arrays, positional pairing, or shared source CARD summaries are not substitutes. A frozen reconstruction exception must recover every owner-qualified requirement association as well as scope ownership.

`type_unit_lowering_decisions[]` identifies every source type/unit fact that is normalized or erased, the exact Core facts/operations that replace it, and the accepted rule plus subject-bound evidence validated before erasure. `sequencing_constraint_lowering_decisions[]` identifies every source/lower ordering edge mapping whose endpoint identity, direction, or encoding is not losslessly reconstructible by the frozen identity rule. Neither family may be replaced by a generic “validated premise” or by the two IR hashes.

`result_determinism_lowering_decisions[]`, `numeric_contract_lowering_decisions[]`, `randomness_lowering_decisions[]`, and `failure_behavior_lowering_decisions[]` record scope preservation, grouping, identity changes, frozen normalizations, and any permitted transitions needed to explain how source requirements became Core contracts. Whenever semantics change, the applicable decision carries a stable `transition_decision_id` plus the required `transition_authorized_by` / subject-bound `transition_evidence_id`, validated before application. Numeric semantic changes additionally retain the exact requested/effective numeric contract IDs/hashes and the exact changed arithmetic/value-set semantics. Resulting execution-scope evidence remains a distinct subject-bound record where that scope family defines one and links back to the lowering evidence through `related_evidence_ids[]`; numeric execution scopes retain the effective contract/mode while the lowering transition remains resolvable through the mapping path. IR hashes, generic numeric mapping rules, and backend flags cannot establish that correspondence or authorize a transition.

This allows a result to be traced through the first representational change rather than beginning provenance only after QSOL-CORE already exists.

## Principle

> The first lowering arrow is part of the language contract, not backend plumbing.