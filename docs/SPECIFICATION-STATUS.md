# Specification Status

QSOL-MORPH is currently **pre-alpha and specification-first**.

This document defines the boundary between the frozen core invariants and the remaining architectural material.

## Current status

PR #1 is the immutable v1.0.0 documentation foundation. PR #2 introduces the first
bounded normative [Core Invariants](CORE-INVARIANTS.md) contract, machine-readable
registry, documentation-agreement validator, tests, and CI. PR #3 introduces the
bounded [Canonical Data Model 1.0.0](CANONICAL-DATA-MODEL.md), closed schema, reference
validator, and fixtures. PR #4 introduces [Canonical Serialization 1.0.0](CANONICAL-SERIALIZATION.md), canonical JSON/JSONL/XML encoders and strict readers, content fingerprints, and round-trip fixtures. The bounded [Execution Trace Foundation](EXECUTION-TRACE-FOUNDATION.md) adds a closed candidate trace schema and a source-bound synthetic receipt consistency validator. No compiler, runtime, human-source parser, production execution-trace validator, or backend exists yet; the full PR #5 execution gate remains incomplete.

## Normative boundary

The statements in `spec/core-invariants.json`, rendered in the controlled blocks of
[Core Invariants](CORE-INVARIANTS.md) and registered domain documents, are normative.
The authority, requirement-language, and change-control sections of that document
govern this contract. The registry is the statement authority; inconsistent copies
fail validation. Registry version 1.0.0 is independent of the historical repository
release v1.0.0 and does not change it.

The canonical model document and `spec/canonical-model.schema.json` additionally
freeze only the logical structures and validation rules explicitly listed there.
Schema validation alone is insufficient: owner resolution, scoped composition,
bindings, and sequencing require the reference validator. Data-model acceptance is
not executable or transport conformance. The model version is independent of the
core invariant registry and historical release version.

The canonical serialization document and `spec/serialization-profile.json` freeze
only the versioned transport encodings, exact round-trip relation, and content
fingerprint explicitly defined there. Transport identity is not executable semantic
equivalence, a grant of authority, or evidence of a research claim.

The trace foundation explicitly separates structural candidate coverage from its
implemented synthetic consistency checks and deferred operational conformance.
Its schema does not freeze the candidate execution semantics, and a passing receipt
is not proof of execution, authorization, or a research claim.

Outside these three bounded contracts, detailed layouts, instruction families,
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

Compatibility for the core invariant registry follows the explicit versioning and change-control policy in [Core Invariants](CORE-INVARIANTS.md#compatibility-and-change-control). Canonical-model compatibility follows [its explicit version/migration boundary](CANONICAL-DATA-MODEL.md#authority-and-deliberately-bounded-scope). Transport compatibility follows [Canonical Serialization](CANONICAL-SERIALIZATION.md). No human-language, runtime, or backend compatibility is promised by these freezes.

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
