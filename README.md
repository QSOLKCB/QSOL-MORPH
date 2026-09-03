# QSOL-MORPH

**Deterministic code morphing for human–AI research computing.**

QSOL-MORPH is the proposed translation, optimization, and execution layer for the QSOL research-language architecture.

> **QSOL describes intent. QSOL-CORE defines meaning. QSOL-MORPH chooses machinery.**

The project aims to let humans and AI reason about one stable semantic program while allowing the implementation beneath it to change across CPUs, GPUs, compiler backends, operating environments, and future accelerators.

## Status

**Experimental / pre-alpha.**

The repository is specification-first and documentation-first. The language grammar, Semantic IR, QSOL-CORE instruction set, lowering contracts, extension profiles, and backend contracts remain provisional until later normative phases freeze them.

PR #1 establishes the architectural foundation. PR #2 is reserved for locking the first core invariants before executable implementation begins.

## Core architecture

```text
QSOL source / human-AI semantic layer
        ↓
Canonical Semantic IR
        ↓  Semantic-to-Core lowering
QSOL-CORE
        ↓  Core-to-Vector/Dataflow lowering
Full Vector/Dataflow IR
        ↓
QSOL-MORPH
        ↓
C / LLVM / Fortran / CUDA / HIP / VM / ...
```

Both lowering arrows are explicit contracts and independently provenance-bearing transformations. Backends consume the established lower pipeline rather than inventing private source semantics.

POSIX is intentionally **not** a mutually exclusive compiler backend. Process, stream, filesystem, environment, and signal behavior belongs in the composable `QX-POSIX` execution profile.

MIDI 2.0 and formal-tool mappings are also extension/adapter concerns, not machinery backends. They belong behind versioned contracts such as `QX-MIDI` and `QX-PROVE`.

## Canonical semantic model

The proposed structural hierarchy is:

```text
JOB [JOB ID]
 └── DECK [DECK ID]
      └── CARD [CARD ID]
           ├── VERB
           ├── NOUN
           ├── OPERANDS
           ├── VALUE
           ├── RESULT BINDING
           ├── TYPE / UNIT
           ├── QUALIFIERS
           ├── SEMANTIC CLASS
           ├── EFFECT REQUIREMENTS[]
           │    ├── DECLARED EFFECT ID
           │    ├── EFFECT KIND
           │    └── REQUIRED CAPABILITIES[]
           ├── RESULT-DETERMINISM CONTRACT
           ├── RANDOMNESS CONTRACT
           ├── NUMERIC CONTRACT
           ├── EXTENSION REQUIREMENTS[]
           ├── FAILURE BEHAVIOR
           └── DEPENDENCY / EFFECT / FAILURE ORDER
```

Stable JOB/DECK/CARD IDs are canonical semantic identities. They survive lossless serialization, both lowering stages, and trace production without renumbering.

`VALUE` carries an immediate or literal value when present. `RESULT BINDING` separately names a value produced for dependent CARDs.

Each protected effect owns its stable declared effect ID, effect kind, and **complete capability set**. A derived CARD-wide capability union may help preflight, but it does not replace the per-effect association.

## Human–AI semantic anchors

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

Optimization and lowering must not silently promote one class into another.

Illustrative source examples are architectural sketches only. Human `.qsl` parsing and canonical text serialization remain deferred until a normative text profile freezes grammar and source-to-Semantic-IR mapping.

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

The final instruction inventory and operational meaning will be defined by the normative QSOL-CORE specification, not by this README.

## Semantic-to-Core lowering

Canonical Semantic IR carries richer research semantics than QSOL-CORE. The first lowering stage therefore has its own normative specification, reference implementation, conformance fixtures, and provenance identity.

The lowering must preserve or explicitly validate before erasure:

- stable JOB/DECK/CARD identity;
- literal values and result bindings;
- epistemic classes and evidence boundaries;
- types and units;
- execution-relevant qualifiers;
- declared effect IDs and complete per-effect capability sets;
- explicit `failure_behavior`;
- result-determinism, numeric, and randomness contracts;
- extension requirements;
- dependency/effect/failure ordering.

Its provenance records lowering-spec and implementation identities plus qualifier, result-determinism, numeric, randomness, and result-binding decisions.

### Result-binding maps

Both mandatory lowering boundaries record `result_binding_map[]` whenever result identities are **preserved or transformed**.

Omission is allowed only when a frozen rule permits deterministic reconstruction of the identity mapping.

That means an unchanged binding does not automatically excuse the map. IR hashes alone do not establish which lower name corresponds to which source result.

## Full Vector/Dataflow IR

The mandatory Vector/Dataflow IR is not merely a vector optimizer input. It preserves the complete supported QSOL-CORE surface while exposing dataflow and vectorization opportunities.

