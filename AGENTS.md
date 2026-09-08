# AGENTS.md

This file is guidance for AI coding/research agents working in QSOL-MORPH.

## Project mission

QSOL-MORPH is a deterministic code-morphing architecture for human–AI research computing.

Core mnemonic:

```text
QSOL describes intent.
QSOL-CORE defines meaning.
QSOL-MORPH chooses machinery.
```

## Current phase

The repository is specification-first and pre-alpha.

Do not implement compiler/runtime/backend code unless the active task explicitly belongs to an implementation phase in `ROADMAP.md`.

PR #1 is documentation foundation. PR #2 is reserved for locking core invariants.

QSOL-CORE implementation must not precede its normative operational specification, including frozen result-determinism and randomness/RNG semantics.

Semantic IR → QSOL-CORE lowering must not be invented inside a backend. Its normative lowering specification and reference implementation must exist before MORPH code-generation backends are treated as end-to-end conforming.

The mandatory Vector/Dataflow IR stage must preserve the complete supported QSOL-CORE surface. Its normative specification must precede the reference Core→Vector/Dataflow lowering, and backends may not bypass that lowering for control, calls, effects, scalar operations, capabilities, machinery requirements, failure behavior, or contracts merely because they are not vectorizable.

Human `.qsl` parsing/serialization must not be implemented from illustrative examples. A normative QSOL text profile must first freeze grammar and source-to-Semantic-IR mapping.

QX-POSIX implementation must not precede its normative profile contract.

Generic GPU backend work must not define accelerator semantics opportunistically; the generic GPU execution contract is frozen before vendor backends. QX-CUDA control implementation must not precede its own versioned normative control contract.

## Semantic rules for agents

When proposing changes:

