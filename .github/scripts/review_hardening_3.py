from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected 1 occurrence, found {count}: {old[:120]!r}")
    p.write_text(text.replace(old, new, 1))
    print(f"patched {path}: {old.splitlines()[0]}")


# First lowering: full owner paths and owner-qualified machinery references.
replace_once(
    "docs/SEMANTIC-TO-CORE-LOWERING.md",
    """machinery_requirement_lowering_decisions[]:
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
""",
    """machinery_requirement_lowering_decisions[]:
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
""",
)
replace_once(
    "docs/SEMANTIC-TO-CORE-LOWERING.md",
    """The source requirement IDs resolve in the input Semantic IR; the lower requirement IDs resolve in the resulting QSOL-CORE representation. The two IR hashes and typed owning scopes qualify those identities. Both ID sets are nonempty, deterministic, and duplicate-free. Unrelated requirements sharing an owning scope use separate mapping groups; they must not be paired by array position or inferred from shared source CARDs.
""",
    """Every source/Core endpoint carries its complete representation-relative `owner_scope_path[]`. Source and lower machinery requirements are owner-qualified composite references, so repeated local requirement IDs such as `gpu` remain distinct across sibling scopes. The source references resolve in the input Semantic IR and the lower references in the resulting QSOL-CORE representation. Both reference sets are nonempty, deterministic, duplicate-free by complete qualified identity, and never paired by array position or inferred from shared source CARDs.
""",
)

# Second lowering: full representation-relative containment paths and composite requirement refs.
for path in ("docs/VECTOR-AND-DATAFLOW.md", "docs/TRACE-AND-PROVENANCE.md"):
    replace_once(
        path,
        """core_scope_refs[]:
    scope_kind
    scope_id

vector_dataflow_scope_refs[]:
    scope_kind
    scope_id
""",
        """core_scope_refs[]:
    owner_scope_path[]:
        scope_kind
        scope_id

vector_dataflow_scope_refs[]:
    owner_scope_path[]:
        scope_kind
        scope_id
""",
    )
    replace_once(
        path,
        """machinery_requirement_mapping_decisions[]:
    core_scope_refs[]
    vector_dataflow_scope_refs[]
    source_machinery_requirement_ids[]
    lower_machinery_requirement_ids[]
    source_card_ids[]
    mapping_rule_id""",
        """machinery_requirement_mapping_decisions[]:
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
    mapping_rule_id""",
    )

replace_once(
    "docs/VECTOR-AND-DATAFLOW.md",
    """Every second-lowering mapping family identifies both ends with typed scope references. A bare ID is insufficient because JOB, DECK, CARD, Core-region, Vector/Dataflow-region, kernel, and backend-unit namespaces may overlap.
""",
    """Every second-lowering mapping family identifies both ends with complete representation-relative containment paths. A bare ID or one-level `{ scope_kind, scope_id }` pair is insufficient because enclosing Core/Vector scopes may each reuse local CARD, region, kernel, or backend-unit IDs. The terminal path element is the referenced scope and every ancestor needed to disambiguate it participates in identity.
""",
)
replace_once(
    "docs/VECTOR-AND-DATAFLOW.md",
    """The source/lower requirement-ID arrays are cardinality-aware. They support preservation, a requirement split across lower regions, or a frozen legal fusion while retaining which exact requirement and capability set reached which lower unit. Scope correspondence alone is insufficient when one Core scope owns multiple machinery requirements.
""",
    """The source/lower machinery-requirement arrays are cardinality-aware owner-qualified references. Each local requirement ID is structurally paired with its complete owning path, so preservation, split, or frozen legal fusion retains exactly which requirement and capability set reached each lower unit without positional inference. Scope correspondence alone is insufficient when local IDs can repeat.
""",
)
replace_once(
    "docs/TRACE-AND-PROVENANCE.md",
    """The second lowering preserves exactly which typed Core scope maps to which typed Vector/Dataflow scope. Bare arrays such as `core_scope_ids[]` and `vector_dataflow_scope_ids[]` are not sufficient because JOB, DECK, CARD, region, kernel, and generated-unit namespaces may overlap.
""",
    """The second lowering preserves exactly which Core scope maps to which Vector/Dataflow scope using complete representation-relative containment paths. Bare IDs or one-level kind/local-ID pairs are insufficient because enclosing Core and Vector/Dataflow scopes may independently reuse CARD, region, kernel, and generated-unit IDs. Every ancestor needed to distinguish the terminal local scope participates in mapping identity.
""",
)
replace_once(
    "docs/TRACE-AND-PROVENANCE.md",
    """The source/lower requirement-ID arrays are cardinality-aware. Scope correspondence and source CARD identity do not identify which requirement was mapped when one Core scope owns several machinery requirements. Each lower requirement must preserve the source target selector/class and complete capability set or identify the frozen rule that transformed them.
""",
    """The source/lower machinery-requirement arrays contain complete owner-qualified references rather than parallel local IDs. Scope correspondence and source CARD identity do not identify which requirement was mapped when local requirement IDs can repeat. Each lower qualified requirement must preserve the corresponding source target selector/class and complete capability set or identify the frozen rule that transformed them.
""",
)

