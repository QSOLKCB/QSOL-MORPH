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
QX-NET      network-related syntax/adapters
```

These names are provisional until frozen by a future specification.

## Core rule

An extension may add versioned syntax, adapters, effects, lowering hooks, or capability **requirements**. Activating or installing an extension never grants a runtime capability by itself, and an extension must not silently redefine frozen core meaning.

If a feature is target-specific, vendor-specific, effectful, or optional, the default assumption is that it belongs in an extension rather than QSOL-CORE.

## Declaring extensions

Extension availability and runtime authorization are separate concerns.

Illustrative source:

```text
USE QX-VEC
USE QX-MATH
USE QX-GPU
USE QX-NET

DENY NETWORK
```

`USE QX-NET` means that the deck expects the network extension/profile to exist. `DENY NETWORK` means that execution is not authorized to perform the network capability. A validator can therefore distinguish unsupported syntax/profile requirements from prohibited runtime effects.

## Capabilities

A capability is runtime permission to perform a class of protected effect or access a class of protected machinery.

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

An **extension profile** describes optional language/adapter functionality that must be available to interpret or lower the deck.

Example:

```text
FETCH DATASET
```

may require a network effect and therefore the `NETWORK` capability. If it uses syntax supplied by QX-NET, the deck may additionally declare:

```text
USE QX-NET
```

If the deck or execution policy declares:

```text
DENY NETWORK
```

then a network-requiring effect must not begin. Capability authorization is unconditional and must succeed before the protected effect starts, even when QX-NET is installed and available.

Conversely, allowing `NETWORK` does not make QX-NET syntax available if that extension is absent.

## Multiple capability requirements

A single protected effect may require more than one capability.

For example, a QX-AI operation that invokes a remote model may require both:

```text
AI_MODEL
NETWORK
```

Every capability required by that specific effect attempt must be granted before the attempt begins. Trace/provenance therefore records the complete per-attempt required-capability set rather than one optional capability label.

## Fail closed

Capability checking should reject rather than silently escalate.

A program denied network access must not have a backend quietly substitute a network-backed helper because that helper is convenient.

Likewise, an unavailable extension must not be treated as equivalent to a denied capability. The diagnostic should say which boundary failed.

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

GPU access may require an execution capability/profile, but selecting GPU machinery is not itself an externally observable Semantic-IR effect. Device selection belongs in MORPH/execution trace metadata.

## POSIX profile

QX-POSIX is a composable execution profile rather than a compiler backend.

Its operational semantics must be frozen by a normative QX-POSIX contract before a reference implementation or backend adapter is allowed to choose process, stream, file, environment, signal, encoding, buffering, failure, or effect-completion behavior.

A program emitted through C, LLVM, or another backend may still use POSIX process, file, signal, environment, and stream semantics when QX-POSIX is explicitly active and every capability required by the specific protected effect is authorized.

## AI capability boundary

AI model interaction is an external effect, not ordinary arithmetic.

A future QX-AI profile should expose material properties such as:

- model/provider identity;
- sampling or deterministic settings;
- input/output boundaries;
- external network requirements;
- complete capability requirements;
- caching;
- provenance;
- replay limitations.

An AI result must not silently acquire a stronger epistemic class merely because the call succeeded.

## MIDI profile

MIDI 2.0 should be an adapter/extension rather than part of the core language.

A QSOL card can retain stable semantics while QX-MIDI maps relevant events or properties into an external MIDI representation.

## Principle

> Keep the core small. Make optional power explicit. An extension defines functionality and requirements; policy grants permissions. Never let one masquerade as the other.
