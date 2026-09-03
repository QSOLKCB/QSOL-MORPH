# QSOL-MORPH

**Deterministic code morphing for human–AI research computing.**

QSOL-MORPH is the proposed translation, optimization, and execution layer for the QSOL research-language architecture.

> **QSOL describes intent. QSOL-CORE defines meaning. QSOL-MORPH chooses machinery.**

The project aims to let humans and AI reason about one stable semantic program while allowing the implementation beneath it to change across CPUs, GPUs, compiler backends, operating environments, and future accelerators.

## Status

**Experimental / pre-alpha.**

The project is currently specification-first and documentation-first. The language grammar, Semantic IR, QSOL-CORE instruction set, lowering contracts, extension profiles, and backend contracts remain provisional until frozen by later normative work.

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
│ qualifiers • effects • contracts        │
└────────────────────┬─────────────────────┘
                     │ semantic-to-core lowering
                     ▼
┌──────────────────────────────────────────┐
│ QSOL-CORE                                │
│ small orthogonal semantic machine        │
└────────────────────┬─────────────────────┘
                     │ core-to-vector/dataflow lowering
                     ▼
┌──────────────────────────────────────────┐
│ FULL VECTOR / DATAFLOW IR                │
│ scalar + vector + control + effects      │
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

Both lowering arrows are explicit contracts and independently provenance-bearing transformations. Backends consume the established lower pipeline rather than inventing private source semantics.

POSIX is intentionally **not** modeled as a mutually exclusive compiler backend. POSIX process, stream, filesystem, environment, and signal behavior belongs in the composable `QX-POSIX` execution profile, whose normative contract is frozen before its reference implementation.

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
           ├── QUALIFIERS
           ├── SEMANTIC CLASS
           ├── EFFECT REQUIREMENTS[]
           │    ├── EFFECT ID / KIND
           │    └── REQUIRED CAPABILITIES[]
           ├── FAILURE BEHAVIOR
           ├── NUMERIC / REPRODUCIBILITY CONTRACTS
           └── DEPENDENCIES / ORDERING
```

A CARD is the smallest independently addressable semantic statement.

Each protected effect binds its own complete capability set. A CARD-level capability union may be useful for static preflight, but it cannot replace the effect-to-capability association used for authorization and provenance.

Illustrative examples:

```text
OBSERVE TEMPERATURE 294.3 K
ASSUME VACUUM TRUE
DERIVE ENERGY = MASS * C * C
TEST ENERGY
TRACE RESULT
LOCK RESULT
```

Illustrative syntax is **not yet a frozen grammar**. Human `.qsl` parsing and lossless text serialization are deferred until a normative QSOL text profile freezes grammar and source-to-Semantic-IR mapping.

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

## Semantic-to-core lowering

Canonical Semantic IR carries richer research semantics than QSOL-CORE. The first lowering stage therefore has its own normative specification, reference implementation, conformance fixtures, and provenance identity.

Conceptually:

```text
Canonical Semantic IR
    ↓
Semantic-to-QSOL-CORE Lowering
    ↓
