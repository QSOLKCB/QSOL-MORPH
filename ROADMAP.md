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

This phase is an explicit gate for PR #7 and every later executable implementation.

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
failure_class
failure_stage
failure_card_id?
failure_card_execution_id?
deck_execution_id?
sequence_index?
backend_detail?
```

`failing_scope_kind` plus `failing_scope_id` is always present and is the authoritative typed identity of the failure location.

When a CARD's unhandled failure caused the record, `failure_card_id` and `failure_card_execution_id` are required and must resolve consistently through `card_executions[]`.

When failure occurs before any CARD execution, such as JOB-scoped contract rejection, DECK setup failure, lowering failure, or protected-machinery denial before CARD use, the trace must **not fabricate a CARD identity**. The typed failing scope remains sufficient and the CARD-specific fields are absent.

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
- `machinery_use_records[]` with stable use identity, governing selection scope/decision/backend unit, applicable authorization IDs, protected-use start index, and optional stop index.

Authorization and protected use share one frozen monotonic event-order domain. Every successful authorization required for a protected use must satisfy:

```text
authorization_sequence_index < protected_use_start_sequence_index
```

Denied machinery has no protected-use start record.

Fallback from a denied target is legal only under a frozen pre-execution rule and must remain a new ordered selection decision rather than overwriting the denied decision.

### Execution-contract scopes

Require stable type-specific record keys:

- `result_determinism_scopes[]` with `result_determinism_scope_id`;
- `numeric_execution_scopes[]` with `numeric_scope_id`;
- `randomness_execution_scopes[]` with `randomness_scope_id`;
- `failure_behavior_bindings[]` with stable `failure_behavior_binding_id`, governed scope/source provenance, requested/effective failure policy, and material mapping/transition identity.

Each scope retains governed computation identity and source provenance. A single execution-wide scope is legal only when a frozen normalization proves it faithfully represents every governed source requirement.

For `randomness_execution_scopes[]`, replay/audit-relevant fields include requested/effective mode, transition authority, RNG algorithm/version, seed, stream identity, parallel partitioning, backend unit, and where applicable:

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

- identified `generated_artifacts[]` linked to backend unit and backend-selection scope/decision, with optimization links and ordered `toolchain_invocation_ids[]` where applicable;
- identified `toolchain_invocations[]` carrying stable invocation ID/order, invocation kind, immutable/versioned material tool identity, target/ABI context, exact flags/configuration, material inputs, reciprocal generated-artifact outputs, backend unit, and backend-selection scope where applicable;
- identified `optimization_provenance[]` recording reference/optimized IR identity, actual transformation sequence, legality evidence, target context, and reciprocal generated-artifact links;
- identified `external_tool_versions[]` with stable links to applicable effect attempts and/or outputs plus immutable/versioned material identity, or an explicit identity-unavailable status that weakens replay/evidence claims;
- identified `cache_reuse_records[]` distinguishing cold execution, verified reuse, unverified hit, or frozen equivalent, with material cache identity, legality rule, reused computation/artifact identity, and verification evidence;
- per-output cache-reuse links where applicable.

Run-wide compiler/tool version lists are summaries only. They cannot substitute for the exact ordered toolchain invocation chain that materially produced one generated artifact.

Ordinary cache substitution is effect-free by default. Effectful reuse requires separately frozen replay/cache semantics preserving declared effects, contextual authorization, source/effect/failure ordering, attempt provenance, output attribution, and observable external state.

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
    backend_detail?
```

This prevents separate runtime invocations of one canonical CARD from collapsing into one ambiguous attempt/non-attempt fact.

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

Legitimate non-attempt reasons include untaken branch, prior fail-stop, CARD not reached, or explicit frozen skip and must resolve to typed control/failure causes where applicable.

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
- failure traces preserve every selected DECK, every concrete CARD execution outcome, typed failure scope, per-effect accounting, machinery authorization/use history, and already-observable outputs/effects.

### Gate condition

No executable QSOL path may emit a research result without enough provenance to bind every identified output to:

- stable run/JOB identity;
- selected DECK and concrete CARD execution(s);
- exact immutable material inputs;
- semantic class and compatible evidence status;
- exact generated target where applicable;
- exact ordered material toolchain invocation chain where generated target bytes are involved;
- resolvable backend-selection/determinism/numeric/randomness/failure-behavior record IDs;
- protected-machinery authorization/use ordering where applicable;
- cache-reuse path;
- resolved extension set;
- concrete material external-tool identity, or explicit identity unavailability with a correspondingly weakened claim;
- concrete effect authorization/attempt/non-attempt history;
- exact external-entropy acquisition attempt(s) where applicable;
- execution/failure context that produced or prevented the result.

## PR #6 — Normative QSOL-CORE Operational Specification

Freeze QSOL-CORE semantics **before** implementing the reference machine.

Planned work:

- freeze initial instruction families and exact instruction inventory;
- define operand, result, type, and state-transition semantics;
- define arithmetic and numeric-contract interaction;
- define result-determinism execution semantics at each supported Core scope;
- define requested/effective determinism transitions and fail-closed behavior;
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
- machinery-requirement mapping;
- result-determinism, numeric, randomness, and failure-behavior mapping;
- effect/capability preservation;
- complete tagged sequencing preservation;
- rejection rules and conformance fixtures.

## PR #9 — Reference Semantic-to-QSOL-CORE Lowering

Implement PR #8.

Every material lowering decision must be provenance-bearing. Required decision families include extension requirements, qualifiers, machinery requirements, result determinism, numerics, randomness, and failure behavior whenever consumed, grouped, normalized, remapped, or otherwise transformed.

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
- lowering diagnostics and conformance/rejection fixtures.

Omission of a mapping family is allowed only under a frozen deterministic identity-scope reconstruction rule covering that family.

## PR #12 — Reference MORPH to C

Implement the first reference machinery/code-generation backend from the mandatory Vector/Dataflow IR.

Require:

- semantics-preserving C emission;
- stable backend-unit identity;
- identified `generated_artifacts[]` with artifact ID/kind/hash, backend unit, backend-selection scope, source provenance, optimization links where applicable, and ordered `toolchain_invocation_ids[]`;
- identified `toolchain_invocations[]` recording the exact material compiler/assembler/linker/code-generation identities, invocation order, target/ABI, deterministic build flags/configuration, material inputs, and reciprocal generated-artifact outputs;
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
- verified cache reuse.

Optimization correctness is more important than speed. Potentially failing pure operations remain observable under fail-stop semantics.

Cache substitution is effect-free by default. Effectful reuse requires separately frozen replay/cache semantics preserving effects, authorization, ordering, failure, provenance, and observable state.

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

> Specify meaning. Preserve identity. Trace concrete execution. Authorize before effects or protected machinery begin. Bind generated bytes to exact toolchain invocations. Optimize only after equivalence is demonstrated.