1. preserve the distinction between meaning and machinery;
2. preserve research/epistemic classes;
3. prefer one canonical concept over synonyms;
4. keep external effects explicit;
5. keep backend-specific controls out of core unless explicitly justified;
6. treat determinism, numeric contracts, randomness, failure behavior, authorization, and provenance as first-class requirements;
7. do not call a performance improvement an optimization unless the required semantics remain valid;
8. do not promote simulation/test/AI output into stronger evidence classes without an explicit frozen rule;
9. bind epistemic class and status to each identified output rather than one execution-wide result label;
10. use class-discriminated `evidence_status` and reject evidence claims incompatible with an output's semantic class;
11. do not silently weaken CARD, DECK, or JOB failure behavior;
12. require successful authorization of **every** capability required by a protected external effect before that effect begins;
13. preserve the explicit effect → complete capability-set association and owner-qualify every declared effect by its complete ordered representation-relative `owner_scope_path[]`; local CARD/operation/effect IDs are not globally unique and must not replace that path;
14. give each concrete protected effect attempt its own identified authorization record; execution-wide capability sets are summaries only;
15. keep protected machinery selection separate from external effects, and require every applicable machinery capability before protected machinery use begins;
16. preserve explicit `machinery_requirements[]`; do not synthesize fake effects merely to authorize GPU/CUDA or another protected target;
17. preserve result bindings used by dependent CARDs across canonicalization, serialization, and lowering;
18. use cardinality-aware result-binding maps at **both** mandatory lowering boundaries when identities are preserved or transformed;
19. treat a potentially failing pure operation as ordering-relevant under fail-stop semantics unless it is proven total;
20. do not dead-eliminate a potentially failing operation merely because its result is unused;
21. preserve stable JOB/DECK/CARD identifiers plus all canonical semantic/enforcement fields across any serialization claiming semantic losslessness;
22. preserve result-determinism, numeric, randomness, failure-behavior, machinery, and extension requirements on the canonical scope that owns them;
23. preserve canonical tagged `sequencing_constraints[]`; effect-order/failure-order views must not replace or truncate the canonical field;
24. distinguish backend selection from optional vendor-control profiles (`CUDA` != `QX-CUDA`, POSIX execution != a compiler backend);
25. distinguish extension availability/functionality from runtime capability authorization; activating an extension never grants permission;
26. preserve the explicit Semantic IR → QSOL-CORE lowering boundary; do not let a backend reinterpret rich semantic CARDs privately;
27. preserve execution-relevant qualifiers through Semantic→Core lowering unless a frozen rule explicitly consumes them and records the resulting decision;
28. preserve `machinery_requirements[]` and explicit failure behavior through Semantic→Core lowering or record a frozen provenance-visible mapping;
29. preserve the complete QSOL-CORE control/effect/machinery/contract surface **and representation-qualified `epistemic_class_bindings[]`** through the mandatory Vector/Dataflow IR; every lower class binding derived from Core retains `source_epistemic_class_binding_ids[]`, and transformed subjects require the applicable frozen `mapping_rule_id` rather than a copied class label;
30. record both mandatory lowering identities/hashes, cardinality-aware result-binding maps, and Core→Vector/Dataflow epistemic-class binding lineage in provenance;
31. record extension, determinism, numeric, randomness, machinery-requirement, and failure-behavior scope mappings through the applicable lowering whenever lower scope identities change; first-lowering source/Core scope references use complete ordered containment paths rather than kind plus local ID, and at both machinery boundaries preserve owner-qualified source/lower machinery-requirement references that pair each local requirement ID with its complete representation-relative owner path;
32. record result-determinism provenance at the JOB/DECK/CARD/region/kernel or other frozen scope where it is valid; do not invent a global pair unless a frozen normalization proves it valid;
33. record scoped numeric contract/mode provenance and never treat a semantics-changing numeric contract as a generic lowering map;
34. record scoped randomness/RNG provenance; every effective `SEEDED` scope has explicit algorithm, version, seed, and stream identity, plus partitioning when it can affect the generated or consumed sequence;
35. separate a governed backend-selection scope from the ordered backend-selection decisions made for that scope, and give the selection-scope record its own stable `backend_selection_scope_id` distinct from the computation `scope_id`;
36. never overwrite a denied target with a fallback target; preserve predecessor decision, frozen fallback rule, authorization outcome, and final-selection decision;
37. bind protected-machinery authorization records to the concrete backend-selection decision/scope they govern; every machinery declaration/reference is representation-qualified by `representation_kind`, content-bound `representation_identity`, complete representation-relative `owner_scope_path[]`, and local requirement ID. Semantic machinery paths use actual JOB/DECK/CARD containment; direct Core paths use actual Core-relative containment and never fabricate Semantic ancestors. Every protected use references its scope's `final_selection_decision_id`, which must be final/executable; denied, rejected, superseded, or merely considered predecessor decisions are never treated as executed machinery. Preserve same-domain authorization-before-use ordering through identified machinery-use records with nonempty representation-qualified `execution_subject_refs[]` for execution-governed work, including actual Core `operation_execution_id` values, while retaining CARD execution arrays only as verified Semantic projections; genuine RUN/DECK pre-execution setup uses its typed initiating scope instead;
38. distinguish a representation-qualified declared effect from runtime `effect_attempt_id` and trace both; direct Core entry must retain Core operation/declaration identity rather than fabricating Semantic CARD lineage;
39. bind each effect attempt to its contextual `effect_authorization_record_id` and canonical representation-qualified `execution_subject_ref`; every attempt whose completion state proves it began (`COMPLETED`, `ABORTED_CLEAN`, `PARTIAL`, or `UNKNOWN`) requires both `effect_begin_sequence_index` and the linked GRANTED authorization's `authorization_sequence_index` in the same event-order domain with authorization strictly before begin; every definitively terminated `COMPLETED`, `ABORTED_CLEAN`, or `PARTIAL` attempt also requires `effect_end_sequence_index` in that domain with begin strictly before end, while `UNKNOWN` may omit end only when termination/completion genuinely cannot be established; `card_id` / `card_execution_id` are required lineage projections only when verified Semantic CARD lineage exists;
40. account **unconditionally** for every applicable declared effect for every selected concrete execution subject with attempt(s), exactly one legitimate identified non-attempt, or structured failure;
41. treat a detected omission of a reachable required effect as structured execution/conformance failure, never as a successful non-attempt;
42. define effect-attempt completion independently from the enclosing CARD or lower-operation outcome;
43. apply completion-state precedence so known `COMPLETED` cannot also be `UNKNOWN`;
44. distinguish `ABORTED_CLEAN` from `NOT_STARTED`, `PARTIAL`, and `UNKNOWN`;
45. record every selected DECK in `deck_executions[]`, including DECKs prevented from starting by prior fail-stop when Semantic execution structure exists;
46. record every CARD in a selected DECK execution in `card_executions[]`, distinguishing executed, failed, untaken, fail-stop-blocked, not-reached, and explicit-skip paths when that Semantic execution structure exists; direct lower-representation execution instead uses its own identified `operation_executions[]` ledger. Every lower-operation untaken, fail-stop-blocked, not-reached, or explicit-skip status carries the applicable typed `governing_control_decision_id?`, `governing_failure_record_id?`, `governing_skip_rule_id?`, and `skip_verification_evidence_id?`; `failure_record_id?` is reserved for a failure caused by the operation itself;
47. bind effect-produced/exposed outputs to concrete `effect_attempt_ids[]`, with reciprocal output IDs on attempts; `NOT_STARTED` attempts have empty acquired-input/output/tool arrays and must never be cited by an output;
48. bind material external-tool identities to concrete effect attempts and/or outputs, not merely to a broad source CARD; explicit attempt/output subject arrays and reciprocal links are mandatory for material participation, and immutable/versioned material identity or an explicit identity-unavailable status must govern replay/evidence claims;
49. runtime cache provenance uses nonempty representation-qualified current `execution_subject_refs[]` for CARD or lower-operation invocations, including the exact direct-Core `operation_execution_id`; CARD identity/execution arrays are conditional verified Semantic projections only, and CARD/operation execution ledgers reciprocally carry their applicable cache-reuse record IDs. Do not satisfy an effectful execution subject from cached prior output if that skips a declared effect or its authorization/ordering/failure/provenance boundary;
50. bind every material runtime input to a stable `input_id` plus exact canonical value/content/artifact identity actually consumed and concrete representation-qualified `consumer_execution_refs[]`; CARD consumer IDs are conditional Semantic projections only;
51. bind each output to nonempty representation-qualified `producer_execution_refs[]`, exact `epistemic_class_binding_ids[]`, exact materially contributing `input_ids[]`, the complete producer-derived `backend_selection_scope_ids[]`, applicable failure-behavior bindings, and exact generated artifact IDs when generated code is involved; retain `producer_card_ids[]` / `producer_card_execution_ids[]` only when verified Semantic lineage exists and never fabricate them for direct Core entry;
52. bind optimized generated artifacts to the exact optimization-record IDs and optimized-IR identity that produced them, with reciprocal generated-artifact IDs on optimization records;
53. give each failure-behavior provenance record a stable `failure_behavior_binding_id` and make output and failure references resolve to the exact applicable records rather than a generic computation `scope_id`;
54. bind every generated artifact to its exact production `backend_selection_decision_id`, one truthful `direct_producer_toolchain_invocation_id`, and ordered `toolchain_invocation_chain_ids[]`; every command-line-driven material toolchain invocation also preserves its exact ordered duplicate-preserving typed `argument_vector[]` so positional flags, libraries, separators, and input/output occurrences cannot be reconstructed from unordered summary arrays. Direct invocation input/output artifact edges must remain truthful and transitive ancestors must not be mislabeled as direct producers;
55. use `failure_card_id` only for the CARD whose unhandled failure actually caused a failure record; pre-CARD or direct lower-operation failures use an always-present typed failing scope and must not fabricate a CARD culprit;
56. prefer small, inspectable transformations.

## Vocabulary

Use current project vocabulary consistently:

```text
JOB
DECK
CARD
stable JOB/DECK/CARD ID
run ID
deck execution
card execution
operation execution
execution subject reference
producer execution reference
VERB
NOUN
result binding
cardinality-aware result binding map
identified input
identified output
epistemic class binding
evidence status
backend-selection scope
backend-selection scope ID
backend-selection decision
fallback rule
machinery requirement
machinery authorization record
machinery use record
result-determinism scope
failure-behavior binding
failure-behavior binding ID
toolchain invocation
toolchain argument vector
direct toolchain producer
toolchain invocation chain
QSOL-CORE
Semantic IR
Semantic-to-Core Lowering
Vector/Dataflow IR
Core-to-Vector/Dataflow Lowering
MORPH
backend
extension profile
extension requirement
extension requirement lowering decision
extension requirement mapping decision
capability
effect
effect requirement
declared effect ID
effect authorization record
effect attempt ID
effect non-attempt record
numeric contract
numeric execution scope
randomness contract
randomness execution scope
tagged sequencing constraint
trace
provenance
```

See `docs/GLOSSARY.md`.

## Illustrative syntax

Until a grammar is frozen, examples are architectural sketches.

Do not infer implementation support from examples in documentation.

Do not implement `.qsl` parsing, formatting, or lossless text serialization until a normative QSOL text-profile specification freezes lexical grammar, syntax, shorthand/default reconstruction, canonical rendering, diagnostics, and source-to-Semantic-IR mapping.

## Semantic lowering work

Read `docs/SEMANTIC-TO-CORE-LOWERING.md` before changing the Semantic IR → QSOL-CORE boundary.

