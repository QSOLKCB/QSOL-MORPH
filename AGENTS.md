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
13. preserve the explicit effect → complete capability-set association; do not replace it with an ambiguous CARD-level union;
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
29. preserve the complete QSOL-CORE control/effect/machinery/contract surface through the mandatory Vector/Dataflow IR;
30. record both mandatory lowering identities/hashes and cardinality-aware result-binding maps in provenance;
31. record extension, determinism, numeric, randomness, machinery-requirement, and failure-behavior scope mappings through the applicable lowering whenever lower scope identities change;
32. record result-determinism provenance at the JOB/DECK/CARD/region/kernel or other frozen scope where it is valid; do not invent a global pair unless a frozen normalization proves it valid;
33. record scoped numeric contract/mode provenance;
34. record scoped randomness/RNG provenance;
35. separate a governed backend-selection scope from the ordered backend-selection decisions made for that scope, and give the selection-scope record its own stable `backend_selection_scope_id` distinct from the computation `scope_id`;
36. never overwrite a denied target with a fallback target; preserve predecessor decision, frozen fallback rule, authorization outcome, and final-selection decision;
37. bind protected-machinery authorization records to the concrete backend-selection decision/scope they govern and preserve same-domain authorization-before-use ordering through identified machinery-use records;
38. distinguish canonical declared `effect_id` from runtime `effect_attempt_id` and trace both;
39. bind each effect attempt to its contextual `effect_authorization_record_id` and preserve same-domain authorization-before-effect-begin ordering where required;
40. account **unconditionally** for every applicable declared effect for every selected concrete `card_execution_id` with attempt(s), exactly one legitimate identified non-attempt, or structured failure;
41. treat a detected omission of a reachable required effect as structured execution/conformance failure, never as a successful non-attempt;
42. define effect-attempt completion independently from the enclosing CARD outcome;
43. apply completion-state precedence so known `COMPLETED` cannot also be `UNKNOWN`;
44. distinguish `ABORTED_CLEAN` from `NOT_STARTED`, `PARTIAL`, and `UNKNOWN`;
45. record every selected DECK in `deck_executions[]`, including DECKs prevented from starting by prior fail-stop;
46. record every CARD in a selected DECK execution in `card_executions[]`, distinguishing executed, failed, untaken, fail-stop-blocked, not-reached, and explicit-skip paths;
47. bind effect-produced/exposed outputs to concrete `effect_attempt_ids[]`, with reciprocal output IDs on attempts;
48. bind material external-tool identities to concrete effect attempts and/or outputs, not merely to a broad source CARD, and require an immutable/versioned material identity or an explicit identity-unavailable status that weakens replay/evidence claims;
49. do not satisfy an effectful CARD from cached prior output if that skips a declared effect or its authorization/ordering/failure/provenance boundary;
50. bind every material runtime input to a stable `input_id` plus exact canonical value/content/artifact identity actually consumed;
51. bind each output to canonical producer CARDs **and concrete `producer_card_execution_ids[]`**, exact materially contributing `input_ids[]`, applicable failure-behavior bindings, and exact generated artifact IDs when generated code is involved;
52. bind optimized generated artifacts to the exact optimization-record IDs and optimized-IR identity that produced them, with reciprocal generated-artifact IDs on optimization records;
53. give each failure-behavior provenance record a stable `failure_behavior_binding_id` and make output references resolve to those record IDs rather than a generic computation `scope_id`;
54. bind every generated artifact to the ordered exact toolchain invocation IDs that produced its bytes, including material tool identity, flags/configuration, target/ABI context, and reciprocal output-artifact links;
55. use `failure_card_id` only for the CARD whose unhandled failure actually caused a failure record; pre-CARD failures use an always-present typed failing scope and must not fabricate a CARD culprit;
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
VERB
NOUN
result binding
cardinality-aware result binding map
identified input
identified output
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

Result-binding mapping must be cardinality-aware. One source result may legally split into several lower bindings, and several source bindings may legally fuse only under a frozen rule. Do not use scalar mapping fields or positional arrays that cannot represent those transformations unambiguously.

When extension requirements, machinery requirements, failure behavior, qualifiers, determinism, numerics, or randomness are materially consumed/remapped/grouped/normalized, provenance must record the corresponding lowering-decision family. IR hashes are not enough. An extension-scope decision may be omitted only under a frozen deterministic identity-scope reconstruction rule that actually preserves ownership.