# Owner-qualified epistemic classes and source contract bindings.
replace_once(
    "docs/TRACE-AND-PROVENANCE.md",
    """epistemic_class_bindings[]:
    card_id
    semantic_class
""",
    """epistemic_class_bindings[]:
    owner_scope_path[]:
        scope_kind
        scope_id
    card_id
    semantic_class
""",
)
replace_once(
    "docs/TRACE-AND-PROVENANCE.md",
    """Separate `card_ids[]` and `epistemic_classes[]` arrays are not an acceptable positional association. Epistemic class is bound directly to canonical CARD identity.
""",
    """Separate `card_ids[]` and `epistemic_classes[]` arrays are not an acceptable positional association. Epistemic class is bound to the CARD's complete ordered absolute `owner_scope_path[]` plus local `card_id`; the path terminates at that CARD. Sibling DECKs may therefore each contain local `CARD 7` with different research classes without collision. Missing, truncated, reordered, or owner-mismatched class paths fail closed.
""",
)
replace_once(
    "docs/TRACE-AND-PROVENANCE.md",
    """result_determinism_bindings[]:
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
""",
    """result_determinism_bindings[]:
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
    owner_scope_path[]:
        scope_kind
        scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
    transition_evidence_id?
""",
)
replace_once(
    "docs/TRACE-AND-PROVENANCE.md",
    """The owning scope may be a JOB, DECK, CARD, or another scope frozen by the semantic model. Distinct source requirements may not be collapsed into one execution-wide declaration unless a frozen normalization proves that collapse is lossless. Failure bindings obey the same [failure-policy transition conditions](#failure-policy-transitions) here and in the execution-scope inventory.
""",
    """The owning source scope is identified by its complete ordered absolute `owner_scope_path[]`, not a bare kind/local ID. The path terminates at the JOB, DECK, CARD, or other frozen scope that owns the contract, so repeated local IDs under sibling containers remain distinct. Distinct source requirements may not be collapsed into one execution-wide declaration unless a frozen normalization proves that collapse is lossless. Failure bindings obey the same [failure-policy transition conditions](#failure-policy-transitions) here and in the execution-scope inventory.
""",
)

# Reproducibility inputs: concrete consumers/acquirers and reciprocal CARD execution links.
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    """inputs[]:
    input_id
    input_kind
    canonical_value?
    content_hash?
    artifact_id_or_version?
    location?
    media_or_schema_type?
    source_card_ids[]?
""",
    """inputs[]:
    input_id
    input_kind
    canonical_value?
    content_hash?
    artifact_id_or_version?
    location?
    media_or_schema_type?
    source_card_ids[]?
    consumer_card_execution_ids[]
    consumer_scope_refs[]?
    effect_attempt_ids[]
""",
)
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    "Paths, URLs, dataset names, and model names are retrieval context, not immutable identity by themselves.\n",
    "Paths, URLs, dataset names, and model names are retrieval context, not immutable identity by themselves. `consumer_card_execution_ids[]` identifies the exact current-run CARD invocations that consumed the value and reciprocates `card_executions[].input_ids[]`, including failed/output-free invocations. `effect_attempt_ids[]` identifies concrete effect acquisitions and reciprocates `effect_attempts[].acquired_input_ids[]`. Genuine pre-CARD setup uses typed `consumer_scope_refs[]`; canonical `source_card_ids[]` is summary context only.\n",
)
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    """card_executions[]:
    card_execution_id
    deck_execution_id
    card_id
    card_status
    execution_order_index?
""",
    """card_executions[]:
    card_execution_id
    deck_execution_id
    card_id
    card_status
    input_ids[]
    cache_reuse_record_ids[]?
    execution_order_index?
""",
)
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    "`card_id` identifies the canonical semantic CARD. `card_execution_id` identifies one concrete runtime execution. This distinction is material for loops, retries, calls, repeated DECK execution, or another construct that can execute the same CARD more than once.\n",
    "`card_id` identifies the canonical semantic CARD. `card_execution_id` identifies one concrete runtime execution. This distinction is material for loops, retries, calls, repeated DECK execution, or another construct that can execute the same CARD more than once. `input_ids[]` reciprocally identifies the material inputs consumed by this invocation, while `cache_reuse_record_ids[]` reciprocally identifies cache decisions applying to this current-run invocation.\n",
)
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    """cache_reuse_records[]:
    cache_reuse_record_id
    classification
    source_card_ids[]
    reused_computation_id?
""",
    """cache_reuse_records[]:
    cache_reuse_record_id
    classification
    source_card_ids[]
    card_execution_ids[]
    reused_computation_id?
""",
)
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    "Candidate classifications are `COLD_EXECUTION`, `VERIFIED_REUSE`, and `UNVERIFIED_HIT`, or frozen equivalents. For `VERIFIED_REUSE`, both `legality_rule_id` and `verification_evidence_id` are mandatory and resolve to the shared rule/evidence ledgers.\n",
    "Candidate classifications are `COLD_EXECUTION`, `VERIFIED_REUSE`, and `UNVERIFIED_HIT`, or frozen equivalents. `card_execution_ids[]` identifies the concrete current-run invocation(s) to which this cache decision applies and reciprocates `card_executions[].cache_reuse_record_ids[]`; one cold retry and one reused retry cannot collapse merely because they share a canonical CARD. For `VERIFIED_REUSE`, both `legality_rule_id` and `verification_evidence_id` are mandatory and resolve to the shared rule/evidence ledgers.\n",
)

