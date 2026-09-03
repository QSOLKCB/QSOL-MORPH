# Failure and Partial-Effect Semantics

QSOL-MORPH treats failure behavior as part of program semantics.

This document is architectural and non-normative until the invariant freeze. Its purpose is to prevent the reference machine and later backends from inventing incompatible answers to the same failed computation.

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

This default deliberately avoids inventing implicit continuation semantics.

If a future JOB construct permits independent DECK continuation, retry, fallback, compensation, or parallel execution after another DECK fails, that behavior must be explicit and frozen, including dependency, cancellation, ordering, artifact-status, and provenance rules.

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

Every protected external effect is modeled as an **identified effect attempt** with its own completion state. A CARD may produce zero, one, or multiple effect attempts, and a DECK/JOB may accumulate many attempts across multiple CARDs.

At minimum, each attempt should distinguish:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

These names are provisional, but the distinctions are semantic and must be mutually exclusive.

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

- denied capability;
- invalid path rejected before opening a file;
- process launch rejected before a child exists.

`NOT_STARTED` is invalid once the protected effect has actually begun.

### COMPLETED

The **effect itself reached its defined external completion boundary**.

Completion is independent of whether the enclosing CARD later reports success or failure.

For example, a process may run to completion and return exit status `2`. The process effect attempt is still `COMPLETED`, while the enclosing CARD may produce `FAILURE(PROCESS_FAILED)` because that completed process returned a non-success status under the active contract.

Likewise, a complete file write may be `COMPLETED` even if a later validation step in the same CARD causes the CARD to fail.

If the process is known to have exited but the implementation cannot fully enumerate everything that process changed elsewhere, the attempt is still `COMPLETED`: the effect's own completion boundary is known. Broader consequence uncertainty belongs in additional provenance, not in the completion-state enum.

A CARD failure must not relabel an already completed effect attempt as `PARTIAL` or `UNKNOWN` merely because the CARD outcome is failure.

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

`PARTIAL` describes the effect attempt, not merely the fact that its enclosing CARD failed.

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

For example, an operation requiring both `AI_MODEL` and `NETWORK` must not begin its remote model effect unless both capabilities have been granted for that execution.

If authorization is denied or cannot be established for any required capability, the attempt fails with state `NOT_STARTED`.

This rule is unconditional for capability authorization. A backend may not downgrade it to "where practical" merely because preflight is inconvenient.

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

- which CARD failed;
- which DECK failed;
- whether the JOB failed or an explicit JOB-level handler changed the outcome;
- at what stage the failure occurred;
- which stable failure class applies;
- which backend/runtime detail was reported;
- which prior DECKs had completed;
- which effect attempts existed, which canonical declared effect produced each one, the complete capability set governing each attempt, and the completion state of each attempt;
- whether any output artifact became externally visible;
- what determinism, numeric, randomness, capability, policy, and extension contracts were active.

A minimal conceptual record may contain:

```text
execution_status
job_status
deck_status
failure_card_id
failure_class
failure_stage
backend_detail?
completed_decks[]
effect_attempts[]
observable_artifacts[]
```

Each `effect_attempts[]` entry should be independently identifiable and may carry fields such as:

```text
effect_attempt_id
declared_effect_id
card_id
effect_kind
required_capabilities[]
sequence_index
completion_state
backend_detail?
observable_artifacts[]
```

`declared_effect_id` links the runtime attempt back to the canonical `EffectRequirement.effect_id`; `effect_attempt_id` identifies the particular runtime attempt. They are not interchangeable.

The trace must not collapse multiple external actions into one aggregate `partial_effect_state`.

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

Partial artifacts may still be scientifically useful, but their status must reflect the execution that actually occurred.

## Backend rule

Backends may translate failure into native mechanisms such as return codes, tagged unions, exceptions, traps, CUDA status codes, or other target facilities.

Those are implementation choices.

They must map back to the same QSOL CARD/DECK/JOB success/failure semantics and the same per-effect-attempt completion semantics.

## Principle

> Failure is observable behavior. Effect completion belongs to the effect attempt, not the CARD outcome. Known completion takes precedence over consequence uncertainty. Authorization happens before the effect. Do not leave any of these to backend folklore.
