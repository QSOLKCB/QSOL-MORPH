# QSOL-MORPH Roadmap

QSOL-MORPH is being developed specification-first. The project deliberately separates architectural agreement from executable implementation so that later code is judged against an explicit semantic contract rather than allowing implementation accidents to become the specification.

## Development rule

> Meaning is frozen before machinery is optimized.

No phase may silently weaken an invariant established by an earlier frozen phase. Backend-specific convenience does not override semantic preservation, determinism requirements, epistemic distinctions, numeric contracts, capability authorization, failure semantics, concrete execution accounting, or traceability.

## PR #1 — Documentation Foundation

**Status:** current

Establish the non-normative architecture and vocabulary before implementation.

Deliverables:

- project architecture;
- human/AI language model;
- JOB → DECK → CARD → VERB/NOUN hierarchy;
- candidate Semantic IR;
- semantic-to-core lowering boundary;
- full semantics-preserving Vector/Dataflow model;
- deterministic execution model;
- provenance and trace model;
- failure and partial-effect model;
- backend and code-morphing model;
- extension-profile model;
- effect-capability and machinery-capability authorization models;
- canonical serialization direction;
- contribution and AI-agent guidance;
- glossary and documentation index.

**Gate:** documentation must clearly distinguish illustrative syntax from frozen semantics.

## PR #2 — Lock in Core Invariants

Freeze the first normative QSOL-MORPH constitution.

Planned work:

- assign stable invariant identifiers;
- define MUST / MUST NOT / SHOULD interpretation;
- freeze semantic-preservation rules;
- freeze nondeterminism disclosure requirements;
- freeze numeric-contract preservation requirements;
- freeze epistemic non-promotion requirements;
- freeze backend-independence boundaries;
- freeze inspectability and traceability requirements;
- freeze the small-core / extension boundary;
- freeze hidden-effect rules and the distinction between external-effect authorization and protected-machinery authorization;
- freeze failure, fail-stop, JOB propagation, per-DECK/per-CARD execution accounting, and effect attempt/non-attempt disclosure rules;
- freeze concrete execution identity as distinct from canonical JOB/DECK/CARD identity;
- add a machine-readable invariant registry;
- add validation that documentation and registry agree;
- define invariant change-control procedure.

No compiler or backend implementation is required for this PR.

## PR #3 — Canonical Data Model

Define and implement the first machine-readable representation of:

```text
JOB → DECK → CARD → VERB / NOUN
```

Planned scope:

- stable JOB/DECK/CARD identifiers;
- source locations and canonical containment/order;
- typed operands;
- result bindings naming values produced for dependent CARDs;
- values and units;
- qualifiers;
- semantic classes;
- `effect_requirements[]` with stable effect identity/kind and complete `required_capabilities[]` for each protected external effect;
- `machinery_requirements[]` with stable requirement identity, target selector/class, and complete `required_capabilities[]` for protected machinery use without reclassifying machinery selection as an effect;
- result-determinism requirements at JOB, DECK, CARD, or another explicitly frozen owning scope;
- numeric contract identity/parameters at the scope where they govern `NUMERIC` execution;
- randomness/reproducibility requirements at their canonical owning scope;
- explicit scoped `failure_behavior` on CARD, DECK, or JOB where the frozen model permits non-default recovery/continuation/compensation behavior;
- dependencies;
- tagged `sequencing_constraints[]` preserving source-order, effect-order, failure-order, and any future frozen sequencing kind;
- `extension_requirements[]` binding each profile to its required version/range and contract identity where applicable;
- deterministic canonical ordering;
- schema validation;
- reference fixtures.

The normative data model must freeze how JOB/DECK/CARD execution contracts compose or refine one another before an executable phase can derive effective scopes. A child scope may not silently weaken a parent requirement.

Only CARDs proven **pure and total** under the active contract may be freely reordered when dependencies permit. A CARD that may fail is semantically observable under fail-stop execution and must preserve ordering against externally observable effects unless an explicit frozen construct permits otherwise.

## PR #4 — Canonical Machine-Readable Serialization

Implement deterministic serialization for the complete canonical data model **without inventing the human QSOL grammar**.

Initial targets:

- JSONL streaming profile;
- canonical JSON representation;
- XML interchange representation.

Every lossless format must round-trip all canonical semantic and enforcement fields, including stable JOB/DECK/CARD identities and containment/order, scoped execution contracts, result bindings, qualifiers, effect requirements, machinery requirements, explicit failure behavior, extension requirements, dependencies, and complete tagged sequencing constraints.