Unsupported semantic constructs or qualifiers fail explicitly. Do not silently drop, no-op, default, or defer their meaning to a backend.

## Vector/Dataflow IR work

Read `docs/VECTOR-AND-DATAFLOW.md` before changing the mandatory lower computational IR.

Because every backend path traverses this IR, it must represent or preserve the full supported QSOL-CORE surface, including:

- scalar and vector data operations;
- control flow;
- calls/returns and call state;
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
extension_requirement_mapping_decisions[]
machinery_requirement_mapping_decisions[]
core_to_vector_result_determinism_mapping_decisions[]
core_to_vector_numeric_contract_mapping_decisions[]
core_to_vector_randomness_mapping_decisions[]
failure_behavior_mapping_decisions[]
```

A mapping family may be omitted only under a frozen deterministic identity-scope reconstruction rule that actually covers that family.

## Result-determinism, numeric, randomness, and failure provenance

Do not assume one execution-wide contract governs an entire run.

Result determinism uses scoped requested/effective guarantees and any pre-execution transition authority.

Numeric provenance binds scope identity to numeric contract ID/hash and the material numeric mode actually used.

Randomness provenance binds scope identity to requested/effective randomness mode and, where material, RNG algorithm, version, seed, stream, and partitioning.

Result-determinism, numeric, and randomness execution-scope records use their own stable type-specific record keys. Output scope-ID arrays reference those keys, not the generic governed computation `scope_id`.

Failure behavior provenance uses identified records:

```text
failure_behavior_bindings[]:
    failure_behavior_binding_id
    scope_kind
    scope_id
    source_card_ids[]
    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
```

Outputs reference applicable `failure_behavior_binding_ids[]`. The frozen default fail-stop behavior has a stable identity when it materially governs execution; it must not be inferred only from skipped CARDs or DECKs.

A recorded transition is evidence, not authorization. If a required contract cannot be satisfied and no frozen pre-execution rule authorizes the transition, fail closed.

## Backend-selection and machinery-authorization provenance work

Do not assume one backend decision governs an entire JOB, and do not store fallback by mutating one selected-backend field.

Use governed scopes:

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

`backend_selection_scope_id` is the stable identity of the selection-scope record. `scope_kind` + `scope_id` identify the computation governed by that record. They are not aliases. Decisions, machinery authorization/use records, generated artifacts, and outputs reference `backend_selection_scope_id`.

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
    machinery_authorization_record_ids[]?
    decision_status
```

A denied GPU decision followed by CPU fallback remains two decisions. Preserve the denial, its authorization record, the fallback rule, the predecessor link, and the final decision ID.

Protected machinery authorization is a separate ledger and must bind the specific selection decision plus applicable canonical machinery requirement IDs. When protected-use ordering is material, record identified `machinery_use_records[]` with all applicable authorization-record IDs plus `protected_use_start_sequence_index` in the same frozen monotonic event-order domain as each authorization's `authorization_sequence_index`. Require `authorization_sequence_index < protected_use_start_sequence_index`. Denied machinery has no protected-use start record.

## Execution-path provenance work

Canonical membership is not execution evidence.

Use one aggregate `run_id`, identified `deck_executions[]`, and identified `card_executions[]`.

Every selected DECK remains represented even if prior fail-stop prevents it from starting. Every CARD in a selected DECK execution receives an outcome/path record. A pure TEST on an untaken branch must be distinguishable from a TEST that ran successfully even when neither produces output or effect.

Execution-path cause references must be typed and resolvable. Do not use one untyped catch-all ID namespace for control decisions and failure records.

Failure records always carry `failing_scope_kind` plus `failing_scope_id`. `failure_card_id?` and `failure_card_execution_id?` are present only when a CARD execution actually caused the failure; pre-CARD failure must never synthesize those fields.

## Input provenance work

Do not treat a mutable locator as the identity of a material input.

Each material input requires a stable ID plus canonical value or immutable content/artifact identity. Paths, URLs, dataset names, model names, and similar locators may aid retrieval but do not replace content identity.

If the required material input identity cannot be established, fail replay/provenance validation closed rather than guessing.

