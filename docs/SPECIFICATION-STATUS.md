# Specification Status

QSOL-MORPH is currently **pre-alpha and specification-first**.

This document defines the boundary between the frozen core invariants and the remaining architectural material.

## Current status

PR #1 is the immutable v1.0.0 documentation foundation. PR #2 introduces the first
bounded normative [Core Invariants](CORE-INVARIANTS.md) contract, machine-readable
registry, documentation-agreement validator, tests, and CI. No compiler, runtime,
parser, canonical data model, operational trace validator, or backend exists yet.

## Normative boundary

The statements in `spec/core-invariants.json`, rendered in the controlled blocks of
[Core Invariants](CORE-INVARIANTS.md) and registered domain documents, are normative.
The authority, requirement-language, and change-control sections of that document
govern this contract. The registry is the statement authority; inconsistent copies
fail validation. Registry version 1.0.0 is independent of the historical repository
release v1.0.0 and does not change it.

Only this bounded contract is frozen. Detailed layouts, instruction families,
examples, syntax, algorithms, operational contracts, extension profiles, and later
roadmap phases remain architectural and non-normative until their own explicit
specification freeze. Uppercase requirement words outside the declared normative
boundary do not silently promote candidate material into compatibility promises.

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

Compatibility for the core invariant registry follows the explicit versioning and change-control policy in [Core Invariants](CORE-INVARIANTS.md#compatibility-and-change-control). No language, runtime, data-format, or backend compatibility is promised by this freeze.

## Design review rule

When a conflict exists between:

1. scientific meaning;
2. deterministic/reproducible behavior;
3. inspectability;
4. backend convenience;
5. implementation performance;

higher items in that list take precedence unless a future normative specification explicitly defines a different trade-off.

## Frozen cross-cutting invariants

The following controlled statements are normative. Other content in this document
remains architectural or candidate material unless separately frozen. See
[Core Invariants](CORE-INVARIANTS.md) for authority, compatibility, and validation limits.


<!-- BEGIN QSOL CORE INVARIANTS -->

Registry version: 1.0.0

### QM-INV-024: Freeze before implementation

Operational Core, lowering, Vector/Dataflow, extension, and backend implementations MUST follow their applicable frozen specifications. The invariant registry MUST NOT be treated as an instruction set, data schema, grammar, execution engine, or authorization to implement later roadmap phases. Documentation MUST distinguish implemented behavior from design targets.

<!-- END QSOL CORE INVARIANTS -->
