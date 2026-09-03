# Extensions and Capabilities

QSOL-MORPH should keep the core deliberately small and move optional machinery behind explicit extension profiles.

## Extension profiles

Candidate profiles include:

```text
QX-VEC      vector operations
QX-MATH     scientific numerics
QX-POSIX    POSIX processes and streams
QX-GPU      generic accelerator execution
QX-CUDA     CUDA-specific controls
QX-AI       model interaction
QX-PROVE    formal-verification adapters
QX-MIDI     MIDI 2.0 integration
QX-NET      network access
```

These names are provisional until frozen by a future specification.

## Core rule

An extension may add capability. It should not silently redefine frozen core meaning.

If a feature is target-specific, vendor-specific, effectful, or optional, the default assumption is that it belongs in an extension rather than QSOL-CORE.

## Declaring extensions

Illustrative source:

```text
USE QX-VEC
USE QX-MATH
USE QX-GPU
DENY QX-NET
```

This allows a program to expose its execution surface before it runs.

## Capabilities

A capability is permission to perform a class of effect.

Candidate capability families include:

```text
FILESYSTEM_READ
FILESYSTEM_WRITE
NETWORK
PROCESS
CLOCK
RANDOM
GPU
AI_MODEL
EXTERNAL_TOOL
```

The final naming scheme is not frozen.

## Effects versus capabilities

An **effect** describes what an operation does.

A **capability** describes what the execution environment allows.

Example:

```text
FETCH DATASET
```

may require a network effect and therefore a network capability.

If the deck declares:

```text
DENY QX-NET
```

then reachable network-requiring operations should be rejected before execution where practical.

## Fail closed

Capability checking should prefer rejection over silent escalation.

A program denied network access must not have a backend quietly substitute a network-backed helper because that helper is convenient.

## Extension versioning

Extensions should be independently versionable.

A frozen deck should be able to identify the extension contract it expects, for example conceptually:

```text
USE QX-VEC VERSION 1
```

The exact syntax is not yet defined.

## Backend-specific controls

Vendor controls belong behind explicit profiles.

Generic source:

```text
RUN MODEL ON GPU
```

Target-specific source:

```text
USE QX-CUDA
RUN MODEL ON CUDA WITH:
    threads 128
```

A generic backend should not be required to understand CUDA-specific launch syntax.

## AI capability boundary

AI model interaction is an external effect, not ordinary arithmetic.

A future QX-AI profile should expose material properties such as:

- model/provider identity;
- sampling or deterministic settings;
- input/output boundaries;
- external network requirements;
- caching;
- provenance;
- replay limitations.

An AI result must not silently acquire a stronger epistemic class merely because the call succeeded.

## MIDI profile

MIDI 2.0 should be an adapter/extension rather than part of the core language.

A QSOL card can retain stable semantics while QX-MIDI maps relevant events or properties into an external MIDI representation.

## Principle

> Keep the core small. Make optional power explicit. Never let an extension smuggle new meaning into old syntax.
