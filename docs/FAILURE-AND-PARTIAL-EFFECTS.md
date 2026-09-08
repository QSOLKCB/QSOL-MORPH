# Failure and Partial-Effect Semantics

QSOL-MORPH treats failure behavior as part of program semantics.

This document is architectural and non-normative until the invariant freeze. Its purpose is to prevent the reference machine and later backends from inventing incompatible answers to the same failed computation.

Record inventories here are projections of the [canonical trace contract](TRACE-AND-PROVENANCE.md#one-record-contract-not-independent-mirror-schemas), not independent weaker schemas. Conditional field requirements, exact cross-record capability equality, typed non-reach causes, representation-qualified execution subjects, and content-bound rule/evidence validation apply to failure manifests too. Shorter inventories never waive those checks.

## Core outcome model

A CARD evaluation conceptually produces one of two outcomes:

```text
SUCCESS(value?)
FAILURE(record)
```

A failure is not an ordinary value and must not be represented by an implicit sentinel such as `0`, `false`, an empty string, NaN, or a backend-specific magic return value unless the frozen type/operation contract explicitly defines that value as ordinary data.

## Default DECK behavior

The candidate default is **fail-stop**.

An unhandled CARD failure stops further CARD execution in the DECK.

Earlier successfully committed effects remain part of history. Later cards do not run merely because a backend happens to support continuing after an error.

If QSOL later introduces recovery, retry, compensation, or exception-like constructs, those must be explicit semantic constructs with defined ordering and provenance rules.

## Default JOB behavior

A JOB coordinates DECKs, so DECK failure must have a JOB-level meaning.

The candidate default is also fail-stop at the JOB boundary:

```text
CARD failure
    ↓ unhandled
DECK failure
    ↓ unhandled
JOB failure
```

When a DECK fails and no explicit JOB-level recovery rule handles that failure:

- the enclosing JOB becomes failed;
- no later DECK in the JOB starts;
- a dependent DECK or comparison must not execute against missing, failed, or partial output as though it were complete;
- already completed DECKs and their externally observable effects remain part of provenance;
- partial artifacts may be retained only with their failed/partial status intact.

Every DECK selected for the JOB execution remains represented in provenance even when it never starts. A later DECK prevented by fail-stop is not deleted from execution history; it receives an explicit non-started/skipped outcome or frozen equivalent.

This default deliberately avoids inventing implicit continuation semantics.

If a future JOB construct permits independent DECK continuation, retry, fallback, compensation, or parallel execution after another DECK fails, that behavior must be explicit and frozen, including dependency, cancellation, ordering, artifact-status, and provenance rules.

### Failure-policy authority

A failure-policy binding records immutable/versioned requested and effective behavior definitions. Any semantic change, including fail-stop changed to continue, retry, or compensation, requires `mapping_or_transition_rule_id` resolving to an accepted `CONTRACT_TRANSITION` rule and `transition_evidence_id` resolving to passing evidence for that exact `FAILURE_BEHAVIOR_BINDING` subject before activation or application. A representation-only mapping uses a separate rule kind, `FAILURE_BEHAVIOR_MAPPING`, and must establish unchanged semantics; it cannot authorize a behavioral change. Missing or unverifiable authority/evidence rejects the transition under the unchanged applicable rejection/fail-stop contract. The effective policy cannot authorize itself. These are the [canonical failure-policy transition conditions](TRACE-AND-PROVENANCE.md#failure-policy-transitions), including their subject/context and validation-before-application requirements.

## Pure CARD failure

A pure CARD that fails commits no semantic state.

Examples include:

- invalid arithmetic-domain operations;
- type/domain contract failure;
- failed pure preconditions.

A failed pure evaluation must not leave behind a partially assigned result.

Pure does **not** imply unobservable under fail-stop execution. A pure CARD that may fail can change whether later effects occur. Therefore a potentially failing pure CARD cannot be freely moved across observable effects unless an explicit ordering/commit rule proves the transformation preserves failure behavior.

Only operations proven pure **and total** under the active contract are candidates for unconstrained dependency-based reordering or dead-result elimination.

## Arithmetic failures

The reference semantics must define arithmetic-domain failure before executable backends are accepted.

At minimum:

```text
DIV x 0  -> FAILURE(DIVIDE_BY_ZERO)
MOD x 0  -> FAILURE(MODULO_BY_ZERO)
```

Integer overflow, floating-point exceptional values, transcendental domain errors, and conversion failures must be governed by the active type and numeric contracts rather than by whatever behavior a target language or processor happens to provide.

Undefined target behavior is not a valid QSOL semantic contract.

## Effect attempts

Effects complicate failure because the external world may already have changed.

Every protected external effect is modeled as an **identified effect attempt** with its own authorization decision and completion state. A CARD or lower operation may produce zero, one, or multiple effect attempts, and a DECK/JOB or lower-entry execution may accumulate many attempts across multiple execution subjects.

At minimum, each attempt should distinguish:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

These names are provisional, but the distinctions are semantic and must be mutually exclusive.

A declared effect does not necessarily have an attempt. Its execution subject may be on an untaken branch, may never be reached after an earlier fail-stop failure, or may be explicitly skipped under a frozen rule. The trace must distinguish those legitimate non-attempts from a backend silently omitting a reachable declared effect. An explicit skip must identify its governing frozen rule and passing applicability evidence for the concrete invocation; a reason label alone is not permission. Every not-reached reason, including `CARD_NOT_REACHED` or a lower-subject equivalent, requires a validated typed control/failure cause or verified frozen skip for that exact invocation.

A detected omission of a **reachable required effect** is not an ordinary non-attempt outcome. It is an implementation/conformance failure and must produce a structured failed execution outcome. Recording `BACKEND_OMISSION_DETECTED` (or a frozen equivalent) cannot be used to legitimize success after the backend skipped required semantic behavior.

## Completion-state decision rule

The state is determined in this order:

```text
1. NOT_STARTED
   The protected effect never began.

2. COMPLETED
   The effect reached its defined external completion boundary.
   This takes precedence whenever completion is known, even if the
   broader external consequences of the completed operation cannot be
   fully enumerated.

3. The effect began and is known not to have completed:
   a. ABORTED_CLEAN
      No externally observable change occurred.
   b. PARTIAL
      Some externally observable portion occurred.
   c. UNKNOWN
      Whether the incomplete attempt was clean or partial cannot be
      established.

4. UNKNOWN
   Whether the effect reached its completion boundary cannot be
   established.
```

A conforming implementation must not choose between `COMPLETED` and `UNKNOWN` for the same known-completed attempt. Known completion wins. `UNKNOWN` is reserved for unknown completion, or for a known-incomplete attempt whose observability cannot be classified as clean or partial.

### NOT_STARTED

The protected effect never began.

Examples may include:

- denied capability after a runtime attempt has been identified but before the protected effect begins;
- invalid path rejected before opening a file;
- process launch rejected before a child exists.

`NOT_STARTED` is invalid once the protected effect has actually begun.

A declaration that was never reached is different: if no runtime attempt object exists at all, use an explicit effect non-attempt record rather than inventing a `NOT_STARTED` attempt.

### COMPLETED

The **effect itself reached its defined external completion boundary**.

Completion is independent of whether the enclosing CARD or lower operation later reports success or failure.

For example, a process may run to completion and return exit status `2`. The process effect attempt is still `COMPLETED`, while the enclosing CARD may produce `FAILURE(PROCESS_FAILED)` because that completed process returned a non-success status under the active contract.

Likewise, a complete file write may be `COMPLETED` even if a later validation step in the same execution subject causes that subject to fail.

If the process is known to have exited but the implementation cannot fully enumerate everything that process changed elsewhere, the attempt is still `COMPLETED`: the effect's own completion boundary is known. Broader consequence uncertainty belongs in additional provenance, not in the completion-state enum.

An enclosing failure must not relabel an already completed effect attempt as `PARTIAL` or `UNKNOWN` merely because the execution subject outcome is failure.

### ABORTED_CLEAN

The effect began, did **not** reach its defined completion boundary, and the implementation can establish that **no externally observable change occurred**.

Examples may include:

- a buffered operation that begins internally but discards its buffer before publication;
- an atomic external operation that aborts before commit and can prove no external state changed;
- a staged write whose temporary state is never made externally visible and is removed before failure is reported.

`ABORTED_CLEAN` is distinct from `NOT_STARTED` because the protected operation did begin. It is distinct from `PARTIAL` because no portion became externally observable, and distinct from `UNKNOWN` because the absence of observable change is established rather than uncertain.

### PARTIAL

The effect began, became externally observable in some incomplete form, and did **not** reach its defined completion boundary before failure.

Examples may include:

- a file write that wrote a prefix before storage failure;
- a streamed network write that transmitted some records before disconnect;
- an external process launch/interaction that changed state but did not reach the operation's defined completion boundary.

`PARTIAL` describes the effect attempt, not merely the fact that its enclosing execution subject failed.

### UNKNOWN

`UNKNOWN` applies only when the attempt cannot be placed in one of the known states above.

Two cases remain:

- whether the effect reached its completion boundary cannot be established; or
- the effect is known to have begun and not completed, but the implementation cannot establish whether the incomplete attempt was externally clean or partial.

`UNKNOWN` must not override a known `COMPLETED` state merely because some downstream or broader side effects of the completed operation are difficult to enumerate.

`UNKNOWN` is preferable to inventing a clean rollback, partial-effect claim, or completed-effect claim without evidence.

## Capability authorization and preconditions

Capability authorization is a hard boundary, not a best-effort preflight.

**Every protected external effect must have every capability in its complete required-capability set successfully authorized before that effect begins.**

Authorization is contextual to the concrete runtime attempt. Each identified effect attempt therefore links to an identified authorization record that preserves at least:

```text
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

`effect_requirement_ref` identifies the protected declaration in the representation that owns it. `execution_subject_ref` identifies the concrete CARD or lower-operation invocation to which authorization applies. Semantic CARD attempts require matching `card_id` and `card_execution_id`; a direct QSOL-CORE attempt resolves to `CORE_OPERATION` / `operation_execution_id`, with CARD fields absent unless verified Semantic lineage is retained.

Before accepting the authorization, validate exact complete-set equality between the hash-bound declaration in the named representation, its trace declaration, the attempt, and the authorization record. Also validate their complete owner/execution identities, effect kind, and reciprocal attempt/authorization links. The canonical set must be fully granted with no denied member; granted and denied sets are disjoint. Matching truncated runtime copies are not enough: a declaration requiring `{AI_MODEL, NETWORK}` cannot be authorized by copying and granting only `{AI_MODEL}` in both runtime records. These checks are required in addition to event ordering and follow [Declaration-bound authorization validation](TRACE-AND-PROVENANCE.md#declaration-bound-authorization-validation).

Authorization ordering and effect-begin ordering use the same frozen monotonic event-order domain. For every protected effect known to begin:

```text
authorization_sequence_index < effect_begin_sequence_index
```

A denied authorization has no effect-begin event. A generic attempt counter or source-order index is not a substitute for this authorization-before-begin proof.

Execution-wide granted/denied capability summaries are useful diagnostics, but they do not prove which policy decision governed one particular attempt.

For example, an operation requiring both `AI_MODEL` and `NETWORK` must not begin its remote model effect unless both capabilities have been granted by the authorization record for that attempt.

If authorization is denied or cannot be established for any required capability after a runtime attempt has been identified, the attempt fails with state `NOT_STARTED` and retains the denial record.

This rule is unconditional for capability authorization. A backend may not downgrade it to "where practical" merely because preflight is inconvenient.

Protected machinery authorization is a separate boundary. Selecting GPU/CUDA or another protected target is not an external effect, but every machinery capability required by the applicable canonical machinery requirement must be authorized before that machinery is used. A denied machinery requirement must not be represented as a fake external effect attempt merely to fit this model.

Protected machinery use is represented by identified `machinery_use_records[]`. Each use record references the applicable successful machinery authorization records and records the protected-use start/stop event in the same frozen ordering domain:

```text
machinery_use_records[]:
    machinery_use_record_id
    backend_selection_scope_id
    backend_selection_decision_id
    machinery_authorization_record_ids[]
    generated_artifact_ids[]
    output_ids[]
    protected_use_kind
    protected_use_start_sequence_index
    protected_use_stop_sequence_index?
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
    backend_unit_id?
```

`backend_selection_decision_id` identifies the concrete selection decision governing the use, not merely its shared selection scope. `generated_artifact_ids[]` identifies the exact generated executable/kernel/bytecode bytes actually launched by the protected use and remains available when failure occurs before any output exists; every referenced artifact must resolve consistently with the selection scope/decision/backend unit. `execution_subject_refs[]` identifies the actual participating runtime invocations. Semantic CARD uses resolve to `card_executions[]`; direct Core uses resolve to exact `CORE_OPERATION` / `operation_execution_id` entries. `source_card_ids[]` / `card_execution_ids[]`, when present, are verified Semantic projections and cannot stand in for a lower-operation subject.

For genuine pre-execution RUN/DECK machinery setup only, an empty execution-subject array requires `initiating_scope_ref`, a typed `{ scope_kind, scope_id }` reference to the actual initiating RUN or DECK_EXECUTION, resolving to `run_id` or `deck_execution_id`. A direct QSOL-CORE operation is not pre-CARD setup and must identify its operation execution. Shared uses list their actual participating execution subjects under the frozen execution mapping. `output_ids[]` is the reciprocal occurrence-level join to `outputs[].machinery_use_record_ids[]`; exact requirement identity is resolved through the linked canonical machinery authorization records and their absolute-owner-path `machinery_requirement_refs[]`, not a bare requirement-ID list on the use record. These fields follow the [canonical machinery-use contract](TRACE-AND-PROVENANCE.md#machinery-authorization-and-use-provenance).

Every referenced authorization must have completed before protected use begins:

```text
machinery_authorization.authorization_sequence_index
    < machinery_use.protected_use_start_sequence_index
```

A denied machinery authorization must not have a machinery-use start record. A failure that occurs after GPU/CUDA or other protected machinery has begun must retain the concrete use record rather than leaving authorization as an unconnected policy outcome.

Other non-authorization checks, such as static validation or external-system preconditions that cannot always be known in advance, should occur before an effect begins where practical. Failure of those checks after an effect begins must use the per-attempt effect model rather than pretending the effect never happened.

## Prior effects and ordering

Source order is semantically relevant whenever reordering could change failure or external observability.

If:

```text
@010 WRITE A
@011 DIV X 0
@012 WRITE B
```

then source-order fail-stop semantics permit `WRITE A` to complete before the division fails and prevent `WRITE B` from starting. A scheduler must not move the failing division before `WRITE A` merely because the division is pure and data-independent.

Similarly, if:

```text
@010 WRITE A
@011 WRITE B
@012 FAIL
```

and the first two write attempts completed before `@012` failed, both remain observable and must remain individually represented in the trace.

A backend must not pretend that the DECK or JOB was transactional unless the source explicitly requested a transaction-like construct whose semantics are frozen and supported.

## Process and external-tool failures

External process/tool failure should produce a structured QSOL failure plus target-specific detail where useful.

Conceptually:

```text
failure_class = PROCESS_FAILED
failure_card_id = @042
backend_detail.exit_status = 2
```

If the process itself ran to its defined completion boundary, its effect attempt is `COMPLETED` even though the CARD outcome is `PROCESS_FAILED`.

The target-specific detail enriches the record but does not replace the stable semantic failure class.

## File and network failures

Filesystem and network operations should similarly preserve a stable semantic failure class while retaining per-attempt completion detail and implementation detail where useful.

Examples:

```text
FILE_WRITE_FAILED
NETWORK_CONNECT_FAILED
NETWORK_TRANSFER_FAILED
```

Exact names are not frozen in this documentation phase.

## Trace requirements

A failed execution should be traceable with enough information to answer:

- which aggregate run/JOB failed;
- every DECK selected for that JOB run and the outcome of each one, including DECKs prevented from starting;
- every CARD in those selected DECKs and whether it executed, failed, was on untaken control flow, was blocked by prior fail-stop, or was explicitly skipped under a frozen rule;
- every lower-operation execution when the run legitimately entered QSOL-CORE or another lower representation without Semantic CARD execution structure;
- which identified control decision or failure record caused an untaken or blocked execution path;
- which typed scope failed, and which concrete CARD or lower-operation execution subject caused it when applicable;
- which exact stable failure-behavior bindings governed the failure and its propagation or handling;
- which exact result-determinism, numeric, and randomness scope records governed the failure;
- at what stage the failure occurred;
- which stable failure class applies;
- which backend/runtime detail was reported;
- which backend-selection scopes and ordered decisions, including denied candidates and fallback predecessors, governed authorization and use;
- which declared effects existed;
- which effect attempts existed, which exact representation-qualified effect declaration produced each one, which concrete execution subject owned each attempt, which authorization decision governed each attempt, the complete capability set governing each attempt, the authorization-before-begin ordering evidence, and the completion state of each attempt;
- why any declared effect had no runtime attempt for a concrete execution subject and which typed control/failure cause or verified frozen skip rule governs that reason;
- which protected machinery was actually used, which concrete execution subjects or genuine pre-execution initiating scope owned that use, which successful authorization records governed it, and whether every authorization completed before protected use began;
- whether any output artifact became externally visible and which concrete attempt or machinery use produced/exposed it;
- what determinism, numeric, randomness, capability, machinery-authorization, policy, and extension contracts were active.

A minimal conceptual record may contain:

```text
run_id
execution_status
job_id?
job_status?
deck_executions[]?
card_executions[]?
operation_executions[]?
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
rule_records[]
validation_evidence[]
observable_output_ids[]
```

Failure identity is carried by `failure_records[]`; the aggregate record references a `primary_failure_record_id?` when one failure is designated primary rather than duplicating a mandatory CARD field at the top level.

The backend-selection ledgers are required wherever machinery authorization/use records reference their scope or decision IDs. Preserve denied candidates, fallback predecessor chains, and final decisions, not just a selected-backend label. A standalone failure manifest must retain the complete transitive closure of its references, including governing policy bindings, result-determinism/numeric/randomness scope ledgers, requirements, rules, evidence, operation/CARD execution subjects, and observable outputs, inline or through retrievable content-bound trace records. A dangling ID or an unbound mutable external trace link is incomplete provenance. The ledger definitions are those in [Trace and Provenance](TRACE-AND-PROVENANCE.md#failure-trace), not independent weaker schemas. Fallback decisions retain their applicable `BACKEND_FALLBACK` rule and subject-bound pre-application evidence; a denied candidate and a fallback sharing a scope never share authorization by implication.

Each selected DECK is represented through an identified record such as:

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

`governing_failure_record_id?` identifies the earlier concrete failure that blocks a selected DECK from starting under the active failure policy. `failure_record_id?` identifies a failure caused by this DECK execution itself. A fail-stop-skipped DECK requires the governing cause and must not overload the caused-failure field with that different meaning.

A derived `completed_decks[]` summary may be useful, but it is not a substitute for identified per-DECK execution records because it cannot represent the failed DECK and later DECKs that never started.

Execution-path causes use distinct typed namespaces. A control decision is identified independently from a failure record:

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

`failing_scope_kind` plus `failing_scope_id` is always present. It identifies the actual JOB, DECK execution, CARD execution, Core/lower-operation execution, lowering, backend-selection scope, machinery boundary, or other frozen typed scope where the failure occurred.

`failure_behavior_binding_ids[]` is required and resolves to the exact stable failure-policy bindings active for this event and its handling/propagation, including the applicable frozen default fail-stop binding. A computation-scope match or a resulting retry/skip path does not identify the governing policy when multiple bindings or transitions exist. A rejected requested policy is not an effective handling policy; pre-CARD/lower-entry rejections retain the actual setup/rejection-handling binding. Missing, stale, or incompatible governing bindings make the failure trace incomplete.

`result_determinism_scope_ids[]`, `numeric_scope_ids[]`, and `randomness_scope_ids[]` are also required exact-set relations. Derive the complete applicable sets from the typed failing scope, the concrete execution subject when present, and validated lowering/contract mappings, then require every recorded ID to resolve to the retained type-specific ledger. Empty arrays are valid only when no scope in that family governs the failure. An output-free numeric or RNG failure cannot omit its governing contract merely because no result exists from which to infer it.

For a CARD-caused failure, `failure_card_id` and `failure_card_execution_id` are required and resolve consistently through `card_executions[]`. For a failure before any CARD executes or in a legitimate direct lower-operation execution, those CARD-specific fields are absent. `operation_execution_id`, where applicable, names the actual lower execution subject. A producer must not fabricate a CARD attribution simply to satisfy a schema.

`control_decision_id` and `failure_record_id` are not interchangeable, even if their textual values happen to overlap.

Each Semantic CARD execution is likewise identified, conceptually:

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

For a failed CARD outcome, `failure_record_id` is required and resolves to the exact `failure_records[]` entry governing that concrete outcome, directly or through an explicitly frozen and validated propagation relation. Multiple same-class failures, retries, or propagation records cannot be distinguished by repeated `failure_class`/`failure_stage` strings. Those optional summaries may be derived only from the referenced record and never replace its stable key. A failed DECK has the same conditional requirement. A CARD merely blocked by prior failure uses its governing cause instead of fabricating a failure caused by that CARD.

A lower-entry execution uses `operation_executions[]` with representation-qualified operation identity and concrete `operation_execution_id`, as defined by the canonical trace contract. It does not manufacture a CARD execution to reuse the Semantic ledger.

An untaken branch points to the identified control decision that selected the other path. Prior fail-stop or another failure-caused non-reach points to the identified failure record that blocked execution. A catch-all `governing_control_or_failure_id` is not valid because it erases the target namespace.

Candidate execution outcomes may include successful execution, failed execution, untaken branch, prior fail-stop, subject not reached, or explicit frozen skip. The exact vocabulary remains provisional, but Semantic membership in `card_ids[]` must not be mistaken for proof that the CARD ran. Explicit skips require a governing skip rule and passing evidence for that exact execution subject under the rules below; skipping a parent subject cannot evade accounting for its effects. Every not-reached outcome requires a validated typed control/failure cause or verified skip for the exact invocation under [Required causes for non-reach](TRACE-AND-PROVENANCE.md#required-causes-for-non-reach).

Each `effect_requirements[]` entry preserves the exact representation-qualified declared effect, owning path, effect kind, and complete required-capability set.

Each `effect_authorization_records[]` entry preserves the contextual policy decision governing one identified attempt and its representation-qualified concrete execution subject.

Each `effect_attempts[]` entry should be independently identifiable and may carry fields such as:

```text
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

`effect_requirement_ref` links the runtime attempt to the exact effect declaration in the representation that owns it; `effect_attempt_id` identifies the particular runtime attempt; and `execution_subject_ref` identifies the concrete invocation/path in which it occurred. Semantic CARD projections are conditional. Generic `sequence_index` may order attempts as records, but it does not substitute for `effect_begin_sequence_index` when proving authorization-before-effect ordering. For `completion_state = NOT_STARTED`, begin/end indices are absent and `acquired_input_ids[]`, `observable_output_ids[]`, and `external_tool_ids[]` are empty. A retained output must never cite a `NOT_STARTED` attempt through `effect_attempt_ids[]`; failure projections inherit the same reciprocal rejection rule as the canonical trace. Material external-tool attribution also uses explicit attempt/output subject arrays and reciprocal links rather than broad CARD-only association.

When a declared effect has no runtime attempt for a concrete execution subject, an identified non-attempt record explains why:

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

Legitimate candidate reasons include untaken branch, prior fail-stop, subject not reached, and explicit frozen skip, subject to mandatory cause validation. Untaken control flow requires an applicable `governing_control_decision_id`; failure-caused non-reach requires an applicable `governing_failure_record_id`; explicit skip requires the rule/evidence pair below. A generic not-reached reason requires one of these same validated cause forms and has no cause-free exception. The cause must actually prevent the exact invocation under the active control/dependency/failure contract. An unrelated decision, another loop iteration's cause, a handled nonblocking failure, or a dangling/circular cause chain is invalid. Missing or unverifiable causes force structured conformance failure. A detected backend omission of a reachable effect is likewise a structured implementation/conformance failure, not a legitimate status label.

An explicit frozen skip requires both `governing_skip_rule_id` and `skip_verification_evidence_id`. They resolve to `rule_records[].rule_id` of kind `EFFECT_SKIP` and passing `validation_evidence[].validation_evidence_id` for this exact non-attempt record, declaration, concrete execution subject, and active semantic/policy context. Definitions, authority versions/content identities, evidence subjects, and same-domain validation-before-application ordering follow [Referenced rules and validation evidence](TRACE-AND-PROVENANCE.md#referenced-rules-and-validation-evidence). A reason label, optional control/failure link, or evidence for a different invocation is insufficient. Missing, unresolved, inapplicable, or unverifiable skip authority/evidence forces structured conformance failure rather than legitimizing an omitted reachable effect.

Declared-effect accounting is unconditional. For every selected concrete execution subject, every applicable declaration must resolve to one or more attempts, exactly one legitimate identified non-attempt, or structured failure when accounting cannot be established or a reachable required effect was omitted. There is no optional declaration-completeness audit mode and no backend/profile/optimization switch may disable this rule.

The trace must not collapse multiple external actions into one aggregate `partial_effect_state`, must not collapse protected machinery use into authorization outcomes alone, and must not collapse selected DECKs, CARD executions, or lower-operation execution paths into aggregate status that loses which semantic/runtime units actually ran.

## Determinism and failure

Determinism applies to failure behavior too.

Under a strict contract, the same canonical program, declared inputs, and execution contract should not alternate unpredictably between success and a semantic failure merely because the backend has an unspecified race or ordering decision.

When an external system is itself nondeterministic, that boundary must be declared and traced.

## Epistemic boundary

A failed execution cannot silently acquire a successful research status.

For example:

```text
FAILED TEST != VALIDATION
FAILED PROOF ATTEMPT != PROOF
PARTIAL SIMULATION != COMPLETE SIMULATION RESULT
```

Partial artifacts may still be scientifically useful, but their status must reflect the execution that actually occurred. Any non-class-preserving evidence claim requires the accepted frozen `EPISTEMIC_TRANSITION` rule and passing, content-bound substantive evidence for that exact output before claim publication, as defined by [Evidence status](TRACE-AND-PROVENANCE.md#evidence-status). A successful authorization record, model confidence, or relabeled output status cannot turn failed TEST or simulation output into PROOF.

## Backend rule

Backends may translate failure into native mechanisms such as return codes, tagged unions, exceptions, traps, CUDA status codes, or other target facilities.

Those are implementation choices.

They must map back to the same QSOL success/failure semantics, the same concrete representation-qualified execution-subject ledger, the same typed control/failure causality and governing failure-policy/execution-contract bindings, the same per-effect authorization/attempt/non-attempt ordering semantics, the same protected-machinery selection/authorization/use ledger, and the rule that a reachable declared-effect omission is failure rather than successful execution.

The [future trace-validator conformance cases](TRACE-AND-PROVENANCE.md#conformance-cases-for-the-future-trace-validator) also apply to failure-domain projections. In particular, matching failure summaries, matching truncated capability sets, a cause-free not-reached label, or fabricated Semantic lineage for a lower-entry subject are rejection cases, not sufficient evidence.

## Principle

> Failure is observable behavior. Record every selected DECK, every concrete execution-subject outcome, every typed control/failure cause, the actual governing failure and execution contracts, every declared effect's authorization/attempt or verified non-attempt reason, and every protected machinery use with its selection history and concrete execution subject. Fail when a reachable required effect is omitted. Effect completion belongs to the effect attempt, not the enclosing execution outcome. Authorization happens before the protected boundary. Do not leave any of these to backend folklore.