A legal lowering must preserve or explicitly validate before erasure:

- epistemic class and evidence boundaries;
- types and units;
- result bindings;
- execution-relevant qualifiers;
- `effect_requirements[]` and each effect's stable `effect_id` plus complete capability set;
- `machinery_requirements[]` or a frozen provenance-visible representation for later MORPH authorization;
- explicit scoped `failure_behavior`;
- JOB/DECK/CARD-scoped result-determinism, numeric, and randomness contracts;
- extension requirements including profile/version/contract identity and their canonical owning scope;
- tagged source/effect/failure sequencing constraints;
- CARD / DECK / JOB provenance.

Result-binding mapping must be cardinality-aware. One source result may legally split into several lower bindings, and several source bindings may legally fuse only under a frozen rule. Every many-to-one or many-to-many mapping group therefore requires `mapping_rule_id` resolving to the accepted frozen rule for that exact qualified source/lower binding set; never infer fusion legality from array position, equal local names, or producer success. Do not use scalar mapping fields or positional arrays that cannot represent those transformations unambiguously.

When extension requirements, machinery requirements, failure behavior, qualifiers, determinism, numerics, or randomness are materially consumed/remapped/grouped/normalized, provenance must record the corresponding lowering-decision family. IR hashes are not enough. An extension-scope decision may be omitted only under a frozen deterministic identity-scope reconstruction rule that actually preserves ownership.

At this first boundary, `machinery_requirement_lowering_decisions[]` uses identified `mapping_group_id` records with typed `source_scope_refs[]` and `core_scope_refs[]`, plus nonempty deterministic `source_machinery_requirement_refs[]` and `lower_machinery_requirement_refs[]`. Every machinery-requirement reference pairs its local `machinery_requirement_id` with the complete representation-relative `owner_scope_path[]` of the scope that owns it; source/Core scope arrays are correspondence context and never a positional join. Records also retain source CARD provenance and `mapping_rule_id`. Resolve each qualified requirement in the hash-bound source Semantic IR or resulting Core IR. Separate unrelated requirements sharing a scope; a frozen rule defines every split/fusion relation and the target selector/complete capability set reaching each lower requirement. Scope correspondence, repeated local IDs, or array position cannot substitute for an owner-qualified requirement identity. A reconstruction exception must recover both ownership and every qualified requirement association.

For `result_determinism_lowering_decisions[]`, `numeric_contract_lowering_decisions[]`, `randomness_lowering_decisions[]`, and `failure_behavior_lowering_decisions[]`, a first-lowering **semantic** change requires stable `transition_decision_id`, accepted versioned/content-bound `CONTRACT_TRANSITION` authority in `transition_authorized_by`, and passing lowering `transition_evidence_id` bound to `subject_kind = LOWERING_TRANSITION_DECISION`, `subject_id = transition_decision_id`, the exact requested/effective contract pair, complete owner-qualified Semantic/Core scopes, and active context, with validation preceding application in the shared event-order domain. Numeric semantic changes additionally identify the exact requested/source and effective numeric contract IDs/hashes; a new tolerance/fast-math contract, reassociation/FMA permission, effective precision, rounding, or denormal change is not a generic mapping. The resulting execution-scope record preserves the applicable authority under its own stable identity; result-determinism/randomness/failure target evidence remains subject-bound and distinct from lowering-decision evidence, linked through `related_evidence_ids[]` where defined. IR hashes, backend flags, generic mapping rules, or post-application success are not proof.

Unsupported semantic constructs or qualifiers fail explicitly. Do not silently drop, no-op, default, or defer their meaning to a backend.

## Vector/Dataflow IR work

Read `docs/VECTOR-AND-DATAFLOW.md` before changing the mandatory lower computational IR.

Because every backend path traverses this IR, it must represent or preserve the full supported QSOL-CORE surface, including:

- scalar and vector data operations;
- control flow;
- calls/returns and call state;
- representation-qualified `epistemic_class_bindings[]`, including `source_epistemic_class_binding_ids[]` and an accepted frozen `mapping_rule_id` whenever the bound subject is renamed, split, fused, relocated, changes owner path/kind, or otherwise is not deterministically identity-reconstructible;
- explicit effects with declared effect identity;
- complete per-effect required-capability sets;
- protected-machinery requirements/metadata;
- result bindings and qualifiers where still material;
- explicit failure behavior where still material;
- failure/totality classification;
- tagged source/effect/failure sequencing constraints;
- scoped result-determinism, numeric, randomness, and extension contracts including extension ownership;
- provenance and identities needed for per-effect-attempt tracing.

A non-vectorizable QSOL-CORE operation is not permission to bypass the IR. Use a defined scalar/control/effect/pass-through construct or fail conformance.

The Core→Vector/Dataflow stage is independently provenance-bearing. Trace at least:

```text
core_ir_hash
vector_dataflow_spec_version
vector_dataflow_implementation_version
vector_dataflow_ir_hash
result_binding_map[]
epistemic_class_bindings[]
extension_requirement_mapping_decisions[]
machinery_requirement_mapping_decisions[]
core_to_vector_result_determinism_mapping_decisions[]
core_to_vector_numeric_contract_mapping_decisions[]
core_to_vector_randomness_mapping_decisions[]
failure_behavior_mapping_decisions[]
```

Every retained lower `epistemic_class_bindings[]` entry resolves to the exact Vector/Dataflow representation/subject and carries the complete applicable `source_epistemic_class_binding_ids[]`. When the bound subject is transformed rather than identity-preserved under a frozen reconstruction rule, `mapping_rule_id` is mandatory and must validate that exact source-binding set → lower-subject relation. A copied `semantic_class`, source CARD summary, or local-ID match is not class provenance.

For `machinery_requirement_mapping_decisions[]`, typed scope mappings alone are not enough when one Core scope owns several machinery requirements or sibling scopes reuse a local requirement ID. Preserve `source_machinery_requirement_refs[]` and `lower_machinery_requirement_refs[]`, with every entry pairing its local `machinery_requirement_id` to the complete representation-relative `owner_scope_path[]`, so each target selector/capability set reaches the correct lower region without positional inference.

A mapping family may be omitted only under a frozen deterministic identity-scope reconstruction rule that actually covers that family. A semantics-changing `core_to_vector_numeric_contract_mapping_decisions[]` record is not such a mapping: it requires the exact requested/effective numeric contract IDs/hashes plus the same stable transition decision, accepted `CONTRACT_TRANSITION` authority, and passing pre-application evidence required at the first boundary.

## Result-determinism, numeric, randomness, and failure provenance

Do not assume one execution-wide contract governs an entire run.

Result determinism uses scoped requested/effective guarantees and any pre-execution transition authority.