It carries or represents:

- scalar and vector operations;
- result/data identities and dependencies;
- control flow and calls;
- explicit effects with declared effect IDs and complete capability sets;
- qualifiers and failure behavior where still material;
- dependency/effect/failure ordering;
- result-determinism, numeric, randomness, and extension contracts;
- provenance links back to QSOL-CORE and originating semantic CARDs.

A non-vectorizable operation is not permission to bypass this IR.

## Determinism, numerics, and randomness

Result determinism and randomness are separate facets.

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

A `NUMERIC` result contract is incomplete without the numeric contract defining legal variation.

Provenance is scoped because different CARDs, regions, kernels, or generated units may use different legal contracts or machinery:

```text
backend_selection_scopes[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
```

A single execution-wide scope is valid only when a frozen rule proves one entry genuinely governs every relevant source computation.

Seeded replay records RNG algorithm, version, seed, stream identity, and parallel partitioning/stream mapping where applicable.

## Failure and effect attempts

Failure is observable behavior.

The candidate default is fail-stop:

```text
SUCCESS(value?)
FAILURE(record)
```

An unhandled CARD failure stops its DECK. An unhandled DECK failure fails its JOB and prevents later DECKs from starting. Pure failure commits no semantic state.

Every protected external effect attempt is individually identified and records:

```text
effect_attempt_id
declared_effect_id
card_id
effect_kind
required_capabilities[]
completion_state
```

Completion state is one of:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

Known completion takes precedence over uncertainty about broader consequences. Completion belongs to the effect attempt, not the enclosing CARD outcome.

Enclosing failure records use canonical `failure_card_id` for the CARD whose unhandled failure produced the failure record.

## Extensions and capabilities

Extension availability and runtime authorization are independent.

```text
USE QX-NET
DENY NETWORK
```

may mean that the profile is understood while runtime network access is forbidden.

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

Activating an extension never grants runtime permission by itself.

## CUDA without ordinary plumbing

A long-term target experience is:

```text
RUN GRAVITY ON CUDA
```

while QSOL-MORPH handles ordinary target mechanics.

The roadmap freezes a generic GPU execution contract before the CUDA backend. CUDA machinery and QX-CUDA controls remain separate: optional launch/memory/tuning controls require a separately frozen, versioned QX-CUDA contract.

## Trace and provenance

Executable research results should be bound to enough context to explain and reproduce the run.

Core trace material includes:

```text
source identity/hash
canonical Semantic-IR identity/hash
stable JOB/DECK/CARD IDs
semantic effect_requirements[]
semantic-to-core spec + implementation identity
semantic-to-core result_binding_map[]
QSOL-CORE IR hash
core-to-vector/dataflow spec + implementation identity
core-to-vector result_binding_map[]
Vector/Dataflow IR hash
MORPH/compiler identity
backend_selection_scopes[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
identified inputs[]
identified outputs[]
resolved extension identities
capability authorization policy
declared effect IDs + runtime effect attempts
cache_reuse_records[]
optimization decisions
failure records
```

### Identified inputs

Material inputs bind stable `input_id` values to the exact canonical value, content hash, or immutable artifact/version identity actually consumed.

A mutable path, URL, dataset name, or model name is retrieval context, not content identity.

### Identified outputs

Outputs are **not** bare hashes.

Each `outputs[]` entry binds:

```text
output_id
result_binding?
artifact_hash
artifact_location?
semantic_class
status
producer_card_ids[]
backend_selection_scope_ids[]
result_determinism_scope_ids[]
numeric_scope_ids[]
randomness_scope_ids[]
cache_reuse_record_ids[]?
```

A simulation artifact and a separately validated artifact therefore cannot accidentally share one evidence status or machinery/RNG provenance record.

### Cache reuse

Legal cache reuse is provenance-bearing.

`cache_reuse_records[]` distinguishes cold execution from verified reuse or an unverified hit and binds the material cache identity, reused computation/artifact identity, and any legality/verification evidence.

A verified cache reuse does **not** prove that a cold reconstruction still succeeds.

Ordinary cached result substitution is conservative and effect-free by default. Effectful reuse requires an explicit frozen replay/cache semantic preserving the declared effect, authorization, ordering, failure, and per-attempt provenance boundaries.

## Optimization rule

> **A faster semantics-breaking change is not an optimization.**

Optimization is subordinate to:

- semantic preservation;
- epistemic boundaries;
- result-determinism and numeric contracts;
- randomness/replay requirements;
- effect/failure ordering;
- capability authorization;
- provenance.

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

The authoritative details are in `ROADMAP.md`.

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

The repeated architectural rule is simple: **specify meaning before implementing machinery.**

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