The human-readable `.qsl` source profile is explicitly **deferred** until a separate normative text-profile specification freezes lexical grammar, syntax, shorthand/default reconstruction, diagnostics, canonical rendering, and source-to-Semantic-IR mapping.

## PR #5 — Execution Contract, Trace, Failure, and Provenance Foundation

Implement the minimum execution-contract schema required before any QSOL phase is permitted to execute research programs.

This phase is an explicit gate for PR #7 and every later executable implementation. Ledger definitions and conditional validation requirements follow [Trace and Provenance](docs/TRACE-AND-PROVENANCE.md); summaries below are not alternative weaker schemas.

### Aggregate execution identity

The trace contract must bind:

- stable aggregate `run_id`;
- source identity/hash and canonical Semantic IR identity/hash;
- stable `job_id`;
- identified `deck_executions[]` for every selected DECK, including DECKs prevented from starting by fail-stop;
- stable canonical `card_ids[]` for membership plus identified `card_executions[]` for concrete runtime path/outcome;
- `execution_status` and `job_status`;
- identified `control_decisions[]` and `failure_records[]`.

`card_id` identifies canonical meaning. `card_execution_id` identifies one concrete runtime execution. Loops, retries, calls, or repeated DECK execution may produce several `card_execution_id` values for one `card_id`, and the execution contract must preserve that distinction.

### Failure identity

Every `failure_records[]` entry must carry:

```text
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

`failing_scope_kind` plus `failing_scope_id` is always present and is the authoritative typed identity of the failure location.

`failure_behavior_binding_ids[]` resolves to the exact stable policy bindings active for this failure and its propagation/handling, including the applicable frozen default fail-stop binding. A resulting retry/skip path or generic scope match cannot substitute for that relation. Rejected requested policies are not effective handling policies; pre-CARD rejections retain the actual setup/rejection-handling binding.

When a CARD's unhandled failure caused the record, `failure_card_id` and `failure_card_execution_id` are required and must resolve consistently through `card_executions[]`.

When failure occurs before any CARD execution, such as JOB-scoped contract rejection, DECK setup failure, lowering failure, or protected-machinery denial before CARD use, the trace must **not fabricate a CARD identity**. The typed failing scope remains sufficient and the CARD-specific fields are absent.

Failure traces retain `failure_behavior_bindings[]`, `backend_selection_scopes[]`, and `backend_selection_decisions[]` alongside machinery authorization/use ledgers, including denied candidates and fallback predecessors. Standalone failure manifests preserve the complete transitive reference closure, inline or through retrievable content-bound records. Dangling selection, policy, requirement, rule, evidence, or output references fail provenance validation.

### Declared effects and protected machinery

The gate must include:

- canonical `effect_requirements[]`, each carrying source CARD ID, declared effect ID, effect kind, and complete `required_capabilities[]`;
- canonical `machinery_requirements[]`, each carrying stable requirement identity, governing source scope, target selector/class, and complete required-capability set;
- execution-wide capability summaries only as summaries, never as replacements for contextual authorization records.

### Backend-selection and protected-machinery provenance

Require:

- `backend_selection_scopes[]`, each with stable `backend_selection_scope_id`, governed scope/source/backend unit, ordered decision IDs, and final decision ID when execution proceeds;
- `backend_selection_decisions[]`, each with stable decision ID, requested target, selected backend/version/architecture/device, automatic-selection policy/tuning identity where applicable, predecessor/fallback-rule identity where applicable, linked machinery authorization, order, and status;
- `machinery_authorization_records[]` with stable authorization identity, governing selection scope/decision, applicable machinery requirement IDs, complete required/granted/denied capability sets, policy identity/version, authorization outcome, and authorization sequence index;
- `machinery_use_records[]` with stable use identity, governing selection scope/decision/backend unit, concrete participating `card_execution_ids[]`, applicable authorization IDs, protected-use start index, and optional stop index.

The machinery-use CARD-execution references are nonempty for CARD-governed work and resolve to the actual invocations in the current run. Repeated launches under one scope/decision must not collapse retries or iterations. Genuine pre-CARD setup may have an empty array only with `initiating_scope_ref`, a typed reference to the actual initiating RUN or DECK_EXECUTION, resolving to `run_id` or `deck_execution_id`; no fake CARD execution is permitted.

Authorization and protected use share one frozen monotonic event-order domain. Every successful authorization required for a protected use must satisfy:

```text
authorization_sequence_index < protected_use_start_sequence_index
```

Denied machinery has no protected-use start record.

Fallback from a denied target is legal only under a frozen pre-execution rule and must remain a new ordered selection decision rather than overwriting the denied decision.

### Execution-contract scopes and resolvable authority

Require stable type-specific record keys:

- `result_determinism_scopes[]` with `result_determinism_scope_id`;
- `numeric_execution_scopes[]` with `numeric_scope_id`;
- `randomness_execution_scopes[]` with `randomness_scope_id`;
- `failure_behavior_bindings[]` with stable `failure_behavior_binding_id`, governed scope/source provenance, requested/effective failure policy, and material mapping/transition identity.

Each scope retains governed computation identity and source provenance. A single execution-wide scope is legal only when a frozen normalization proves it faithfully represents every governed source requirement.

The gate includes `rule_records[]` and `validation_evidence[]` using the complete [shared reference schemas](docs/TRACE-AND-PROVENANCE.md#referenced-rules-and-validation-evidence). Rule records bind accepted source/specification or policy authority, version/content identity, rule kind, and verifiable definition. Evidence records bind the exact typed subject, rule, evaluated context, verifier identity, outcome, content, and validation/application ordering. Unknown references or producer success labels alone are not valid evidence.

Whenever requested and effective result-determinism or randomness contracts differ, `transition_authorized_by` must resolve to a `CONTRACT_TRANSITION` rule and `transition_evidence_id` to passing evidence for that exact execution-scope record and requested/effective pair. Verify applicable authority before effective-contract activation or use; the shared order domain requires `validation_sequence_index < application_sequence_index`. Missing, stale, wrong-kind, context-mismatched, unverifiable, or late authority/evidence fails closed. Optional fields may be absent only when no transition occurs, not for an undocumented downgrade.

For `randomness_execution_scopes[]`, replay/audit-relevant fields include requested/effective mode, transition authority/evidence, RNG algorithm/version, seed, stream identity, parallel partitioning, backend unit, and where applicable:

```text
entropy_effect_attempt_ids[]
entropy_input_ids[]
```

When `effective_randomness_mode = EXTERNAL-ENTROPY`, the scope must identify the exact authorized protected `RANDOM` acquisition attempt(s) that supplied entropy. Where the entropy value is a material runtime input, it must also identify the immutable entropy input record(s). A randomness mode or source CARD ID alone is not sufficient attribution.

### Inputs and outputs

Require identified immutable `inputs[]`, each binding stable `input_id` to the canonical value, content hash, immutable artifact/version identity, or frozen equivalent actually consumed.

Require identified `outputs[]`, each carrying at least:

```text
output_id
result_binding?
artifact_hash
artifact_location?
semantic_class
status
evidence_status?
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
```

`producer_card_ids[]` identifies canonical semantic producers. **`producer_card_execution_ids[]` identifies the concrete runtime producer executions and is required by the PR #5 gate.** A canonical CARD ID alone cannot distinguish outputs from separate loop iterations, retries, calls, or repeated DECK executions.

Every `producer_card_execution_id` resolves to `card_executions[]`, which identifies the concrete DECK execution and canonical CARD.

`input_ids[]` identifies the exact immutable inputs materially contributing to that output. Execution-wide input availability is not a substitute for per-output attribution.

`failure_behavior_binding_ids[]` resolves to stable `failure_behavior_binding_id` records. A generic computation scope ID is not sufficient to identify which requested/effective failure policy governed the producer path.

When present, `evidence_status` is class-discriminated and must be compatible with `semantic_class`. Generic output status cannot silently promote TEST, VALIDATION, or PROOF class.

### Generated artifacts, optimization, tools, and cache reuse

Require:

- identified `generated_artifacts[]` linked to backend unit, backend-selection scope, and mandatory exact production `backend_selection_decision_id`, with optimization links, one `direct_producer_toolchain_invocation_id`, and ordered `toolchain_invocation_chain_ids[]` where generated bytes are involved;
- identified `toolchain_invocations[]` carrying stable invocation ID/order, invocation kind, immutable/versioned material tool identity, target/ABI context, exact flags/configuration, immutable general `input_ids[]` for material non-generated dependencies, direct generated-artifact inputs/outputs, backend unit, and backend-selection scope where applicable;
- identified `optimization_provenance[]` recording reference/optimized IR identity, actual transformation sequence, legality evidence, target context, and reciprocal generated-artifact links;
- identified `external_tool_versions[]` with stable links to applicable effect attempts and/or outputs plus immutable/versioned material identity, or an explicit identity-unavailable status that weakens replay/evidence claims;
- identified `cache_reuse_records[]` distinguishing cold execution, verified reuse, unverified hit, or frozen equivalent, with material cache identity, legality rule, reused computation/artifact identity, and verification evidence;
- per-output cache-reuse links where applicable.

A generated artifact's production decision must resolve in its recorded selection scope and match its target context. A rejected candidate's artifact must not be attributed to the final fallback decision merely because the two share one scope. Artifact existence does not authorize machinery use.

Toolchain `input_ids[]` bind the immutable bytes of prebuilt objects, libraries, headers, startup files, sysroots, and implicit dependencies not generated in this run. Mutable locators or flags alone are insufficient. The array is empty only when no such material inputs were consumed; composite inputs content-bind the complete material dependency set under a frozen representation. Missing material dependency identity invalidates complete/reproducible build provenance.

Toolchain direct edges and ancestry have different meanings. `input_generated_artifact_ids[]` / `output_generated_artifact_ids[]` record what an invocation directly consumed/emitted. A generated artifact's `direct_producer_toolchain_invocation_id` must point to the invocation that directly emitted it. `toolchain_invocation_chain_ids[]` records ordered transitive build ancestry and must not force every ancestor to claim the final artifact as a direct output.

Run-wide compiler/tool version lists are summaries only. They cannot substitute for the exact direct producer plus ordered material toolchain ancestry of one generated artifact.

For `classification = VERIFIED_REUSE`, require `legality_rule_id` resolving to the applicable `CACHE_SUBSTITUTION` rule and `verification_evidence_id` resolving to passing evidence for the exact reuse record, checked cache identity/artifact, and current inputs/contracts/context before substitution. A label or matching hash alone is insufficient. `UNVERIFIED_HIT` cannot satisfy a CARD: verify successfully before reuse, execute cold, or fail closed.

Ordinary cache substitution is effect-free by default. Effectful reuse requires that the referenced rule is the separately frozen replay/cache semantic preserving declared effects, contextual authorization, source/effect/failure ordering, attempt provenance, output attribution, and observable external state. A generic cache rule is not enough.

### Per-effect authorization and execution-instance accounting

Every protected effect attempt requires an identified authorization record:

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

Every runtime attempt requires:

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
    observable_output_ids[]
    external_tool_ids[]?
```

