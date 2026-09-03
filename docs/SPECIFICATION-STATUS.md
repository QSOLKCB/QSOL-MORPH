# Specification Status

QSOL-MORPH is currently **pre-alpha and specification-first**.

This document defines how to interpret the repository before the core invariants are frozen.

## Current status

The material introduced in the documentation-foundation phase is **architectural and non-normative unless explicitly stated otherwise**.

Examples, keywords, instruction names, command lines, file extensions, extension names, backend lists, serialization layouts, and IR sketches are candidates. They exist to make the design reviewable before implementation.

## Normative boundary

PR #2 is reserved for **Lock in Core Invariants**.

That phase is expected to introduce:

- stable invariant identifiers;
- normative requirement language;
- a machine-readable invariant registry;
- change-control rules;
- explicit compatibility expectations.

Until that PR is merged, phrases such as `MUST`, `MUST NOT`, and `SHOULD` appearing in examples should be read as design intent rather than a released compatibility promise, unless the surrounding text explicitly declares a rule normative.

## Illustrative syntax

Code blocks containing possible QSOL syntax are examples of desired readability and semantic structure. They are not yet a frozen grammar.

For example:

```text
OBSERVE TEMPERATURE 294.3 K
RUN MODEL ON CUDA
TRACE ALL
LOCK RESULT
```

illustrates the intended style:

- explicit verbs;
- recognizable nouns;
- low syntactic noise;
- machine-readable structure;
- visible effects.

It does not yet guarantee those exact tokens or grammar productions.

## Candidate instruction set

The reduced instruction set documented in this repository is intentionally provisional. The project will prefer the smallest orthogonal core that can represent the required semantics without pushing hidden complexity into backends.

## Backend claims

A documented backend is a design target unless implementation status explicitly says otherwise.

Documentation must not imply working CUDA, LLVM, POSIX, Fortran, MIDI, AI, or formal-verification support before such support exists and is tested.

## Compatibility policy

There is no backwards-compatibility guarantee before the first frozen specification release.

Once a semantic version of the specification is declared frozen, compatibility expectations should be stated alongside it.

## Design review rule

When a conflict exists between:

1. scientific meaning;
2. deterministic/reproducible behavior;
3. inspectability;
4. backend convenience;
5. implementation performance;

higher items in that list take precedence unless a future normative specification explicitly defines a different trade-off.