# Failure-policy transition evidence.
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    """failure_behavior_bindings[]:
    failure_behavior_binding_id
    scope_kind
    scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
""",
    """failure_behavior_bindings[]:
    failure_behavior_binding_id
    scope_kind
    scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
    transition_evidence_id?
""",
)
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    "The frozen default fail-stop behavior has a stable identity when it materially governs execution. A manifest must not infer effective failure policy merely from skipped CARDs or DECKs.\n",
    "The frozen default fail-stop behavior has a stable identity when it materially governs execution. A manifest must not infer effective failure policy merely from skipped CARDs or DECKs. When requested and effective failure semantics differ, the rule must resolve to accepted content-bound `CONTRACT_TRANSITION` authority and `transition_evidence_id` must resolve to passing evidence for this exact binding, validated before the effective policy is applied. A representation-only mapping cannot authorize fail-stop becoming continue, retry, or compensate.\n",
)

# Backend fallback projections: rule plus passing subject-bound validation evidence.
for path in ("docs/DETERMINISM-AND-REPRODUCIBILITY.md", "docs/BACKENDS-AND-MORPHING.md"):
    replace_once(
        path,
        """    predecessor_selection_decision_id?
    fallback_rule_id?
    machinery_authorization_record_ids[]?
""",
        """    predecessor_selection_decision_id?
    fallback_rule_id?
    fallback_evidence_id?
    machinery_authorization_record_ids[]?
""",
    )
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    "A denied protected target followed by an authorized fallback remains two ordered decisions. The first decision is not overwritten by the fallback.\n",
    "A denied protected target followed by an authorized fallback remains two ordered decisions. The first decision is not overwritten by the fallback. A fallback requires both an accepted content-bound `BACKEND_FALLBACK` rule and passing `fallback_evidence_id` bound to this exact decision, predecessor, target context, and active policy/contracts, with validation preceding fallback selection/application.\n",
)
replace_once(
    "docs/BACKENDS-AND-MORPHING.md",
    "A denied protected target followed by an authorized fallback must remain represented as **two decisions**, not as one record whose `selected_backend` is overwritten. The fallback decision references its predecessor and the frozen `fallback_rule_id` that permitted the transition. The denied decision retains its machinery-authorization record and status; the later decision retains its own authorization record where required.\n",
    "A denied protected target followed by an authorized fallback must remain represented as **two decisions**, not as one record whose `selected_backend` is overwritten. The fallback decision references its predecessor, an accepted content-bound `BACKEND_FALLBACK` rule through `fallback_rule_id`, and passing subject-bound `fallback_evidence_id` establishing applicability to this exact predecessor/target/policy context before selection. The denied decision retains its machinery-authorization record and status; the later decision retains its own authorization record where required. Unknown, stale, mismatched, self-issued, or late fallback evidence fails closed.\n",
)

