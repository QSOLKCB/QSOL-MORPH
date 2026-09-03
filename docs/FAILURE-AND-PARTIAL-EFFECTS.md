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

## Pure CARD failure

A pure CARD that fails commits no semantic state.

Examples include:

- invalid arithmetic-domain operations;
- type/domain contract failure;
- failed pure preconditions.

A failed pure evaluation must not leave behind a partially assigned result.

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

## Capability and precondition checks

Where practical, capability and static/precondition checks should occur before an external effect begins.

For example, a network operation denied the `NETWORK` capability should fail before opening a connection.

This reduces partial effects, but it does not permit implementations to claim atomicity for external systems that cannot provide it.

## Prior effects and ordering

Effectful CARDs are source-ordered by default under the candidate model.

If:

```text
@010 WRITE A
@011 WRITE B
@012 FAIL
```

and `@010` and `@011` completed before `@012` failed, both writes remain observable and must remain in the trace.

A backend must not pretend that the DECK was transactional unless the source explicitly requested a transaction-like construct whose semantics are frozen and supported.

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
- at what stage it failed;
- which stable failure class applies;
- which backend/runtime detail was reported;
- which prior effects had completed;
- whether the failed effect was `NOT_STARTED`, `PARTIAL`, or `UNKNOWN`;
- whether any output artifact became externally visible;
- what determinism, numeric, randomness, capability, and extension contracts were active.

A minimal conceptual record may contain:

```text
execution_status
failure_card_id
failure_class
failure_stage
backend_detail?
prior_committed_effects[]
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

They must map back to the same QSOL success/failure and partial-effect semantics.

## Principle

> Failure is observable behavior. Do not leave it to backend folklore.