Every non-attempt requires its own stable identity and concrete CARD execution:

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

This prevents separate runtime invocations of one canonical CARD from collapsing into one ambiguous attempt/non-attempt fact.

Explicit frozen skips require both `governing_skip_rule_id` and `skip_verification_evidence_id`, resolving to an applicable `EFFECT_SKIP` rule and passing evidence bound to this exact non-attempt record, declaration, CARD execution, and active context before the skip is applied. Unknown, missing, stale, inapplicable, or unverifiable skip evidence forces conformance failure, not successful omission. Explicit CARD skips carry the same fields with evidence for their `CARD_EXECUTION` subject and cannot bypass accounting for their effects.

Authorization and effect-begin indices share one frozen monotonic event-order domain. Every protected effect known to begin must satisfy:

```text
authorization_sequence_index < effect_begin_sequence_index
```

Denied authorization has no effect-begin event. Generic attempt sequence numbering is not authorization-order proof.

Candidate mutually exclusive attempt states are:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

Known completion takes precedence over broader consequence uncertainty. Completion is a property of the effect attempt, not the enclosing CARD result.

### Unconditional declared-effect completeness

Effect declaration accounting is mandatory, not an optional audit profile.

For **every selected concrete `card_execution_id`**, every applicable canonical effect declaration owned by that CARD must resolve to exactly one of these outcomes:

1. one or more identified `effect_attempts[]` records for that concrete CARD execution when attempts occurred;
2. exactly one identified legitimate `effect_non_attempt_records[]` record for that concrete CARD execution when no attempt occurred; or
3. structured execution/conformance failure when complete accounting cannot be established or a reachable required effect was omitted.

Legitimate non-attempt reasons include untaken branch, prior fail-stop, CARD not reached, or verified explicit frozen skip and must resolve to the applicable typed control/failure cause or governing skip-rule/evidence records.