# Evidence promotion projection: exact validation record required for non-preserving transitions.
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    """evidence_status:
    evidence_class      # TEST / VALIDATION / PROOF / frozen equivalent
    status
    evidence_rule_id?
""",
    """evidence_status:
    evidence_class      # TEST / VALIDATION / PROOF / frozen equivalent
    status
    evidence_rule_id?
    evidence_validation_id?
""",
)
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    "`evidence_class` must be compatible with the output's `semantic_class` and explicit evidence transition. Generic output `status` is non-epistemic and cannot promote TEST into VALIDATION or PROOF.\n",
    "`evidence_class` must be compatible with the output's `semantic_class` and explicit evidence transition. Generic output `status` is non-epistemic and cannot promote TEST into VALIDATION or PROOF. Any non-class-preserving transition requires both `evidence_rule_id` resolving to accepted content-bound `EPISTEMIC_TRANSITION` authority and `evidence_validation_id` resolving to passing evidence for this exact output, artifact hash, original source classes, concrete producers, contributing evidence/inputs, target evidence class, and claim-publication event.\n",
)
replace_once(
    "README.md",
    "When present, `evidence_status` is class-discriminated, conceptually carrying `evidence_class`, evidence `status`, and optional `evidence_rule_id`. It must be compatible with the output's `semantic_class` and any explicit evidence transition. Generic output `status` remains an execution/artifact state and cannot by itself promote TEST to VALIDATION or VALIDATION to PROOF.\n",
    "When present, `evidence_status` is class-discriminated, conceptually carrying `evidence_class`, evidence `status`, optional `evidence_rule_id`, and optional `evidence_validation_id`. It must be compatible with the output's `semantic_class` and any explicit evidence transition. For every non-class-preserving transition, both IDs become mandatory and must resolve to the accepted content-bound rule plus passing subject-bound evidence for this exact output/artifact/producers/context before publication. Generic output `status` remains an execution/artifact state and cannot by itself promote TEST to VALIDATION or VALIDATION to PROOF.\n",
)

# Optimization legality witnesses are structured and verifiable in the reproducibility projection.
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    """    transformation_sequence[]
    legality_witnesses[]
    vectorization_decisions[]?
""",
    """    transformation_sequence[]
    legality_witnesses[]:
        legality_witness_id
        witness_kind
        validation_evidence_id
    vectorization_decisions[]?
""",
)
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    "An optimization profile is configuration, not evidence of what actually ran.\n",
    "Each legality witness is an identified, typed, verifiable record rather than an opaque label. `validation_evidence_id` resolves to passing content-bound evidence for this exact optimization record, binding the reference/optimized IR pair, ordered transformation sequence, active numeric/determinism/randomness/failure contracts, material effects/sequencing/extensions/machinery/inputs/target context, accepted `OPTIMIZATION_LEGALITY` rule, and immutable/versioned verifier identity. A witness for another IR pair or context is invalid.\n\nAn optimization profile is configuration, not evidence of what actually ran.\n",
)

# Reproducibility lowering prose follows complete paths + composite requirement refs.
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    """At the second boundary, every applicable mapping family uses typed `core_scope_refs[]` and `vector_dataflow_scope_refs[]`. Bare scope-ID arrays are not sufficient where namespaces can overlap.

For `machinery_requirement_mapping_decisions[]`, typed scope endpoints are necessary but not sufficient: each mapping also carries `source_machinery_requirement_ids[]` and `lower_machinery_requirement_ids[]` so several requirements owned by one Core scope cannot be confused. Those arrays preserve the exact requirement/capability-set correspondence through preservation, split, or frozen legal fusion.
""",
    """At the second boundary, every applicable mapping family uses `core_scope_refs[]` and `vector_dataflow_scope_refs[]` whose entries carry complete representation-relative `owner_scope_path[]` values. Bare IDs and one-level kind/local-ID pairs are insufficient when enclosing Core/Vector scopes can reuse local IDs.

For `machinery_requirement_mapping_decisions[]`, complete scope paths are necessary but not sufficient: each mapping also carries owner-qualified `source_machinery_requirement_refs[]` and `lower_machinery_requirement_refs[]`, structurally pairing every local machinery requirement ID with its complete owning path. This preserves exact requirement/capability-set correspondence through preservation, split, or frozen legal fusion without positional inference.
""",
)

# Agent-facing toolchain schema: exact IR input array is always explicit.
replace_once(
    "AGENTS.md",
    """    environment_or_config_hash?
    input_ir_hashes[]?
    input_ids[]
""",
    """    environment_or_config_hash?
    input_ir_hashes[]
    input_ids[]
""",
)
replace_once(
    "AGENTS.md",
    "`input_ids[]` resolves to immutable `inputs[]` records for every material dependency not generated in this run, including prebuilt objects, static libraries, headers, startup files, sysroots, and implicit toolchain inputs.\n",
    "`input_ir_hashes[]` is always explicit: it is nonempty with the exact content hash(es) whenever the invocation directly consumes IR, including ordinary non-optimized code generation, and empty only when that invocation consumes no IR. Tool/flags/target/output metadata cannot substitute for this direct content-bound IR edge.\n\n`input_ids[]` resolves to immutable `inputs[]` records for every material dependency not generated in this run, including prebuilt objects, static libraries, headers, startup files, sysroots, and implicit toolchain inputs.\n",
)