Numeric provenance binds scope identity to numeric contract ID/hash and the material numeric mode actually used.

Randomness provenance binds scope identity to requested/effective randomness mode. For every effective `SEEDED` scope, RNG algorithm, RNG version, seed, and stream identity are mandatory; parallel partitioning/stream mapping is also mandatory whenever it can affect generated or consumed values.

Result-determinism, numeric, randomness, and failure-behavior execution-scope records use their own stable type-specific record keys. Every record also carries fully qualified `governed_scope_ref = { representation_kind, representation_identity, owner_scope_path[] }`, with the complete representation-relative containment path to the governed scope. Output scope-ID arrays reference the stable ledger keys, while validation resolves the qualified governed computation; local scope IDs and source CARD summaries are never owner identity.

Failure behavior provenance uses identified records:

```text
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

Outputs and failure records reference applicable `failure_behavior_binding_ids[]`. The frozen default fail-stop behavior has a stable identity when it materially governs execution; it must not be inferred only from skipped CARDs or DECKs.

For a representation-only failure-policy mapping, `mapping_or_transition_rule_id` resolves to an accepted content-bound `FAILURE_BEHAVIOR_MAPPING` rule proving semantic preservation. Whenever requested and effective failure semantics differ, both `mapping_or_transition_rule_id` and `transition_evidence_id` are mandatory: the rule is an accepted `CONTRACT_TRANSITION`, and the evidence is passing, subject-bound `validation_evidence[]` for this exact `FAILURE_BEHAVIOR_BINDING`, requested/effective pair, owning governed scope, and active context. Validation must precede application in the shared event-order domain. A rule assertion without passing pre-application evidence cannot authorize fail-stop becoming continue, retry, compensation, or another semantic change.

A recorded transition is evidence, not authorization. Whenever requested and effective result-determinism or randomness contracts differ, require `transition_authorized_by` resolving to a `CONTRACT_TRANSITION` rule and `transition_evidence_id` resolving to passing evidence for that exact execution-scope record and requested/effective pair. Semantics-changing numeric mappings at either lowering require the corresponding numeric requested/effective contract refs plus the lowering transition-decision/authority/evidence triple. Validate accepted source/policy authority and its version/content identity before effective-contract activation or use. Missing, stale, unknown, context-mismatched, unverifiable, or late authority/evidence fails closed. Optional fields may be absent only when no transition occurs.

Use the shared `rule_records[]` and `validation_evidence[]` definitions in [Trace and Provenance](docs/TRACE-AND-PROVENANCE.md#referenced-rules-and-validation-evidence). Preserve their typed subjects, verifiable rule/evidence content, accepted authority identities, evaluated context, verifier identity, and same-domain `validation_sequence_index < application_sequence_index` for applied transitions, skips, or substitutions. A producer's success label is not evidence, and an operational verification record is neither a research evidence promotion nor a capability grant.

## Backend-selection and machinery-authorization provenance work

Do not assume one backend decision governs an entire JOB, and do not store fallback by mutating one selected-backend field.

Use governed scopes:

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

`backend_selection_scope_id` is the stable identity of the selection-scope record. The full `governed_scope_ref = { representation_kind, representation_identity, owner_scope_path[] }` identifies the canonical computation governed by that record; the terminal path element is the governed scope and every disambiguating ancestor participates in identity. The governed computation and selection-scope record are not aliases. Decisions, machinery authorization/use records, generated artifacts, and outputs reference `backend_selection_scope_id`, while validation resolves its complete `governed_scope_ref`.

and ordered decisions:

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

A denied GPU decision followed by CPU fallback remains two decisions. Preserve the denial, its authorization record, the fallback rule, the predecessor link, the subject-bound fallback evidence, and the final decision ID. Whenever a decision is a fallback, both `fallback_rule_id` and `fallback_evidence_id` are mandatory: the rule resolves to the accepted frozen selection/fallback authority, and the evidence resolves to passing validation for this exact predecessor decision, candidate/fallback pair, governed scope, active context, and applicability conditions. Validation must complete before the fallback selection is applied in the shared event-order domain; unknown, stale, mismatched, or late evidence fails closed.

Protected machinery authorization is a separate ledger. Each `machinery_requirement_refs[]` entry carries `representation_kind`, content-bound `representation_identity`, complete representation-relative `owner_scope_path[]`, and local `machinery_requirement_id`, and must resolve uniquely in that named hash-bound representation. Semantic requirements use actual Semantic containment; direct Core requirements use actual Core-relative containment without fabricated JOB/DECK/CARD ancestry. Authorization also binds the specific backend-selection decision and exact required/granted/denied capability set.

Every execution-governed `machinery_use_records[]` entry has nonempty representation-qualified `execution_subject_refs[]` resolving to actual CARD or lower-operation executions, including the concrete Core `operation_execution_id` for direct QSOL-CORE use. `card_execution_ids[]` / `source_card_ids[]` are conditional verified Semantic projections only. Genuine pre-execution RUN/DECK setup may instead use its typed `initiating_scope_ref`; that exception cannot stand in for an executing Core operation. Every protected use references its selection scope's `final_selection_decision_id`; that decision must be final/executable, and denied/rejected/superseded predecessors cannot be marked as used. Linked machinery authorization records and generated artifacts actually launched must match that same final decision. Each use keeps all applicable authorization-record IDs and `protected_use_start_sequence_index` in the same frozen event-order domain as each authorization's `authorization_sequence_index`; require every applicable authorization index to precede use start. Denied machinery has no protected-use start record.

## Execution-path provenance work

Canonical membership is not execution evidence, and lower-representation entry must not fabricate Semantic membership.

Use one aggregate `run_id`. When Semantic lineage exists, use identified `deck_executions[]` and `card_executions[]`; when execution legitimately enters at QSOL-CORE or another lower representation without Semantic lineage, use identified representation-qualified `operation_executions[]` for the actual lower operations instead.

Every selected DECK remains represented even if prior fail-stop prevents it from starting. Every CARD in a selected DECK execution receives an outcome/path record. A pure TEST on an untaken branch must be distinguishable from a TEST that ran successfully even when neither produces output or effect.

A selected DECK blocked by an earlier failure carries `governing_failure_record_id` resolving to that concrete blocking failure; `failure_record_id` remains reserved for a failure caused by the DECK execution itself. The two meanings must not be overloaded or inferred from child records.

Execution-path cause references must be typed and resolvable. Do not use one untyped catch-all ID namespace for control decisions and failure records.

Every lower-operation execution uses the same typed path-cause discipline as a CARD execution. `operation_executions[]` carries `governing_control_decision_id?`, `governing_failure_record_id?`, `governing_skip_rule_id?`, and `skip_verification_evidence_id?`: an untaken branch requires its controlling decision; a fail-stop/blocked or failure-caused not-reached status requires the concrete blocking failure; an explicit frozen skip requires its accepted rule plus passing evidence bound to the exact `OPERATION_EXECUTION`; a general not-reached status requires one of those validated cause forms. `failure_record_id?` is reserved for a failure caused by that operation execution. Cause-free lower-operation non-reach fails closed.

Runtime CARD and lower-operation execution ledgers also retain reciprocal `cache_reuse_record_ids[]?` whenever a cache decision classifies or substitutes that exact invocation. Direct Core therefore remains joined to its exact `operation_execution_id` without fabricating a CARD execution.

Failure records always carry `failing_scope_kind` plus `failing_scope_id`. `failure_card_id?` and `failure_card_execution_id?` are present only when a CARD execution actually caused the failure; pre-CARD or lower-operation failure must never synthesize those fields.

Every failure record also requires `failure_behavior_binding_ids[]` resolving to the exact policy bindings active for that failure and its propagation/handling, including the applicable default fail-stop binding. It also carries the complete exact-set `result_determinism_scope_ids[]`, `numeric_scope_ids[]`, and `randomness_scope_ids[]` applicable to that failure, including output-free failures. A rejected requested policy is not the effective handling policy; pre-CARD failures retain the actual setup/rejection-handling binding. Do not infer the policy or contract scopes from the resulting execution path.

Failure traces retain `backend_selection_scopes[]`, `backend_selection_decisions[]`, `failure_behavior_bindings[]`, `result_determinism_scopes[]`, `numeric_execution_scopes[]`, and `randomness_execution_scopes[]` alongside machinery authorization/use, including denied candidates and fallback predecessors. A standalone failure manifest preserves the complete transitive reference closure inline or through retrievable content-bound records. Dangling selection, policy, requirement, rule, evidence, contract-scope, or output IDs are incomplete provenance.

## Input provenance work

Do not treat a mutable locator as the identity of a material input.

Each material input requires a stable ID plus canonical value or immutable content/artifact identity. Paths, URLs, dataset names, model names, and similar locators may aid retrieval but do not replace content identity.

Every actual CARD or lower-operation consumer is represented by `consumer_execution_refs[]` using the shared representation-qualified execution-subject shape. Direct Core input consumers therefore resolve the real `operation_execution_id`; `consumer_card_execution_ids[]` is only a conditional verified Semantic projection. Genuine RUN/DECK setup can use typed scope refs, but this is not an exception for an executing lower operation.

If the required material input identity or concrete consumer relation cannot be established, fail replay/provenance validation closed rather than guessing.

## Result provenance work

Each output is independently identified and binds its own provenance:

```text
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
epistemic_class_binding_ids[]
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
generated_artifact_ids[]?
machinery_use_record_ids[]
result_determinism_scope_ids[]
numeric_scope_ids[]
randomness_scope_ids[]
failure_behavior_binding_ids[]
cache_reuse_record_ids[]?
evidence_status?
```

`result_binding_ref?`, when present, identifies the output's exact binding by representation kind/content identity, complete owner path, and local binding ID. Resolve it directly or through the applicable cardinality-aware result-binding maps; never infer a binding from scalar local text, producer-array order, or first-match lookup after a fusion.

`producer_execution_refs[]` is nonempty and identifies the concrete runtime producer subjects in the representation that actually executed. For Semantic CARD execution it resolves to `card_executions[]`; for direct QSOL-CORE or another frozen lower entry it resolves to the matching `operation_executions[]` record and its representation/content identity. `producer_card_ids[]` and `producer_card_execution_ids[]` are conditional retained Semantic-lineage projections: when present, they must agree exactly with the producer refs and verified lineage; when no Semantic lineage exists they are absent rather than fabricated.

`epistemic_class_binding_ids[]` is always explicit and is validated as a duplicate-free exact set derived independently from the concrete producers, entered representation, and every traversed class-binding preservation/mapping relation. A classified output must be justified by that set. Legitimate lower-entry output with no applicable class binding is `UNCLASSIFIED` with an empty set and no evidence claim; operational success cannot synthesize research class.

`input_ids[]` contains the exact immutable input records that materially contributed to this output under the frozen provenance-dependency rule. It is not the whole execution-wide input inventory by default.

`failure_behavior_binding_ids[]` resolves to the exact failure-policy provenance records that governed the producer path. A generic computation `scope_id` is not a substitute for the stable binding-record key.

`evidence_status` is conditionally present by semantic class, but whenever the output is evidence-bearing it is mandatory and class-discriminated:

```text
evidence_class
status
evidence_rule_id
evidence_validation_id
```

Every TEST, VALIDATION, PROOF, or frozen evidence-bearing class requires both IDs even when the class is preserved. For a class-preserving output, `evidence_rule_id` resolves to accepted content-bound `EVIDENCE_STATUS` authority and `evidence_validation_id` resolves to passing OUTPUT-bound substantive evidence for this exact artifact, class bindings, concrete producers, material inputs/tools/evidence identities, and publication event before publication. For a non-class-preserving transition, the rule resolves to `EPISTEMIC_TRANSITION` authority and the validation additionally proves the exact source-class-to-target-class transition. Reject incompatible semantic/evidence-class combinations, missing rule/evidence, another output's evidence, or post-publication validation. Generic output status is never an epistemic promotion or preservation mechanism.

`backend_selection_scope_ids[]` is a duplicate-free exact-set attribution. Derive the complete applicable scope set independently from `producer_execution_refs[]`, their representation-qualified governed scopes, the final executable selection decisions, and the actual interpreted/reference/backend execution relation for those producers; then require recorded equality. An unrelated scope or omitted producer scope fails validation even when no generated artifact or machinery-use record exists to expose the mismatch.

When an effect materially produces or exposes an output, link the output to concrete attempt IDs and link those attempts back to the output. Every output carries explicit `external_tool_ids[]`: use an empty array only when no material external tool contributed. When an external tool materially supplies evidence/data, the nonempty output array and the tool's concrete subject links must agree reciprocally; broad source-CARD attribution or omission of the array is not evidence of no tool participation.

Every output also carries explicit `machinery_use_record_ids[]`. It identifies the exact protected-use occurrence or occurrences that materially produced, supplied, or exposed the output, and every listed use must reciprocally name the output in `machinery_use_records[].output_ids[]`. The array is empty only when no protected machinery use materially contributed. A shared CARD/Core execution, backend-selection scope/decision, backend unit, or generated artifact cannot substitute for this occurrence-level join when several launches or retries are possible.

## External-tool provenance work

A tool name, service label, or mutable endpoint is not sufficient material identity when the tool can affect result bytes or evidence.

Each material `external_tool_versions[]` record must either carry at least one immutable/versioned identity such as a tool version, executable/content hash, model/version ID, immutable artifact ID, or frozen equivalent, or explicitly record that material identity is unavailable. Identity unavailability must weaken the replay/evidence claim according to the frozen policy; it must never be silently treated as fully reproducible provenance.

## Optimization and cache work

Use reference semantics first.

Only operations proven pure and total may be freely reordered solely from data dependencies or removed solely because their results are dead.

Every runtime cache classification/substitution record identifies the actual current invocation(s) through representation-qualified `execution_subject_refs[]`. Semantic `source_card_ids[]` / `card_execution_ids[]` are conditional projections; direct QSOL-CORE and other lower-entry reuse resolves exact `operation_execution_id` values instead. CARD and lower-operation ledgers reciprocally list their applicable cache records. Do not infer a current substitution from canonical source identity, output position, or historical cache-producer provenance.

Do not replace an effectful execution subject with prior cached output if doing so skips a declared effect, contextual capability authorization, sequencing edge, failure, or effect-attempt provenance. Effectful reuse requires an explicit frozen replay/cache semantic. Without such a rule, execute normally or fail closed.

For `classification = VERIFIED_REUSE`, `legality_rule_id` and `verification_evidence_id` are mandatory. Resolve them to an applicable `CACHE_SUBSTITUTION` rule and passing context-bound evidence for the exact reuse record, reused computation/artifact, checked cache identity, exact current `execution_subject_refs[]`, and current inputs/contracts/entry-lowering context before substitution. Effectful reuse requires the specifically applicable separately frozen replay/cache rule, not a generic cache rule, and another retry or historical producer cannot supply the current subject's effect accounting. `UNVERIFIED_HIT` is diagnostic and cannot satisfy an execution subject or supply a verified output: verify successfully before reuse, execute cold, or fail closed. A label, unknown ID, stale evidence, or matching hash alone is insufficient. Use the shared [cache validation contract](docs/TRACE-AND-PROVENANCE.md#cache-reuse-provenance).

A cached artifact may be used as an explicit declared input when the semantic contract says so; that is not the same as silently satisfying an effectful execution subject from cache.

Every toolchain/code-generation invocation that directly consumes IR records explicit `input_ir_hashes[]` containing the exact consumed IR snapshot(s); the array may be empty only when the invocation consumes no IR. Tool/flags/target/backend-unit metadata or differing output hashes do not substitute for this direct content-bound input edge.

When optimized code is generated, the generated artifact records the applicable `optimized_ir_hash` and `optimization_record_ids[]`, while each optimization record reciprocally lists `generated_artifact_ids[]`. The required attribution chain is `output → generated_artifact → optimization provenance`; `backend_unit_id` alone is not sufficient when reference and optimized variants coexist.

For CI and optimization evidence rules, read `docs/OPTIMIZATION-AND-CI.md`.

## Effect authorization, attempt, and non-attempt work

Completion state belongs to the effect attempt, not the enclosing CARD or lower-operation outcome.

Use this precedence:

```text
1. NOT_STARTED if the protected effect never began.
2. COMPLETED if the effect reached its defined completion boundary.
3. If begun and known incomplete:
   ABORTED_CLEAN if no external change occurred;
   PARTIAL if some incomplete portion became observable;
   UNKNOWN if clean-vs-partial cannot be established.