`BACKEND_OMISSION_DETECTED` or frozen equivalent is **not** a successful non-attempt path. It means a reachable required effect was omitted and must produce structured execution/conformance failure.

A declaration with neither attempt nor legitimate non-attempt accounting is always incomplete provenance. No backend, profile, optimization mode, or deployment setting may disable this rule.

### Reference failure contract

Before PR #7 may execute a program, PR #5 must also freeze the execution-failure contract sufficiently for the reference machine to implement it:

- evaluation yields success or structured failure, never an implicit sentinel;
- an unhandled CARD failure stops later CARDs in the DECK by default;
- an unhandled DECK failure fails the enclosing JOB by default and later DECKs do not start;
- dependent consumers/comparisons do not execute against missing or partial failed output;
- future continue/retry/recovery/parallel-JOB behavior requires explicit frozen semantics;
- pure CARD failure commits no semantic state;
- capability authorization succeeds before every protected external effect begins;
- protected machinery authorization succeeds before protected machinery use begins;
- effects already observable before a later failure are not retroactively erased;
- arithmetic-domain errors such as division/modulo by zero produce structured failure;
- failure traces preserve every selected DECK, every concrete CARD execution outcome, typed failure scope and exact failure-policy bindings, per-effect accounting, complete backend-selection/authorization/use history, and already-observable outputs/effects.

### Gate condition

No executable QSOL path may emit a research result without enough provenance to bind every identified output to:

- stable run/JOB identity;
- selected DECK and concrete CARD execution(s);
- exact immutable material inputs;
- semantic class and compatible evidence status;
- exact generated target and its production selection decision where applicable;
- exact direct producer invocation, immutable non-generated build dependencies, and ordered transitive material toolchain ancestry where generated target bytes are involved;
- resolvable backend-selection/determinism/numeric/randomness/failure-behavior record IDs;
- protected-machinery authorization/use ordering and concrete invocation attribution where applicable;
- cache-reuse path and verified substitution rule/evidence where used;
- resolved extension set;
- concrete material external-tool identity, or explicit identity unavailability with a correspondingly weakened claim;
- concrete effect authorization/attempt/non-attempt history, with verified skip authority where used;
- exact external-entropy acquisition attempt(s) where applicable;
- applicable pre-execution transition authority and context-bound verification evidence;
- execution/failure context that produced or prevented the result.

### Conformance cases to freeze before implementation

These are documentation-phase acceptance cases, not claims of implemented runtime tests:

| Case | Required result |
| --- | --- |
| Two iterations of one CARD use the same backend scope/decision | Distinct use records resolve to their actual `card_execution_ids[]`; canonical IDs or event indices alone fail. |
| Protected setup occurs before any CARD | The empty CARD-execution array has a resolvable typed initiating RUN/DECK_EXECUTION; invented CARD attribution fails. |
| A denied candidate and its fallback both have generated artifacts | Each artifact names its own exact production decision; a scope-only or final-decision guess fails. |
| A link consumes a prebuilt library or sysroot whose bytes change | Invocation `input_ids[]` identifies the actual immutable dependency set; unchanged paths/flags alone cannot establish identical build provenance. |
| A requested guarantee is downgraded | Only applicable versioned authority and passing evidence for the exact requested/effective scope, established before application, permit it; unknown, stale, wrong-context, or late evidence fails. |
| A failure occurs under one of several scoped policies | `failure_behavior_binding_ids[]` selects the actual governing bindings, including defaults; inference from the resulting path fails. |
| Failure follows denied-target fallback or protected use | All referenced backend-selection and policy ledgers remain resolvable, including predecessor decisions; dangling references fail. |
| A reachable effect is labeled an explicit frozen skip | The exact invocation has a resolvable permitted skip rule and passing applicability evidence; an unverifiable label is conformance failure. |
| A cache entry claims `VERIFIED_REUSE` | The applicable frozen rule and passing current-context verification evidence resolve; absent evidence, unverified substitution, or effectful substitution under a generic cache rule fails. |

The first-lowering machinery requirement-ID cases are additionally frozen in PR #8 and exercised by PR #9.

## PR #6 — Normative QSOL-CORE Operational Specification

Freeze QSOL-CORE semantics **before** implementing the reference machine.

Planned work:

- freeze initial instruction families and exact instruction inventory;
- define operand, result, type, and state-transition semantics;
- define arithmetic and numeric-contract interaction;
- define result-determinism execution semantics at each supported Core scope;
- define requested/effective determinism transitions, resolvable pre-execution authority/evidence, and fail-closed behavior;
- define randomness modes and RNG algorithm/version/seed/stream/partitioning semantics;
- define interaction between randomness, numeric, and result-determinism contracts;
- define logic including XOR;
- define comparisons;
- define control flow, calls, returns, and STOP;
- define effect operations and their explicit protected boundaries;
- define sequencing/failure behavior and totality properties;
- define structured diagnostics and conformance fixtures.

## PR #7 — QSOL-CORE Reference Machine

Implement the frozen QSOL-CORE operational specification without inventing new semantics.

Requirements:

- deterministic reference execution under the active contract;
- fail-closed contract enforcement;
- full PR #5 provenance;
- complete structured failures;
- conformance against PR #6 fixtures.

## PR #8 — Normative Semantic-to-QSOL-CORE Lowering Specification

Freeze the first mandatory lowering before implementing it.

Specify:

- mapping of every supported Semantic-IR operation to Core;
- preservation of stable source identity/provenance;
- result-binding maps;
- extension requirement mapping;
- qualifier decisions;
- identified cardinality-aware machinery-requirement mappings with typed source/Core scopes and explicit `source_machinery_requirement_ids[]` / `lower_machinery_requirement_ids[]`;
- result-determinism, numeric, randomness, and failure-behavior mapping;
- effect/capability preservation;
- complete tagged sequencing preservation;
- rejection rules and conformance fixtures, including several machinery requirements sharing a source scope but reaching different Core scopes, with missing/swapped/ambiguous associations rejected.

## PR #9 — Reference Semantic-to-QSOL-CORE Lowering

Implement PR #8.

Every material lowering decision must be provenance-bearing. Required decision families include extension requirements, qualifiers, machinery requirements, result determinism, numerics, randomness, and failure behavior whenever consumed, grouped, normalized, remapped, or otherwise transformed.

`machinery_requirement_lowering_decisions[]` requires identified mapping groups, typed `source_scope_refs[]` / `core_scope_refs[]`, and nonempty deterministic `source_machinery_requirement_ids[]` / `lower_machinery_requirement_ids[]`. Resolve requirement IDs in the hash-bound source Semantic IR and resulting Core IR. Separate unrelated requirements sharing a scope; a frozen rule defines any split/fusion relation and the target selector/capability set reaching each lower requirement. Scope correspondence or source CARD IDs alone are insufficient. Omission is legal only under a frozen rule reconstructing every requirement-ID association as well as ownership.

`result_binding_map[]` is required whenever identities are preserved or transformed unless a frozen deterministic reconstruction rule applies.

## PR #10 — Normative Full Vector/Dataflow IR Specification

Freeze the mandatory lower IR before implementing its lowering.

The IR must preserve the complete supported QSOL-CORE surface, including:

- scalar and vector operations;
- control flow;
- calls/returns;
- explicit effects and complete effect-capability requirements;
- protected-machinery requirements;
- sequencing/failure constraints;
- result-determinism, numeric, randomness, extension, and failure-behavior contracts;
- provenance links.

Non-vectorizable operations use explicit scalar/control/effect/pass-through constructs or fail conformance. Backends do not bypass this IR.

## PR #11 — Reference QSOL-CORE-to-Vector/Dataflow Lowering

Implement PR #10 lowering.

Require:

- Vector/Dataflow IR identity/hash;
- cardinality-aware `result_binding_map[]`;
- typed Core → Vector/Dataflow scope mappings for extension, machinery, result-determinism, numeric, randomness, and failure-behavior contract families;
- for `machinery_requirement_mapping_decisions[]`, explicit `source_machinery_requirement_ids[]` and `lower_machinery_requirement_ids[]` in addition to typed scopes, so multiple requirements owned by one Core scope cannot be swapped or detached;
- lowering diagnostics and conformance/rejection fixtures.

Omission of a mapping family is allowed only under a frozen deterministic identity-scope reconstruction rule covering that family.

## PR #12 — Reference MORPH to C

Implement the first reference machinery/code-generation backend from the mandatory Vector/Dataflow IR.

Require:

