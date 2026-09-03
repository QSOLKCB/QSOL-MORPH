# QSOL-MORPH

**Deterministic code morphing for human–AI research computing.**

QSOL-MORPH is the proposed translation, optimization, and execution layer for the QSOL research-language architecture.

> **QSOL describes intent. QSOL-CORE defines meaning. QSOL-MORPH chooses machinery.**

The project aims to let humans and AI reason about one stable semantic program while allowing the implementation beneath it to change across CPUs, GPUs, compiler backends, operating environments, and future accelerators.

## Status

**Experimental / pre-alpha.**

The project is currently specification-first and documentation-first. The language grammar, Semantic IR, QSOL-CORE instruction set, extension profiles, and backend contracts remain provisional until frozen by later normative work.

PR #1 establishes the architectural foundation. PR #2 is reserved for locking in the first core invariants before executable implementation begins.

## Why QSOL-MORPH?

Research code often mixes scientific intent with machinery-specific plumbing:

- numerical algorithms;
- accelerator APIs;
- memory placement;
- process and filesystem behavior;
- build systems;
- provenance;
- reproducibility;
- formal verification glue;
- AI/tool orchestration.

The scientific meaning may stay the same while the machinery changes completely.

QSOL-MORPH separates those layers.

## Architecture

```text
┌──────────────────────────────────────────┐
│ QSOL SOURCE / HUMAN-AI SEMANTIC LAYER   │
│ intent • epistemic class • units        │
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ CANONICAL SEMANTIC MODEL                 │
│ JOB → DECK → CARD → VERB / NOUN         │
│ effects • capabilities • contracts       │
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ QSOL-CORE                                │
│ small orthogonal semantic machine        │
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ VECTOR / DATAFLOW IR                     │
│ vectors • masks • dependencies • fusion │
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ QSOL-MORPH                               │
│ map • specialize • fuse • schedule      │
│ validate legality • emit trace           │
└──────────┬──────────┬──────────┬─────────┘
           │          │          │
           ▼          ▼          ▼
           C        LLVM      FORTRAN      ...
                                   │
                                   ▼
                             CPU / GPU / VM
```

POSIX is intentionally **not** modeled as a mutually exclusive compiler backend. POSIX process, stream, filesystem, environment, and signal behavior belongs in the composable `QX-POSIX` execution profile, which may be used by generated C, LLVM, Fortran, or other targets when explicitly enabled and authorized.

## Semantic model

The proposed structural hierarchy is:

```text
JOB
 └── DECK
      └── CARD
           ├── VERB
           ├── NOUN
           ├── OPERANDS
           ├── TYPE / UNIT
           ├── SEMANTIC CLASS
           ├── EFFECTS
           ├── CAPABILITIES
           ├── NUMERIC / REPRODUCIBILITY CONTRACTS
           └── DEPENDENCIES
```

A CARD is the smallest independently addressable semantic statement.

Illustrative examples:

```text
OBSERVE TEMPERATURE 294.3 K
ASSUME VACUUM TRUE
DERIVE ENERGY = MASS * C * C
TEST ENERGY
TRACE RESULT
LOCK RESULT
```

Illustrative syntax is **not yet a frozen grammar**.

## Human–AI shared semantics

QSOL uses recognizable semantic anchors rather than punctuation-heavy syntax where practical.

Candidate research verbs include:

```text
AIM
OBSERVE
ASSUME
MODEL
DERIVE
RUN
TEST
PROVE
TRACE
LOCK
```

The goal is for the same source to carry useful operational meaning for a researcher, an AI agent, a compiler, and later formal tooling.

Epistemic distinctions are intentional:

```text
OBSERVATION
    !=
ASSUMPTION
    !=
SIMULATION
    !=
DERIVATION
    !=
VALIDATION
    !=
PROOF
```

Optimization must not silently promote one class into another.

## QSOL-CORE direction

QSOL-CORE is intended to remain deliberately small.

Candidate instruction families include:

```text
DATA       LOAD STORE MOVE
ARITH      ADD SUB MUL DIV MOD
LOGIC      AND OR XOR NOT
COMPARE    EQ NE LT LE GT GE
CONTROL    JUMP BRANCH CALL RET STOP
EFFECT     explicit stateful/external operations
```

The final instruction set will be determined by the frozen specification, not by this README.

## Vector and dataflow model

Vectors are semantic data, not promises about physical register width.

For example:

```text
DERIVE X = A * B
DERIVE Y = X + C
DERIVE Z = SQRT Y
```

may lower into a dependency graph that a legal backend can fuse into an equivalent target implementation.

QSOL-MORPH may later map the same vector/dataflow semantics onto:

- scalar loops;
- CPU SIMD;
- AVX-family instructions;
- LLVM vectors;
- CUDA threads/warps;
- other accelerators.

Source code should not need to encode one machine's physical vector width unless it explicitly opts into a target-specific extension.

## Determinism and numeric contracts

Result determinism and randomness are separate facets.

Conceptually:

```text
RESULT DETERMINISM
    STRICT
    NUMERIC
    DECLARED-NONDETERMINISTIC

RANDOMNESS
    NONE
    SEEDED
    EXTERNAL-ENTROPY
    DECLARED-NONDETERMINISTIC
```

`SEEDED` does not replace a result-determinism contract.