4. UNKNOWN if completion itself cannot be established.
```

Every runtime protected effect attempt must record at least:

```text
effect_attempt_id
declared_effect_id
effect_requirement_ref:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
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
acquired_input_ids[]
observable_output_ids[]
external_tool_ids[]
```

The `effect_requirement_ref` and `execution_subject_ref` are canonical. A Semantic CARD-backed attempt sets the conditional CARD fields and those fields must agree with the verified Semantic owner/execution. A legitimate direct QSOL-CORE attempt instead names the hash-bound Core operation and its concrete `operation_execution_id`; CARD fields are absent unless Semantic lineage is actually retained and verifiable. Lower-entry execution never manufactures CARD identities merely to satisfy provenance.

`acquired_input_ids[]` is explicit on every attempt and reciprocates `inputs[].effect_attempt_ids[]`. It may be nonempty even when the producer later fails or the attempt publishes no output. For `completion_state = NOT_STARTED`, both `acquired_input_ids[]` and `observable_output_ids[]` are empty because no protected acquisition or observable effect began.

`external_tool_ids[]` is explicit on every attempt. Use an empty array only when no material external model, prover, process, service, or other tool participated in that concrete attempt. Every listed tool resolves to `external_tool_versions[]` and reciprocally lists the attempt in its `effect_attempt_ids[]`; omission is incomplete provenance, not an assertion of no tool participation. A `NOT_STARTED` attempt necessarily has an empty tool array.

Every contextual effect authorization record must identify the same `effect_requirement_ref` and canonical `execution_subject_ref`, complete required/granted/denied capability sets, policy identity/version, authorization outcome, and `authorization_sequence_index?`. When verified Semantic CARD lineage exists, its conditional CARD fields agree exactly with that subject; direct Core operation execution omits them. All required capabilities must be granted before effect begin. For every attempt whose completion state is `COMPLETED`, `ABORTED_CLEAN`, `PARTIAL`, or `UNKNOWN`, `effect_begin_sequence_index` is mandatory and its linked GRANTED authorization must carry `authorization_sequence_index`; both are in one frozen monotonic event-order domain and must satisfy `authorization_sequence_index < effect_begin_sequence_index`. For `COMPLETED`, `ABORTED_CLEAN`, and `PARTIAL`, `effect_end_sequence_index` is mandatory in that same domain and must satisfy `effect_begin_sequence_index < effect_end_sequence_index`; `UNKNOWN` may omit end only when the attempt's termination/completion boundary cannot be established and records it whenever a definite termination event is known. `NOT_STARTED` has no begin/end event. Generic attempt `sequence_index` is neither authorization-order nor effect-boundary-order proof.

If a declared effect has no attempt for a concrete execution subject, record an identified legitimate non-attempt carrying the same `effect_requirement_ref` and `execution_subject_ref`, with conditional CARD fields only when Semantic lineage exists:

```text
effect_non_attempt_record_id
declared_effect_id
effect_requirement_ref
execution_subject_ref
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