- semantics-preserving C emission;
- stable backend-unit identity;
- identified `generated_artifacts[]` with artifact ID/kind/hash, backend unit, backend-selection scope and mandatory exact production `backend_selection_decision_id`, source provenance, optimization links where applicable, `direct_producer_toolchain_invocation_id`, and ordered `toolchain_invocation_chain_ids[]`;
- identified `toolchain_invocations[]` recording the exact material compiler/assembler/linker/code-generation identities, invocation order, target/ABI, deterministic build flags/configuration, immutable non-generated dependency `input_ids[]`, direct generated-artifact inputs/outputs, backend unit, and backend-selection scope;
- truthful direct-edge invariants: only the direct producer invocation lists an artifact in `output_generated_artifact_ids[]`, while transitive ancestors remain in the artifact's ordered chain and prebuilt dependencies resolve through `inputs[]`;
- reference/optimized equivalence evidence where optimization is used;
- no bypass around the Vector/Dataflow IR.

A run-wide compiler/version inventory may remain as a summary, but it is not sufficient artifact provenance when several compilation/link stages or configurations are possible.

## PR #13 — Morph Optimization Passes

Introduce optimization only after the reference path exists.

Potential passes:

- vectorization;
- fusion;
- memory placement;
- deterministic parallelization;
- common-subexpression work;
- dead-result elimination only for operations proven pure and total unless original failure is explicitly preserved at the same observable point;
- verified cache reuse under the PR #5 rule/evidence validation contract.

Optimization correctness is more important than speed. Potentially failing pure operations remain observable under fail-stop semantics.

`VERIFIED_REUSE` requires its resolvable `legality_rule_id` and passing context-bound `verification_evidence_id` before substitution. Unverified hits cannot supply results. Cache substitution is effect-free by default; effectful reuse requires the specifically applicable separately frozen replay/cache semantics preserving effects, authorization, ordering, failure, provenance, and observable state.

## PR #14 — Normative QX-POSIX Contract

Freeze QX-POSIX before implementing it.

Specify process, stream, file, environment, signal, byte/text conversion, encoding, buffering, failure, effect-boundary, capability, ordering, and provenance semantics.

## PR #15 — QX-POSIX Reference Implementation

Implement PR #14 as a composable profile usable by generated targets. POSIX is not a compiler backend.

## PR #16 — LLVM Backend

Add an LLVM machinery backend after the C reference path and POSIX profile contract are established.

LLVM must preserve the same Vector/Dataflow, contract, provenance, effect, failure, and authorization semantics.

## PR #17 — Normative Generic GPU Execution Contract

Freeze vendor-neutral accelerator execution semantics before CUDA implementation.

Specify generic device selection, protected-machinery requirements, data movement, synchronization, determinism/numeric constraints, failure, authorization, and provenance.

## PR #18 — CUDA Backend

Implement CUDA as a machinery backend against PR #17.

CUDA selection is machinery. It does not itself imply or activate `QX-CUDA`.

## PR #19 — Normative QX-CUDA Control Contract

Freeze optional CUDA-specific language controls separately from CUDA machinery selection.

Specify launch/memory/tuning control validation, lowering, determinism, failure, provenance, and versioning.

## PR #20 — QX-CUDA Reference Control Implementation

Implement PR #19. Generic CUDA-targeted programs remain valid without QX-CUDA when they do not use QX-CUDA-owned controls.

## PR #21 — Additional Backends

Add additional actual machinery/code-generation targets only after their required contracts are frozen.

MIDI mapping remains a `QX-MIDI` adapter/extension workstream, not a backend. Formal-tool integration remains behind a proof/verification extension such as `QX-PROVE`, not a backend.

## PR #22 — Formalization

Formalize the frozen semantic core and critical invariants where useful.

Potential targets include:

- semantic preservation across lowerings;
- result-binding correspondence;
- effect/capability authorization invariants;
- protected-machinery authorization-before-use;
- fail-stop sequencing;
- determinism contracts;
- epistemic non-promotion;
- optimization equivalence.

## Deferred normative workstream — QSOL text profile

The human `.qsl` grammar remains deferred until a normative text-profile specification freezes:

- lexical grammar;
- source grammar;
- shorthand/default reconstruction;
- diagnostics;
- canonical text rendering;
- source-to-Semantic-IR mapping.

Examples before that freeze are illustrative and must not become accidental parser law.

## Principle

> Specify meaning. Preserve identity. Trace concrete execution. Authorize before effects or protected machinery begin. Bind generated bytes to truthful direct toolchain edges plus exact transitive ancestry. Optimize only after equivalence is demonstrated.
