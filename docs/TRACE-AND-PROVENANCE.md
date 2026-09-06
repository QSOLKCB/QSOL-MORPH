# Trace and Provenance

QSOL-MORPH treats provenance as part of execution semantics for research workflows.

This document is architectural and non-normative until the relevant contracts are frozen. Its purpose is to ensure that later implementations can explain not only what bytes were produced, but which semantic units, concrete executions, lowerings, machinery decisions, authorization decisions, execution paths, entropy acquisitions, external tools, toolchain invocations, and evidence transitions produced them.

### One record contract, not independent mirror schemas

The record definitions and cross-record validation conditions in this document apply wherever the same records appear, including the README, agent guidance, roadmap gates, reproducibility manifests, and failure-domain traces. Shorter inventories are projections of this model, not permission to omit conditionally required fields or weaken validation. `?` means conditional presence: the applicability rules below decide when the field is required. A standalone projection retains the transitive closure needed to validate its records, inline or through retrievable content-bound references. These architectural requirements do not freeze an executable format or implement the later roadmap phases.

## Trace questions

A complete trace should be able to answer:

- what source and canonical Semantic IR were executed;
- which stable JOB, DECK, and CARD identities were selected;
- which concrete DECK and CARD executions actually occurred;
- which typed control decision or identified failure record caused an untaken or blocked path;
- how Semantic IR lowered into QSOL-CORE;
- how QSOL-CORE lowered into the mandatory Vector/Dataflow IR;
- how result bindings were preserved, renamed, split, fused, or otherwise mapped;
- how extension, machinery, result-determinism, numeric, randomness, and failure-behavior scopes mapped through both mandatory lowerings;
- which machinery-selection decisions were considered, denied, superseded, or finally used;
- which protected machinery requirements applied and whether authorization completed before protected use began;
- which protected effects were declared for each concrete CARD execution, authorized, attempted, completed, aborted, partially observed, or legitimately not attempted;
- which external-entropy acquisition attempt(s) and immutable entropy input(s) governed every applicable EXTERNAL-ENTROPY randomness scope;
- what exact immutable inputs were consumed and which ones materially contributed to each output;
- which concrete CARD executions, effect attempts, tools, generated artifacts, optimization records, direct toolchain producers, transitive toolchain ancestry, and execution-contract scopes produced each output;
- whether cache reuse occurred and under what legality evidence;
- what epistemic class and evidence status belongs to each output;
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

These layers describe different objects. A flat manifest may serialize them together, but it must not erase their identities or joins.

## Stable source identities

Stable JOB/DECK/CARD identities originate in the canonical semantic model. A trace records them; it does not synthesize, renumber, or infer them from array position.

```text
source_trace:
    source_hash
    spec_version
    run_id?
    job_id
    deck_ids[]
    card_ids[]
    source_location?
```

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

### Epistemic class bindings

```text
epistemic_class_bindings[]:
    card_id
    semantic_class
```

Separate `card_ids[]` and `epistemic_classes[]` arrays are not an acceptable positional association. Epistemic class is bound directly to canonical CARD identity.

### Declared effect requirements

```text
effect_requirements[]:
    declared_effect_id
    card_id
    effect_kind
    required_capabilities[]
```

The complete capability set belongs to that specific effect. A CARD-wide capability union may be useful for preflight but cannot replace the per-effect association.

A canonical declaration is source identity. Runtime accounting is performed against each applicable concrete `card_execution_id`, because the same canonical CARD may execute more than once.

