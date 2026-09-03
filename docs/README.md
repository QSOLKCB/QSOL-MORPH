# QSOL-MORPH Documentation

This directory contains the architectural documentation for QSOL-MORPH.

The documentation-foundation phase is intentionally **non-normative**. PR #2 is reserved for freezing the first core invariants.

## Start here

1. [Specification Status](SPECIFICATION-STATUS.md)
2. [Design Principles](DESIGN-PRINCIPLES.md)
3. [Architecture](ARCHITECTURE.md)
4. [Human–AI Language Model](LANGUAGE-MODEL.md)
5. [Candidate Semantic IR](SEMANTIC-IR.md)

## Execution model

- [Vector and Dataflow](VECTOR-AND-DATAFLOW.md)
- [Backends and Morphing](BACKENDS-AND-MORPHING.md)
- [Extensions and Capabilities](EXTENSIONS-AND-CAPABILITIES.md)
- [Determinism and Reproducibility](DETERMINISM-AND-REPRODUCIBILITY.md)
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

Until the normative invariant/specification phase is merged, examples show intended semantic shape rather than a backwards-compatible language promise.

## Core mnemonic

```text
QSOL describes intent.
QSOL-CORE defines meaning.
QSOL-MORPH chooses machinery.
```
