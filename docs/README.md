# QSOL-MORPH Documentation

This directory contains the architectural documentation for QSOL-MORPH.

The historical documentation foundation remains **non-normative**. PR #2 freezes the [Core Invariants](CORE-INVARIANTS.md) contract and its controlled domain copies. PR #3 adds the bounded [Canonical Data Model](CANONICAL-DATA-MODEL.md). Other schemas, grammar, and operational contracts remain candidates.

## Start here

1. [Specification Status](SPECIFICATION-STATUS.md) and [Core Invariants](CORE-INVARIANTS.md)
2. [Design Principles](DESIGN-PRINCIPLES.md)
3. [Architecture](ARCHITECTURE.md)
4. [Human–AI Language Model](LANGUAGE-MODEL.md)
5. [Canonical Data Model](CANONICAL-DATA-MODEL.md) and [Candidate Semantic IR](SEMANTIC-IR.md)
6. [Semantic-to-QSOL-CORE Lowering](SEMANTIC-TO-CORE-LOWERING.md)

## Execution model

- [Semantic-to-QSOL-CORE Lowering](SEMANTIC-TO-CORE-LOWERING.md)
- [Vector and Dataflow](VECTOR-AND-DATAFLOW.md)
- [Backends and Morphing](BACKENDS-AND-MORPHING.md)
- [Extensions and Capabilities](EXTENSIONS-AND-CAPABILITIES.md)
- [Determinism and Reproducibility](DETERMINISM-AND-REPRODUCIBILITY.md)
- [Failure and Partial Effects](FAILURE-AND-PARTIAL-EFFECTS.md)
- [Trace and Provenance](TRACE-AND-PROVENANCE.md)
- [Serialization](SERIALIZATION.md)
- [Optimization and CI](OPTIMIZATION-AND-CI.md)

## Project planning

- [Roadmap](../ROADMAP.md)
- [Contributing](../CONTRIBUTING.md)
- [AI / Agent Guidance](../AGENTS.md)

## Reading rule

Illustrative syntax is not a frozen grammar.

The following is an architectural example:

```text
OBSERVE TEMPERATURE 294.3 K
RUN MODEL ON GPU
TRACE ALL
LOCK RESULT
```

Examples show intended semantic shape rather than a backwards-compatible language promise. The core-invariant freeze does not freeze these examples or their grammar.

The intended lowering chain is explicit:

```text
Canonical Semantic IR
    ↓
Semantic-to-QSOL-CORE Lowering
    ↓
QSOL-CORE
    ↓
Vector/Dataflow IR
    ↓
MORPH
    ↓
backend
```

No backend owns or invents the meaning of an earlier arrow.

## Core mnemonic

```text
QSOL describes intent.
QSOL-CORE defines meaning.
QSOL-MORPH chooses machinery.
```