The declaration in the trace must match the corresponding declaration in the hash-bound canonical input, including owner, effect kind, and complete capability set. Agreement between two truncated runtime copies is not agreement with the canonical declaration. See [Declaration-bound authorization validation](#declaration-bound-authorization-validation).

### Protected machinery requirements

```text
machinery_requirements[]:
    machinery_requirement_id
    scope_kind
    scope_id
    source_card_ids[]
    target_selector_or_class
    required_capabilities[]
```

A GPU requirement does not turn GPU selection into an external effect. It is a separate protected-machinery authorization boundary.

### Source contract bindings

```text
result_determinism_bindings[]:
    scope_kind
    scope_id
    source_card_ids[]
    requested_result_determinism

numeric_contract_bindings[]:
    scope_kind
    scope_id
    source_card_ids[]
    numeric_contract_id
    numeric_contract_hash

randomness_contract_bindings[]:
    scope_kind
    scope_id
    source_card_ids[]
    requested_randomness_mode

failure_behavior_bindings[]:
    failure_behavior_binding_id
    scope_kind
    scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
    transition_evidence_id?
```

`failure_behavior_binding_id` is the stable record identity used by result and failure provenance. It is distinct from the generic computation `scope_id` and remains resolvable even when several bindings or policy transitions concern one governed computation.

The owning scope may be a JOB, DECK, CARD, or another scope frozen by the semantic model. Distinct source requirements may not be collapsed into one execution-wide declaration unless a frozen normalization proves that collapse is lossless. Failure bindings obey the same [failure-policy transition conditions](#failure-policy-transitions) here and in the execution-scope inventory.

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
        scope_kind
        scope_id
        requirement_hash
    governing_scope_refs[]:
        representation_kind
        ir_hash
        scope_kind
        scope_id
    source_card_ids[]
```

`resolved_extension_id` is the stable resolution-record key, not the profile name or requested range. `resolved_version` is the exact selected profile version. `contract_id` and `contract_hash` bind the actual contract interpreting it. The nonempty `implementation_components[]` identifies every material profile implementation, adapter, and lowering hook used for this resolution, with its exact version and immutable content hash. A frozen content-bound package manifest may represent a complete component/dependency closure; a package label, mutable endpoint, or version range cannot. Content needed to validate the resolution must be embedded in the trace closure or retrievable and hash-verifiable. Material external tools invoked by an adapter retain their separate external-tool identities.

Each nonempty `source_requirement_refs[]` entry is a composite reference to one exact requirement in the hash-bound original input representation: the typed owning scope plus the canonical hash of the complete `ExtensionRequirement` value, including profile, requested version/range, and any required contract identity. It resolves to the owned canonical requirement, not to an arbitrarily selected child CARD. Ambiguous duplicate requirements require a frozen canonical deduplication rule or fail resolution. `representation_kind` distinguishes Semantic IR, Core IR, and other explicitly frozen input representations; an execution that legitimately starts with Core IR must not fabricate a Semantic IR source.

Each nonempty `governing_scope_refs[]` identifies the actual typed scope(s) and IR version in which the resolution interprets syntax, adapters, effects, or lowering hooks. Source ownership remains separately preserved. Validate that the resolved profile/version satisfies every referenced source requirement, that any required contract identity matches, and that the identified implementation components implement that exact contract. Unknown versions, mismatched hashes, missing components, unresolved owners, or an unestablished requirement-to-resolution association fail closed before the extension is used.

Different resolutions of one source range have different resolution identities and retain their actual governed scopes. Several requirements may share a resolution only when each one is explicitly referenced and satisfied. Both extension-lowering mapping families reference applicable `resolved_extension_ids[]`; a permitted identity-mapping reconstruction may omit a redundant mapping record, never the exact material resolution or its source/owner association. A frozen reconstruction rule must recover the same requirement, resolution, and governed-scope relation without guessing from a profile name.

### Cardinality-aware result-binding maps

Result-binding maps are identified mapping groups:

```text
result_binding_map[]:
    mapping_group_id
    source_bindings[]:
        source_card_id?
        binding_id
    lower_bindings[]:
        binding_id
    mapping_rule_id?
```

This model supports:

- one-to-one preservation or rename;
- one-to-many split;
- many-to-one frozen legal fusion;
- many-to-many only when an explicit frozen rule permits it.

`source_bindings[]` and `lower_bindings[]` use deterministic canonical ordering. Positional inference is not sufficient. A map is required whenever result identities are preserved or transformed unless a frozen rule permits deterministic reconstruction of the complete mapping.

### First-lowering scope mappings

Every decision family that maps a scoped semantic requirement identifies both ends with typed scope references rather than untyped IDs.

```text
scope_ref:
    scope_kind
    scope_id
```

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

Machinery requirements additionally need an explicit requirement-level association at this first boundary:

```text
machinery_requirement_lowering_decisions[]:
    mapping_group_id
    source_scope_refs[]
    core_scope_refs[]
    source_machinery_requirement_ids[]
    lower_machinery_requirement_ids[]
    source_card_ids[]
    mapping_rule_id
```

Both scope arrays contain typed `scope_ref` values. Source requirement IDs resolve in the input Semantic IR and lower requirement IDs in the resulting Core IR, qualified by the corresponding IR hashes and owning scopes. Both requirement-ID sets are nonempty, deterministic, and duplicate-free. Unrelated requirements sharing a scope use separate mapping groups. Splits or frozen legal fusions must identify every source/lower requirement and a frozen rule defining the exact relation, including the target selector and complete capability set for each lower requirement. Neither shared scope IDs nor list position can substitute for that association.

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

The second lowering preserves exactly which typed Core scope maps to which typed Vector/Dataflow scope. Bare arrays such as `core_scope_ids[]` and `vector_dataflow_scope_ids[]` are not sufficient because JOB, DECK, CARD, region, kernel, and generated-unit namespaces may overlap.

```text
core_scope_refs[]:
    scope_kind
    scope_id

vector_dataflow_scope_refs[]:
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
transition_authorized_by?
```

Use the applicable mapping family for:

- extension requirements;
- protected-machinery requirements;
- result determinism;
- numeric contracts and material numeric modes;
- randomness contracts;
- failure behavior.

`machinery_requirement_mapping_decisions[]` additionally identifies the stable machinery-requirement records on both sides of the lowering boundary:

```text
machinery_requirement_mapping_decisions[]:
    core_scope_refs[]
    vector_dataflow_scope_refs[]
    source_machinery_requirement_ids[]
    lower_machinery_requirement_ids[]
    source_card_ids[]
    mapping_rule_id
    backend_unit_ids[]?
```

The source/lower requirement-ID arrays are cardinality-aware. Scope correspondence and source CARD identity do not identify which requirement was mapped when one Core scope owns several machinery requirements. Each lower requirement must preserve the source target selector/class and complete capability set or identify the frozen rule that transformed them.

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
    scope_kind
    scope_id
    source_card_ids[]
    backend_unit_id?
    selection_decision_ids[]
    final_selection_decision_id?
```

`backend_selection_scope_id` is the stable selection-record key. `scope_kind` plus `scope_id` identify the governed computation and are not aliases for the selection-scope record identity.

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
    source_card_ids[]
    machinery_requirement_ids[]
    required_capabilities[]
    granted_capabilities[]
    denied_capabilities[]
    capability_policy_id
    capability_policy_version
    authorization_status
    authorization_sequence_index?
```

Protected use is independently identified:

```text
machinery_use_records[]:
    machinery_use_record_id
    backend_selection_scope_id
    backend_selection_decision_id
    backend_unit_id?
    source_card_ids[]
    card_execution_ids[]
    initiating_scope_ref?
    machinery_authorization_record_ids[]
    protected_use_start_sequence_index
    protected_use_stop_sequence_index?
```

`card_execution_ids[]` identifies the concrete CARD invocations participating in this use, not all invocations of the source CARD or backend unit. It is nonempty for CARD-governed work, and every ID resolves through `card_executions[]` to the corresponding canonical CARD and DECK execution in this run. A repeated launch, retry, or loop iteration receives a distinct use record with the correct concrete invocation IDs; an event index alone is not this join.

For genuine pre-CARD machinery setup only, the CARD-execution array may be empty and `initiating_scope_ref` is required instead. This is a typed `{ scope_kind, scope_id }` reference to the actual aggregate RUN or DECK_EXECUTION that initiated setup, resolving to `run_id` or `deck_execution_id`. It must not invent a CARD execution. A use serving several CARD executions must list the actual participating executions under the frozen lowering/execution mapping.

Authorization and use indices live in one frozen monotonic event-order domain. Every applicable successful machinery authorization satisfies:

```text
authorization_sequence_index < protected_use_start_sequence_index
```

Denied machinery has no use-start record.

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

Run-wide compiler/tool versions are useful summaries, but they cannot identify the exact build path for one artifact when different backend units or stages use different versions, flags, targets, linkers, or generated-code options.

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
    environment_or_config_hash?
    input_ir_hashes[]?
    input_ids[]
    input_generated_artifact_ids[]?
    output_generated_artifact_ids[]
    backend_unit_id?
    backend_selection_scope_id?
```

`material_tool_identity` is immutable/versioned identity sufficient to distinguish the actual compiler, assembler, linker, code generator, or frozen equivalent used by that invocation. It may be represented by a version plus binary/content hash, immutable tool artifact ID, or another frozen identity adequate for the reproducibility claim.

`input_ids[]` resolves to identified immutable `inputs[]` records for every material input not generated in this run, including prebuilt objects, static libraries, headers, startup files, sysroots, and implicit toolchain dependencies. It is empty only when no such inputs were consumed. A path, library name, search flag, or tool version is not the identity of the bytes read. A composite dependency input must content-bind the complete material dependency set through a frozen manifest representation. Missing material input identity invalidates a complete/reproducible build-provenance claim.

`input_generated_artifact_ids[]` and `output_generated_artifact_ids[]` are **direct edges** in the build graph. If invocation `link-1` consumes `obj-1` and emits `exe-1`, then `obj-1` appears in `link-1.input_generated_artifact_ids[]` and `exe-1` appears in `link-1.output_generated_artifact_ids[]`. A prebuilt library consumed by the same linker instead appears in `link-1.input_ids[]`; it must not be fabricated as an artifact generated by this run.

The reciprocal direct-producer invariant is therefore narrow and exact: a generated artifact's `direct_producer_toolchain_invocation_id` must resolve to an invocation whose `output_generated_artifact_ids[]` contains that artifact. An invocation listed only in `toolchain_invocation_chain_ids[]` is not required to list the final artifact as a direct output.

For example:

```text
compile-1: source/IR -> obj-1
link-1:    obj-1 + prebuilt-lib-1 -> exe-1
link-1.input_generated_artifact_ids = [obj-1]
link-1.input_ids = [prebuilt-lib-1]

obj-1.direct_producer_toolchain_invocation_id = compile-1
obj-1.toolchain_invocation_chain_ids = [compile-1]

exe-1.direct_producer_toolchain_invocation_id = link-1
exe-1.toolchain_invocation_chain_ids = [compile-1, link-1]
```

`compile-1.output_generated_artifact_ids[]` contains `obj-1`, not `exe-1`; `link-1.output_generated_artifact_ids[]` contains `exe-1`. `prebuilt-lib-1` resolves to its consumed immutable identity in `inputs[]`. This preserves the truthful direct-output relation, external build dependencies, and exact transitive build ancestry.

Where every intermediate generated artifact is retained, `toolchain_invocation_chain_ids[]` must be consistent with the graph reachable through direct input/output artifact edges. If a future frozen profile permits omission of intermediate artifacts, it must define how the transitive chain remains content-bound and verifiable rather than fabricating direct-output edges.

A generated artifact cannot claim reproducible byte provenance from a run-wide compiler list alone.

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

A rule name or a producer's success label is not evidence of permission. Contract transitions, explicit skips, verified cache substitutions, backend fallback, epistemic transitions, and optimization acceptance use shared, resolvable rule and evidence records:

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
    evidence_hash
    evidence_content?
    evidence_location?
```

Candidate `rule_kind` values include `CONTRACT_TRANSITION`, `EFFECT_SKIP`, `CACHE_SUBSTITUTION`, `BACKEND_FALLBACK`, `FAILURE_BEHAVIOR_MAPPING`, `EPISTEMIC_TRANSITION`, and `OPTIMIZATION_LEGALITY`. `authority_kind` distinguishes a frozen source/specification authority from an execution policy. The authority ID and version/content identity must resolve to the authority actually accepted for this run; a backend cannot authorize itself by inventing a rule record. Rule content must be embedded or retrievable through a content-bound location, and its hash must verify. The rule definition includes its permitted operation, scope, and applicability conditions. A record of kind `FAILURE_BEHAVIOR_MAPPING` permits only a verified representation change, not a change in failure semantics.

`subject_kind` defines the target namespace: `RESULT_DETERMINISM_SCOPE`, `RANDOMNESS_SCOPE`, `FAILURE_BEHAVIOR_BINDING`, `CARD_EXECUTION`, `EFFECT_NON_ATTEMPT_RECORD`, `CACHE_REUSE_RECORD`, `BACKEND_SELECTION_DECISION`, `OUTPUT`, or `OPTIMIZATION_RECORD` resolves to that ledger's stable record key. The evidence must name the same rule as the subject's rule reference and bind the exact subject and evaluated context, not another run, invocation, contract, cache entry, target decision, output, or IR pair. `verifier_identity` identifies the verification method and its immutable/versioned implementation.

Evidence content must likewise be embedded or retrievable and hash-verifiable. It contains the evaluated context and checks needed to establish applicability; `evaluated_context_hash` binds that context canonically. An `outcome = PASS` string alone is insufficient. Validation must establish that the evidence supports the rule under the current source, policy, inputs, and execution contracts. Unknown IDs, unavailable definitions, wrong kinds, stale versions, mismatched context, and failed or unverifiable evidence fail closed.

For an applied transition, skip, cache substitution, fallback, or optimized-variant acceptance, `application_sequence_index` is required and denotes the actual subject's activation, skip, substitution, selection, claim-publication, or acceptance event. It shares the frozen monotonic event-order domain with `validation_sequence_index`, which must precede it. A rejected decision has no application event. Reporting a rule or validating it after application cannot retroactively authorize behavior.

These records are provenance about operational permission and checks, not TEST/VALIDATION/PROOF research outputs and not capability grants. Referencing them never bypasses effect or protected-machinery authorization. An epistemic transition requires its specific rule's substantive research evidence in addition to the operational record that verifies it; ordinary operational authorization cannot manufacture that evidence.

## Stable execution-contract scope records

Execution scope records have type-specific stable keys distinct from the generic computation scope they govern.

```text
result_determinism_scopes[]:
    result_determinism_scope_id
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
    scope_kind
    scope_id
    source_card_ids[]
    numeric_contract_id
    numeric_contract_hash
    material_numeric_mode
    backend_unit_id?

randomness_execution_scopes[]:
    randomness_scope_id
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
    scope_kind
    scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
    transition_evidence_id?
```

Output references resolve directly to `result_determinism_scope_id`, `numeric_scope_id`, `randomness_scope_id`, and `failure_behavior_binding_id`. They never infer those records from a generic `scope_id`.

Whenever requested and effective result-determinism or randomness contracts differ, both `transition_authorized_by` and `transition_evidence_id` are required. The former resolves to `rule_records[].rule_id` of kind `CONTRACT_TRANSITION`; the latter resolves to `validation_evidence[].validation_evidence_id` for that exact execution-scope record. Evidence binds the requested/effective contracts, accepted source/policy authority, and governing numeric/randomness context, and must establish authorization before the effective contract is activated or used. A missing, unknown, inapplicable, or post-execution authority is an unauthorized transition and fails closed. The optional notation permits absence only when no transition occurred; it does not permit an undocumented downgrade. Lowering that applies a transition must preserve this authorization/evidence relation into the governed execution scope.

### Failure-policy transitions

The requested and effective failure-behavior IDs resolve to immutable/versioned behavior definitions, including the applicable default fail-stop contract. They may not be free labels whose meaning changes in place. A source/effective difference must be classified by actual semantics, not merely by whether the strings differ.

For a representation-only difference, `mapping_or_transition_rule_id` is required and resolves to an accepted content-bound rule of kind `FAILURE_BEHAVIOR_MAPPING` that establishes preservation of the exact requested/effective behavior, scope, propagation, and ordering. A frozen identity-reconstruction exception may omit redundant representation mapping only when it proves that same correspondence. Calling continue, retry, compensation, or a changed propagation boundary a representation change is invalid.

Any semantic change requires both `mapping_or_transition_rule_id` of kind `CONTRACT_TRANSITION` and `transition_evidence_id` identifying passing evidence for `subject_kind = FAILURE_BEHAVIOR_BINDING` and this exact `failure_behavior_binding_id`. The rule and evidence bind the requested/effective behavior definitions, owning and applicable concrete execution scopes, accepted source/policy authority, and material dependencies, ordering, effects, and execution contracts. They must establish permission for that exact behavior change before the effective policy is activated or applied to a failure. This includes a fail-stop request changed into continue, retry, or compensation.

No accepted frozen rule, no semantic transition. Missing, stale, ambiguous, self-authorized, context-mismatched, unverifiable, or late evidence rejects the change and invokes the applicable unchanged rejection/fail-stop contract. An unauthorized effective policy cannot authorize its own acceptance or its rejection handling. Representation-only rules cannot substitute for semantic-transition authority, and recording a later successful continuation is not proof that continuation was permitted. Both lowering boundaries and all policy references on outputs/failures preserve this distinction and the required evidence.

### External-entropy attribution

When `effective_randomness_mode = EXTERNAL-ENTROPY`, the randomness scope must identify the exact protected `RANDOM` acquisition attempt or attempts that supplied entropy through `entropy_effect_attempt_ids[]`. Each referenced attempt must resolve to the ordinary effect authorization/attempt ledger and therefore prove authorization completed before acquisition began.

Where the acquired entropy becomes a material runtime input, `entropy_input_ids[]` identifies the immutable input record(s), such as a canonical captured value, content hash, immutable artifact identity, or another frozen identity sufficient to distinguish what was actually consumed. If raw entropy is intentionally not retained, a frozen audit identity may establish what acquisition was used, but the manifest must not claim byte-for-byte replayability unless the consumed entropy value is actually reconstructable.

The randomness mode itself never authorizes entropy access and never substitutes for the protected `RANDOM` effect attempt.

A single execution-wide scope record is valid only when a frozen normalization proves it faithfully represents every governed source requirement.

## Execution trace

Potential fields include:

```text
run_id
job_id
deck_executions[]
card_executions[]
control_decisions[]
failure_records[]
execution_status
job_status
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

Execution-wide capability arrays and `runtime_compiler_versions[]` are summaries only. Contextual authorization records prove per-boundary authorization, and `toolchain_invocations[]` plus generated-artifact direct/ancestry links prove the exact artifact-producing build graph.

## DECK and CARD execution ledgers

Every selected DECK remains identified even when fail-stop prevents it from starting:

```text
deck_executions[]:
    deck_execution_id
    deck_id
    deck_status
    card_execution_ids[]
    execution_order_index?
    failure_record_id?
```

Every CARD execution is a distinct runtime object:

```text
card_executions[]:
    card_execution_id
    deck_execution_id
    card_id
    card_status
    execution_order_index?
    governing_control_decision_id?
    governing_failure_record_id?
    governing_skip_rule_id?
    skip_verification_evidence_id?
    failure_record_id?
```

Canonical `card_id` identifies the semantic CARD. `card_execution_id` identifies one concrete execution of that CARD. The distinction matters for loops, retries, calls, repeated DECK execution, or any future construct that can execute one canonical CARD more than once.

`failure_record_id` is required for a failed CARD or DECK outcome and resolves to the exact failure record governing that outcome, directly or through an explicitly frozen and validated propagation relation. Equal failure classes/stages do not identify a failure event. A blocked/not-started CARD instead uses its governing cause and must not fabricate a failure caused by that CARD. Summary failure labels, when retained, must agree with the referenced record and cannot replace it.

Membership in `card_ids[]` is not proof that a CARD ran. An explicitly skipped CARD uses the rule/evidence requirements in [Effect non-attempt records](#effect-non-attempt-records), with evidence bound to its `CARD_EXECUTION` subject. Skipping the parent CARD cannot evade the accounting and rule validation for its effects. Every not-reached CARD also obeys the typed cause requirements below; `CARD_NOT_REACHED` is not a cause-free status.

## Typed execution-path causality and failures

Control decisions and failures have distinct identified namespaces:

```text
control_decisions[]:
    control_decision_id
    card_execution_id
    control_kind
    decision
    sequence_index?
    backend_detail?

failure_records[]:
    failure_record_id
    failing_scope_kind
    failing_scope_id
    failure_behavior_binding_ids[]
    failure_class
    failure_stage
    failure_card_id?
    failure_card_execution_id?
    deck_execution_id?
    sequence_index?
    backend_detail?
```

`failing_scope_kind` plus `failing_scope_id` is the always-present typed identity of the scope where the failure occurred. Frozen scope kinds may include JOB, DECK_EXECUTION, CARD_EXECUTION, BACKEND_SELECTION_SCOPE, LOWERING, or another explicitly specified execution scope.

`failure_behavior_binding_ids[]` is required and resolves to the exact `failure_behavior_bindings[]` records governing this failure and its propagation or handling. It includes the applicable frozen default fail-stop binding, not just explicit recovery policies. When several policies or transitions concern one computation, the failure references those actually active at that event; it must not infer policy from the resulting path or a generic scope ID. A rejected requested policy is not an effective handling policy. Pre-CARD rejection records retain the applicable setup/rejection-handling binding without inventing a CARD culprit. Missing or incompatible governing bindings make the failure trace incomplete.

`failure_card_id` remains the canonical source-CARD identity **when a CARD's unhandled failure caused the record**. `failure_card_execution_id` identifies the corresponding concrete runtime CARD execution. For a CARD-caused failure, both are required and must resolve consistently through `card_executions[]`.

A failure that occurs before any CARD execution, such as JOB-scoped contract rejection, DECK setup failure, protected-machinery denial before CARD use, or another pre-CARD execution failure, must not invent a CARD identity. In that case the typed failing scope is authoritative and `failure_card_id` / `failure_card_execution_id` are absent.

An untaken branch references `governing_control_decision_id`. Prior fail-stop or another failure-caused non-reach references `governing_failure_record_id`. A catch-all control-or-failure ID is invalid because it erases the target namespace.

### Required causes for non-reach

Every legitimate not-reached CARD path or effect non-attempt must have a cause that actually prevents this concrete invocation under the frozen source/control/failure semantics. The reason selects the required typed cause:

- untaken branch requires `governing_control_decision_id` resolving to the concrete controlling decision;
- prior fail-stop or other failure-caused non-reach requires `governing_failure_record_id` resolving to the concrete failure whose active policy blocks this invocation;
- explicit frozen skip requires both `governing_skip_rule_id` and `skip_verification_evidence_id` under the skip contract;
- `CARD_NOT_REACHED` or a general equivalent requires one of those same validated cause forms. It has no cause-free exception.

The cause must resolve in this run and be applicable to the exact CARD/DECK execution and effect declaration being accounted for. Validate its control/dependency relation and causal ordering; an unrelated failure, a decision from another loop iteration, a handled failure whose policy permits continuation, or merely the existence of a record with that ID cannot establish non-reach. A cause inherited from an enclosing DECK/JOB must retain a resolvable, validated path to that enclosing cause. Reject unresolved, circular, contradictory, or unsupported cause chains. Multiple cause fields must agree under a frozen composition rule, not allow a producer to choose whichever label hides an omission.

For a verified skip cause, the evidence is subject-bound to the affected CARD execution or non-attempt record as appropriate. A parent's skip evidence alone cannot stand in for required effect accounting. For control/failure causes, any context or ordering evidence needed to validate that cause is required despite optional inventory notation; inability to establish causality fails closed. Missing or unverifiable causes produce structured execution/conformance failure, never successful accounting for an omitted reachable effect.

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
```

Every material input requires a stable `input_id` plus a canonical value or immutable content/artifact identity sufficient to identify what was actually consumed. Paths, URLs, dataset names, and model names are retrieval context, not immutable identity by themselves.

## Effect authorization

Every protected effect attempt has a contextual authorization decision:

```text
effect_authorization_records[]:
    effect_authorization_record_id
    effect_attempt_id
    declared_effect_id
    card_id
    card_execution_id
    required_capabilities[]
    granted_capabilities[]
    denied_capabilities[]
    capability_policy_id
    capability_policy_version
    authorization_status
    authorization_sequence_index?
```

### Declaration-bound authorization validation

Before accepting authorization, resolve the attempt's declaration using its canonical `declared_effect_id` and owning `card_id` in the hash-bound input. The trace declaration must match that canonical record. Then require:

```text
canonical_declaration.required_capabilities
    = trace_declaration.required_capabilities
    = effect_attempt.required_capabilities
    = effect_authorization.required_capabilities
```

This is exact equality of complete canonical capability sets, not subset containment, list-prefix equality, or agreement between runtime copies alone. Sets use canonical capability identities with deterministic ordering; duplicate or invalid entries fail validation rather than hiding missing capabilities. A runtime record cannot remove an extension-required capability, replace the set by a CARD-wide union, or choose a weaker declaration.

The declaration, attempt, and authorization must agree on declared effect and canonical CARD identity; the attempt's effect kind must match the declaration. Authorization and attempt must agree on `card_execution_id` and have reciprocal attempt/authorization IDs, and that execution must resolve to the same canonical CARD in this run. A record for another effect, retry, or invocation cannot authorize this attempt.

For successful authorization, every member of the canonical required set is granted, none is denied, the granted/denied sets are disjoint, and the contextual policy and successful status are valid for that exact attempt. Both the complete-set checks and the same-domain authorization-before-begin checks are required before the protected boundary. Any mismatch, unresolved declaration, missing grant, or invalid decision fails closed. For example, copying only `AI_MODEL` into both runtime records when the declaration requires `{AI_MODEL, NETWORK}` is rejected even if the copied subset is fully granted and its authorization precedes effect begin.

## Effect attempts

```text
effect_attempts[]:
    effect_attempt_id
    declared_effect_id
    card_id
    card_execution_id
    effect_kind
    required_capabilities[]
    effect_authorization_record_id
    sequence_index
    effect_begin_sequence_index?
    effect_end_sequence_index?
    completion_state
    backend_detail?
    observable_output_ids[]
    external_tool_ids[]?
```

`card_id` identifies the canonical declaration owner. `card_execution_id` identifies the concrete runtime invocation in which this attempt occurred. Attempts from different retries, loop iterations, calls, or repeated DECK executions must never collapse merely because they share one canonical CARD ID.

Authorization and effect-begin indices share one frozen monotonic event-order domain. Every protected attempt known to begin satisfies:

```text
authorization_sequence_index < effect_begin_sequence_index
```

Denied authorization has no effect-begin event. Generic attempt `sequence_index` is not authorization-order proof. A preceding authorization whose required set disagrees with the canonical declaration is still invalid.

### Effect completion states

The candidate states are mutually exclusive:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

Known completion takes precedence over uncertainty about broader external consequences. Completion belongs to the effect attempt, not to the enclosing CARD outcome.

## Effect non-attempt records

A declared effect may legitimately have no runtime attempt for a particular concrete CARD execution when control flow, prior failure, or another frozen rule prevents the effect from being attempted.

```text
effect_non_attempt_records[]:
    effect_non_attempt_record_id
    declared_effect_id
    card_id
    card_execution_id
    effect_kind
    non_attempt_reason
    governing_control_decision_id?
    governing_failure_record_id?
    governing_skip_rule_id?
    skip_verification_evidence_id?
    backend_detail?
```

The stable `effect_non_attempt_record_id` distinguishes separate non-attempt facts even when the same canonical CARD/effect declaration is encountered more than once. `card_execution_id` binds each non-attempt to the exact runtime invocation/path being accounted for.

Candidate legitimate reasons include untaken branch, prior fail-stop, CARD not reached, and explicit frozen skip, but every such record must satisfy [Required causes for non-reach](#required-causes-for-non-reach). Untaken control flow resolves to a `control_decision_id`; failure-caused non-reach resolves to a `failure_record_id`; `CARD_NOT_REACHED` requires a validated typed control/failure cause or a verified frozen skip. The generic reason alone is never sufficient.

An explicit frozen skip requires both `governing_skip_rule_id` and `skip_verification_evidence_id`. They resolve to a `rule_records[]` entry of kind `EFFECT_SKIP` and passing `validation_evidence[]` for this exact non-attempt record, declaration, CARD execution, and active semantic/policy context. The rule must explicitly permit this skip and its applicability must be verified before the skip is applied. Optional control/failure references, a free-text reason, or a rule valid only for another invocation cannot substitute for these records. An unknown, missing, inapplicable, or unverifiable skip rule forces structured conformance failure; a reachable required effect omitted without a valid skip rule is a backend omission, not success.

`BACKEND_OMISSION_DETECTED` or frozen equivalent means a reachable required effect was omitted. It forces structured execution/conformance failure and cannot coexist with successful enclosing execution.

### Unconditional declaration accounting

Declaration completeness is not an optional audit mode.

For every selected concrete `card_execution_id`, every applicable canonical `effect_requirement` owned by that CARD must resolve to exactly one of these provenance outcomes:

1. one or more identified `effect_attempts[]` records for that `card_execution_id` when execution/retry semantics produce attempts;
2. exactly one identified legitimate `effect_non_attempt_records[]` record for that `card_execution_id` when no attempt occurred; or
3. a structured execution/conformance failure if complete accounting itself cannot be established or a reachable required effect was omitted.

A declared effect with neither an attempt nor a legitimate non-attempt record is always incomplete provenance and fails closed. Profiles, backends, optimization modes, or deployment settings may not disable this requirement.

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
    effect_attempt_ids[]?
    output_ids[]?
```

For a material external tool, service, model, prover, process, or instrument, `tool_name_or_service` and a mutable endpoint are labels/locators only. `material_identity_status = IDENTIFIED` requires an immutable or versioned `material_identity_value`, such as an executable/content hash, tool version bound strongly enough for the active claim, model/version ID, immutable artifact ID, or frozen equivalent.

If exact material identity cannot be established, record `material_identity_status = UNAVAILABLE` (or a frozen equivalent) and the strongest replay/evidence claim must be weakened or rejected according to the frozen policy. Identity unavailability may never be silently treated as full reproducibility.

Extension resolution identifies the adapter/profile contract. It does not substitute for the actual tool, service, model, prover, process, or instrument identity.

## Cache reuse provenance

```text
cache_reuse_records[]:
    cache_reuse_record_id
    classification
    source_card_ids[]
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

For `VERIFIED_REUSE`, `legality_rule_id` and `verification_evidence_id` are mandatory. They resolve to a `rule_records[]` entry of kind `CACHE_SUBSTITUTION` and passing, content-bound `validation_evidence[]` for this exact cache-reuse record. The record must identify the reused computation/artifact and the checked cache key/artifact content, either directly through the corresponding hash fields or through resolvable immutable cached-output/producer provenance. Evidence verifies the material cache identity and substitution legality against the current inputs, contracts, and execution context before substitution is applied. A matching hash or a producer's `VERIFIED_REUSE` label alone is not verification evidence.

Ordinary result substitution is effect-free by default. Effectful reuse additionally requires that the referenced rule is the separately frozen replay/cache semantic covering this operation's declared effects, contextual authorization, ordering, failure, attempt provenance, output attribution, and external state behavior. A generic cache rule does not permit effectful substitution.

An `UNVERIFIED_HIT` remains diagnostic and cannot satisfy a CARD or produce a verified-reuse output. It must undergo successful verification before reuse, trigger cold execution, or fail closed. Missing, stale, mismatched, failed, or unavailable verification evidence invalidates `VERIFIED_REUSE`; optional notation for other classifications never waives its conditions.

Verified cache reuse does not prove cold reconstructability.

## Result trace

Results are identified records rather than bare hashes plus one shared semantic class.

```text
outputs[]:
    output_id
    result_binding?
    artifact_hash
    artifact_location?
    semantic_class
    status
    producer_card_ids[]
    producer_card_execution_ids[]
    input_ids[]
    effect_attempt_ids[]?
    external_tool_ids[]?
    backend_selection_scope_ids[]
    generated_artifact_ids[]?
    result_determinism_scope_ids[]
    numeric_scope_ids[]
    randomness_scope_ids[]
    failure_behavior_binding_ids[]
    cache_reuse_record_ids[]?
    evidence_status?
```

`producer_card_ids[]` records the canonical semantic producers. `producer_card_execution_ids[]` records the concrete runtime CARD execution(s) that actually produced, materially supplied, or published the output. Every concrete producer resolves through `card_executions[]` to its `deck_execution_id` and canonical `card_id`.

The concrete producer-execution relation is required whenever runtime producer attribution is part of the trace contract, including whenever the same canonical CARD can execute more than once. A canonical CARD ID alone is insufficient for loops, retries, repeated calls, or repeated DECK execution.

`input_ids[]` identifies the exact immutable inputs materially contributing to the output. Execution-wide input availability is not a substitute.

`effect_attempt_ids[]`, where applicable, identifies concrete effect attempts that produced or exposed the output. Those attempts reciprocally list the output in `observable_output_ids[]`.

`external_tool_ids[]`, where applicable, identifies the exact material tools/services/models/provers that supplied the output.

`generated_artifact_ids[]` identifies the exact executable/kernel/bytecode artifact that ran where applicable. The artifact links onward to its optimization provenance, its direct toolchain producer, and its ordered transitive toolchain ancestry.

`failure_behavior_binding_ids[]` resolves to the exact identified failure-policy records that governed the producer path. A generic computation `scope_id` cannot substitute for this record-level join.

The execution-contract scope arrays resolve directly to the stable type-specific scope-record keys described above.

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

No evidence promotion is implicit. Compare the claimed class against the original hash-bound semantic producers and their actual evidence, not just a producer-written output label. For any epistemic change that is not class-preserving under the frozen semantic rule, including simulation/TEST/AI output claimed as VALIDATION or PROOF, both `evidence_rule_id` and `evidence_validation_id` are mandatory. Classes are not assumed to form a numeric strength ranking; every proposed non-preserving transition needs its own applicable rule.

`evidence_rule_id` resolves to an accepted, versioned, content-bound `EPISTEMIC_TRANSITION` rule. `evidence_validation_id` resolves to passing `validation_evidence[]` with `subject_kind = OUTPUT` and this exact `output_id`. Its evaluated context binds the output artifact hash, original source class bindings, concrete producer executions, contributing input/evidence identities, requested target evidence class/status, and applicable evidence contract. The substantive evidence required by that rule must be retrievable, hash-verifiable, and checked with the identified accepted verifier before the stronger/different claim is published. For a PROOF claim this includes the applicable proposition, proof/certificate, and formal checking obligations required by the frozen proof contract; test success, model confidence, or an operational `PASS` record is not a replacement.

A missing accepted transition rule means the promotion is rejected. Unknown, wrong-kind, stale, unavailable, failed, context-mismatched, or post-publication evidence likewise rejects the claim. Assigning the stronger class directly to `outputs[].semantic_class`, omitting `evidence_status`, or routing it through an adapter cannot bypass the source-to-output class check. A distinct validation/proof CARD may produce separately identified evidence under its frozen semantics; it does not retroactively relabel the original simulation or TEST artifact. Class-preserving records need not invent transition evidence, but remain subject to their own evidence-status validation rules.

## Failure trace

A failed execution retains enough information to distinguish the enclosing outcome from prior completed effects or machinery use without inventing a CARD culprit.

```text
run_id
execution_status
job_id
job_status
deck_executions[]
card_executions[]
control_decisions[]
failure_records[]
failure_behavior_bindings[]
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
rule_records[]
validation_evidence[]
observable_output_ids[]
```

A failure trace includes the backend-selection scope and decision ledgers referenced by its machinery authorization/use records, including denied candidates and fallback predecessors, not just the final target. Every `failure_behavior_binding_ids[]` reference resolves to the retained governing policy bindings. A standalone failure manifest must preserve the complete transitive closure of its references, including applicable rules, evidence, requirements, and observable outputs, either inline or through retrievable content-bound trace records. An unresolvable ID or an unbound mutable external trace link is incomplete provenance.

The primary failure resolves through `failure_records[]` to an always-present typed failing scope. `failure_card_id` is canonical only for CARD-caused failures and is absent for legitimate pre-CARD failures.

Effect-attempt completion is independent of CARD success. A completed process effect may coexist with a failed CARD if the process completed and returned a non-success status under the active contract.

Protected machinery authorization outcomes are not enough by themselves. If protected machinery actually began, `machinery_use_records[]` preserve the concrete use, its CARD-execution or pre-CARD initiating-scope relation, and ordering evidence.

## Provenance validation rules

At minimum, a future validator should reject or fail closed when:

- stable JOB/DECK/CARD identities are missing or silently renumbered;
- an epistemic class becomes detached from its CARD;
- a declared effect loses its per-effect capability binding;
- declaration, attempt, and authorization capability sets do not exactly match the hash-bound canonical declaration, or their owner/execution/reciprocal identity links disagree;
- a protected machinery requirement disappears before MORPH;
- a machinery-requirement mapping cannot identify the exact source and lower requirement records at either lowering boundary when multiple requirements share a scope;
- a result-binding map cannot represent the actual split/fusion cardinality;
- a lowering scope mapping uses ambiguous untyped endpoints where namespaces can overlap;
- a required extension ownership mapping becomes positional or implicit;
- a material resolved extension lacks its exact profile version, contract hash, implementation-component identities, or resolvable owning requirement and governed scopes;
- a requested execution contract differs from its effective contract without resolvable, versioned, applicable pre-execution authority and passing context-bound evidence;
- a failure-policy semantic change is disguised as representation mapping or lacks the required pre-application transition evidence;
- a rule/evidence reference has the wrong kind, subject, context, content hash, or order;
- a fallback lacks an actual predecessor, an applicable frozen BACKEND_FALLBACK rule, or passing context-bound evidence before its decision is applied;
- output scope IDs do not resolve to stable type-specific scope records;
- an output or failure's failure-behavior reference does not resolve to the exact applicable stable `failure_behavior_binding_id`;
- a failed CARD/DECK outcome lacks its exact `failure_record_id` or substitutes matching class/stage summaries;
- a concrete output cannot be joined to the CARD execution that produced it;
- a CARD-governed machinery use cannot be joined to its concrete participating CARD executions;
- a genuine pre-CARD machinery use fabricates CARD executions or omits its typed initiating runtime scope;
- an EXTERNAL-ENTROPY randomness scope cannot resolve to the exact protected RANDOM acquisition attempt(s), and to immutable entropy input identity where required by the audit/replay contract;
- an effect attempt or non-attempt cannot be joined to its concrete `card_execution_id`;
- a non-attempt record has no stable identity;
- an explicit skip lacks a resolvable frozen skip rule and passing applicability evidence for that invocation;
- CARD_NOT_REACHED or another non-reach reason has no validated typed control/failure/verified-skip cause for the exact invocation;
- any applicable declared effect lacks both attempt and legitimate non-attempt accounting for a selected concrete CARD execution;
- an effect begins before its authorization completed;
- protected machinery begins before every applicable authorization completed;
- denied protected machinery nevertheless has a use-start record;
- a reachable required effect is omitted;
- an effect non-attempt record points to an untyped or unresolved cause;
- a failure lacks a typed failing-scope identity;
- a failure trace omits referenced backend-selection scopes, decisions, or other records needed to resolve its provenance;
- a pre-CARD failure fabricates `failure_card_id`, or a CARD-caused failure omits the matching canonical/concrete CARD identities;
- cold execution and cache reuse become indistinguishable;
- `VERIFIED_REUSE` lacks a matching frozen legality rule, checked cache identity, or passing verification evidence, or an unverified hit supplies an output;
- an optimized artifact cannot be joined to its optimization record;
- optimization legality witnesses are opaque labels or do not verify against the exact IR pair, complete transformation sequence, and active contracts;
- a generated artifact omits its exact production `backend_selection_decision_id` or is attributed to the final fallback decision instead;
- a generated artifact cannot resolve its direct producer toolchain invocation;
- a generated artifact's ordered toolchain ancestry is inconsistent with the direct generated-artifact input/output graph under the active profile;
- a transitive toolchain ancestor is falsely recorded as directly outputting a final artifact merely to satisfy chain membership;
- a toolchain invocation omits material tool identity, immutable non-generated `input_ids[]`, or material build flags/configuration required by the active reproducibility claim;
- output evidence status contradicts semantic class;
- an epistemic promotion lacks its applicable frozen rule and passing subject/content-bound substantive evidence before claim publication;
- a mutable input locator substitutes for immutable input identity;
- a material external tool has neither immutable/versioned material identity nor an explicit identity-unavailable state that weakens the claim.

### Conformance cases for the future trace validator

These are documentation acceptance cases for the applicable roadmap gates, not a claim that executable validation already exists. They apply equally to canonical traces and their manifest, failure, and agent-facing projections.

| Case | Accept only when | Reject mutations |
| --- | --- | --- |
| Multi-capability effect | Canonical declaration, trace declaration, attempt, and authorization all require `{AI_MODEL, NETWORK}`; every required capability is granted to the same attempt before begin. | Copy only `AI_MODEL` into both runtime records; truncate the trace declaration too; substitute another declaration or retry; omit or deny `NETWORK`. |
| Failure-policy change | An accepted CONTRACT_TRANSITION rule and passing evidence authorize the exact fail-stop-to-retry binding before activation; a representation-only rename instead proves unchanged semantics under its mapping rule. | Missing/stale rule; late evidence; evidence for another binding; continue disguised as representation mapping; requested/effective labels whose content changed. |
| CARD not reached | A typed controlling decision, blocking failure, or verified skip actually prevents this exact invocation and its effect under the active contract. | No cause; cause from another loop iteration; handled nonblocking failure; dangling/circular cause; unverified parent skip. |
| Backend fallback | The actual earlier denied candidate, accepted BACKEND_FALLBACK rule, and passing subject-bound evidence permit this target switch before the fallback decision; protected use is independently authorized. | Arbitrary/stale rule ID; wrong predecessor/scope; late validation; explicit target disallowing fallback; replacement mislabeled initial selection. |
| Epistemic transition | The accepted EPISTEMIC_TRANSITION rule's substantive evidence is verified for this exact output, source class, producer executions, and requested claim before publication. | TEST success claimed as PROOF; missing proof obligations; different artifact's evidence; direct relabeling of output semantic class; omission of evidence status to evade the check. |
| Optimization legality | Typed content-bound witnesses verify the exact IR pair, complete pass sequence, and active numeric/determinism/randomness/failure and other material contracts before optimized-variant acceptance. | Opaque `PASS`; wrong IR pair; changed tolerance or failure policy; incomplete pass coverage; unavailable verifier/evidence; finite tests represented as universal proof. |
| Failed CARD outcome | The failed execution's `failure_record_id` resolves to its exact governing failure or validated propagation relation. | Class/stage summaries only; another invocation's same-class failure; unresolved ID; fake CARD failure for a merely blocked path. |
| Extension resolution | Each material resolution retains exact version, contract hash, complete implementation-component identities, owning requirement refs, and actual governed scopes; the selected version satisfies the source range. | Profile/range only; missing adapter/hook identity; wrong owner; incompatible version/hash; identity-mapping omission used to erase the material resolution. |

For every case involving referenced rules or evidence, also reject missing content, hash mismatch, an unaccepted authority/verifier, a wrong subject namespace, and evidence that cannot establish the required pre-application ordering. A positive example is conditional on an actually accepted frozen rule; the table does not create one by example.

## Principle

> Trace meaning, not just bytes. Preserve stable semantic identity, typed scope correspondence, concrete execution identity, unconditional declared-effect accounting, authorization-before-use ordering, truthful direct build edges, transitive toolchain ancestry, and the exact evidence chain from immutable inputs through lowerings, optimization, toolchain invocations, and machinery to each output or failure.