A `NUMERIC` result contract must bind the numeric rules that define legal variation. A seeded run must record enough information to reproduce its stream, including RNG algorithm, version, seed, stream identity, and parallel partitioning where applicable.

Traces must distinguish requested from effective determinism whenever an explicitly authorized downgrade occurs.

## Failure semantics

Failure is observable behavior and therefore part of the language architecture.

The candidate default is fail-stop:

```text
SUCCESS(value?)
FAILURE(record)
```

An unhandled failure stops the DECK. Pure failures commit no semantic state. Effects already observable before a later failure are not retroactively erased.

Effectful failure must distinguish states such as:

```text
NOT_STARTED
COMPLETED
PARTIAL
UNKNOWN
```

This prevents C, LLVM, CUDA, POSIX adapters, or future backends from inventing mutually incompatible error behavior.

See [Failure and Partial-Effect Semantics](docs/FAILURE-AND-PARTIAL-EFFECTS.md).

## Capabilities and extensions

Extension availability and runtime permission are separate concerns.

For example:

```text
USE QX-NET
DENY NETWORK
```

may mean that the language/profile is understood while runtime network access is forbidden.

Candidate profiles include:

```text
QX-VEC
QX-MATH
QX-POSIX
QX-GPU
QX-CUDA
QX-AI
QX-PROVE
QX-MIDI
QX-NET
```

Optional machinery should not silently expand or redefine QSOL-CORE.

## CUDA without ordinary plumbing

A long-term target experience is:

```text
RUN GRAVITY ON CUDA
```

while QSOL-MORPH handles ordinary target mechanics such as allocation, transfer, launch geometry, synchronization, and generated-kernel structure.

Material choices remain inspectable and provenance-bound.

Expert target-specific controls may exist behind explicit profiles such as `QX-CUDA`.

## Trace and provenance

Executable research results should be bound to enough context to explain and reproduce the run.

Potential trace material includes:

```text
source hash
semantic IR hash
specification version
MORPH/compiler identity
backend / target identity
requested and effective result determinism
numeric contract
RNG algorithm + version + seed + stream + partitioning
capabilities
extensions
inputs / output hashes
optimization decisions
failure / partial-effect state
```

A cached result is not evidence that a cold reconstruction still works. A benchmark from one machine is not automatically a target claim for another machine.

## Optimization rule

> **A faster semantics-breaking change is not an optimization.**

QSOL-MORPH optimization is subordinate to:

- semantic preservation;
- determinism and numeric contracts;
- effect/failure ordering;
- provenance;
- epistemic boundaries;
- declared resource constraints.

## Documentation

Start with [docs/README.md](docs/README.md).

Key documents:

- [Specification Status](docs/SPECIFICATION-STATUS.md)
- [Design Principles](docs/DESIGN-PRINCIPLES.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Human–AI Language Model](docs/LANGUAGE-MODEL.md)
- [Candidate Semantic IR](docs/SEMANTIC-IR.md)
- [Vector and Dataflow](docs/VECTOR-AND-DATAFLOW.md)
- [Backends and Morphing](docs/BACKENDS-AND-MORPHING.md)
- [Extensions and Capabilities](docs/EXTENSIONS-AND-CAPABILITIES.md)
- [Determinism and Reproducibility](docs/DETERMINISM-AND-REPRODUCIBILITY.md)
- [Failure and Partial Effects](docs/FAILURE-AND-PARTIAL-EFFECTS.md)
- [Trace and Provenance](docs/TRACE-AND-PROVENANCE.md)
- [Optimization and CI](docs/OPTIMIZATION-AND-CI.md)
- [Roadmap](ROADMAP.md)
- [AI / Agent Guidance](AGENTS.md)

## Development sequence

The project is deliberately staged:

```text
PR #1  Documentation Foundation
PR #2  Lock in Core Invariants
PR #3  Canonical Data Model
PR #4  Canonical Serialization
PR #5  Execution Contract, Trace, Failure, and Provenance Foundation
PR #6  Normative QSOL-CORE Operational Specification
PR #7  QSOL-CORE Reference Machine
PR #8  Vector/Dataflow IR
PR #9  Reference MORPH to C
...    optimization, POSIX profile, LLVM, GPU, CUDA
```

The roadmap is intentionally designed so executable research code does not precede the contracts needed to interpret and audit its behavior, and QSOL-CORE implementation does not precede its normative operational specification.

## Design influences

QSOL-MORPH borrows architectural lessons rather than reproducing historical systems:

- **Transmeta:** stable semantics above replaceable machinery;
- **Cray:** vector-first data movement and chaining;
- **RISC:** small orthogonal cores;
- **Bell Labs / Unix:** composition and explicit streams;
- **Apollo:** compact memorable operational vocabulary;
- **mainframe record systems:** JOB / DECK / CARD discipline.

## Non-goals

QSOL-MORPH does not initially aim to:

- replace every compiler;
- replace CUDA, LLVM, Fortran, or POSIX;
- hide all machine characteristics;
- guarantee identical floating-point behavior across every target without an explicit contract;
- become a universal kitchen-sink language.

The project should reuse mature machinery whenever that machinery already solves the lower-level problem well.

## License

QSOL-MORPH is released under the **Apache License 2.0** unless otherwise noted. See [LICENSE](LICENSE).

---

**QSOL-IMC Research Architecture**