QSOL-CORE + preserved metadata/provenance
```

The lowering must preserve or explicitly validate before erasure:

- epistemic class and evidence boundaries;
- types and units;
- execution-relevant qualifiers;
- effect requirements and complete per-effect capability sets;
- explicit failure behavior;
- determinism, numeric, and randomness contracts;
- extension identities;
- source/effect/failure ordering;
- CARD / DECK / JOB provenance.

Unsupported semantic constructs or qualifiers fail explicitly instead of being dropped or delegated to a backend to reinterpret.

See [Semantic-to-QSOL-CORE Lowering](docs/SEMANTIC-TO-CORE-LOWERING.md).

## Full Vector/Dataflow IR

The mandatory Vector/Dataflow IR is not merely a vector optimizer input. It preserves the complete supported QSOL-CORE surface while exposing dataflow and vectorization opportunities.

It therefore carries or represents:

- scalar and vector operations;
- control flow and calls;
- explicit effects and complete capability sets;
- qualifiers and failure behavior where still material;
- dependency/effect/failure ordering;
- determinism, numeric, randomness, and extension contracts;
- provenance links to QSOL-CORE and originating semantic CARDs.

The QSOL-CORE → Vector/Dataflow transformation has its own normative specification and reference lowering before the first MORPH code-generation backend.

For vectorizable work:

```text
DERIVE X = A * B
DERIVE Y = X + C
DERIVE Z = SQRT Y
```

may become a dependency graph that a legal backend can fuse into an equivalent target implementation.

QSOL-MORPH may later map the same semantics onto scalar loops, CPU SIMD, AVX-family instructions, LLVM vectors, CUDA threads/warps, or other accelerators.

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

A `NUMERIC` result contract must bind the numeric rules that define legal variation. The trace also binds the material numeric mode actually used when permitted choices such as FMA, denormal handling, precision, or math-library mode can affect legal bytes.

A seeded run must record enough information to reproduce its stream, including RNG algorithm, version, seed, stream identity, and parallel partitioning where applicable.

Traces must distinguish requested from effective determinism and randomness whenever an explicitly authorized transition occurs.

## Failure and effect-attempt semantics

Failure is observable behavior and therefore part of the language architecture.

The candidate default is fail-stop:

```text
SUCCESS(value?)
FAILURE(record)
```

An unhandled failure stops the DECK and propagates to the JOB by default. Pure failures commit no semantic state. Effects already observable before a later failure are not retroactively erased.

Each protected external effect attempt receives its own completion state:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

where `ABORTED_CLEAN` means the effect began, did not complete, and is proven to have produced no externally observable change.

Completion belongs to the effect attempt, not the CARD outcome. A process may be `COMPLETED` yet cause its CARD to report `PROCESS_FAILED` because the completed process returned a non-success status.

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

An extension may define optional syntax, adapters, effects, or capability **requirements**. Activating an extension never grants a runtime capability by itself.

## CUDA without ordinary plumbing

A long-term target experience is:

```text
RUN GRAVITY ON CUDA
```

while QSOL-MORPH handles ordinary target mechanics such as allocation, transfer, launch geometry, synchronization, and generated-kernel structure.

The roadmap freezes a generic GPU execution contract before the CUDA backend. CUDA machinery and QX-CUDA controls remain separate: the CUDA backend implements generic accelerator semantics, while optional launch/memory/tuning controls require a separately frozen, versioned QX-CUDA contract before implementation.

## Trace and provenance

Executable research results should be bound to enough context to explain and reproduce the run.

Potential trace material includes:

```text
source hash
semantic IR hash
semantic-to-core spec + implementation identity
QSOL-CORE IR hash
core-to-vector/dataflow spec + implementation identity
Vector/Dataflow IR hash
MORPH/compiler identity
backend / target identity
backend-selection policy + tuning identity when automatic
requested and effective result determinism
numeric contract + material numeric mode
requested/effective randomness + RNG identity
capability requirements + authorization policy
resolved extension identities
identified effect attempts + complete capability sets + completion states
inputs / output hashes
optimization decisions
failure records
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

Dead-result elimination may remove an operation solely because its result is unused only when the operation is proven pure and total, unless its original failure is explicitly preserved at the same observable point.

## Documentation

Start with [docs/README.md](docs/README.md).

Key documents:

- [Specification Status](docs/SPECIFICATION-STATUS.md)
- [Design Principles](docs/DESIGN-PRINCIPLES.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Human–AI Language Model](docs/LANGUAGE-MODEL.md)
- [Candidate Semantic IR](docs/SEMANTIC-IR.md)
- [Semantic-to-QSOL-CORE Lowering](docs/SEMANTIC-TO-CORE-LOWERING.md)
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

The project is deliberately staged. The authoritative details are in `ROADMAP.md`; the key sequence is:

```text
PR #1   Documentation Foundation
PR #2   Lock in Core Invariants
PR #3   Canonical Data Model
PR #4   Canonical Machine-Readable Serialization
PR #5   Execution Contract, Trace, Failure, and Provenance Foundation
PR #6   Normative QSOL-CORE Operational Specification
PR #7   QSOL-CORE Reference Machine
PR #8   Normative Semantic-to-QSOL-CORE Lowering Specification
PR #9   Reference Semantic-to-QSOL-CORE Lowering
PR #10  Normative Full Vector/Dataflow IR Specification
PR #11  Reference QSOL-CORE-to-Vector/Dataflow Lowering
PR #12  Reference MORPH to C
PR #13  Morph Optimization Passes
PR #14  Normative QX-POSIX Contract
PR #15  QX-POSIX Reference Implementation
PR #16  LLVM Backend
PR #17  Normative Generic GPU Execution Contract
PR #18  CUDA Backend
PR #19  Normative QX-CUDA Control Contract
PR #20  QX-CUDA Reference Control Implementation
PR #21  Additional Backends
PR #22  Formalization
```

The human `.qsl` text profile remains a deferred normative workstream until its grammar and source mapping are frozen.

The roadmap deliberately repeats one rule across the architecture: **specify meaning before implementing machinery.**

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
