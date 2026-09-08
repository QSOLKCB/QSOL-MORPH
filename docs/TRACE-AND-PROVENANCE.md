# Trace and Provenance

QSOL-MORPH treats provenance as part of execution semantics for research workflows.

This document is architectural and non-normative until the relevant contracts are frozen. Its purpose is to ensure that later implementations can explain not only what bytes were produced, but which semantic units, concrete executions, lowerings, machinery decisions, authorization decisions, execution paths, entropy acquisitions, external tools, toolchain invocations, and evidence transitions produced them.

### One record contract, not independent mirror schemas

The record definitions and cross-record validation conditions in this document apply wherever the same records appear, including the README, agent guidance, roadmap gates, reproducibility manifests, and failure-domain traces. Shorter inventories are projections of this model, not permission to omit conditionally required fields or weaken validation. `?` means conditional presence: the applicability rules below decide when the field is required. A standalone projection retains the transitive closure needed to validate its records, inline or through retrievable content-bound references. These architectural requirements do not freeze an executable format or implement the later roadmap phases.

In particular, complete canonical machinery-capability coverage, concrete cache-substitution subjects, concrete input consumers/acquisitions, owner-qualified result bindings, and representation-qualified execution subjects are shared requirements of every projection. Canonical sequencing endpoints use the [typed endpoint contract](SERIALIZATION.md#typed-sequencing-endpoints); shorter references to sequencing or binding identity do not waive its namespace and ownership checks.

## Trace questions

A complete trace should be able to answer:

- what source and canonical Semantic IR were executed when that lineage exists;
- which stable JOB, DECK, and CARD identities were selected when Semantic execution structure exists;
- which concrete DECK/CARD executions or lower-representation operation executions actually occurred;
- which typed control decision, identified failure, or verified frozen skip caused an untaken, blocked, not-reached, or explicitly skipped CARD/lower operation;
- how Semantic IR lowered into QSOL-CORE when that boundary was traversed;
- how QSOL-CORE lowered into the mandatory Vector/Dataflow IR when that boundary was traversed;
- how result bindings were preserved, renamed, split, fused, or otherwise mapped;
- how extension, machinery, result-determinism, numeric, randomness, and failure-behavior scopes mapped through both mandatory lowerings;
- how every execution-relevant qualifier was preserved or consumed, under which frozen rule, and what exact Core facts or constraints represent its validated effect;
- which machinery-selection decisions were considered, denied, superseded, or finally used;
- which protected machinery requirements applied, whether the protected use followed the final executable selection decision, and whether authorization completed before protected use began;
- which protected effects were declared for each concrete execution subject, authorized, attempted, completed, aborted, partially observed, or legitimately not attempted;
- which external-entropy acquisition attempt(s) and immutable entropy input(s) governed every applicable EXTERNAL-ENTROPY randomness scope;
- what exact immutable inputs were consumed, by which concrete execution subjects or acquisition attempts, and which ones materially contributed to each output;
- which concrete producer execution subjects, effect attempts, tools, generated artifacts, optimization records, direct toolchain producers, transitive toolchain ancestry, and execution-contract scopes produced each output;
- which concrete execution subjects used cache substitution rather than cold execution and under what legality evidence;
- what exact duplicate-preserving toolchain argument vector was used when positional command-line semantics were material;
- what epistemic class and evidence status belongs to each output when such semantic lineage is present;
- whether execution failed, at what typed scope, and what had already become observable.

## Trace layers

A future trace may contain several connected layers:

```text
SOURCE TRACE
SEMANTIC TRACE
SEMANTIC-TO-CORE TRACE
CORE-TO-VECTOR/DATAFLOW TRACE
MORPH TRACE
EXECUTION TRACE
RESULT TRACE
```

These layers describe different objects. A flat manifest may serialize them together, but it must not erase their identities or joins. A legitimate execution may begin at a lower layer such as QSOL-CORE; untraversed upstream layers are absent rather than synthesized.

## Stable source identities

Stable JOB/DECK/CARD identities originate in the canonical semantic model. A trace records them; it does not synthesize, renumber, or infer them from array position.

```text
source_trace:
    source_hash
    spec_version
    run_id?
    job_id
    deck_identities[]:
        deck_id
        owner_scope_path[]:
            scope_kind
            scope_id
    card_identities[]:
        card_id
        owner_scope_path[]:
            scope_kind
            scope_id
    source_location?
```

Each `deck_identities[]` path is the complete ordered canonical containment path from the JOB through the referenced DECK and terminates at that `deck_id`. Each `card_identities[]` path includes the owning JOB and DECK and terminates at that `card_id`. Every ancestor needed to distinguish reused local IDs participates in identity. Parallel bare `deck_ids[]` / `card_ids[]`, positional pairing, first-match lookup, or list order cannot establish containment; missing, truncated, reordered, ambiguous, or owner-mismatched identity paths fail closed.

## Semantic trace

Potential fields include:

```text
semantic_ir_hash
job_ids[]
deck_ids[]
card_ids[]
dependency_graph_hash
epistemic_class_bindings[]
extension_requirements[]
effect_requirements[]
machinery_requirements[]
result_determinism_bindings[]
numeric_contract_bindings[]
randomness_contract_bindings[]
failure_behavior_bindings[]
```

The semantic-trace `job_ids[]`, `deck_ids[]`, and `card_ids[]` are inventory summaries only. They do not establish parentage or owner identity. Canonical containment is resolved from the hash-bound Semantic IR and the owner-qualified identities in `source_trace`; no semantic binding may infer ownership from these summary arrays or their relative positions.

### Epistemic class bindings

```text
epistemic_class_bindings[]:
    owner_scope_path[]:
        scope_kind
        scope_id
    card_id
    semantic_class
```

Separate `card_ids[]` and `epistemic_classes[]` arrays are not an acceptable positional association. Epistemic class is bound to the CARD's complete ordered absolute `owner_scope_path[]` plus local `card_id`; the path terminates at that CARD. Sibling DECKs may therefore each contain local `CARD 7` with different research classes without collision. Missing, truncated, reordered, or owner-mismatched class paths fail closed.

### Declared effect requirements

Effect declarations are representation-qualified so the same runtime contract works for a Semantic entry and for a legitimate lower-representation entry such as direct QSOL-CORE:

```text
effect_requirements[]:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
    declared_effect_id
    card_id?
    operation_id?
    effect_kind
    required_capabilities[]
```

`representation_identity` is the content-bound identity of the representation that owns the declaration, normally `semantic_ir_hash`, `core_ir_hash`, or another frozen lower-IR hash. The complete capability set belongs to that specific effect. A CARD-wide or operation-wide capability union may be useful for preflight but cannot replace the per-effect association.

For Semantic IR, the path is the ordered canonical containment path `JOB -> DECK -> CARD`, `card_id` is required, and `operation_id` is absent unless a frozen Semantic model explicitly defines one. For direct QSOL-CORE or another lower representation, the path terminates at the actual operation-owning scope, `operation_id` is required when the declaration belongs to a concrete operation, and no Semantic CARD identity is fabricated. A retained `card_id` on a lower declaration is lineage metadata only and must be independently verifiable through traversed provenance.

Resolve every traced effect declaration by the complete tuple `(representation_kind, representation_identity, owner_scope_path[], declared_effect_id)` to exactly one declaration in the named hash-bound representation. Every ancestor needed to distinguish reused local IDs is part of identity. The path is never inferred from a local CARD/operation/effect ID, list position, producer IDs, or first-match lookup. The trace declaration must match the resolved declaration's effect kind and complete capability set. Missing, incomplete, swapped, ambiguous, wrong-representation, or owner-mismatched paths fail closed. Agreement between two truncated runtime copies is not agreement with the canonical declaration. See [Declaration-bound authorization validation](#declaration-bound-authorization-validation).

### Protected machinery requirements

Machinery declarations are representation-qualified for the same reason as effect declarations: direct lower-representation entry must identify the requirement that actually exists in that representation rather than manufacture a Semantic owner.

```text
machinery_requirements[]:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
    machinery_requirement_id
    source_card_ids[]?
    source_operation_ids[]?
    target_selector_or_class
    required_capabilities[]
```

`representation_identity` is the content-bound identity of the representation that owns the machinery requirement, normally `semantic_ir_hash`, `core_ir_hash`, `vector_dataflow_ir_hash`, or another frozen lower-IR hash. A GPU requirement does not turn GPU selection into an external effect; it remains a separate protected-machinery authorization boundary.

For Semantic IR, `representation_kind` identifies Semantic IR, `representation_identity = semantic_ir_hash`, and `owner_scope_path[]` is the complete ordered canonical `JOB -> DECK -> CARD` containment path through the actual owner as applicable. For legitimate direct QSOL-CORE entry, `representation_kind = QSOL_CORE`, `representation_identity = core_ir_hash`, and the path is the complete Core-relative containment path from the Core representation root through the actual requirement-owning function/block/operation or other frozen Core scope. It does **not** start with a fabricated JOB. `source_card_ids[]` is conditional verified Semantic lineage only; `source_operation_ids[]`, when present, must resolve in the named lower representation and cannot replace the full owner path.

Resolve every traced machinery requirement by the complete tuple `(representation_kind, representation_identity, owner_scope_path[], machinery_requirement_id)` to exactly one requirement in the named hash-bound representation. Every ancestor needed to distinguish reused local scope IDs participates in identity. The resolved declaration must retain the exact target selector/class and complete capability set. A lowered requirement additionally retains its validated source-to-lower requirement mapping. Missing, ambiguous, swapped, wrong-representation, or owner-mismatched paths fail closed. A runtime copy, source-CARD summary, local operation ID, or capability union cannot replace that canonical association. [Canonical machinery coverage](#canonical-machinery-coverage) is checked before accepting either a grant or a protected use.

### Source contract bindings

```text
result_determinism_bindings[]:
    owner_scope_path[]:
        scope_kind
        scope_id
    source_card_ids[]
    requested_result_determinism

numeric_contract_bindings[]:
    owner_scope_path[]:
        scope_kind
        scope_id
    source_card_ids[]
    numeric_contract_id
    numeric_contract_hash

randomness_contract_bindings[]:
    owner_scope_path[]:
        scope_kind
        scope_id
    source_card_ids[]
    requested_randomness_mode

failure_behavior_bindings[]:
    failure_behavior_binding_id
    governed_scope_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
    transition_evidence_id?
```

`failure_behavior_binding_id` is the stable record identity used by result and failure provenance. It is distinct from the generic computation `scope_id` and remains resolvable even when several bindings or policy transitions concern one governed computation.

Source and execution failure bindings use this one canonical representation-qualified shape. In the Semantic-trace layer, `governed_scope_ref.representation_kind` identifies Semantic IR and `governed_scope_ref.representation_identity` is the content-bound `semantic_ir_hash`; the complete ordered `owner_scope_path[]` terminates at the JOB, DECK, CARD, or other frozen scope that owns the contract. Later execution/lowered bindings keep the same field shape while naming their actual governed representation and identity. There is no alternate direct-`owner_scope_path[]` failure-binding form sharing this stable-ID namespace. Missing representation identity, truncated/ambiguous owner paths, or owner/representation mismatch fails closed.

Distinct source requirements may not be collapsed into one execution-wide declaration unless a frozen normalization proves that collapse is lossless. Failure bindings obey the same [failure-policy transition conditions](#failure-policy-transitions) here and in the execution-scope inventory.

## Semantic-to-Core trace

The Semantic IR to QSOL-CORE transition is independently provenance-bearing.

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

The canonical identity field names are `semantic_to_core_spec_version` and `semantic_to_core_implementation_version`.

### Resolved extension identities

A source extension requirement is not the installed implementation that satisfied it. Every material resolution uses an identified record:

```text
resolved_extensions[]:
    resolved_extension_id
    profile_name
    resolved_version
    contract_id
    contract_hash
    implementation_components[]:
        component_kind
        component_id
        component_version
        component_content_hash
        component_location?
    source_requirement_refs[]:
        representation_kind
        ir_hash
        owner_scope_path[]:
            scope_kind
            scope_id
        requirement_hash
    governing_scope_refs[]:
        representation_kind
        ir_hash
        owner_scope_path[]:
            scope_kind
            scope_id
    source_card_ids[]
```

`resolved_extension_id` is the stable resolution-record key, not the profile name or requested range. `resolved_version` is the exact selected profile version. `contract_id` and `contract_hash` bind the actual contract interpreting it. The nonempty `implementation_components[]` identifies every material profile implementation, adapter, and lowering hook used for this resolution, with its exact version and immutable content hash. A frozen content-bound package manifest may represent a complete component/dependency closure; a package label, mutable endpoint, or version range cannot. Content needed to validate the resolution must be embedded in the trace closure or retrievable and hash-verifiable. Material external tools invoked by an adapter retain their separate external-tool identities.

Each nonempty `source_requirement_refs[]` entry is a composite reference to one exact requirement in the hash-bound original input representation: `representation_kind`, `ir_hash`, the complete representation-relative `owner_scope_path[]`, and the canonical hash of the complete `ExtensionRequirement` value, including profile, requested version/range, and any required contract identity. Every ancestor needed to disambiguate the owning local scope participates in identity. A one-level `{ scope_kind, scope_id }` pair is insufficient when sibling containers reuse CARD, region, or other local IDs. The reference resolves to the owned canonical requirement, not to an arbitrarily selected child CARD. Ambiguous duplicate requirements require a frozen canonical deduplication rule or fail resolution. `representation_kind` distinguishes Semantic IR, Core IR, and other explicitly frozen input representations; an execution that legitimately starts with Core IR must not fabricate a Semantic IR source.

Each nonempty `governing_scope_refs[]` identifies the actual representation-relative scope path(s) and IR version in which the resolution interprets syntax, adapters, effects, or lowering hooks. Source ownership remains separately preserved. Validate each full path against the hash-bound representation and reject missing, truncated, reordered, ambiguous, or owner-mismatched paths. Then validate that the resolved profile/version satisfies every referenced source requirement, that any required contract identity matches, and that the identified implementation components implement that exact contract. Unknown versions, mismatched hashes, missing components, unresolved owners, or an unestablished requirement-to-resolution association fail closed before the extension is used.

Different resolutions of one source range have different resolution identities and retain their actual governed scopes. Several requirements may share a resolution only when each one is explicitly referenced and satisfied. Both extension-lowering mapping families reference applicable `resolved_extension_ids[]`; a permitted identity-mapping reconstruction may omit a redundant mapping record, never the exact material resolution or its source/owner association. A frozen reconstruction rule must recover the same requirement, resolution, and governed-scope relation without guessing from a profile name.

### Qualifier lowering decisions

Execution-relevant qualifiers are not opaque lowering metadata. Every qualifier that is consumed, transformed, relocated, or otherwise represented by something other than a verbatim lower qualifier uses an identified decision record:

```text
qualifier_lowering_decisions[]:
    qualifier_lowering_decision_id
    source_qualifier_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        qualifier_key_path[]
        qualifier_value_hash
    disposition                 # PRESERVED | CONSUMED
    core_scope_refs[]:
        owner_scope_path[]:
            scope_kind
            scope_id
    resulting_core_refs[]:
        owner_scope_path[]:
            scope_kind
            scope_id
        result_kind
        result_key_or_id
        result_value_hash?
    resolved_extension_ids[]?
    lowering_rule_id?
    validation_evidence_id?
```

`qualifier_lowering_decision_id` is the stable decision identity. `source_qualifier_ref` resolves the exact qualifier in the hash-bound Semantic IR by representation identity, complete owning path, deterministic key/path inside `qualifiers{}`, and canonical value hash. The full qualifier value must be obtainable from the hash-bound Semantic IR or an equivalent content-bound reference; the hash is not permission to ignore an unavailable value. Target/adapter/placement/tuning/extension-control qualifiers with the same key text under different CARD/DECK/JOB owners remain distinct because their complete owner paths differ.

`core_scope_refs[]` identifies every Core scope whose meaning, machinery constraints, authorization requirements, or lowering behavior is affected by this decision. `resulting_core_refs[]` identifies the exact lower facts that represent the qualifier's effect, such as preserved lower qualifier metadata, target constraints, machinery requirements, adapter/extension bindings, placement constraints, tuning constraints, or another frozen Core fact/decision. Each result ref resolves in `core_ir_hash` by complete owner path plus its frozen kind/key/ID and, where the value itself is material, its canonical value hash. A Core IR hash alone, a broad target label, or source CARD summary cannot show what happened to the qualifier.

For `disposition = PRESERVED`, the resulting Core refs must prove exact value-preserving representation or an explicitly frozen deterministic identity reconstruction. No opaque decision entry is needed merely to restate a qualifier that remains byte/semantics-identical under the frozen representation, but if a decision record is emitted it must still resolve consistently.

For `disposition = CONSUMED`, or for any non-verbatim transformation whose effect can change machinery, authorization, placement, tuning, extension behavior, legality, or execution semantics, both `lowering_rule_id` and `validation_evidence_id` are mandatory. `lowering_rule_id` resolves to an accepted versioned/content-bound `rule_records[]` entry of kind `QUALIFIER_LOWERING`. `validation_evidence_id` resolves to passing `validation_evidence[]` with `subject_kind = QUALIFIER_LOWERING_DECISION` and `subject_id = qualifier_lowering_decision_id`. Its evaluated context binds the exact source qualifier/value, `semantic_ir_hash`, `core_ir_hash`, complete target scope/result refs, applicable resolved extension identities/contracts, active execution contracts, and any machinery/capability implications needed by the rule.

The rule must explicitly permit consuming or transforming this qualifier into those exact Core facts under that context. Validation must complete before the transformed lower fact is applied or relied upon in the shared event-order domain. A generic extension presence record, backend choice, post-lowering success, or unvalidated rule name does not authorize qualifier consumption. If an extension owns/interprets the qualifier, `resolved_extension_ids[]` is required and must resolve to the exact profile/version/content/contract records that authorize the rule's interpretation.

Unsupported or unverifiable execution-relevant qualifiers fail lowering. They must not be silently erased, defaulted, or converted into an unrelated Core fact. One source qualifier may legitimately produce several Core facts only when all resulting refs are explicit and the accepted rule/evidence validates that exact relation; several source qualifiers must not be collapsed into one decision unless a frozen rule defines and proves that composition without losing ownership or value identity.

### Cardinality-aware result-binding maps

Result-binding maps are identified mapping groups:

```text
result_binding_map[]:
    mapping_group_id
    source_bindings[]:
        source_card_id?
        owner_scope_path[]:
            scope_kind
            scope_id
        binding_id
    lower_bindings[]:
        owner_scope_path[]:
            scope_kind
            scope_id
        binding_id
    mapping_rule_id?   # REQUIRED for every many-to-one or many-to-many group
```

Each binding is identified by its complete typed `owner_scope_path[]` and local `binding_id` within the exact representation on that side of the hash-bound lowering boundary. At Semantic-to-Core the source and lower contexts are `semantic_ir_hash` and `core_ir_hash`; at Core-to-Vector/Dataflow they are `core_ir_hash` and `vector_dataflow_ir_hash`. A flattened manifest must keep each map associated with its boundary and both IR identities. A hash or local binding name from a different representation cannot satisfy the reference.

The owner path is the ordered absolute containment path from the representation root to the binding's defining scope, with a known `scope_kind` and stable `scope_id` for every segment. Include all enclosing scopes needed to distinguish local names. An empty path is valid only for an actual representation-root binding, never an unknown local owner. Each complete reference resolves to exactly one binding defined by that scope in that IR. `source_card_id`, when present as source provenance, must agree with the resolved producer and cannot replace the owner path. Lowered scopes need not fabricate a source CARD as their owner.

Thus two Core scopes or Vector/Dataflow kernels can each define local binding `v0` without ambiguity: their owner paths differ. A split can name both qualified `v0` bindings; a fusion can name several distinct qualified sources. The dependent consumer must resolve to that same qualified binding, not the first matching local name. Missing/invalid owner paths, duplicate definitions under one complete key, wrong representation, or unresolved producers fail conformance.

This model supports:

- one-to-one preservation or rename;
- one-to-many split;
- many-to-one frozen legal fusion;
- many-to-many only when an explicit frozen rule permits it.

For every many-to-one or many-to-many mapping group, `mapping_rule_id` is mandatory and resolves to the accepted frozen, content-bound rule that defines the value semantics of the fusion/reassociation and how dependent references are redirected. The rule must apply to this exact qualified source/lower binding set and lowering boundary. Missing, unknown, wrong-boundary, context-mismatched, or unverifiable rule identity rejects the mapping rather than silently choosing which source value a dependent consumes. One-to-one preservation/rename and one-to-many split may omit the field only where the frozen default/reconstruction semantics unambiguously define that non-fusing relation.

`source_bindings[]` and `lower_bindings[]` use deterministic canonical ordering by the complete qualified references, with no duplicate member in an array. Path segments retain containment order. Positional inference and sorting by `binding_id` alone are not sufficient. A map is required whenever result identities are preserved or transformed unless a frozen rule permits deterministic reconstruction of the complete mapping, including every owner path and both representation identities. Identity of local name text alone is not that reconstruction rule. Both mandatory lowerings and all manifest projections use this same qualified map.

### First-lowering scope mappings

Every decision family that maps a scoped semantic requirement identifies both ends with typed scope references rather than untyped IDs.

```text
scope_ref:
    owner_scope_path[]:
        scope_kind
        scope_id
```

`owner_scope_path[]` is the complete ordered absolute containment path within the representation named by that lowering boundary. For Semantic-IR endpoints it includes JOB, DECK, and CARD ancestors as applicable; for Core endpoints it includes every enclosing Core scope needed to distinguish locally repeated IDs. The terminal path element is the referenced scope itself. A bare `(scope_kind, scope_id)` pair is not a valid first-lowering endpoint when local IDs can repeat. Missing, truncated, reordered, or ambiguous paths fail conformance for extension, machinery, result-determinism, numeric, randomness, and failure-behavior decision families.

For example:

```text
extension_requirement_lowering_decisions[]:
    source_scope_ref
    core_scope_refs[]
    source_card_ids[]
    resolved_extension_ids[]
    profile_name
    resolved_version_or_content_identity
    contract_id_or_hash?
    mapping_rule_id
```

The same typed-endpoint principle applies to machinery-requirement, result-determinism, numeric-contract, randomness, and failure-behavior lowering decisions. A JOB-owned requirement must not be silently relocated to a CARD or detached from the Core scope that inherits it.

For first-lowering contract decision families that can change semantics, the applicable decision record also carries:

```text
transition_decision_id?
transition_authorized_by?
transition_evidence_id?
```

For `numeric_contract_lowering_decisions[]`, the decision additionally identifies the exact content-bound requested/source and effective Core numeric contracts whenever they are not identical:

```text
requested_numeric_contract_ref?:
    numeric_contract_id
    numeric_contract_hash
effective_numeric_contract_ref?:
    numeric_contract_id
    numeric_contract_hash
```

For `result_determinism_lowering_decisions[]`, `numeric_contract_lowering_decisions[]`, `randomness_lowering_decisions[]`, and `failure_behavior_lowering_decisions[]`, **any semantic change** between source/requested and effective Core contracts requires `transition_decision_id`, `transition_authorized_by`, and `transition_evidence_id`. A numeric semantic change includes changing the legal value set or arithmetic behavior: for example strict IEEE behavior to tolerance/fast-math semantics, new reassociation/FMA permission, reduced precision, changed rounding/denormal behavior, or another contract change not already permitted by the source contract. Merely renaming or structurally relocating an identical content-bound numeric contract is representation mapping, not a semantic transition.

`transition_decision_id` is the stable identity of that exact first-lowering semantic-transition decision. `transition_authorized_by` resolves to an accepted versioned/content-bound `CONTRACT_TRANSITION` rule. `transition_evidence_id` resolves to passing `validation_evidence[]` with `subject_kind = LOWERING_TRANSITION_DECISION` and `subject_id = transition_decision_id`, binding the exact requested/effective pair, complete owner-qualified source/Core scopes, accepted transition authority, and active context. For numeric changes the evidence additionally binds both numeric contract IDs/hashes and the exact semantic difference being authorized. Its validation event must precede application of the changed Core contract in the shared event-order domain. A generic numeric mapping rule, backend fast-math flag, IR hash, or rule assertion without passing subject-bound pre-application evidence is unauthorized and fails closed. The transition fields may be absent only when no semantic transition occurred.

The authority and evidence lineage are preserved into each resulting execution-contract record without reusing one singular evidence record for a different subject. Every affected result-determinism scope, randomness scope, or failure-behavior binding receives its own `transition_evidence_id`, bound to that exact execution-scope record under its type-specific subject kind. Numeric execution scopes retain the effective content-bound numeric contract and material numeric mode, while the trace closure retains the numeric lowering decision and its pre-application transition authority/evidence. One-to-many lowering therefore preserves distinct target-scope identity while keeping the authorized numeric transition resolvable from every affected mapping path. IR hashes, mapping metadata, identical authority labels, or post-application success cannot substitute for this subject-bound evidence chain.

Machinery requirements additionally need an explicit requirement-level association at this first boundary:

```text
machinery_requirement_lowering_decisions[]:
    mapping_group_id
    source_scope_refs[]
    core_scope_refs[]
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

Both scope arrays contain the complete-path `scope_ref` values defined above. Source and lower machinery requirements are owner-qualified composite references pairing `owner_scope_path[]` with the local `machinery_requirement_id`; they resolve in the input Semantic IR and resulting Core IR respectively. The reference sets are nonempty, deterministic, and duplicate-free by complete qualified identity. Splits or frozen legal fusions must preserve every source/lower qualified requirement and a frozen rule defining the exact relation, including target selector and complete capability set. Shared scope IDs, repeated local requirement IDs, and list position cannot substitute for this association.

A mapping family may be omitted only when a frozen deterministic reconstruction rule proves both scope correspondence and every applicable requirement-ID association without loss. Generic metadata or IR hashes alone are not such a rule. See [Semantic-to-Core machinery preservation](SEMANTIC-TO-CORE-LOWERING.md#protected-machinery-requirements).

## Core-to-Vector/Dataflow trace

The mandatory QSOL-CORE to Vector/Dataflow IR transition is a separate provenance-bearing transformation.

```text
core_ir_hash
vector_dataflow_spec_version
vector_dataflow_implementation_version
vector_dataflow_ir_hash
result_binding_map[]
extension_requirement_mapping_decisions[]
machinery_requirement_mapping_decisions[]
core_to_vector_result_determinism_mapping_decisions[]
core_to_vector_numeric_contract_mapping_decisions[]
core_to_vector_randomness_mapping_decisions[]
failure_behavior_mapping_decisions[]
vector_dataflow_lowering_diagnostics[]
```

This boundary uses the same cardinality-aware result-binding map semantics.

### Typed second-lowering contract mappings

The second lowering preserves exactly which Core scope maps to which Vector/Dataflow scope using complete representation-relative containment paths. Bare IDs or one-level kind/local-ID pairs are insufficient because enclosing Core and Vector/Dataflow scopes may independently reuse CARD, region, kernel, and generated-unit IDs. Every ancestor needed to distinguish the terminal local scope participates in mapping identity.

```text
core_scope_refs[]:
    owner_scope_path[]:
        scope_kind
        scope_id

vector_dataflow_scope_refs[]:
    owner_scope_path[]:
        scope_kind
        scope_id
```

A generic mapping record may contain:

```text
core_scope_refs[]
vector_dataflow_scope_refs[]
source_card_ids[]
mapping_rule_id
backend_unit_ids[]?
transition_decision_id?
transition_authorized_by?
transition_evidence_id?
```

Use the applicable mapping family for:

- extension requirements;
- protected-machinery requirements;
- result determinism;
- numeric contracts and material numeric modes;
- randomness contracts;
- failure behavior.

For `core_to_vector_numeric_contract_mapping_decisions[]`, a semantics-changing decision additionally records content-bound `requested_numeric_contract_ref` and `effective_numeric_contract_ref` values with `numeric_contract_id` and `numeric_contract_hash` on each side.

For `core_to_vector_result_determinism_mapping_decisions[]`, `core_to_vector_numeric_contract_mapping_decisions[]`, `core_to_vector_randomness_mapping_decisions[]`, and `failure_behavior_mapping_decisions[]`, any semantic change between requested/source and effective lower contracts requires `transition_decision_id`, `transition_authorized_by`, and `transition_evidence_id`. The numeric definition of semantic change is the same as at the first boundary: a newly permitted tolerance, reassociation/FMA/fast-math behavior, precision/rounding/denormal change, or other legal-value/arithmetic change is a contract transition rather than generic mapping.

The decision ID identifies the exact Core→Vector/Dataflow semantic-transition decision. The authority must resolve to the accepted versioned/content-bound `CONTRACT_TRANSITION` rule; the evidence must resolve to passing `validation_evidence[]` with `subject_kind = LOWERING_TRANSITION_DECISION` and `subject_id = transition_decision_id`, binding the exact requested/effective pair, owner-qualified source/lower scopes, accepted authority, and active context. Numeric evidence also binds the requested/effective numeric contract IDs/hashes and exact authorized semantic difference. Its validation event must precede application of the changed lower contract. A generic mapping rule, backend numeric flag, or rule assertion without passing subject-bound pre-application evidence is an unauthorized transition and fails closed. These fields may be absent only when the mapping is semantics-preserving and no contract transition occurred.

Each resulting execution-contract record preserves the transition through the trace closure under its own stable scope/binding identity. Result-determinism/randomness/failure records retain their dedicated subject-bound target evidence; numeric execution scopes retain the effective contract/mode and remain linked through the owner-qualified numeric mapping decision to its lowering transition evidence. Reusing one evidence ID for unrelated singular subjects remains invalid.

`machinery_requirement_mapping_decisions[]` additionally identifies the stable machinery-requirement records on both sides of the lowering boundary:

```text
machinery_requirement_mapping_decisions[]:
    core_scope_refs[]
    vector_dataflow_scope_refs[]
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
    backend_unit_ids[]?
```

The source/lower machinery-requirement arrays contain complete owner-qualified references rather than parallel local IDs. Scope correspondence and source CARD identity do not identify which requirement was mapped when local requirement IDs can repeat. Each lower qualified requirement must preserve the corresponding source target selector/class and complete capability set or identify the frozen rule that transformed them.

`extension_requirement_mapping_decisions[]` additionally retains the applicable profile/version/content/contract identity and `resolved_extension_ids[]` resolving to the exact records defined above. Repeated profile/version summaries must agree with those records and cannot replace their owning-requirement or implementation-component references.

If a Core scope splits into multiple kernels, several Core scopes fuse into one lower region, or scope identity otherwise changes, that mapping is provenance-visible. Each mapping family may be omitted only under a frozen deterministic identity-scope reconstruction rule that covers that family. IR hashes alone do not establish scope correspondence.

## MORPH trace

Potential fields include:

```text
vector_dataflow_ir_hash
morph_version
optimization_profile
optimization_provenance[]
backend_selection_scopes[]
backend_selection_decisions[]
machinery_authorization_records[]
machinery_use_records[]
generated_artifacts[]
toolchain_invocations[]
vectorization_decisions[]
fusion_decisions[]
memory_placement_decisions[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
failure_behavior_bindings[]
rule_records[]
validation_evidence[]
```

## Backend-selection provenance

A governed computation and the ordered machinery decisions made for it are separate objects.

```text
backend_selection_scopes[]:
    backend_selection_scope_id
    governed_scope_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
    source_card_ids[]
    backend_unit_id?
    selection_decision_ids[]
    final_selection_decision_id?
```

`backend_selection_scope_id` is the stable selection-record key. `governed_scope_ref` identifies the exact computation through the representation kind/content-or-run identity plus its complete representation-relative `owner_scope_path[]`; the terminal path element is the governed scope itself. Every enclosing scope needed to distinguish reused local IDs participates in identity. `source_card_ids[]` is corroborating provenance only and cannot replace owner qualification. Missing, truncated, reordered, ambiguous, wrong-representation, or unresolved paths fail closed. The governed computation and the selection-scope record key are distinct identities.

```text
backend_selection_decisions[]:
    backend_selection_decision_id
    backend_selection_scope_id
    decision_sequence_index
    requested_target
    selected_backend
    selected_backend_version?
    target_architecture?
    device?
    selection_policy_id?
    selection_policy_version?
    selection_tuning_id?
    selection_tuning_hash?
    predecessor_selection_decision_id?
    fallback_rule_id?
    fallback_evidence_id?
    machinery_authorization_record_ids[]?
    decision_status
```

A denied protected target followed by an authorized fallback remains two ordered decisions. The denied decision is never overwritten by the fallback.

### Fallback authority

Every fallback or replacement of an earlier candidate requires `predecessor_selection_decision_id`, `fallback_rule_id`, and `fallback_evidence_id`. The predecessor resolves to the actual earlier decision in the same selection scope, with an earlier `decision_sequence_index`; the decision chain is acyclic and preserves all denied/superseded candidates. A replacement cannot evade these requirements by describing itself as a new initial selection.

`fallback_rule_id` resolves to an accepted, versioned, content-bound `rule_records[]` entry of kind `BACKEND_FALLBACK`. `fallback_evidence_id` resolves to passing `validation_evidence[]` with `subject_kind = BACKEND_SELECTION_DECISION` and `subject_id` equal to this fallback decision's stable ID. The evidence binds the predecessor and its outcome, the original source target/qualifiers, the proposed target/version/device, the selection policy/tuning identity, applicable machinery requirements, and the active execution contracts. The rule must actually permit this target change in that context; neither a generic `ON BEST` label nor a backend-supplied rule name authorizes it.

Applicability validation completes before the fallback is applied. The evidence's `application_sequence_index` equals the fallback's `decision_sequence_index`, in the same event-order domain, and `validation_sequence_index` must precede it. Missing, stale, unknown, wrong-kind, context-mismatched, or unverifiable authority/evidence rejects the fallback rather than silently choosing another target. Even an authorized fallback still needs its own applicable machinery authorization before protected use; the denied predecessor's permissions cannot be reused as grants. Initial selection is governed by its source/selection policy, not by fabricated fallback evidence.

## Machinery authorization and use provenance

```text
machinery_authorization_records[]:
    machinery_authorization_record_id
    backend_selection_scope_id
    backend_selection_decision_id
    source_card_ids[]?
    machinery_requirement_refs[]:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        machinery_requirement_id
    required_capabilities[]
    granted_capabilities[]
    denied_capabilities[]
    capability_policy_id
    capability_policy_version
    authorization_status
    authorization_sequence_index?
```

### Canonical machinery coverage

Before accepting any machinery authorization, resolve every `machinery_requirement_refs[]` entry by the complete tuple `(representation_kind, representation_identity, owner_scope_path[], machinery_requirement_id)` to exactly one requirement in the named hash-bound representation. For a Semantic requirement, the representation is Semantic IR and the path is the ordered absolute canonical containment path from the JOB through the owning DECK and CARD as applicable. For a direct QSOL-CORE or other lower-entry requirement, the representation identifies that actual lower IR and the path is the complete representation-relative containment path from that representation's root through the real requirement owner; no JOB/DECK/CARD ancestor is fabricated.

Every ancestor needed to distinguish reused local IDs is part of the identity even when the local requirement ID happens to be unique in one document. The terminal element is the actual owner. The path is not inferred from `source_card_ids[]`, backend scope, execution subject, list position, or first-match lookup. Validate the traced requirement's representation identity, complete owner path, target selector/class, and complete capability set against that exact named representation record, not against another runtime copy. For requirements carried through lowering, validate the source/lower requirement associations and frozen mapping rules against every traversed IR hash. A map cannot silently discard a source permission or manufacture authorization. Unknown, ambiguous, mismatched, duplicate, wrong-representation, or owner-mismatched requirement references fail closed; a bare locally scoped requirement ID is never sufficient.

For an authorization record `A`, define `C(A)` as the union of the complete canonical capability sets of every uniquely resolved requirement named by `A.machinery_requirement_refs[]`. The membership, owner, representation, and target applicability of each individual requirement remain validated even when capability names or local requirement IDs overlap. Require:

```text
for each referenced requirement R:
    trace_requirement(R).required_capabilities
        = canonical_requirement(R).required_capabilities

A.required_capabilities = C(A)

for authorization_status = GRANTED:
    A.granted_capabilities = C(A)
    A.denied_capabilities = {}
```

These are exact canonical set equalities, not subset containment or agreement between shortened copies. Capability arrays have valid canonical identities, deterministic ordering, and no duplicates. Granted and denied sets are disjoint and contain only capabilities from the record's canonical required set. A record that denies or has not established every required permission may describe rejection/incomplete authorization, but it cannot authorize use. A broader environment grant is only a policy input; this contextual decision records the exact required set it actually evaluated.

Every referenced requirement must apply to this record's exact backend-selection decision, target, representation-qualified owning scope, concrete execution context where applicable, and policy context. A grant for another requirement, representation, resource, candidate, or invocation context does not count merely because it uses the same capability names. The record's selection decision must resolve to its recorded selection scope, and any retained source CARD association must agree with independently verified lineage and the validated lowering relation.

Before accepting a protected use, independently derive the **complete applicable requirement set** from the hash-bound entry representation and every traversed lowering, the actual selection decision/target, the concrete participating representation-qualified execution subjects or genuine pre-execution initiating scope, and the frozen scope/extension/lowering applicability rules. Do not derive completeness solely from the requirement IDs or authorization IDs that the producer chose to list. Every applicable Semantic JOB/DECK/CARD requirement, direct lower-operation requirement, inherited requirement, and lowered requirement must be accounted for under the actual entry/lineage path.

The union of representation-qualified requirement identities covered by the use's linked, context-compatible successful authorization records must equal that independently derived set, with no missing or unrelated requirement. For each requirement, the covering authorization must satisfy its entire canonical capability set; grants from unrelated records or contexts cannot be pooled to repair a partial decision. Several requirements sharing one capability still retain their individual identity and policy applicability. A grouping of requirements is valid only when the same context actually governs every member and the record evaluates their exact canonical union.

All of those checks, successful policy outcomes, and authorization-before-use ordering are required together before the protected boundary. An empty authorization list is valid only when the canonical applicability rules establish that no protected requirement applies, not because the runtime omitted the requirements. A canonical requirement for `{GPU, NETWORK}` is not satisfied by a runtime requirement, authorization, and use that consistently mention only `{GPU}`. Likewise, dropping a second applicable requirement entirely fails coverage even if every remaining record is internally consistent. Invalid coverage rejects authorization/use and produces structured failure; a trace of a violation must not report the use as authorized.

Protected use is independently identified:

```text
machinery_use_records[]:
    machinery_use_record_id
    backend_selection_scope_id
    backend_selection_decision_id
    backend_unit_id?
    generated_artifact_ids[]
    execution_subject_refs[]:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    source_card_ids[]?
    card_execution_ids[]?
    initiating_scope_ref?
    machinery_authorization_record_ids[]
    output_ids[]
    protected_use_start_sequence_index
    protected_use_stop_sequence_index?
```

`execution_subject_refs[]` is the canonical concrete participant relation for this protected use. For execution-governed machinery work it is nonempty and every entry uses the shared representation-qualified `execution_subject_ref`. A Semantic CARD participant resolves through `card_executions[]`; a direct QSOL-CORE participant uses `subject_kind = CORE_OPERATION` and resolves through `operation_executions[]` to its exact `operation_execution_id` in the hash-bound Core representation. Future frozen lower representations use their own explicit subject kinds. A repeated launch, retry, loop iteration, call, or repeated Core operation invocation receives the correct concrete execution refs; an event index, backend unit, local operation/CARD ID, or source summary is not this join.

`source_card_ids[]` and `card_execution_ids[]` are conditional Semantic-lineage projections. When verified Semantic CARD participants exist, these arrays agree exactly with the CARD-backed subset of `execution_subject_refs[]` and resolve through the retained lineage. On a legitimate direct Core run without Semantic lineage they are absent rather than fabricated or treated as empty substitutes for the actual Core execution subjects. A use may include both lower and retained Semantic references only when the frozen lineage/execution mapping proves that relation without double-counting one occurrence.

Every protected use executes the **final executable selection decision** for its `backend_selection_scope_id`. A selection scope with a protected use must have `final_selection_decision_id`, and the use must satisfy:

```text
machinery_use.backend_selection_decision_id
    = backend_selection_scope.final_selection_decision_id
```

The referenced decision resolves in that scope's `selection_decision_ids[]`, belongs to the same scope, and has a `decision_status` that the frozen selection contract classifies as final/executable. A denied, rejected, superseded, or merely considered predecessor cannot be the decision attached to a protected use. Every machinery authorization record used to authorize that occurrence must govern this same final decision. A generated artifact may remain truthfully attributed to an earlier rejected candidate, but such an artifact cannot appear in `machinery_use_records[].generated_artifact_ids[]` for a use governed by the final fallback decision unless an explicit frozen multi-decision execution model defines and validates that relation. No such implicit multi-decision-use model exists here.

`generated_artifact_ids[]` identifies the exact generated executable, kernel, bytecode, or equivalent artifact bytes actually launched or consumed by this protected-use occurrence. Every reference resolves to `generated_artifacts[]` and must be compatible with this use's backend-selection scope, final executable selection decision, and backend unit. The array is nonempty whenever protected use executes generated code, including a use that later fails before producing any output. It is empty only when the protected operation genuinely consumes no generated artifact. `backend_unit_id`, selection scope, output attribution, or an earlier candidate decision cannot reconstruct this identity when reference and optimized variants coexist.

`output_ids[]` identifies all outputs materially produced or exposed by this exact protected-use event. Every listed output reciprocally contains this `machinery_use_record_id` in `outputs[].machinery_use_record_ids[]`, and every output-side machinery-use reference resolves back to a use record whose `output_ids[]` contains that output. The relation is occurrence-specific: matching execution subject, backend-selection scope, generated artifact, or authorization records cannot substitute for the exact use-record join when the same protected machinery is launched more than once. A protected use that produces or exposes no output records an empty array rather than borrowing another use's output.

For genuine pre-execution RUN/DECK machinery setup only, `execution_subject_refs[]` may be empty and `initiating_scope_ref` is required instead. This is a typed `{ scope_kind, scope_id }` reference to the actual aggregate RUN or DECK_EXECUTION that initiated setup, resolving to `run_id` or `deck_execution_id`. It must not invent a CARD or Core operation execution. A direct QSOL-CORE operation performing protected work is **not** pre-execution setup and therefore must use its real Core execution subject. A use serving several execution subjects must list the actual participating subjects under the frozen lowering/execution mapping.

Authorization and use indices live in one frozen monotonic event-order domain. Every applicable successful machinery authorization satisfies:

```text
authorization_sequence_index < protected_use_start_sequence_index
```

Denied machinery has no use-start record. Correct event order does not cure incomplete canonical requirement/capability coverage or a use attached to a non-final selection decision.

## Generated artifact provenance

```text
generated_artifacts[]:
    generated_artifact_id
    artifact_kind
    artifact_hash
    backend_unit_id
    backend_selection_scope_id
    backend_selection_decision_id
    source_card_ids[]?
    optimized_ir_hash?
    optimization_record_ids[]?
    direct_producer_toolchain_invocation_id
    toolchain_invocation_chain_ids[]
    artifact_location?
```

`backend_selection_decision_id` is required and resolves to the exact decision that governed production of this artifact. That decision must belong to the recorded `backend_selection_scope_id` and match its target context. The scope's final decision is not a substitute: an artifact produced for a rejected candidate remains attributed to that candidate even when another decision ultimately executes. Artifact existence does not authorize protected use.

Generated artifacts link concrete target output to the machinery decision that produced them. When an artifact comes from optimized IR, `optimization_record_ids[]` and `optimized_ir_hash` identify the actual transformation history.

`direct_producer_toolchain_invocation_id` names the one invocation that directly emitted this artifact. `toolchain_invocation_chain_ids[]` is the ordered material ancestry of compiler/assembler/linker/code-generation invocations whose outputs contributed transitively to the artifact bytes. The chain includes the direct producer but chain membership does **not** mean that every ancestor directly emitted the final artifact.

## Toolchain invocation provenance

Run-wide compiler/tool versions are useful summaries, but they cannot identify the exact build path for one artifact when different backend units or stages use different versions, flags, targets, linkers, generated-code options, or position-sensitive argument order.

```text
toolchain_invocations[]:
    toolchain_invocation_id
    invocation_sequence_index
    invocation_kind
    tool_name
    material_tool_identity
    target_or_architecture?
    abi?
    flags[]
    argument_vector[]:
        argument_index
        argument_kind
        argument_text
        input_id?
        generated_artifact_id?
        ir_hash?
        output_generated_artifact_id?
    environment_or_config_hash?
    input_ir_hashes[]
    input_ids[]
    input_generated_artifact_ids[]?
    output_generated_artifact_ids[]
    backend_unit_id?
    backend_selection_scope_id?
```

`material_tool_identity` is immutable/versioned identity sufficient to distinguish the actual compiler, assembler, linker, code generator, or frozen equivalent used by that invocation. It may be represented by a version plus binary/content hash, immutable tool artifact ID, or another frozen identity adequate for the reproducibility claim.

`argument_vector[]` is the canonical ordered, duplicate-preserving argument sequence supplied to the identified tool after the executable itself. `argument_index` values are contiguous and strictly increasing from zero; array order must agree with those indices. `argument_text` is the exact argument token under the frozen invocation/encoding contract. Candidate `argument_kind` values distinguish ordinary flags/options/literals from immutable non-generated inputs, generated-artifact inputs, direct IR inputs, output-artifact/path arguments, separators, response-file arguments, or another frozen typed token. Repeated tokens and repeated references are legal when the actual command line repeats them.

Whenever an argument denotes a material object already identified elsewhere, its typed reference is required and must resolve to the exact same object: `input_id` for an immutable non-generated `inputs[]` dependency, `generated_artifact_id` for an input produced in this run, `ir_hash` for an IR input, and `output_generated_artifact_id` where a positional output argument names a generated artifact. The summary arrays below remain useful duplicate-free inventories/direct graph edges, but they do not reconstruct command-line order. A material command-line input occurrence missing from `argument_vector[]`, or a typed vector reference absent from/inconsistent with the corresponding inventory, fails complete build provenance.

Position-sensitive driver/linker semantics are therefore preserved. For example, `--whole-archive`, a static library, `--no-whole-archive`, and another library remain four ordered occurrences; two invocations with the same `flags[]`, `input_ids[]`, and generated-artifact input set but a different `argument_vector[]` are different material invocations. Static-library order, group delimiters, option scope, duplicate libraries, and other positional semantics may not be normalized away by sorting or set conversion.

If an implementation uses response files, wrapper scripts, a shell command, or another indirection instead of a directly represented argv, the frozen invocation contract must preserve an equivalent exact command sequence plus the immutable content identity of every material response/script/input involved. A mutable response-file path or reconstructed flag set is not equivalent. `flags[]` is summary/configuration metadata and cannot substitute for `argument_vector[]` whenever command-line ordering can affect produced bytes or symbol resolution.

`input_ir_hashes[]` is always explicit and contains the exact content hash(es) of every IR snapshot directly consumed by the invocation. It must be nonempty whenever the invocation consumes Semantic/Core/Vector-Dataflow/backend IR, including ordinary non-optimized code generation; it is empty only when that invocation consumes no IR. A generated artifact's direct producer must therefore content-bind the precise IR revision that produced its bytes. Source summaries, backend-unit identity, tool flags, target identity, transitive artifact ancestry, or a differing output hash cannot substitute for the direct IR input edge.

`input_ids[]` resolves to identified immutable `inputs[]` records for every material input not generated in this run, including prebuilt objects, static libraries, headers, startup files, sysroots, and implicit toolchain dependencies. It is empty only when no such inputs were consumed. A path, library name, search flag, or tool version is not the identity of the bytes read. A composite dependency input must content-bind the complete material dependency set through a frozen manifest representation. Missing material input identity invalidates a complete/reproducible build-provenance claim.

`input_generated_artifact_ids[]` and `output_generated_artifact_ids[]` are **direct edges** in the build graph. If invocation `link-1` consumes `obj-1` and emits `exe-1`, then `obj-1` appears in `link-1.input_generated_artifact_ids[]` and `exe-1` appears in `link-1.output_generated_artifact_ids[]`. A prebuilt library consumed by the same linker instead appears in `link-1.input_ids[]`; it must not be fabricated as an artifact generated by this run. These arrays identify graph membership, not position. Their material command-line occurrences are represented in `argument_vector[]` when the tool invocation is argv-driven.

The reciprocal direct-producer invariant is therefore narrow and exact: a generated artifact's `direct_producer_toolchain_invocation_id` must resolve to an invocation whose `output_generated_artifact_ids[]` contains that artifact. An invocation listed only in `toolchain_invocation_chain_ids[]` is not required to list the final artifact as a direct output.

For example:

```text
compile-1: source/IR -> obj-1
link-1 argv:
    0: --whole-archive
    1: obj-1              # GENERATED_ARTIFACT_INPUT -> obj-1
    2: prebuilt-lib-1     # INPUT -> prebuilt-lib-1
    3: --no-whole-archive
    4: -o
    5: exe-1              # OUTPUT_GENERATED_ARTIFACT -> exe-1

link-1.input_generated_artifact_ids = [obj-1]
link-1.input_ids = [prebuilt-lib-1]

obj-1.direct_producer_toolchain_invocation_id = compile-1
obj-1.toolchain_invocation_chain_ids = [compile-1]

exe-1.direct_producer_toolchain_invocation_id = link-1
exe-1.toolchain_invocation_chain_ids = [compile-1, link-1]
```

`compile-1.output_generated_artifact_ids[]` contains `obj-1`, not `exe-1`; `link-1.output_generated_artifact_ids[]` contains `exe-1`. `prebuilt-lib-1` resolves to its consumed immutable identity in `inputs[]`. The ordered vector preserves the exact positional semantics while the direct graph edges preserve truthful artifact ancestry.

Where every intermediate generated artifact is retained, `toolchain_invocation_chain_ids[]` must be consistent with the graph reachable through direct input/output artifact edges. If a future frozen profile permits omission of intermediate artifacts, it must define how the transitive chain remains content-bound and verifiable rather than fabricating direct-output edges.

A generated artifact cannot claim reproducible byte provenance from a run-wide compiler list or unordered flag/input inventories alone.

## Optimization provenance

```text
optimization_provenance[]:
    optimization_record_id
    source_card_ids[]
    backend_unit_id?
    reference_ir_hash
    optimized_ir_hash
    transformation_sequence[]
    legality_witnesses[]:
        legality_witness_id
        witness_kind
        validation_evidence_id
    vectorization_decisions[]?
    fusion_decisions[]?
    memory_placement_decisions[]?
    target_context_measurements[]?
    resource_model_assumptions[]?
    generated_artifact_ids[]
```

Each legality witness has a stable `legality_witness_id` and a declared `witness_kind`, such as a checked proof certificate, verified static analysis, or a contract-permitted differential check. It is not an opaque label. `validation_evidence_id` resolves to the shared content-bound evidence record, which supplies `evidence_hash`, embedded or retrievable evidence content, immutable/versioned `verifier_identity`, an accepted `OPTIMIZATION_LEGALITY` rule, and a passing outcome. The evidence's `subject_kind = OPTIMIZATION_RECORD` and `subject_id = optimization_record_id` bind it to this exact transformation record. IDs are unique in their ledger namespace; a duplicated ID cannot stand for different evidence or subjects.

The canonically hashed evaluated context includes the exact `reference_ir_hash`, `optimized_ir_hash`, ordered transformation sequence and material pass versions/options, applicable numeric contract identities and material modes, requested/effective determinism and randomness contracts, active failure-behavior identities, and all material effect, sequencing, extension, machinery, input, and target assumptions. These values or content-bound references must be available to the verifier, not merely replaced by an unexplained context hash. A witness for another IR pair, failure policy, tolerance, target, or pass sequence is invalid for this record.

The frozen legality rule defines which witness kinds and verification methods are sufficient for the requested semantic guarantee. A finite differential test does not prove a universal equivalence claim merely because it passes, and timing measurements are not legality evidence. The validator checks the witness kind against the rule and verifies the actual evidence content and subject/context binding; a self-issued `PASS` string is insufficient. Evidence must cover the complete ordered transformation, or an explicitly verified composition of all per-step witnesses with matching intermediate IRs and contracts.

An optimized variant may be constructed speculatively, but it cannot be accepted for execution or verified reuse as semantics-preserving until its required witnesses validate. That acceptance is the evidence's application event and follows validation in the shared event-order domain. Missing, failed, unavailable, or context-mismatched evidence rejects the optimized variant; executing an independently conforming reference path remains a separate recorded choice. An empty witness list is allowed only for an explicitly frozen identity/no-transformation case with identical IRs and preserved contracts, not for a changed optimized artifact.

An optimization profile is configuration, not evidence of what actually ran. The required join for an optimized result is resolvable as:

```text
output
  -> generated_artifact
      -> optimization_provenance
      -> direct toolchain producer
      -> ordered toolchain ancestry
```

`backend_unit_id` alone is not sufficient when one unit produces reference and optimized variants.

## Referenced rules and validation evidence

A rule name or a producer's success label is not evidence of permission. Contract transitions, qualifier consumption, explicit skips, verified cache substitutions, backend fallback, epistemic transitions, and optimization acceptance use shared, resolvable rule and evidence records:

```text
rule_records[]:
    rule_id
    rule_kind
    authority_kind
    authority_id
    authority_version_or_hash
    rule_content_hash
    rule_content?
    rule_location?

validation_evidence[]:
    validation_evidence_id
    rule_id
    subject_kind
    subject_id
    evaluated_context_hash
    verifier_identity
    outcome
    validation_sequence_index
    application_sequence_index?
    related_evidence_ids[]?
    evidence_hash
    evidence_content?
    evidence_location?
```

Candidate `rule_kind` values include `CONTRACT_TRANSITION`, `QUALIFIER_LOWERING`, `EFFECT_SKIP`, `CACHE_SUBSTITUTION`, `BACKEND_FALLBACK`, `FAILURE_BEHAVIOR_MAPPING`, `EPISTEMIC_TRANSITION`, and `OPTIMIZATION_LEGALITY`. `authority_kind` distinguishes a frozen source/specification authority from an execution policy. The authority ID and version/content identity must resolve to the authority actually accepted for this run; a backend cannot authorize itself by inventing a rule record. Rule content must be embedded or retrievable through a content-bound location, and its hash must verify. The rule definition includes its permitted operation, scope, and applicability conditions. A record of kind `FAILURE_BEHAVIOR_MAPPING` permits only a verified representation change, not a change in failure semantics. A `QUALIFIER_LOWERING` rule permits only the exact qualifier preservation/consumption/transformation relation its content and validated context define; it is not generic permission to drop qualifiers.

`subject_kind` defines the target namespace: `LOWERING_TRANSITION_DECISION`, `QUALIFIER_LOWERING_DECISION`, `RESULT_DETERMINISM_SCOPE`, `RANDOMNESS_SCOPE`, `FAILURE_BEHAVIOR_BINDING`, `CARD_EXECUTION`, `OPERATION_EXECUTION`, `EFFECT_NON_ATTEMPT_RECORD`, `CACHE_REUSE_RECORD`, `BACKEND_SELECTION_DECISION`, `OUTPUT`, or `OPTIMIZATION_RECORD` resolves to that ledger's stable record key. `LOWERING_TRANSITION_DECISION` resolves to the stable `transition_decision_id` on a first- or second-lowering semantic-transition record. `QUALIFIER_LOWERING_DECISION` resolves to `qualifier_lowering_decision_id`. The evidence must name the same rule as the subject's rule reference and bind the exact subject and evaluated context, not another run, invocation, contract, cache entry, target decision, output, IR pair, qualifier, or downstream execution scope. `verifier_identity` identifies the verification method and its immutable/versioned implementation.

`related_evidence_ids[]`, when present, is an ordered duplicate-free provenance relation to other validation evidence whose facts are material inputs to this subject's validation. Every referenced evidence ID resolves in the same trace closure, has independently valid rule/subject/context/content/order, and precedes the dependent evidence's application where that predecessor is required for authorization. A related evidence record never changes the dependent evidence's singular `subject_kind`/`subject_id` and cannot substitute for evidence bound directly to the dependent subject. The relation is acyclic. In particular, an execution-scope transition created by lowering uses its own subject-bound evidence and cites the applicable lowering-transition evidence through this field; it does not reuse the lowering evidence ID as though both records had one subject.

Evidence content must likewise be embedded or retrievable and hash-verifiable. It contains the evaluated context and checks needed to establish applicability; `evaluated_context_hash` binds that context canonically. An `outcome = PASS` string alone is insufficient. Validation must establish that the evidence supports the rule under the current source, policy, inputs, and execution contracts. Unknown IDs, unavailable definitions, wrong kinds, stale versions, mismatched context, and failed or unverifiable evidence fail closed.

For an applied transition, qualifier consumption/transformation, skip, cache substitution, fallback, or optimized-variant acceptance, `application_sequence_index` is required and denotes the actual subject's activation, lower-fact application, skip, substitution, selection, claim-publication, or acceptance event. It shares the frozen monotonic event-order domain with `validation_sequence_index`, which must precede it. A rejected decision has no application event. Reporting a rule or validating it after application cannot retroactively authorize behavior.

These records are provenance about operational permission and checks, not TEST/VALIDATION/PROOF research outputs and not capability grants. Referencing them never bypasses effect or protected-machinery authorization. An epistemic transition requires its specific rule's substantive research evidence in addition to the operational record that verifies it; ordinary operational authorization cannot manufacture that evidence.

## Stable execution-contract scope records

Execution scope records have type-specific stable keys distinct from the generic computation scope they govern.

```text
result_determinism_scopes[]:
    result_determinism_scope_id
    governed_scope_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
    source_card_ids[]
    requested_result_determinism
    effective_result_determinism
    transition_authorized_by?
    transition_evidence_id?
    backend_unit_id?

numeric_execution_scopes[]:
    numeric_scope_id
    governed_scope_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
    source_card_ids[]
    numeric_contract_id
    numeric_contract_hash
    material_numeric_mode
    backend_unit_id?

randomness_execution_scopes[]:
    randomness_scope_id
    governed_scope_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
    source_card_ids[]
    requested_randomness_mode
    effective_randomness_mode
    transition_authorized_by?
    transition_evidence_id?
    rng_algorithm?
    rng_version?
    seed?
    stream_id?
    parallel_partitioning?
    entropy_effect_attempt_ids[]?
    entropy_input_ids[]?
    backend_unit_id?

failure_behavior_bindings[]:
    failure_behavior_binding_id
    governed_scope_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
    transition_evidence_id?
```

All four families use the same fully qualified `governed_scope_ref` rule as backend selection. A type-specific ledger ID distinguishes records but does not establish which canonical computation the record governs. The complete path must resolve uniquely in the named representation, with the terminal segment naming the governed scope. Sibling DECKs may therefore each contain local `CARD 7` while their execution contracts remain distinct. `source_card_ids[]` is summary provenance only. Missing, truncated, reordered, ambiguous, wrong-representation, or owner-mismatched paths fail validation.

Output references resolve directly to `result_determinism_scope_id`, `numeric_scope_id`, `randomness_scope_id`, and `failure_behavior_binding_id`. They never infer those records from a local computation ID or source CARD summary.

Whenever requested and effective result-determinism or randomness contracts differ, both `transition_authorized_by` and `transition_evidence_id` are required. The former resolves to `rule_records[].rule_id` of kind `CONTRACT_TRANSITION`; the latter resolves to `validation_evidence[].validation_evidence_id` for that exact execution-scope record. Evidence binds the requested/effective contracts, accepted source/policy authority, and governing numeric/randomness context, and must establish authorization before the effective contract is activated or used. A missing, unknown, inapplicable, or post-execution authority is an unauthorized transition and fails closed. The optional notation permits absence only when no transition occurred; it does not permit an undocumented downgrade. When the transition originates in a lowering decision, this execution-scope evidence is distinct from the lowering evidence and must include the applicable lowering `transition_evidence_id` value(s) in `related_evidence_ids[]`; preserving authority does not mean reusing an evidence ID across subjects.

### Seeded randomness replay identity

For every `randomness_execution_scopes[]` record with `effective_randomness_mode = SEEDED`, `rng_algorithm`, `rng_version`, `seed`, and `stream_id` are mandatory, nonempty material replay identities. They identify the exact generator family/algorithm, immutable or versioned generator semantics, seed value, and logical stream used by that governed scope. An implementation default, package default, algorithm family name without versioned semantics, or a mode label by itself is not enough to reproduce the stream.

`parallel_partitioning` is additionally mandatory whenever partitioning, lane/thread assignment, substream derivation, counter/key allocation, chunking, work distribution, or another parallel rule can change which random values the governed computation consumes. The value must identify the frozen mapping strongly enough to reconstruct the same stream assignment. It may be absent only when the applicable RNG/execution contract proves partitioning cannot affect the generated or consumed sequence. Missing required SEEDED identity makes the replay claim invalid and fails reproducibility validation rather than falling back to implementation defaults.

### Failure-policy transitions

The requested and effective failure-behavior IDs resolve to immutable/versioned behavior definitions, including the applicable default fail-stop contract. They may not be free labels whose meaning changes in place. A source/effective difference must be classified by actual semantics, not merely by whether the strings differ.

For a representation-only difference, `mapping_or_transition_rule_id` is required and resolves to an accepted content-bound rule of kind `FAILURE_BEHAVIOR_MAPPING` that establishes preservation of the exact requested/effective behavior, scope, propagation, and ordering. A frozen identity-reconstruction exception may omit redundant representation mapping only when it proves that same correspondence. Calling continue, retry, compensation, or a changed propagation boundary a representation change is invalid.

Any semantic change requires both `mapping_or_transition_rule_id` of kind `CONTRACT_TRANSITION` and `transition_evidence_id` identifying passing evidence for `subject_kind = FAILURE_BEHAVIOR_BINDING` and this exact `failure_behavior_binding_id`. The rule and evidence bind the requested/effective behavior definitions, owning and applicable concrete execution scopes, accepted source/policy authority, and material dependencies, ordering, effects, and execution contracts. They must establish permission for that exact behavior change before the effective policy is activated or applied to a failure. This includes a fail-stop request changed into continue, retry, or compensation. When the binding is the result of a semantic-changing lowering, its evidence additionally cites the applicable lowering-transition evidence in `related_evidence_ids[]`; the lowering and binding retain distinct evidence IDs because they are distinct subjects.

No accepted frozen rule, no semantic transition. Missing, stale, ambiguous, self-authorized, context-mismatched, unverifiable, or late evidence rejects the change and invokes the applicable unchanged rejection/fail-stop contract. An unauthorized effective policy cannot authorize its own acceptance or its rejection handling. Representation-only rules cannot substitute for semantic-transition authority, and recording a later successful continuation is not proof that continuation was permitted. Both lowering boundaries and all policy references on outputs/failures preserve this distinction and the required evidence.

### External-entropy attribution

When `effective_randomness_mode = EXTERNAL-ENTROPY`, the randomness scope must identify the exact protected `RANDOM` acquisition attempt or attempts that supplied entropy through `entropy_effect_attempt_ids[]`. Each referenced attempt must resolve to the ordinary effect authorization/attempt ledger and therefore prove authorization completed before acquisition began.

Where the acquired entropy becomes a material runtime input, `entropy_input_ids[]` identifies the immutable input record(s), such as a canonical captured value, content hash, immutable artifact identity, or another frozen identity sufficient to distinguish what was actually consumed. The referenced input's `effect_attempt_ids[]` and the acquisition attempt's `acquired_input_ids[]` must agree with this entropy attribution, and its concrete consumers remain identified even if they fail without producing outputs. If raw entropy is intentionally not retained, a frozen audit identity may establish what acquisition was used, but the manifest must not claim byte-for-byte replayability unless the consumed entropy value is actually reconstructable.

The randomness mode itself never authorizes entropy access and never substitutes for the protected `RANDOM` effect attempt.

A single execution-wide scope record is valid only when a frozen normalization proves it faithfully represents every governed source requirement.

## Execution trace

Potential fields include:

```text
run_id
job_id?
deck_executions[]?
card_executions[]?
operation_executions[]
control_decisions[]
failure_records[]
execution_status
job_status?
runtime_compiler_versions[]
backend_selection_scopes[]
backend_selection_decisions[]
machinery_requirements[]
machinery_authorization_records[]
machinery_use_records[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
failure_behavior_bindings[]
rule_records[]
validation_evidence[]
inputs[]
required_capabilities[]
granted_capabilities[]
denied_capabilities[]
capability_policy_id
capability_policy_version
capabilities_used[]
resolved_extensions[]
effect_requirements[]
effect_authorization_records[]
effect_attempts[]
effect_non_attempt_records[]
cache_reuse_records[]
external_tool_versions[]
generated_artifacts[]
toolchain_invocations[]
start_stop_metadata?
```

Execution-wide capability arrays and `runtime_compiler_versions[]` are summaries only. Contextual authorization records prove per-boundary authorization, and `toolchain_invocations[]` plus generated-artifact direct/ancestry links prove the exact artifact-producing build graph and, where command-line ordering is material, the exact ordered invocation argument vector. `job_id`, DECK/CARD ledgers, and Semantic CARD lineage are conditional on actual retained Semantic execution structure; direct Core entry does not synthesize them.

## DECK, CARD, and lower-operation execution ledgers

Every selected DECK remains identified even when fail-stop prevents it from starting when Semantic execution structure exists:

```text
deck_executions[]:
    deck_execution_id
    deck_id
    deck_status
    card_execution_ids[]
    execution_order_index?
    governing_failure_record_id?
    failure_record_id?
```

`governing_failure_record_id?` identifies an earlier concrete failure whose active policy prevented this selected DECK from starting or otherwise blocked it. For a DECK marked non-started/skipped because of prior fail-stop, this field is required and must resolve to the actual blocking failure plus applicable failure-behavior binding. `failure_record_id?` has a different meaning: it identifies a failure caused by this DECK execution itself. The two fields are not aliases and causal ordering must be validated rather than inferred from list position.

Every Semantic CARD execution is a distinct runtime object:

```text
card_executions[]:
    card_execution_id
    deck_execution_id
    card_id
    card_status
    input_ids[]
    cache_reuse_record_ids[]?
    execution_order_index?
    governing_control_decision_id?
    governing_failure_record_id?
    governing_skip_rule_id?
    skip_verification_evidence_id?
    failure_record_id?
```

Canonical `card_id` identifies the semantic CARD. `card_execution_id` identifies one concrete execution of that CARD. The distinction matters for loops, retries, calls, repeated DECK execution, or any future construct that can execute one canonical CARD more than once.

`input_ids[]` identifies all and only the material inputs actually consumed by this invocation under the frozen operation/provenance contract, with reciprocal `inputs[].consumer_execution_refs[]` and, when Semantic lineage is retained, `inputs[].consumer_card_execution_ids[]` links. A failed or output-free invocation still records the inputs it consumed; an unstarted invocation must not claim inputs merely available to its DECK. `cache_reuse_record_ids[]` is required whenever a runtime cache classification record concerns this invocation and is reciprocal with that record's `execution_subject_refs[]` plus conditional `card_execution_ids[]`. Neither relation is inferred from canonical CARD identity or the order of output arrays.

A legitimate execution that enters at QSOL-CORE or another frozen lower representation without Semantic CARD lineage uses an identified operation ledger instead of fabricating `card_executions[]`:

```text
operation_executions[]:
    operation_execution_id
    operation_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        operation_id
    operation_kind
    operation_status
    input_ids[]
    cache_reuse_record_ids[]?
    execution_order_index?
    governing_control_decision_id?
    governing_failure_record_id?
    governing_skip_rule_id?
    skip_verification_evidence_id?
    failure_record_id?
    source_card_ids[]?
    source_card_execution_ids[]?
```

`operation_ref` resolves to exactly one operation in the named content-bound representation. For direct QSOL-CORE entry, `representation_kind = QSOL_CORE` and `representation_identity = core_ir_hash`; the owner path contains the complete Core containment path needed to disambiguate local operation IDs. `operation_execution_id` identifies one concrete runtime invocation of that lower operation. `source_card_ids[]` / `source_card_execution_ids[]` are optional lineage only: if present they must be verifiable through an actually traversed lowering/lineage chain; if no Semantic lineage exists they are absent. Lower-entry execution must never manufacture a CARD or CARD execution merely to satisfy a projection.

`input_ids[]` and `cache_reuse_record_ids[]` are direct occurrence-level relations for this lower invocation. Inputs reciprocate through `inputs[].consumer_execution_refs[]`; runtime cache records reciprocate through their representation-qualified `execution_subject_refs[]`. A failed or output-free Core operation therefore retains both what it consumed and whether it executed cold or was satisfied under an applicable cache-substitution decision.

`failure_record_id?` identifies a failure **caused by this operation execution** and is required for a failed operation outcome. It must not be overloaded as the cause of an operation that never ran. Non-reach/path status uses the typed governing fields instead:

- an untaken branch requires `governing_control_decision_id` resolving to the concrete controlling decision for this `operation_execution_id`;
- prior fail-stop or another failure-caused block requires `governing_failure_record_id` resolving to the actual earlier failure whose active failure-behavior binding prevents this operation;
- an explicit frozen skip requires both `governing_skip_rule_id` and `skip_verification_evidence_id`, with evidence bound to `subject_kind = OPERATION_EXECUTION` and this exact `operation_execution_id` before the skip is applied;
- a general NOT_REACHED / SUBJECT_NOT_REACHED / frozen equivalent requires one of those same validated cause forms and has no cause-free success path.

A lower-operation record whose status says untaken, blocked, not reached, or explicitly skipped but omits/inconsistently combines the applicable typed cause fields is invalid. A control decision from another iteration, a handled failure that does not block this subject, a stale skip rule, or post-skip validation does not establish causality. These checks use the shared [Required causes for non-reach](#required-causes-for-non-reach) contract.

The canonical reusable runtime subject reference is:

```text
execution_subject_ref:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
    subject_kind
    subject_id
    execution_id
```

For Semantic CARD execution, `subject_kind = CARD`, `subject_id = card_id`, and `execution_id = card_execution_id`; the reference resolves through `card_executions[]` and the hash-bound Semantic containment path. For direct Core execution, `subject_kind = CORE_OPERATION`, `subject_id = operation_id`, and `execution_id = operation_execution_id`; the reference resolves through `operation_executions[]`. Future frozen lower representations use their own explicit subject kinds under the same representation-qualified rule. Local IDs, matching names, or a source-CARD summary do not identify a runtime subject without the representation and complete owner path.

`failure_record_id` is required for a failed CARD, DECK, or operation execution outcome and resolves to the exact failure record governing that outcome, directly or through an explicitly frozen and validated propagation relation. Equal failure classes/stages do not identify a failure event. A blocked/not-started subject instead uses its governing cause and must not fabricate a failure caused by that subject. Summary failure labels, when retained, must agree with the referenced record and cannot replace it.

Membership in `card_ids[]` is not proof that a CARD ran. An explicitly skipped CARD uses the rule/evidence requirements in [Effect non-attempt records](#effect-non-attempt-records), with evidence bound to its `CARD_EXECUTION` subject. Skipping the parent CARD cannot evade the accounting and rule validation for its effects. Lower-entry operation execution uses the corresponding `OPERATION_EXECUTION` subject and does not fabricate Semantic membership; its own skip/non-reach status is validated by the typed cause fields above.

## Typed execution-path causality and failures

Control decisions and failures have distinct identified namespaces:

```text
control_decisions[]:
    control_decision_id
    card_execution_id?
    operation_execution_id?
    control_kind
    decision
    sequence_index?
    backend_detail?

failure_records[]:
    failure_record_id
    failing_scope_kind
    failing_scope_id
    failure_behavior_binding_ids[]
    result_determinism_scope_ids[]
    numeric_scope_ids[]
    randomness_scope_ids[]
    failure_class
    failure_stage
    failure_card_id?
    failure_card_execution_id?
    operation_execution_id?
    deck_execution_id?
    sequence_index?
    backend_detail?
```

`failing_scope_kind` plus `failing_scope_id` is the always-present typed identity of the scope where the failure occurred. Frozen scope kinds may include JOB, DECK_EXECUTION, CARD_EXECUTION, CORE_OPERATION_EXECUTION, BACKEND_SELECTION_SCOPE, LOWERING, or another explicitly specified execution scope.

`failure_behavior_binding_ids[]` is required and resolves to the exact `failure_behavior_bindings[]` records governing this failure and its propagation or handling. It includes the applicable frozen default fail-stop binding, not just explicit recovery policies. When several policies or transitions concern one computation, the failure references those actually active at that event; it must not infer policy from the resulting path or a generic scope ID. A rejected requested policy is not an effective handling policy. Pre-CARD/lower-entry rejection records retain the applicable setup/rejection-handling binding without inventing a CARD culprit. Missing or incompatible governing bindings make the failure trace incomplete.

Each failure record also carries the complete applicable `result_determinism_scope_ids[]`, `numeric_scope_ids[]`, and `randomness_scope_ids[]`. Derive those sets independently from the typed failing scope, the concrete execution subject where applicable, and the validated lowering/contract mappings, then require the recorded arrays to equal the complete applicable ledger sets. An empty array is valid only when no execution-contract scope in that family governs the failure. A producer may not omit a stricter parent scope, a material numeric mode, or the RNG contract merely because no output was published. Every referenced scope ID resolves to the retained type-specific execution-contract ledger.

`failure_card_id` remains the canonical source-CARD identity **when a CARD's unhandled failure caused the record**. `failure_card_execution_id` identifies the corresponding concrete runtime CARD execution. For a CARD-caused failure, both are required and must resolve consistently through `card_executions[]`.

A failure that occurs before any CARD execution or in a legitimate lower-entry operation with no Semantic CARD lineage must not invent a CARD identity. The typed failing scope and, where applicable, `operation_execution_id` are authoritative; `failure_card_id` / `failure_card_execution_id` are absent unless verified Semantic lineage establishes that a CARD execution actually caused the failure.

An untaken branch references `governing_control_decision_id`. Prior fail-stop or another failure-caused non-reach references `governing_failure_record_id`. A catch-all control-or-failure ID is invalid because it erases the target namespace.

### Required causes for non-reach

Every legitimate not-reached execution subject or effect non-attempt must have a cause that actually prevents this concrete invocation under the frozen control/failure semantics. The reason selects the required typed cause:

- untaken branch requires `governing_control_decision_id` resolving to the concrete controlling decision;
- prior fail-stop or other failure-caused non-reach requires `governing_failure_record_id` resolving to the concrete failure whose active policy blocks this invocation;
- explicit frozen skip requires both `governing_skip_rule_id` and `skip_verification_evidence_id` under the skip contract;
- `SUBJECT_NOT_REACHED`, `CARD_NOT_REACHED`, `OPERATION_NOT_REACHED`, or a general equivalent requires one of those same validated cause forms. It has no cause-free exception.

These fields are present directly on both `card_executions[]` and `operation_executions[]` as applicable, and on `effect_non_attempt_records[]` for the effect-accounting projection. `failure_record_id` on a CARD/operation execution is never a substitute because it identifies a failure caused by that execution, not the earlier cause preventing it from running.

The cause must resolve in this run and be applicable to the exact execution subject and effect declaration being accounted for. Validate its control/dependency relation and causal ordering; an unrelated failure, a decision from another loop iteration, a handled failure whose policy permits continuation, or merely the existence of a record with that ID cannot establish non-reach. A cause inherited from an enclosing scope must retain a resolvable, validated path to that enclosing cause. Reject unresolved, circular, contradictory, or unsupported cause chains. Multiple cause fields must agree under a frozen composition rule, not allow a producer to choose whichever label hides an omission.

For a verified skip cause, the evidence is subject-bound to the affected execution subject or non-attempt record as appropriate. A parent's skip evidence alone cannot stand in for required effect accounting. For control/failure causes, any context or ordering evidence needed to validate that cause is required despite optional inventory notation; inability to establish causality fails closed. Missing or unverifiable causes produce structured execution/conformance failure, never successful accounting for an omitted reachable effect.

## Inputs

```text
inputs[]:
    input_id
    input_kind
    canonical_value?
    content_hash?
    artifact_id_or_version?
    location?
    media_or_schema_type?
    source_card_ids[]?
    consumer_execution_refs[]
    consumer_card_execution_ids[]?
    consumer_scope_refs[]?
    effect_attempt_ids[]
```

Every material input requires a stable `input_id` plus a canonical value or immutable content/artifact identity sufficient to identify what was actually consumed. Paths, URLs, dataset names, and model names are retrieval context, not immutable identity by themselves.

`consumer_execution_refs[]` contains the exact concrete runtime subjects that consumed this identified input. Each entry uses the shared representation-qualified `execution_subject_ref` and resolves to `card_executions[]` or `operation_executions[]` as applicable. The relation remains mandatory for a consumer that fails, produces no output, or has a later retry. `consumer_card_execution_ids[]`, when present, is the exact Semantic-lineage projection of the CARD-backed subset and must agree with those refs; it is absent or empty on a direct Core run with no CARD consumers. A canonical `source_card_ids[]` summary, when present, must agree with verified lineage and does not replace runtime subject identity.

`effect_attempt_ids[]` identifies the concrete effect acquisition(s) that supplied the captured input, such as a file read, clock sample, network response, or external-entropy acquisition. It is nonempty for effect-acquired input and empty only when no effect acquisition supplied that input. Each referenced attempt resolves to its declaration, execution subject, authorization, and completion/ordering evidence, and reciprocally lists this input in `acquired_input_ids[]`. The frozen operation contract must establish that the attempt supplied these exact captured bytes/value. A denied or `NOT_STARTED` attempt cannot supply a captured input. A failed/partial attempt may supply only the material actually acquired and permitted by the failure contract; do not invent a capture for an attempt that supplied nothing.

Acquisition and consumption are different roles: the acquiring execution subject may differ from the subjects that later consume the input. Both relations must remain explicit. Independent acquisitions retain distinct capture identities even when their content hashes happen to match, unless a frozen representation preserves the full occurrence-to-consumer relation without loss. A single captured immutable value may legitimately have several identified consumers. Matching paths, canonical CARD IDs, operation IDs, or equal bytes alone cannot assign captures to iterations.

Inputs with no operation/CARD consumer must not fabricate one. Build-only inputs retain their actual consuming `toolchain_invocations[].input_ids[]` relations. Genuine run/DECK setup instead requires `consumer_scope_refs[]`, each a typed `{ scope_kind, scope_id }` reference to the actual RUN or DECK_EXECUTION (`run_id` or `deck_execution_id`) that consumed the input. These non-operation relations do not waive concrete execution-subject references when an operation/CARD consumption also occurs.

Input, consumer, and acquisition IDs are duplicate-free and resolve within the same run/reference closure. Validate the actual consumption/acquisition relation and its causal ordering under the frozen operation contract, not only the existence of named IDs. Output `input_ids[]` may describe transitive material dependencies; that output relation does not replace the direct-consumer ledger. Failure traces retain consumed inputs and their consumer/acquisition closure even if no output references them. Missing, swapped, ambiguous, wrong-run, or unverifiable attribution fails provenance validation rather than guessing which read or retry used a value.

## Effect authorization

Every protected effect attempt has a contextual authorization decision:

```text
effect_authorization_records[]:
    effect_authorization_record_id
    effect_attempt_id
    effect_requirement_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        declared_effect_id
    execution_subject_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    card_id?
    card_execution_id?
    required_capabilities[]
    granted_capabilities[]
    denied_capabilities[]
    capability_policy_id
    capability_policy_version
    authorization_status
    authorization_sequence_index?
```

### Declaration-bound authorization validation

Before accepting authorization, resolve `effect_requirement_ref` by its complete tuple `(representation_kind, representation_identity, owner_scope_path[], declared_effect_id)` to exactly one effect declaration in the named hash-bound representation. Then resolve `execution_subject_ref` to the exact concrete execution in that same run and verify that the frozen representation/execution model makes that subject the owner or invoking context for the declaration. For a Semantic CARD-backed attempt, the subject resolves through `card_executions[]`, the owner path terminates at that CARD, and `card_id` / `card_execution_id` are required and agree exactly. For a direct QSOL-CORE attempt, the subject resolves through `operation_executions[]` to the hash-bound Core operation and `card_id` / `card_execution_id` are absent unless verified Semantic lineage is actually retained. A lookup by only `declared_effect_id`, local CARD/operation ID, or their pair is invalid because local IDs may repeat across owners.

The traced `effect_requirements[]` entry must carry the same representation identity and complete owner path and match that declaration. Missing, truncated, reordered, ambiguous, wrong-representation, wrong-execution, or owner-mismatched references fail closed before capability comparison. Then require:

```text
canonical_declaration.required_capabilities
    = trace_declaration.required_capabilities
    = effect_attempt.required_capabilities
    = effect_authorization.required_capabilities
```

This is exact equality of complete canonical capability sets, not subset containment, list-prefix equality, or agreement between runtime copies alone. Sets use canonical capability identities with deterministic ordering; duplicate or invalid entries fail validation rather than hiding missing capabilities. A runtime record cannot remove an extension-required capability, replace the set by a CARD/operation-wide union, or choose a weaker declaration.

The declaration, attempt, and authorization must agree on the complete `effect_requirement_ref`; the attempt's effect kind must match the declaration. Authorization and attempt must agree on the complete `execution_subject_ref` and have reciprocal attempt/authorization IDs. A record for another effect, retry, operation execution, or CARD invocation cannot authorize this attempt. Conditional CARD fields, when present, must resolve as verified lineage from that subject and are never independent authority.

For successful authorization, every member of the canonical required set is granted, none is denied, the granted/denied sets are disjoint, and the contextual policy and successful status are valid for that exact attempt. Both the complete-set checks and the same-domain authorization-before-begin checks are required before the protected boundary. Any mismatch, unresolved declaration, missing grant, fabricated lineage, or invalid decision fails closed. For example, copying only `AI_MODEL` into both runtime records when the declaration requires `{AI_MODEL, NETWORK}` is rejected even if the copied subset is fully granted and its authorization precedes effect begin.

## Effect attempts

```text
effect_attempts[]:
    effect_attempt_id
    effect_requirement_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        declared_effect_id
    execution_subject_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    card_id?
    card_execution_id?
    effect_kind
    required_capabilities[]
    effect_authorization_record_id
    sequence_index
    effect_begin_sequence_index?
    effect_end_sequence_index?
    completion_state
    backend_detail?
    acquired_input_ids[]
    observable_output_ids[]
    external_tool_ids[]
```

`effect_requirement_ref` identifies the exact declared protected effect in the representation that actually owns it. `execution_subject_ref` identifies the concrete runtime invocation in which the attempt occurred. Semantic CARD attempts require the matching conditional CARD fields; direct Core operation attempts do not. Attempts from different retries, loop iterations, calls, or repeated lower-operation executions must never collapse merely because they share one local CARD/operation/effect ID.

`acquired_input_ids[]` identifies the captured material input records actually supplied by this acquisition attempt and is reciprocal with `inputs[].effect_attempt_ids[]`. It is empty for an attempt that acquired no material input. It is independent of `observable_output_ids[]`: a read may supply an input to an execution subject that later fails without publishing any output. See the [input consumer and acquisition rules](#inputs).

Authorization and effect-begin indices share one frozen monotonic event-order domain. Every protected attempt whose completion state is `COMPLETED`, `ABORTED_CLEAN`, `PARTIAL`, or `UNKNOWN` represents an effect that began under the five-state model. For every such begun attempt, `effect_begin_sequence_index` is mandatory; the linked authorization record must have `authorization_status = GRANTED`, must carry `authorization_sequence_index`, and must satisfy:

```text
authorization_sequence_index < effect_begin_sequence_index
```

The `?` notation on the begin and authorization indices permits absence only where the protected effect did not begin, principally `NOT_STARTED`/denied authorization. A producer cannot mark an attempt as begun/completed/partial/unknown and omit the shared-order evidence. Generic attempt `sequence_index` is not authorization-order proof. A preceding authorization whose required set disagrees with the canonical declaration is still invalid.

### Effect completion states

The candidate states are mutually exclusive:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

For `completion_state = NOT_STARTED`, no protected effect began. `effect_begin_sequence_index` and `effect_end_sequence_index` are absent, and both `acquired_input_ids[]` and `observable_output_ids[]` are empty. `external_tool_ids[]` is also empty because no material external-tool invocation can be attributed to an effect attempt that never began. An output MUST NOT reciprocally reference a `NOT_STARTED` attempt through `outputs[].effect_attempt_ids[]`; such a trace is contradictory and fails closed.

Known completion takes precedence over uncertainty about broader external consequences. Completion belongs to the effect attempt, not to the enclosing CARD/lower-operation outcome.

## Effect non-attempt records

A declared effect may legitimately have no runtime attempt for a particular concrete execution subject when control flow, prior failure, or another frozen rule prevents the effect from being attempted.

```text
effect_non_attempt_records[]:
    effect_non_attempt_record_id
    effect_requirement_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        declared_effect_id
    execution_subject_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    card_id?
    card_execution_id?
    effect_kind
    non_attempt_reason
    governing_control_decision_id?
    governing_failure_record_id?
    governing_skip_rule_id?
    skip_verification_evidence_id?
    backend_detail?
```

The stable `effect_non_attempt_record_id` distinguishes separate non-attempt facts even when the same declaration is encountered more than once. `execution_subject_ref` binds each non-attempt to the exact runtime invocation/path being accounted for. Conditional CARD fields are Semantic-lineage projections only.

Candidate legitimate reasons include untaken branch, prior fail-stop, subject not reached, and explicit frozen skip, but every such record must satisfy [Required causes for non-reach](#required-causes-for-non-reach). Untaken control flow resolves to a `control_decision_id`; failure-caused non-reach resolves to a `failure_record_id`; a general not-reached reason requires a validated typed control/failure cause or a verified frozen skip. The generic reason alone is never sufficient.

An explicit frozen skip requires both `governing_skip_rule_id` and `skip_verification_evidence_id`. They resolve to a `rule_records[]` entry of kind `EFFECT_SKIP` and passing `validation_evidence[]` for this exact non-attempt record, declaration, execution subject, and active policy context. The rule must explicitly permit this skip and its applicability must be verified before the skip is applied. Optional control/failure references, a free-text reason, or a rule valid only for another invocation cannot substitute for these records. An unknown, missing, inapplicable, or unverifiable skip rule forces structured conformance failure; a reachable required effect omitted without a valid skip rule is a backend omission, not success.

`BACKEND_OMISSION_DETECTED` or frozen equivalent means a reachable required effect was omitted. It forces structured execution/conformance failure and cannot coexist with successful enclosing execution.

### Unconditional declaration accounting

Declaration completeness is not an optional audit mode.

For every selected concrete `execution_subject_ref`, every applicable effect declaration owned by that subject or its governed scope must resolve to exactly one of these provenance outcomes:

1. one or more identified `effect_attempts[]` records for that execution subject when execution/retry semantics produce attempts;
2. exactly one identified legitimate `effect_non_attempt_records[]` record for that execution subject when no attempt occurred; or
3. a structured execution/conformance failure if complete accounting itself cannot be established or a reachable required effect was omitted.

A declared effect with neither an attempt nor a legitimate non-attempt record is always incomplete provenance and fails closed. Profiles, backends, optimization modes, deployment settings, entry representation, or audit settings may not disable this requirement.

## External-tool provenance

```text
external_tool_versions[]:
    external_tool_id
    tool_kind
    tool_name_or_service
    material_identity_status
    material_identity_kind?
    material_identity_value?
    endpoint_or_location?
    source_card_ids[]?
    effect_attempt_ids[]
    output_ids[]
```

For a material external tool, service, model, prover, process, or instrument, `tool_name_or_service` and a mutable endpoint are labels/locators only. `material_identity_status = IDENTIFIED` requires an immutable or versioned `material_identity_value`, such as an executable/content hash, tool version bound strongly enough for the active claim, model/version ID, immutable artifact ID, or frozen equivalent.

If exact material identity cannot be established, record `material_identity_status = UNAVAILABLE` (or a frozen equivalent) and the strongest replay/evidence claim must be weakened or rejected according to the frozen policy. Identity unavailability may never be silently treated as full reproducibility.

Every material external-tool record has explicit `effect_attempt_ids[]` and `output_ids[]` arrays, with at least one concrete subject across the two arrays. Each referenced effect attempt reciprocally lists the tool in `effect_attempts[].external_tool_ids[]`; each referenced output reciprocally lists it in `outputs[].external_tool_ids[]`. Conversely, every attempt/output external-tool reference resolves to a tool record that names that exact subject. A canonical `source_card_ids[]` summary, shared endpoint, equal tool name, or repeated material identity cannot reconstruct this occurrence-level relation across retries. A material tool with no concrete attempt or output subject is incomplete provenance and fails closed rather than floating at CARD scope.

Extension resolution identifies the adapter/profile contract. It does not substitute for the actual tool, service, model, prover, process, or instrument identity.

## Cache reuse provenance

```text
cache_reuse_records[]:
    cache_reuse_record_id
    classification
    execution_subject_refs[]:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    source_card_ids[]?
    card_execution_ids[]?
    reused_computation_id?
    cache_key_hash?
    cached_artifact_hash?
    cached_output_id?
    cache_producer_run_id?
    legality_rule_id?
    verification_evidence_id?
    material_cache_identity_hash
```

Candidate classifications are `COLD_EXECUTION`, `VERIFIED_REUSE`, and `UNVERIFIED_HIT`, or frozen equivalents.

`execution_subject_refs[]` is the canonical **current-run** runtime-subject relation for cache lookup, cold execution classification, or substitution. It is nonempty for every runtime cache record. Semantic CARD subjects resolve through `card_executions[]`; direct QSOL-CORE and other frozen lower-entry subjects resolve through `operation_executions[]` to the exact `operation_execution_id`. A cache record must never fabricate Semantic CARD ancestry merely because the same canonical computation once had such lineage.

`source_card_ids[]` and `card_execution_ids[]` are conditional Semantic-lineage projections of the CARD-backed subset of `execution_subject_refs[]`. When present they agree exactly with those refs and the retained lineage; on a legitimate lower-entry runtime subject without Semantic lineage they are absent. Every runtime CARD subject reciprocally lists this record in `card_executions[].cache_reuse_record_ids[]`; every lower-operation subject reciprocally lists it in `operation_executions[].cache_reuse_record_ids[]`. Canonical CARD/operation IDs, output-array position, or historical producer identity cannot substitute for these current execution joins.

One concrete invocation executing cold and another using the cache require distinct records linked to their respective execution subjects, even when they represent the same canonical CARD or Core operation. A grouped record may list several execution subjects only when its classification, cached material, and verified rule/evidence apply to every listed current invocation. Otherwise split the records. Whole-subject cold execution and whole-subject substitution cannot both be claimed for the same `execution_subject_ref`; a future partial/region reuse contract must represent typed subsubjects explicitly rather than overloading these whole-execution records.

For `VERIFIED_REUSE`, `legality_rule_id` and `verification_evidence_id` are mandatory. They resolve to a `rule_records[]` entry of kind `CACHE_SUBSTITUTION` and passing, content-bound `validation_evidence[]` for this exact cache-reuse record. The record must identify the reused computation/artifact and the checked cache key/artifact content, either directly through the corresponding hash fields or through resolvable immutable cached-output/producer provenance. Evidence verifies the material cache identity and substitution legality against the exact current `execution_subject_refs[]`, their consumed inputs, contracts, entry/lowering identity, and execution context before substitution is applied. The evidence's evaluated context includes that complete invocation set; changing the set invalidates the evidence. A matching hash or a producer's `VERIFIED_REUSE` label alone is not verification evidence.

Ordinary result substitution is effect-free by default. Effectful reuse additionally requires that the referenced rule is the separately frozen replay/cache semantic covering this operation's declared effects, contextual authorization, ordering, failure, attempt provenance, output attribution, and external state behavior. Validate that rule against the attempt/non-attempt/authorization accounting for each exact current `execution_subject_ref` to which the cache contract applies; accounting for another retry, another lower-operation invocation, or the historical cache producer cannot discharge the current subject's effects. A generic cache rule does not permit effectful substitution.

An `UNVERIFIED_HIT` remains diagnostic and cannot satisfy an execution subject or produce a verified-reuse output. It must undergo successful verification before reuse, trigger cold execution, or fail closed. Missing, stale, mismatched, failed, or unavailable verification evidence invalidates `VERIFIED_REUSE`; optional notation for other classifications never waives its conditions. A diagnostic hit and the actual cold/reuse outcome remain distinguishable records or an explicitly frozen validated state transition, not contradictory applied outcomes.

A build-only cache operation or diagnostic with no runtime CARD/lower-operation subject may have an empty `execution_subject_refs[]` only when the applicable build/diagnostic provenance identifies its actual non-runtime subject in the retained trace closure. Such a record cannot satisfy a runtime execution subject, waive its effect accounting, or be cited as evidence of runtime substitution. Never invent an execution subject for a build-only operation, and never use this exception to omit an actual runtime consumer.

Output cache references are validated through the reuse record's concrete execution-subject links and the frozen producer/dependency relation to that output. Each output lists only records that materially contributed to it. Unknown, wrong-run, mismatched canonical/concrete, contradictory, or unverifiable substitution subjects fail closed. This join remains available even without an output because both CARD and lower-operation execution ledgers reciprocally reference their cache records.

Verified cache reuse does not prove cold reconstructability.

## Result trace

Results are identified records rather than bare hashes plus one shared semantic class.

```text
outputs[]:
    output_id
    result_binding_ref?:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        binding_id
    artifact_hash
    artifact_location?
    semantic_class
    status
    producer_execution_refs[]:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    producer_card_ids[]?
    producer_card_execution_ids[]?
    input_ids[]
    effect_attempt_ids[]?
    external_tool_ids[]
    backend_selection_scope_ids[]
    machinery_use_record_ids[]
    generated_artifact_ids[]?
    result_determinism_scope_ids[]
    numeric_scope_ids[]
    randomness_scope_ids[]
    failure_behavior_binding_ids[]
    cache_reuse_record_ids[]?
    evidence_status?
```

`result_binding_ref?`, when present, identifies exactly one named result binding by `(representation_kind, representation_identity, owner_scope_path[], binding_id)`. `representation_identity` is the content-bound identity of the named Semantic/Core/Vector-Dataflow representation, normally its IR hash. The complete ordered owner path terminates at the binding-defining scope and includes every ancestor needed to distinguish reused local names. If the output is attributed to producers or bindings in another representation, the applicable `result_binding_map[]` chain must connect those qualified endpoints to this exact referenced binding. After a legal fusion, the output may name the fused lower binding; it must not choose one source `v0` by scalar text, producer-array position, or first match. Omit the field only when the output genuinely has no result-binding identity. Missing representation identity, truncated/ambiguous owner paths, unresolved bindings, or an absent required mapping chain fail provenance validation.

`producer_execution_refs[]` is the canonical nonempty producer relation. Each entry is a shared `execution_subject_ref` identifying the concrete runtime subject that actually produced, materially supplied, or published the output. A Semantic producer resolves through `card_executions[]`; a legitimate direct QSOL-CORE producer resolves through `operation_executions[]` and the hash-bound Core representation. The output must never fabricate upstream Semantic history merely because another projection expects CARD fields.

`producer_card_ids[]` and `producer_card_execution_ids[]` are conditional retained-lineage projections. When verified Semantic lineage exists, they must be present as required by the active Semantic audit profile, agree exactly with the Semantic CARD-backed subset of `producer_execution_refs[]`, and resolve through `card_executions[]`. When no Semantic lineage exists on a legitimate lower-representation entry, both arrays are absent rather than empty placeholders that pretend to identify producers. Empty/fabricated CARD arrays cannot replace the nonempty producer-execution relation.

The concrete producer relation is required whenever runtime producer attribution is part of the trace contract. Local operation/CARD IDs alone are insufficient for loops, retries, repeated calls, repeated DECK execution, or repeated Core operation execution.

`input_ids[]` identifies the exact immutable inputs materially contributing to the output. Execution-wide input availability is not a substitute, and this transitive output relation does not replace each input's direct concrete consumer/acquisition links.

`effect_attempt_ids[]`, where applicable, identifies concrete effect attempts that produced or exposed the output. Those attempts reciprocally list the output in `observable_output_ids[]`. A referenced attempt must have begun; `NOT_STARTED` attempts cannot appear in this relation.

`external_tool_ids[]` is an explicit array identifying the exact material tools/services/models/provers that supplied the output, and every listed tool reciprocally names this output in `external_tool_versions[].output_ids[]`. It is empty when no material external tool supplied the output.

`machinery_use_record_ids[]` is an explicit array identifying the exact protected-use event or events that materially produced or exposed the output. Every listed use reciprocally names this output in `machinery_use_records[].output_ids[]`. It is empty only when no protected machinery use materially contributed to the output. Producer execution, backend-selection scope, generated-artifact identity, and authorization IDs remain supporting context but cannot replace this occurrence-level join.

`generated_artifact_ids[]` identifies the exact executable/kernel/bytecode artifact that ran where applicable. The artifact links onward to its optimization provenance, its direct toolchain producer, and its ordered transitive toolchain ancestry.

`failure_behavior_binding_ids[]` resolves to the exact identified failure-policy records that governed the producer path. A generic computation `scope_id` cannot substitute for this record-level join.

`cache_reuse_record_ids[]` resolves to records with explicit current representation-qualified execution subjects under the applicable cache contract; those subjects must match the actual material producer/dependency relation. Separate arrays of output producers and cache records are not a positional or all-to-all association, and a direct-Core output cannot cite a CARD-only cache subject.

The execution-contract scope arrays are normative **exact-set attributions**, not optional lists of whichever governing records a producer chooses to mention. For each output, derive the complete applicable record set independently for result determinism, numeric behavior, randomness, and failure behavior from `producer_execution_refs[]`, their representation-qualified containment, any retained Semantic DECK/JOB containment, the canonical owner-qualified contracts that apply to those producer paths, and every material Semantic→Core / Core→Vector-Dataflow mapping or frozen deterministic identity-scope reconstruction rule needed to reach the exact lower/backend units and generated artifacts that produced the output. Frozen inheritance, composition, override, and normalization rules determine which source/lower contracts remain materially governing; a producer may not weaken the set by simply omitting an applicable ancestor or mapped lower scope.

Validation then requires exact duplicate-free set equality between the four output arrays and the independently derived applicable stable record IDs:

```text
set(result_determinism_scope_ids[]) == applicable_result_determinism_scope_ids(output)
set(numeric_scope_ids[]) == applicable_numeric_scope_ids(output)
set(randomness_scope_ids[]) == applicable_randomness_scope_ids(output)
set(failure_behavior_binding_ids[]) == applicable_failure_behavior_binding_ids(output)
```

An array is empty only when its independently derived applicable set is empty. Every supplied ID must resolve to the correct type-specific ledger record **and** actually govern a material producer path; extra unrelated scopes fail just as missing applicable scopes do. When several concrete producers contribute to one output, derive the union of every materially governing scope after the frozen composition/mapping rules are applied. This validation is performed from the hash-bound entry/lowering/execution evidence, never from the output's own claimed arrays, so an output cannot detach itself from a stricter or otherwise material contract by omission.

### Evidence status

When present, evidence status is class-discriminated:

```text
evidence_status:
    evidence_class      # TEST / VALIDATION / PROOF / frozen equivalent
    status
    evidence_rule_id?
    evidence_validation_id?
```

The evidence class must be compatible with the output's `semantic_class` and explicit evidence transition. Generic output `status` is an execution/artifact state and cannot promote epistemic class.

No evidence promotion is implicit. Compare the claimed class against the original hash-bound semantic producers and their actual evidence when such lineage exists, not just a producer-written output label. For any epistemic change that is not class-preserving under the frozen semantic rule, including simulation/TEST/AI output claimed as VALIDATION or PROOF, both `evidence_rule_id` and `evidence_validation_id` are mandatory. Classes are not assumed to form a numeric strength ranking; every proposed non-preserving transition needs its own applicable rule.

`evidence_rule_id` resolves to an accepted, versioned, content-bound `EPISTEMIC_TRANSITION` rule. `evidence_validation_id` resolves to passing `validation_evidence[]` with `subject_kind = OUTPUT` and this exact `output_id`. Its evaluated context binds the output artifact hash, original source class bindings where present, concrete producer execution subjects, contributing input/evidence identities, requested target evidence class/status, and applicable evidence contract. The substantive evidence required by that rule must be retrievable, hash-verifiable, and checked with the identified accepted verifier before the stronger/different claim is published. For a PROOF claim this includes the applicable proposition, proof/certificate, and formal checking obligations required by the frozen proof contract; test success, model confidence, or an operational `PASS` record is not a replacement.

A missing accepted transition rule means the promotion is rejected. Unknown, wrong-kind, stale, unavailable, failed, context-mismatched, or post-publication evidence likewise rejects the claim. Assigning the stronger class directly to `outputs[].semantic_class`, omitting `evidence_status`, or routing it through an adapter cannot bypass the source-to-output class check. A distinct validation/proof CARD may produce separately identified evidence under its frozen semantics; it does not retroactively relabel the original simulation or TEST artifact. Class-preserving records need not invent transition evidence, but remain subject to their own evidence-status validation rules.

## Failure trace

A failed execution retains enough information to distinguish the enclosing outcome from prior completed effects or machinery use without inventing a CARD culprit.

```text
run_id
execution_status
job_id?
job_status?
deck_executions[]?
card_executions[]?
operation_executions[]
control_decisions[]
failure_records[]
failure_behavior_bindings[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
primary_failure_record_id?
backend_selection_scopes[]
backend_selection_decisions[]
machinery_requirements[]
effect_requirements[]
effect_authorization_records[]
effect_attempts[]
effect_non_attempt_records[]
machinery_authorization_records[]
machinery_use_records[]
inputs[]
cache_reuse_records[]
rule_records[]
validation_evidence[]
observable_output_ids[]
```

A failure trace includes the backend-selection scope and decision ledgers referenced by its machinery authorization/use records, including denied candidates and fallback predecessors, not just the final target. It also retains `result_determinism_scopes[]`, `numeric_execution_scopes[]`, and `randomness_execution_scopes[]` needed by each failure record's exact scope-ID attribution, even when execution fails before producing an output. Every `failure_behavior_binding_ids[]` reference resolves to the retained governing policy bindings. A standalone failure manifest must preserve the complete transitive closure of its references, including applicable execution-contract scopes, rules, evidence, requirements, consumed inputs, cache subjects, and observable outputs, either inline or through retrievable content-bound trace records. An unresolvable ID, selectively omitted applicable contract scope, or unbound mutable external trace link is incomplete provenance. Consumed input and cache-to-invocation relations remain required even when `observable_output_ids[]` is empty.

The primary failure resolves through `failure_records[]` to an always-present typed failing scope. `failure_card_id` is canonical only for CARD-caused failures and is absent for legitimate pre-CARD or lower-operation failures without Semantic lineage.

Effect-attempt completion is independent of CARD/lower-operation success. A completed process effect may coexist with a failed execution subject if the process completed and returned a non-success status under the active contract.

Protected machinery authorization outcomes are not enough by themselves. If protected machinery actually began, `machinery_use_records[]` preserve the concrete use, its representation-qualified execution-subject relation or genuine pre-execution initiating-scope relation, the scope's final executable selection decision, complete canonical requirement coverage, generated artifact identity where applicable, and ordering evidence. A direct Core machinery use must remain joined to its actual Core operation execution even when it fails before producing an output.

## Provenance validation rules

At minimum, a future validator should reject or fail closed when:

- stable JOB/DECK/CARD identities are missing or silently renumbered when Semantic lineage is present;
- a lower-entry run fabricates Semantic JOB/DECK/CARD or CARD-execution identities that did not exist;
- an epistemic class becomes detached from its CARD;
- a declared effect loses its per-effect capability binding or representation-qualified declaration identity;
- declaration, attempt, and authorization capability sets do not exactly match the hash-bound declaration, or their owner/execution/reciprocal identity links disagree;
- a protected machinery requirement disappears before MORPH;
- a machinery requirement/declaration or authorization reference omits `representation_kind`, `representation_identity`, the complete representation-relative owner path, or the local requirement ID; resolves against the wrong entry representation; or forces direct Core to fabricate a Semantic JOB/DECK/CARD owner;
- a machinery authorization's required set differs from the exact canonical union of its uniquely resolved representation-qualified requirement refs, or a successful grant does not cover that exact set;
- a machinery use omits an independently applicable canonical requirement or uses grants for another target, scope, representation, or policy context, even when its listed records and event ordering agree;
- a machinery use references a backend-selection decision other than its scope's `final_selection_decision_id`, lacks a final executable decision, or uses a denied/rejected/superseded candidate as though it executed;
- an execution-governed machinery use cannot be joined to its concrete representation-qualified `execution_subject_refs[]`, including the actual `operation_execution_id` for direct Core work;
- conditional machinery-use CARD arrays disagree with verified Semantic lineage or are fabricated for a lower-entry use;
- an output that materially depends on protected machinery cannot be joined reciprocally to the exact `machinery_use_record_id` occurrence that produced or exposed it;
- a machinery-requirement mapping cannot identify the exact source and lower requirement records at either lowering boundary when multiple requirements share a scope;
- an execution-relevant qualifier is consumed, transformed, relocated, or otherwise non-verbatim without an identified `qualifier_lowering_decision_id`, exact owner-qualified source qualifier/value, resolvable resulting Core scopes/facts, accepted applicable `QUALIFIER_LOWERING` rule, and passing subject-bound pre-application evidence;
- a qualifier-lowering decision cites an extension-owned interpretation without the exact resolved extension identity/contract, or a rule/evidence pair for a different qualifier/value/scope;
- a result-binding map cannot represent the actual split/fusion cardinality;
- a result-binding endpoint lacks its complete typed owner path or cannot resolve uniquely within the correct hash-bound representation;
- a sequencing endpoint loses its kind, owner path, stable ID, or direction during serialization/lowering;
- a lowering scope mapping uses ambiguous untyped endpoints where namespaces can overlap;
- a required extension ownership mapping becomes positional or implicit;
- a material resolved extension lacks its exact profile version, contract hash, implementation-component identities, or resolvable owning requirement and governed scopes;
- a requested execution contract differs from its effective contract without resolvable, versioned, applicable pre-execution authority and passing context-bound evidence;
- a semantic-changing numeric lowering at either boundary is represented as a generic mapping or backend numeric flag instead of carrying the requested/effective numeric contract refs plus stable transition decision, accepted `CONTRACT_TRANSITION` authority, and passing pre-application evidence;
- a semantic-changing lowering lacks a stable `transition_decision_id`, subject-bound lowering evidence, or distinct target-scope evidence linked through `related_evidence_ids[]` where that target-scope evidence family exists, or reuses one evidence ID for different singular subjects;
- a failure-policy semantic change is disguised as representation mapping or lacks the required pre-application transition evidence;
- a rule/evidence reference has the wrong kind, subject, context, content hash, order, or an invalid/cyclic related-evidence relation;
- a fallback lacks an actual predecessor, an applicable frozen BACKEND_FALLBACK rule, or passing context-bound evidence before its decision is applied;
- output scope IDs do not resolve to stable type-specific scope records;
- an output or failure's failure-behavior reference does not resolve to the exact applicable stable `failure_behavior_binding_id`;
- a failed CARD/DECK/lower-operation outcome lacks its exact `failure_record_id` or substitutes matching class/stage summaries;
- a lower-operation execution reports untaken, fail-stop-blocked, not-reached, or explicit-skip status without the required typed control/failure/skip-rule cause and any required pre-application skip evidence;
- a concrete output cannot be joined to at least one representation-qualified producer execution subject;
- Semantic producer CARD arrays are required by retained lineage but disagree with the producer execution refs, or are fabricated for a direct lower-entry output;
- a genuine pre-execution machinery setup fabricates execution subjects or omits its typed initiating runtime scope;
- a direct Core protected machinery use is misclassified as pre-execution setup instead of naming its operation execution;
- a SEEDED randomness scope omits `rng_algorithm`, `rng_version`, `seed`, or `stream_id`, or omits material `parallel_partitioning` when the frozen stream mapping says partitioning can change consumed random values;
- an EXTERNAL-ENTROPY randomness scope cannot resolve to the exact protected RANDOM acquisition attempt(s), and to immutable entropy input identity where required by the audit/replay contract;
- an effect attempt or non-attempt cannot be joined to its representation-qualified concrete execution subject;
- an effect attempt/authorization for direct QSOL-CORE execution requires or fabricates a Semantic `card_id` / `card_execution_id` instead of resolving a Core operation execution;
- a non-attempt record has no stable identity;
- an explicit skip lacks a resolvable frozen skip rule and passing applicability evidence for that invocation;
- a not-reached reason has no validated typed control/failure/verified-skip cause for the exact invocation;
- any applicable declared effect lacks both attempt and legitimate non-attempt accounting for a selected concrete execution subject;
- an effect has a begun completion state but omits `effect_begin_sequence_index`, the linked GRANTED authorization's `authorization_sequence_index`, or the required same-domain authorization-before-begin inequality;
- a `NOT_STARTED` effect attempt claims an acquired input, observable output, material external tool, or is reciprocally cited by an output;
- protected machinery begins before every applicable authorization completed;
- denied protected machinery nevertheless has a use-start record;
- a reachable required effect is omitted;
- an effect non-attempt record points to an untyped or unresolved cause;
- a failure lacks a typed failing-scope identity;
- a failure trace omits referenced backend-selection scopes, decisions, or other records needed to resolve its provenance;
- a pre-CARD/lower-operation failure fabricates `failure_card_id`, or a CARD-caused failure omits the matching canonical/concrete CARD identities;
- cold execution and cache reuse become indistinguishable;
- a runtime cache record lacks nonempty representation-qualified current `execution_subject_refs[]`, disagrees with reciprocal CARD/lower-operation execution links, fabricates Semantic CARD subjects for direct Core, or borrows another invocation's evidence/effect accounting;
- `VERIFIED_REUSE` lacks a matching frozen legality rule, checked cache identity, or passing verification evidence, or an unverified hit supplies an output;
- an optimized artifact cannot be joined to its optimization record;
- optimization legality witnesses are opaque labels or do not verify against the exact IR pair, complete transformation sequence, and active contracts;
- a generated artifact omits its exact production `backend_selection_decision_id` or is attributed to the final fallback decision instead;
- a generated artifact cannot resolve its direct producer toolchain invocation;
- a generated artifact's ordered toolchain ancestry is inconsistent with the direct generated-artifact input/output graph under the active profile;
- a transitive toolchain ancestor is falsely recorded as directly outputting a final artifact merely to satisfy chain membership;
- a toolchain invocation omits material tool identity, immutable non-generated `input_ids[]`, material build flags/configuration, or the ordered duplicate-preserving `argument_vector[]` required to reconstruct position-sensitive invocation semantics;
- a toolchain argument vector has missing/duplicate/noncontiguous indices, loses duplicate occurrences or positional separators, or contains typed input/artifact/IR/output references inconsistent with the invocation's material input/output ledgers;
- output evidence status contradicts semantic class;
- an epistemic promotion lacks its applicable frozen rule and passing subject/content-bound substantive evidence before claim publication;
- a mutable input locator substitutes for immutable input identity;
- an input loses its actual concrete consumer execution refs or effect-acquisition attempts, or a failed/output-free invocation loses consumed-input attribution;
- reciprocal input/consumer/acquisition links disagree, captures are assigned by local CARD/operation ID or path alone, or a denied/unstarted acquisition claims a captured input;
- a material external tool has neither immutable/versioned material identity nor an explicit identity-unavailable state that weakens the claim;
- a material external tool lacks a concrete effect-attempt/output subject, or its `effect_attempt_ids[]` / `output_ids[]` links disagree with reciprocal attempt/output `external_tool_ids[]` references.

### Conformance cases for the future trace validator

These are documentation acceptance cases for the applicable roadmap gates, not a claim that executable validation already exists. They apply equally to canonical traces and their manifest, failure, and agent-facing projections.

| Case | Accept only when | Reject mutations |
| --- | --- | --- |
| Direct Core protected effect | `input_representation = QSOL_CORE`; the effect declaration resolves in the hash-bound Core IR; authorization and attempt use the same Core `execution_subject_ref` / `operation_execution_id`; all required capabilities are granted before begin; Semantic CARD fields are absent unless independently retained as verified lineage. | Fabricated `card_id`/`card_execution_id`; missing Core operation execution; declaration resolved through a nonexistent Semantic IR; local operation ID without representation/owner path; authorization for another Core invocation. |
| Direct Core protected machinery use | `input_representation = QSOL_CORE`; each applicable machinery requirement/ref names `QSOL_CORE`, `core_ir_hash`, the complete Core-relative owner path and local requirement ID; authorization resolves that exact Core declaration/capability set; `execution_subject_refs[]` contains the actual Core `CORE_OPERATION` / `operation_execution_id`; the use references the scope's final executable decision; all authorizations precede use. | Requirement path forced to start at JOB; missing representation identity; fabricated Semantic machinery declaration or CARD execution; empty execution subjects treated as pre-execution setup; predecessor/denied/superseded decision used as the executed decision; another Core invocation's subject; scope/event index used as the concrete join. |
| Direct Core output | A nonempty `producer_execution_refs[]` entry resolves to the actual Core `operation_execution_id`; complete applicable contract scopes are derived from that Core producer and retained mappings; Semantic producer arrays are absent unless verified lineage exists. | Empty producer refs; fabricated CARD producers; treating absent upstream Semantic history as an error; deriving scopes only from nonexistent CARD executions. |
| Lower-operation non-reach | The lower operation is represented by its exact `operation_execution_id`; an untaken status resolves to the controlling decision, a fail-stop/blocked status resolves to the blocking failure, and an explicit skip has accepted rule plus passing pre-application evidence bound to this OPERATION_EXECUTION. `failure_record_id` is absent unless the operation itself failed. | Cause-free NOT_REACHED; blocking failure placed in `failure_record_id`; control decision from another invocation; skip rule without evidence; fabricated CARD cause/lineage. |
| Qualifier consumption | The exact owner-qualified source qualifier/value resolves in Semantic IR; the decision identifies every material Core scope/fact; an accepted `QUALIFIER_LOWERING` rule and passing subject-bound evidence validate that exact effect before application; extension-owned interpretation resolves its exact extension contract. | Opaque `qualifier_lowering_decisions[]` entry; dropped/defaulted qualifier; wrong value/owner/Core fact; rule without evidence; evidence for another qualifier; validation after lower fact application. |
| Multi-capability effect | Canonical declaration, trace declaration, attempt, and authorization all require `{AI_MODEL, NETWORK}`; every required capability is granted to the same attempt before begin. | Copy only `AI_MODEL` into both runtime records; truncate the trace declaration too; substitute another declaration or retry; omit or deny `NETWORK`. |
| Begun effect ordering | Every `COMPLETED`, `ABORTED_CLEAN`, `PARTIAL`, or `UNKNOWN` attempt has a concrete begin index; its linked authorization is GRANTED, has a concrete authorization index in the same event-order domain, and the authorization index precedes begin. | Begun state with missing begin index; GRANTED authorization with missing ordering index; late authorization; generic attempt sequence used as proof; denied authorization paired with a begun state. |
| Numeric contract transition | A representation-only numeric mapping proves identical content-bound semantics. Any semantic change carries exact requested/effective numeric contract IDs/hashes plus a stable transition-decision ID, accepted CONTRACT_TRANSITION authority, and passing subject-bound evidence validated before the changed lower contract is applied. | Strict IEEE changed to tolerance/fast-math with only a mapping rule or backend flag; missing requested/effective hashes; rule without evidence; late evidence; evidence for another scope/contract pair. |
| SEEDED randomness scope | `effective_randomness_mode = SEEDED` has explicit RNG algorithm, version, seed, and stream identity; material parallel partitioning/stream mapping is recorded whenever it can change consumption. | Implementation defaults; missing RNG version; missing seed/stream; omitted material partitioning; mode label treated as replay identity. |
| Failure-policy change | An accepted CONTRACT_TRANSITION rule and passing lowering-decision evidence authorize the exact fail-stop-to-retry transition before activation; the resulting `FAILURE_BEHAVIOR_BINDING` has distinct subject-bound evidence that cites the lowering evidence through `related_evidence_ids[]`. A representation-only rename instead proves unchanged semantics under its mapping rule. | Missing/stale rule; late evidence; same evidence ID reused for lowering and binding; target evidence omits required lowering lineage; evidence for another decision/binding; continue disguised as representation mapping; requested/effective labels whose content changed. |
| CARD not reached | A typed controlling decision, blocking failure, or verified skip actually prevents this exact invocation and its effect under the active contract. | No cause; cause from another loop iteration; handled nonblocking failure; dangling/circular cause; unverified parent skip. |
| Backend fallback | The actual earlier denied candidate, accepted BACKEND_FALLBACK rule, and passing subject-bound evidence permit this target switch before the fallback decision; protected use is independently authorized and references the fallback/final executable decision. | Arbitrary/stale rule ID; wrong predecessor/scope; late validation; explicit target disallowing fallback; replacement mislabeled initial selection; protected use attached to the denied/superseded predecessor. |
| Epistemic transition | The accepted EPISTEMIC_TRANSITION rule's substantive evidence is verified for this exact output, source class, producer executions, and requested claim before publication. | TEST success claimed as PROOF; missing proof obligations; different artifact's evidence; direct relabeling of output semantic class; omission of evidence status to evade the check. |
| Optimization legality | Typed content-bound witnesses verify the exact IR pair, complete pass sequence, and active numeric/determinism/randomness/failure and other material contracts before optimized-variant acceptance. | Opaque `PASS`; wrong IR pair; changed tolerance or failure policy; incomplete pass coverage; unavailable verifier/evidence; finite tests represented as universal proof. |
| Failed execution outcome | The failed execution subject's `failure_record_id` resolves to its exact governing failure or validated propagation relation. | Class/stage summaries only; another invocation's same-class failure; unresolved ID; fake CARD failure for a lower-operation or merely blocked path. |
| Extension resolution | Each material resolution retains exact version, contract hash, complete implementation-component identities, owning requirement refs, and actual governed scopes; the selected version satisfies the source range. | Profile/range only; missing adapter/hook identity; wrong owner; incompatible version/hash; identity-mapping omission used to erase the material resolution. |
| Multi-capability machinery and complete use coverage | Resolve representation-qualified canonical requirements, validate their trace/lowering copies, require the exact canonical capability union and full grant, cover every independently applicable requirement for the actual final decision/use before start, and require every linked authorization to govern that same final decision. | Copy only `GPU` when a requirement needs `{GPU, NETWORK}`; truncate the trace copy too; drop a second applicable requirement; add unrelated grants; use another candidate/representation's authorization; use a predecessor decision; keep correct event order but incomplete coverage. |
| Concrete cache substitution | Current runtime subjects are nonempty representation-qualified `execution_subject_refs[]`; CARD or direct-Core operation invocations reciprocally reference the record; two invocations of the same canonical computation retain distinct cold/reuse records; passing reuse evidence/effect accounting is bound to the exact substituted subject set. | CARD-only subject for direct Core; omit runtime execution refs; use the historical cache producer as the current subject; swap retries/operation invocations; infer a Cartesian product from a multi-producer output; reuse another invocation's effect accounting; claim both applied cold and whole-subject reuse. |
| Ordered toolchain arguments | The invocation records a contiguous duplicate-preserving `argument_vector[]` whose exact tokens and typed input/generated-artifact/IR/output references match the material command line; summary inventories agree without replacing order. | Sort libraries; collapse duplicates; move `--whole-archive` across libraries; same `flags[]`/input sets with different argv accepted as identical; response-file path without immutable content/command semantics. |
| Typed sequencing identity | Every directed edge resolves by endpoint kind, complete typed owner path, and stable ID in its containing representation, under the shared serialization contract. | Drop kind/path; confuse CARD `7` with effect `7`; join repeated local CARD IDs under different DECKs; reverse direction while retaining ID text; resolve against a different representation. |
| Qualified lower bindings | Each side of both lowering maps resolves its full owner path and binding ID in the correct input/output IR; a split names both distinct scoped `v0` bindings and a fusion retains each qualified source. | Keep local `v0` only; omit an enclosing scope; substitute a different IR; sort names and infer owners; duplicate a fully qualified binding; use an identity exception that cannot reconstruct ownership. |
| Concrete runtime input consumers and acquisition | Repeated CARD/Core operation invocations retain distinct captured input identities, exact `consumer_execution_refs[]`, and actual acquisition attempt/input links, including when an invocation fails with no output. | Keep only canonical source CARD IDs; swap consumers or acquisition attempts; collapse independent equal-content captures without occurrence mapping; use an output as the only join; fabricate inputs for denied/unstarted reads. |
| Representation-qualified machinery authorization | Each authorization names every requirement by representation kind/content identity, complete representation-relative owner path, and local requirement ID, resolves that tuple uniquely in the named hash-bound representation, and validates the exact canonical capability union. Semantic sibling DECK/CARD-local IDs and direct Core operation-local IDs remain distinct without fabricated ancestry. | Bare local requirement ID; missing representation identity; immediate owner only; missing/swapped ancestor; infer owner from source CARDs; force a Core path through JOB/DECK/CARD; owner-mismatched lowering copy; first-match lookup. |
| Repeated protected-use output attribution | Two protected launches under one concrete execution subject/scope retain distinct `machinery_use_record_id` values and reciprocal use/output links, so each output resolves to the exact launch that produced or exposed it. | Infer use from CARD/Core execution/scope/artifact alone; attach both outputs to both launches; omit the use-side or output-side reciprocal link; borrow another launch's authorization/use occurrence. |
| Material external-tool attribution | Every material tool record has at least one concrete effect-attempt/output subject and reciprocal `external_tool_ids[]` links; retries using different tool/model versions remain separately attributable. | Tool floats only at `source_card_ids[]`; omit both subject arrays; swap retry/output subjects; one-sided attempt/output link; equal endpoint/name used as attribution. |
| NOT_STARTED effect attempt | A denied/unstarted attempt has no begin/end event, acquired inputs, observable outputs, or material external tools, and no output cites it as a producer/exposer. | Nonempty `observable_output_ids[]`; output reciprocally cites the unstarted attempt; acquired input or tool attribution despite no begin event. |

For every case involving referenced rules or evidence, also reject missing content, hash mismatch, an unaccepted authority/verifier, a wrong subject namespace, and evidence that cannot establish the required pre-application ordering. A positive example is conditional on an actually accepted frozen rule; the table does not create one by example. The [serialization conformance cases](SERIALIZATION.md#sequencing-conformance-cases) additionally cover typed endpoint round trips across nested and flattened formats.

## Principle

> Trace meaning, not just bytes. Preserve stable semantic identity when it exists, representation-qualified concrete execution identity at every entry layer, typed scope correspondence, typed non-reach causes, unconditional declared-effect accounting, final-selection consistency, authorization-before-use ordering, truthful direct build edges, exact ordered toolchain arguments, transitive toolchain ancestry, and the exact evidence chain from immutable inputs through lowerings, optimization, toolchain invocations, and machinery to each output or failure.
