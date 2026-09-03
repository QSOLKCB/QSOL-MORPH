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

Only operations proven pure **and total** under the active contract are candidates for unconstrained dependency-based reordering.

## Arithmetic failures

The reference semantics must define arithmetic-domain failure before executable backends are accepted.

At minimum:

```text
DIV x 0  -> FAILURE(DIVIDE_BY_ZERO)
MOD x 0  -> FAILURE(MODULO_BY_ZERO)
```

Integer overflow, floating-point exceptional values, transcendental domain errors, and conversion failures must be governed by the active type and numeric contracts rather than by whatever behavior a target language or processor happens to provide.

Undefined target behavior is not a valid QSOL semantic contract.

## Effectful CARD failure

Effects complicate failure because the external world may already have changed.

QSOL-MORPH should distinguish at least:

```text
NOT_STARTED
COMPLETED
PARTIAL
UNKNOWN
```

These names are provisional, but the distinction is important.

### NOT_STARTED

The operation failed before any externally observable effect began.

Examples may include:

- denied capability;
- invalid path rejected before opening a file;
- process launch rejected before a child exists.

### COMPLETED

The effect completed, but a later operation failed.

A later failure must not erase the fact that the completed effect occurred.

### PARTIAL

The effect began and some externally observable portion occurred before failure.

Examples may include:

- a file write that wrote a prefix before storage failure;
- a streamed network write that transmitted some records before disconnect;
- an external process that started and changed state before returning failure.

### UNKNOWN

The implementation cannot establish whether or how much of the external effect became observable.

`UNKNOWN` is preferable to inventing a clean rollback claim without evidence.

## Capability authorization and preconditions

Capability authorization is a hard boundary, not a best-effort preflight.

**Every protected external effect must have its required capability successfully authorized before that effect begins.**

For example, an operation requiring `NETWORK` must not open a socket, resolve through a network-backed helper, transmit data, or otherwise begin the protected network effect unless `NETWORK` has been granted for that execution.

If authorization is denied or cannot be established, the operation fails with the effect state `NOT_STARTED`.

This rule is unconditional for capability authorization. A backend may not downgrade it to "where practical" merely because preflight is inconvenient.

Other non-authorization checks, such as static validation or external-system preconditions that cannot always be known in advance, should occur before an effect begins where practical. Failure of those checks after an effect begins must use the partial-effect model rather than pretending the effect never happened.

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

and `@010` and `@011` completed before `@012` failed, both writes remain observable and must remain in the trace.

A backend must not pretend that the DECK or JOB was transactional unless the source explicitly requested a transaction-like construct whose semantics are frozen and supported.

## Process and external-tool failures

External process/tool failure should produce a structured QSOL failure plus target-specific detail where useful.

Conceptually:

```text
failure_class = PROCESS_FAILED
card_id = @042
backend_detail.exit_status = 2
```

The target-specific detail enriches the record but does not replace the stable semantic failure class.

## File and network failures

Filesystem and network operations should similarly preserve a stable semantic class while retaining implementation detail where useful.

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
- which prior effects and DECKs had completed;
- whether the failed effect was `NOT_STARTED`, `PARTIAL`, or `UNKNOWN`;
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
prior_committed_effects[]
completed_decks[]
partial_effect_state
observable_artifacts[]
```

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

They must map back to the same QSOL CARD/DECK/JOB success/failure and partial-effect semantics.

## Principle

> Failure is observable behavior. Authorization happens before the effect. Do not leave either to backend folklore.