Legitimate reasons include untaken branch, prior fail-stop, subject not reached, or explicit frozen skip. Separate concrete executions of the same canonical CARD or lower operation require separate non-attempt records.

An explicit frozen skip requires both `governing_skip_rule_id` and `skip_verification_evidence_id`. They resolve to an applicable `EFFECT_SKIP` rule and passing evidence for this exact non-attempt record, declaration, concrete execution subject, and active context before the skip is applied. Missing, unresolved, inapplicable, or unverifiable skip evidence is conformance failure, not successful omission. Explicit Semantic CARD skips carry the same fields with evidence bound to their `CARD_EXECUTION` subject and cannot evade accounting for their effects. See the shared [non-attempt validation rules](docs/TRACE-AND-PROVENANCE.md#effect-non-attempt-records).

Declared-effect accounting is unconditional. For every selected concrete execution subject, every applicable effect declaration must resolve to attempt(s), exactly one legitimate identified non-attempt, or structured failure. No profile, backend, optimization mode, deployment setting, or audit switch may disable this rule.

A detected omission of a reachable required effect is **not** a successful non-attempt reason. It forces structured execution/conformance failure. Do not let `BACKEND_OMISSION_DETECTED` coexist with successful enclosing execution.

Do not collapse multiple effect attempts into one aggregate partial-effect flag.

## Extension and capability work

An extension profile supplies optional versioned syntax, adapters, effects, or lowering hooks. It does not grant execution permission.

For example, `USE QX-NET` and `ALLOW NETWORK`/`DENY NETWORK` operate at different boundaries. Likewise, a remote QX-AI effect may require both `AI_MODEL` and `NETWORK` capabilities.

Protected machinery capabilities such as `GPU` use the machinery-requirement/authorization path and must not be forced into the external-effect schema.

Before implementing an extension with material operational semantics, follow the roadmap's freeze-before-implementation rule.

## Backend work

Backend-specific behavior belongs behind explicit backend or extension boundaries.

Generated target code should remain inspectable where practical.

Toolchain provenance distinguishes the invocation that directly emitted an artifact from the full transitive chain that materially contributed to it, and preserves the exact positional tool arguments whenever order can change output bytes or symbol resolution.

Use identified invocation records such as:

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

`argument_vector[]` is ordered and duplicate-preserving. Its indices are contiguous from zero and agree with array order; `argument_text` is the exact argument token under the frozen invocation encoding. Typed references connect material input, generated-artifact, IR, and output tokens to the same immutable records carried by the summary/direct-edge arrays. Static-library order, `--whole-archive`/`--no-whole-archive`, grouping/separators, duplicate libraries, and other positional semantics must not be reconstructed by sorting or set conversion. `flags[]`, `input_ids[]`, and generated-artifact input arrays are summaries/direct graph edges, not an argv substitute.

Response files, wrapper scripts, shell commands, or similar indirections require an equivalent frozen exact command sequence plus immutable content identity for every material response/script/input involved. A mutable response-file path or unordered flag set cannot support complete invocation reconstruction.

`input_ir_hashes[]` is always explicit: it is nonempty with the exact direct IR content hash(es) whenever an invocation consumes IR, including ordinary non-optimized code generation, and empty only when it consumes no IR. Tool, flags, target, or output identity cannot substitute for this edge. `input_ids[]` resolves to immutable `inputs[]` records for every material dependency not generated in this run, including prebuilt objects, static libraries, headers, startup files, sysroots, and implicit toolchain inputs. It is empty only when no such inputs were consumed. Composite inputs content-bind the complete dependency set through a frozen representation. Paths, library names, flags, and tool versions alone do not identify the bytes read; missing material input identity invalidates complete/reproducible build provenance. Prebuilt inputs must not be fabricated as outputs of this run.

Every generated artifact records a mandatory `backend_selection_decision_id` for the exact decision governing its production, consistently with its selection scope and target context. An artifact for a rejected candidate must not be attributed to the scope's final fallback decision, and artifact existence does not grant protected-use authorization.

Every generated artifact records one `direct_producer_toolchain_invocation_id` plus ordered `toolchain_invocation_chain_ids[]`. `input_generated_artifact_ids[]` and `output_generated_artifact_ids[]` are direct edges: only an invocation that actually emits an artifact lists it as an output. A transitive ancestor remains in the artifact's chain but must not falsely claim the final artifact as a direct output.

For `compile → object → link → executable`, the compiler directly outputs the object, the linker directly outputs the executable, the executable's ordered chain may still contain both invocation IDs, and the linker's `argument_vector[]` preserves the exact interleaving of options, generated objects, prebuilt libraries, and output arguments. A run-wide compiler-version list is summary metadata only; it is not sufficient build provenance when different units or stages can use different compiler/linker versions, flags, or argument order.

A backend implements frozen semantics. It does not define them.

A backend must consume the established lower pipeline; it must not become a second Semantic IR → QSOL-CORE compiler or bypass the mandatory Core→Vector/Dataflow lowering.

Backend selection must be recorded at the scope it governs. The selection-scope record has its own stable `backend_selection_scope_id`; automatic selection additionally traces selection policy/tuning identity. Fallback must preserve the ordered selection-decision chain. Protected machinery use must reference the scope's final executable decision and satisfy linked authorization before execution begins, with same-domain ordering evidence where required.

CUDA backend implementation follows the frozen generic GPU contract. QX-CUDA vendor controls are a separate optional profile.

## Serialization work

A format claiming semantic losslessness must round-trip all execution-, dependency-, authorization-, and reference-relevant canonical fields, including:

- stable JOB/DECK/CARD identifiers and explicit JOB→DECK→CARD containment/source order;
- result bindings;
- semantic classes;
- qualifiers;
- effect requirements and complete per-effect capability sets;
- machinery requirements and complete per-machinery capability sets;
- explicit failure behavior;
- JOB/DECK/CARD-scoped result-determinism, numeric, and randomness contracts;
- extension/profile identities and versions;
- complete tagged `sequencing_constraints[]`.

Effect-order and failure-order views may be derived from tagged sequencing entries but may not replace the canonical sequencing field.

Do not silently default, discard, flatten, relocate, or renumber a stable identity, hierarchy relation, source-order relation, or semantic/enforcement field during transport.

Machine-readable canonical interchange may proceed before the human QSOL grammar is frozen. Human `.qsl` parsing/serialization may not.

## Documentation hierarchy

Read in this order when context is limited:

1. `docs/SPECIFICATION-STATUS.md`
2. `docs/DESIGN-PRINCIPLES.md`
3. `docs/ARCHITECTURE.md`
4. `docs/LANGUAGE-MODEL.md`
5. `docs/SEMANTIC-IR.md`
6. `docs/SEMANTIC-TO-CORE-LOWERING.md`
7. `docs/VECTOR-AND-DATAFLOW.md` when lower IR/backend/optimization work is involved
8. the domain-specific document relevant to the task
9. `ROADMAP.md`

## Change discipline

Do not broaden scope merely because an adjacent improvement is attractive.

If a task targets one phase, leave later-phase work in `ROADMAP.md` unless it is required to make the current phase internally correct.

## Review discipline

For every substantive change, ask:

- Did meaning change?
- Did a stable JOB/DECK/CARD identity, containment edge, or source-order relation disappear or get renumbered without explicit migration?
- Did a scoped determinism, numeric, randomness, failure, machinery, or extension contract disappear or move to the wrong scope?
- Did semantic/evidence class detach from its CARD/output or become internally contradictory?
- Did a result binding disappear or become impossible to map through a split/fusion?
- Did either lowering lose a cardinality-aware result-binding map?
- Did Core→Vector/Dataflow lose a representation-qualified epistemic class binding, its `source_epistemic_class_binding_ids[]`, or the frozen mapping rule required for a transformed bound subject?
- Did either lowering lose extension-, machinery-requirement, or failure-behavior mapping provenance?
- Did a machinery-requirement mapping at either boundary lose the stable source/lower requirement IDs and become ambiguous among several requirements sharing one scope?
- Did Core→Vector/Dataflow lose determinism/numeric/randomness scope mappings?
- Did an effect become implicit or lose its complete capability-set association?
- Did a protected-machinery requirement disappear, lose its representation-qualified identity, force direct Core through a fabricated Semantic owner path, or get misrepresented as an external effect?
- Did protected machinery use begin before all required capabilities were authorized, lose the ordering evidence needed to prove that invariant, or reference a decision other than its scope's final executable selection decision?
- Did a machinery use lose its concrete representation-qualified execution subjects, including a direct Core operation execution, or genuine pre-execution initiating scope?
- Did backend fallback overwrite an earlier denied/failed selection rather than preserve a decision chain?
- Did a backend-selection decision/reference lose its resolvable `backend_selection_scope_id`?
- Did a concrete effect attempt lose its contextual authorization record or canonical `execution_subject_ref`?
- Did a direct QSOL-CORE or other lower-entry effect/output/input/machinery/cache use fabricate Semantic CARD identities instead of using its representation-qualified operation/execution subject?
- Did a lower-operation untaken/fail-stop/not-reached/explicit-skip status lose its required typed control/failure/skip-rule cause, or overload `failure_record_id` as a blocking cause?
- Did a begun effect omit `effect_begin_sequence_index`, omit the linked GRANTED authorization's `authorization_sequence_index`, or fail the same-domain authorization-before-begin inequality?
- Did a definitively terminated `COMPLETED`, `ABORTED_CLEAN`, or `PARTIAL` effect omit `effect_end_sequence_index`, or fail the same-domain begin-before-end inequality?
- Did a runtime attempt lose its representation-qualified declared-effect link?
- Did a legitimate non-attempt lose its stable record ID, concrete execution subject, or typed resolvable execution-path cause?
- Did an explicit skip lack a resolvable permitted frozen rule and passing applicability evidence for its exact invocation?
- Did any applicable declared effect lack attempt/non-attempt/failure accounting for a selected concrete execution subject?
- Did a detected reachable-effect omission fail to fail execution/conformance?
- Did a selected DECK disappear because fail-stop prevented it from starting?
- Did a CARD membership list get mistaken for execution evidence?
- Did a pre-CARD or lower-operation failure fabricate a failing CARD identity?
- Did scoped determinism/numeric/randomness/failure provenance collapse into false globals or lose stable record keys?
- Did a semantics-changing numeric contract at either lowering boundary avoid exact requested/effective contract refs, accepted `CONTRACT_TRANSITION` authority, subject-bound pre-application evidence, or stable transition-decision identity?
- Did a `SEEDED` randomness scope omit algorithm, version, seed, stream identity, or material partitioning/stream mapping?
- Did a requested/effective contract transition lose its resolvable versioned authority, exact subject/context evidence, or pre-application validation?
- Did a first-lowering semantic transition omit stable `transition_decision_id`, reuse lowering evidence as target-scope evidence, or fail to connect distinct target evidence through `related_evidence_ids[]` where applicable?
- Did a failure-behavior binding lose its stable record ID or an output/failure lose the exact governing binding IDs?
- Did a failure manifest omit referenced selection scopes, decisions, policy bindings, execution-contract scopes, rules, evidence, or other records needed for complete reference closure?
- Did an output lose its representation-qualified concrete producer execution, exact epistemic-class binding set, material input, exact backend-selection scope set, RNG, exact generated-artifact, concrete effect-attempt, failure-policy, or external-tool references?
- Did an evidence-bearing TEST/VALIDATION/PROOF output omit `evidence_status`, its accepted class-specific/transition rule, or passing output-bound evidence even when the class is preserved?
- Did an output gain incompatible TEST/VALIDATION/PROOF status?
- Did a material input retain only a mutable locator or lose its representation-qualified concrete consumer execution?
- Did a material external tool retain only a mutable name/endpoint without an explicit identity-unavailable downgrade?
- Did an optimized artifact lose the optimization record(s) that produced it?
- Did a generated artifact lose its exact production selection decision, direct producer, ordered transitive toolchain ancestry, material tool identity, or build flags/configuration?
- Did a toolchain invocation omit immutable non-generated input identities, confuse prebuilt dependencies with this run's generated outputs, or lose/reorder/deduplicate its material `argument_vector[]` so positional command-line semantics cannot be reconstructed exactly?
- Did a transitive toolchain ancestor get falsely recorded as directly outputting the final artifact?
- Did an extension get mistaken for a capability grant or leak into core?
- Did a serializer lose JOB→DECK→CARD containment/order, the canonical tagged sequencing field, or replace it with incomplete parallel arrays?
- Did a failure record use `card_id` where canonical `failure_card_id` is required, or require `failure_card_id` where no CARD actually failed?
- Did human text implementation invent grammar before normative text-profile freeze?
- Did reordering/dead-result elimination change failure/effect observability?
- Did cache reuse lose the exact current `execution_subject_refs[]`, fail the reciprocal CARD/lower-operation execution join, or skip effect authorization, ordering, failure, or attempt provenance?
- Did `VERIFIED_REUSE` lack its applicable frozen legality rule and passing current-context verification evidence, or did an unverified hit supply a result?
- Did a backend invent semantics not yet frozen, including Core determinism/randomness/RNG semantics?
- Did Vector/Dataflow IR drop or bypass control, calls, effects, epistemic bindings, machinery requirements, capabilities, contracts, or scalar semantics?
- Could one known-completed attempt also be `UNKNOWN`?
- Was a cleanly aborted begun effect mislabeled?
- Did QX-POSIX or QX-CUDA implementation precede its normative contract?
- Did generic GPU/CUDA implementation invent unfrozen accelerator, fallback, or machinery-authorization semantics?
- Did documentation claim functionality that does not exist?

If any answer is yes, make the change explicit or reject it.