## Result provenance work

Each output is independently identified and binds its own provenance:

```text
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

`producer_card_ids[]` identifies canonical semantic producers. `producer_card_execution_ids[]` identifies the concrete runtime producer executions and must resolve through `card_executions[]` to their canonical CARD and DECK execution. The canonical CARD ID alone is insufficient when a CARD may execute more than once.

`input_ids[]` contains the exact immutable input records that materially contributed to this output under the frozen provenance-dependency rule. It is not the whole execution-wide input inventory by default.

`failure_behavior_binding_ids[]` resolves to the exact failure-policy provenance records that governed the producer path. A generic computation `scope_id` is not a substitute for the stable binding-record key.

`evidence_status`, when present, is class-discriminated:

```text
evidence_class
status
evidence_rule_id?
```

Reject incompatible semantic/evidence-class combinations. Generic output status is not an epistemic promotion mechanism.

When an effect materially produces or exposes an output, link the output to concrete attempt IDs and link those attempts back to the output. When an external tool materially supplies evidence/data, link the tool to concrete attempts and/or outputs rather than only the broad source CARD.

## External-tool provenance work

A tool name, service label, or mutable endpoint is not sufficient material identity when the tool can affect result bytes or evidence.

Each material `external_tool_versions[]` record must either carry at least one immutable/versioned identity such as a tool version, executable/content hash, model/version ID, immutable artifact ID, or frozen equivalent, or explicitly record that material identity is unavailable. Identity unavailability must weaken the replay/evidence claim according to the frozen policy; it must never be silently treated as fully reproducible provenance.

## Optimization and cache work

Use reference semantics first.

Only operations proven pure and total may be freely reordered solely from data dependencies or removed solely because their results are dead.

Do not replace an effectful CARD with prior cached output if doing so skips a declared effect, contextual capability authorization, sequencing edge, failure, or effect-attempt provenance. Effectful reuse requires an explicit frozen replay/cache semantic. Without such a rule, execute normally or fail closed.

A cached artifact may be used as an explicit declared input when the semantic contract says so; that is not the same as silently satisfying an effectful CARD from cache.

When optimized code is generated, the generated artifact records the applicable `optimized_ir_hash` and `optimization_record_ids[]`, while each optimization record reciprocally lists `generated_artifact_ids[]`. The required attribution chain is `output → generated_artifact → optimization provenance`; `backend_unit_id` alone is not sufficient when reference and optimized variants coexist.

For CI and optimization evidence rules, read `docs/OPTIMIZATION-AND-CI.md`.

## Effect authorization, attempt, and non-attempt work

Completion state belongs to the effect attempt, not the enclosing CARD outcome.

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
card_id
card_execution_id
effect_kind
required_capabilities[]
effect_authorization_record_id
sequence_index
effect_begin_sequence_index?
effect_end_sequence_index?
completion_state
observable_output_ids[]
external_tool_ids[]?
```

Every contextual effect authorization record must identify the attempt/declaration/CARD **and concrete `card_execution_id`**, complete required/granted/denied capability sets, policy identity/version, authorization outcome, and `authorization_sequence_index?`. All required capabilities must be granted before effect begin. When ordering auditability is required, `authorization_sequence_index` and `effect_begin_sequence_index` are in one frozen monotonic event-order domain and must satisfy `authorization_sequence_index < effect_begin_sequence_index`. A denied attempt has no begin event. Generic attempt `sequence_index` is not a substitute.

If a declared effect has no attempt for a concrete CARD execution, record an identified legitimate non-attempt:

```text
effect_non_attempt_record_id
declared_effect_id
card_id
card_execution_id
effect_kind
non_attempt_reason
governing_control_decision_id?
governing_failure_record_id?
backend_detail?
```

Legitimate reasons include untaken branch, prior fail-stop, CARD not reached, or explicit frozen skip. Separate invocations of the same canonical CARD require separate non-attempt records.

Declared-effect accounting is unconditional. For every selected concrete `card_execution_id`, every applicable effect declaration must resolve to attempt(s), exactly one legitimate identified non-attempt, or structured failure. No profile, backend, optimization mode, deployment setting, or audit switch may disable this rule.

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

Every generated artifact must be attributable to the exact ordered toolchain invocation chain that produced its bytes. Use identified records such as:

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
    input_generated_artifact_ids[]?
    output_generated_artifact_ids[]
    backend_unit_id?
    backend_selection_scope_id?
```

`generated_artifacts[].toolchain_invocation_ids[]` records the ordered invocation IDs that materially produced the artifact, and invocation records reciprocally identify their output artifacts. A run-wide compiler-version list is summary metadata only; it is not sufficient build provenance when different units or stages can use different compiler/linker versions or flags.

A backend implements frozen semantics. It does not define them.

A backend must consume the established lower pipeline; it must not become a second Semantic IR → QSOL-CORE compiler or bypass the mandatory Core→Vector/Dataflow lowering.

Backend selection must be recorded at the scope it governs. The selection-scope record has its own stable `backend_selection_scope_id`; automatic selection additionally traces selection policy/tuning identity. Fallback must preserve the ordered selection-decision chain. Protected machinery use must satisfy linked authorization before execution begins, with same-domain ordering evidence where required.

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
- Did either lowering lose extension-, machinery-requirement, or failure-behavior mapping provenance?
- Did Core→Vector/Dataflow lose determinism/numeric/randomness scope mappings?
- Did an effect become implicit or lose its complete capability-set association?
- Did a protected-machinery requirement disappear or get misrepresented as an external effect?
- Did protected machinery use begin before all required capabilities were authorized, or lose the ordering evidence needed to prove that invariant?
- Did backend fallback overwrite an earlier denied/failed selection rather than preserve a decision chain?
- Did a backend-selection decision/reference lose its resolvable `backend_selection_scope_id`?
- Did a concrete effect attempt lose its contextual authorization record or concrete `card_execution_id`?
- Did authorization move until after an effect began, or lose the begin-order evidence needed to prove otherwise?
- Did a runtime attempt lose its canonical declared-effect link?
- Did a legitimate non-attempt lose its stable record ID, concrete `card_execution_id`, or typed resolvable execution-path cause?
- Did any applicable declared effect lack attempt/non-attempt/failure accounting for a selected concrete CARD execution?
- Did a detected reachable-effect omission fail to fail execution/conformance?
- Did a selected DECK disappear because fail-stop prevented it from starting?
- Did a CARD membership list get mistaken for execution evidence?
- Did a pre-CARD failure fabricate a failing CARD identity?
- Did scoped determinism/numeric/randomness/failure provenance collapse into false globals or lose stable record keys?
- Did a failure-behavior binding lose its stable record ID or an output lose the binding IDs that governed its producer path?
- Did an output lose its canonical producer, concrete producer execution, material input, backend, RNG, exact generated-artifact, concrete effect-attempt, failure-policy, or external-tool references?
- Did an output gain incompatible TEST/VALIDATION/PROOF status?
- Did a material input retain only a mutable locator?
- Did a material external tool retain only a mutable name/endpoint without an explicit identity-unavailable downgrade?
- Did an optimized artifact lose the optimization record(s) that produced it?
- Did a generated artifact lose the exact ordered toolchain invocation IDs, tool identity, or build flags/configuration that produced its bytes?
- Did an extension get mistaken for a capability grant or leak into core?
- Did a serializer lose JOB→DECK→CARD containment/order, the canonical tagged sequencing field, or replace it with incomplete parallel arrays?
- Did a failure record use `card_id` where canonical `failure_card_id` is required, or require `failure_card_id` where no CARD actually failed?
- Did human text implementation invent grammar before normative text-profile freeze?
- Did reordering/dead-result elimination change failure/effect observability?
- Did cache reuse skip effect authorization, ordering, failure, or attempt provenance?
- Did a backend invent semantics not yet frozen, including Core determinism/randomness/RNG semantics?
- Did Vector/Dataflow IR drop or bypass control, calls, effects, machinery requirements, capabilities, contracts, or scalar semantics?
- Could one known-completed attempt also be `UNKNOWN`?
- Was a cleanly aborted begun effect mislabeled?
- Did QX-POSIX or QX-CUDA implementation precede its normative contract?
- Did generic GPU/CUDA implementation invent unfrozen accelerator, fallback, or machinery-authorization semantics?
- Did documentation claim functionality that does not exist?

If any answer is yes, make the change explicit or reject it.