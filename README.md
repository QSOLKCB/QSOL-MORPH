# QSOL-MORPH

**Deterministic code morphing for human–AI research computing.**

QSOL-MORPH is a code translation, optimisation, and execution layer for the emerging QSOL research-language architecture.

Its purpose is simple:

> **QSOL describes intent. QSOL-CORE defines meaning. QSOL-MORPH chooses machinery.**

A QSOL program should describe what a researcher intends to compute without forcing that researcher, or an assisting AI, to manually rewrite the same computation for every processor, accelerator, operating environment, or execution backend.

QSOL-MORPH provides the translation boundary between stable QSOL semantics and changing computational machinery.

---

## Status

**Experimental / pre-alpha.**

QSOL-MORPH is currently an architectural research project.

Interfaces, intermediate representations, backend models, and specifications are expected to evolve substantially during early development.

The project presently defines a direction rather than claiming production readiness.

---

# Why QSOL-MORPH?

Modern research software frequently mixes several different concerns:

* scientific intent;
* numerical algorithms;
* hardware architecture;
* parallelisation;
* memory placement;
* accelerator APIs;
* operating-system behaviour;
* provenance;
* reproducibility;
* build systems;
* foreign-language interfaces.

This creates unnecessary coupling.

A researcher may know exactly what should be computed while still needing to express that calculation separately as:

* Python;
* C;
* Fortran;
* CUDA;
* shell;
* SIMD intrinsics;
* GPU kernels;
* workflow configuration;
* formal verification glue.

The scientific meaning did not change.

Only the machinery changed.

QSOL-MORPH is intended to separate those two layers.

---

# Core Principle

```text
MEANING
    ↓
QSOL Semantic Representation

COMPUTATION
    ↓
QSOL Vector / Dataflow IR

MACHINERY
    ↓
QSOL-MORPH
```

Humans and AI collaborate at the semantic layer.

QSOL-MORPH maps that meaning onto available computational machinery.

---

# Conceptual Architecture

```text
┌─────────────────────────────────────┐
│             QSOL SOURCE             │
│                                     │
│ AIM OBSERVE ASSUME MODEL DERIVE     │
│ RUN TEST PROVE TRACE LOCK           │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│         CANONICAL QSOL IR           │
│                                     │
│ JOB → DECK → CARD → VERB / NOUN     │
│ typed • canonical • hashable        │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│       VECTOR / DATAFLOW IR          │
│                                     │
│ vectors • masks • dependencies      │
│ fusion • pipelines • reductions     │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│            QSOL-MORPH               │
│                                     │
│ lower • map • fuse • vectorise      │
│ specialise • schedule • verify      │
└────┬─────┬─────┬─────┬─────┬───────┘
     │     │     │     │     │
     ▼     ▼     ▼     ▼     ▼
   POSIX   C   LLVM  FORTRAN CUDA
                              │
                         ┌────┴────┐
                         ▼         ▼
                        CPU       GPU
```

Additional backend families may eventually include:

```text
HIP
OpenCL
Vulkan Compute
WebAssembly
native QSOL VM
MIDI 2.0
Lean 4
specialised accelerators
future architectures
```

Backend support does not imply that all targets share identical performance characteristics.

They should, where applicable, share defined QSOL semantics.

---

# Design Influences

QSOL-MORPH deliberately borrows architectural ideas rather than reinventing them.

## Transmeta

Transmeta's Code Morphing approach demonstrated the power of maintaining a stable software-visible execution model while translating operations onto substantially different underlying machinery.

QSOL-MORPH applies a related principle to research software:

```text
stable semantics
       ↓
translation
       ↓
replaceable machinery
```

The target architecture is an implementation detail.

Program meaning is not.

---

## Cray

Cray systems demonstrated the value of treating vector computation as a fundamental architectural operation.

QSOL-MORPH therefore treats:

* vectors;
* reductions;
* masks;
* pipelines;
* chained operations;
* data locality;

as first-class optimisation opportunities rather than merely library conventions.

For example:

```text
DERIVE X = A * B
DERIVE Y = X + C
DERIVE Z = SQRT Y
```

may be represented as:

```text
A ─┐
   MUL ── ADD ── SQRT ── Z
B ─┘      ↑
          C
```

A suitable backend may fuse this pipeline into a single execution kernel without changing its defined result.

---

## RISC

QSOL-MORPH follows a reduced-semantic-complexity philosophy.

Rich research constructs should lower into a deliberately small and regular computational core.

Conceptually:

```text
LOAD
STORE
MOVE

ADD
SUB
MUL
DIV
MOD

AND
OR
XOR
NOT

CMP
JUMP
CALL
RET
```

The final instruction set is not yet frozen.

The design objective is.

> Prefer a small orthogonal core over an expanding collection of special cases.

---

## Bell Labs and Unix

Programs should compose.

QSOL workflows should be capable of representing operations resembling:

```text
LOAD observations
| FILTER temperature > 300 K
| MODEL thermal
| TEST error < 0.01
| TRACE
| SAVE results
```

Unlike traditional untyped text pipelines, QSOL streams may carry structured and typed semantic records.

---

## Apollo Guidance Computer

The Apollo Guidance Computer and DSKY demonstrated the usefulness of compact, memorable operational vocabularies.

QSOL explores a similarly constrained semantic model using concepts such as:

```text
VERB
NOUN
CARD
DECK
JOB
```

A potential canonical operation might resemble:

```text
OBSERVE TEMPERATURE 294.3 K
```

where:

```text
VERB  = OBSERVE
NOUN  = TEMPERATURE
VALUE = 294.3
UNIT  = K
```

---

## Mainframe and Punch-Card Systems

QSOL borrows the conceptual discipline of jobs, decks, and records without reproducing fixed-column programming.

The proposed hierarchy is:

```text
JOB
 └── DECK
      ├── CARD
      ├── CARD
      └── CARD
```

A CARD represents an atomic semantic operation.

A DECK represents an executable semantic workflow.

A JOB coordinates one or more decks.

---

# Example

A future QSOL research deck might resemble:

```text
DECK NBODY-001

AIM SIMULATE NBODY

USE QX-VEC
USE QX-GPU

SET DT 0.001 s
SET STEPS 1_000_000

VECTOR POSITION f64[3, N]
VECTOR VELOCITY f64[3, N]
VECTOR MASS     f64[N]

RUN NBODY ON GPU

TEST CONSERVATION

TRACE EXECUTION
TRACE NUMERICS

SAVE POSITION
LOCK RESULT

END
```

QSOL-MORPH could inspect this program and determine that:

* the primary workload is vectorisable;
* operations are suitable for accelerator execution;
* intermediate arrays can remain device-resident;
* multiple operations can be fused;
* the selected execution environment must be recorded for reproducibility.

---

# CUDA Without the Plumbing

One objective of QSOL-MORPH is to make accelerator access proportional to the scientific complexity of the task rather than the complexity of the accelerator API.

A user may eventually write:

```text
RUN GRAVITY ON CUDA
```

rather than manually implementing ordinary infrastructure such as:

```text
device allocation
host/device copies
launch geometry
kernel boilerplate
synchronisation
cleanup
```

QSOL-MORPH may generate those mechanisms.

The generated implementation should remain inspectable.

For example:

```text
qsol morph gravity.qsl --to=cuda
qsol morph gravity.qsl --show-ir
```

Explicit low-level tuning should remain possible when required.

Example conceptual syntax:

```text
RUN GRAVITY ON CUDA WITH:
    blocks 256
    threads 128
    shared 48 KiB
```

The simple path should remain simple.

The advanced path should remain available.

---

# Abstract Vector Machine

QSOL-MORPH may define a target-independent vector intermediate representation.

Conceptually:

```text
VLOAD A      -> V0
VLOAD B      -> V1
VMUL V0 V1   -> V2
VADD V2 4.0  -> V3
VSTORE V3    -> C
```

These operations do not necessarily correspond directly to physical registers.

They describe computation.

QSOL-MORPH may lower them into:

```text
scalar loops
CPU SIMD
AVX
LLVM vectors
CUDA kernels
GPU warps
accelerator-specific operations
```

without requiring the research source to encode a fixed hardware width.

---

# Kernel Fusion

Consider:

```text
DERIVE X = A * B
DERIVE Y = X + C
DERIVE Z = SQRT Y
```

A naïve implementation may allocate and materialise both `X` and `Y`.

QSOL-MORPH may instead generate an equivalent fused computation:

```text
Z[i] = sqrt(A[i] * B[i] + C[i])
```

Possible advantages include:

* reduced temporary allocation;
* reduced memory traffic;
* improved cache locality;
* reduced GPU global-memory traffic;
* fewer kernel launches.

Optimisation must not silently alter defined semantics.

---

# Determinism

QSOL-MORPH is intended for research computing.

Reproducibility therefore has priority over opaque optimisation.

Execution choices affecting reproducibility should be discoverable.

A trace may eventually contain information resembling:

```text
EXECUTION

backend      CUDA
device       NVIDIA GPU
precision    f64
compiler     QSOL-MORPH x.y.z
kernel_hash  sha256:...
source_hash  sha256:...
seed         18437
```

No significant source of nondeterminism should be silently introduced by a backend.

When deterministic execution cannot be guaranteed, that fact should be explicitly represented.

---

# No Hidden Machinery

QSOL-MORPH should prefer explicit computational effects.

Operations involving significant external effects should be visible at the semantic level.

For example:

```text
FETCH DATASET
SPAWN MODEL
ASK AI
ALLOCATE MATRIX
WRITE RESULT
```

A simple assignment should not unexpectedly:

* access a network;
* launch an AI model;
* create threads;
* perform filesystem mutation;
* allocate enormous storage;
* modify unrelated state.

The source should remain an honest description of the computation.

---

# Semantic Stability

QSOL-MORPH separates stable semantics from evolving implementation strategies.

A QSOL program written against a frozen semantic specification should not require redesign merely because execution hardware changes.

Conceptually:

```text
QSOL DECK
    ↓
QSOL IR
    ↓
QSOL-MORPH
    ├── 2026 CPU
    ├── 2026 GPU
    ├── future accelerator
    └── future architecture
```

The backend may change.

The program's declared meaning should not.

---

# Extension Profiles

The QSOL computational core should remain deliberately small.

Additional capabilities may be introduced through extension profiles.

Possible examples:

```text
QX-VEC      vector operations
QX-MATH     scientific numerics
QX-POSIX    POSIX processes and streams
QX-GPU      accelerator execution
QX-CUDA     CUDA-specific control
QX-AI       model interaction
QX-PROVE    formal verification
QX-MIDI     MIDI 2.0 integration
QX-NET      network capabilities
```

A program may explicitly declare its requirements:

```text
USE QX-VEC
USE QX-MATH
USE QX-GPU

DENY QX-NET
```

This enables execution environments to determine required capabilities before running a deck.

---

# Human–AI Collaboration

QSOL-MORPH is part of a broader experiment in programming-language design for joint human and AI work.

The objective is not merely to make source code easy for an AI to generate.

The objective is for humans and AI to reason about the **same operational semantics**.

This encourages:

* canonical syntax;
* small vocabularies;
* explicit intent;
* deterministic behaviour;
* typed research concepts;
* minimal syntactic ambiguity;
* inspectable compilation;
* reproducible transformations.

An AI should ideally propose semantic operations rather than arbitrary textual mutations.

For example:

```text
ADD CARD AFTER @018:
    SEED RNG 18437
```

or:

```text
FUSE @042 @043
```

The resulting transformation can then be validated against the same semantic model understood by the compiler and human researcher.

---

# Research Semantics

QSOL distinguishes between different kinds of scientific statements.

For example:

```text
OBSERVE
ASSUME
DERIVE
MODEL
TEST
PROVE
```

These concepts are intentionally not interchangeable.

In particular:

```text
OBSERVATION
    ≠
ASSUMPTION
    ≠
SIMULATION
    ≠
DERIVATION
    ≠
VALIDATION
    ≠
PROOF
```

QSOL-MORPH must preserve those distinctions when translating computation.

Optimisation may change machinery.

It must not upgrade epistemic status.

---

# Potential Command-Line Interface

The following interface is illustrative and not yet stable:

```text
qsol morph experiment.qsl
qsol morph experiment.qsl --to=c
qsol morph experiment.qsl --to=llvm
qsol morph experiment.qsl --to=fortran
qsol morph experiment.qsl --to=cuda

qsol morph experiment.qsl --show-ir
qsol morph experiment.qsl --show-vector-ir
qsol morph experiment.qsl --explain

qsol run experiment.qsl
qsol trace experiment.qsl
qsol verify experiment.qsl
```

A possible automatic target:

```text
qsol morph experiment.qsl --to=host
```

may select a suitable backend for the current execution environment while recording the exact choice in the execution trace.

---

# Proposed Invariants

Early architectural invariants may include:

### MORPH-INV-001

**Semantic preservation**

A valid morph transformation MUST preserve all semantics defined as invariant by the source program and active QSOL specification.

### MORPH-INV-002

**Explicit nondeterminism**

A backend MUST NOT silently introduce nondeterministic behaviour where deterministic execution is required.

### MORPH-INV-003

**Inspectable transformation**

Generated intermediate representations and target code SHOULD be inspectable using standard QSOL tooling.

### MORPH-INV-004

**No epistemic promotion**

Translation and optimisation MUST NOT change the epistemic classification of research statements.

### MORPH-INV-005

**Backend independence**

Programs MUST NOT require target-specific constructs unless they explicitly request a target-specific extension.

### MORPH-INV-006

**Traceability**

Material execution decisions SHOULD be recordable in a deterministic execution manifest.

### MORPH-INV-007

**Small core**

Backend-specific functionality MUST NOT expand QSOL-CORE when the behaviour can be represented through an extension profile.

### MORPH-INV-008

**Meaning before machinery**

Hardware optimisation MUST remain subordinate to declared program semantics.

---

# Initial Development Direction

A conservative implementation roadmap may begin with:

## Phase 0: Specification

* define terminology;
* define CARD / DECK / JOB model;
* define initial semantic IR;
* define transformation invariants;
* define determinism requirements;
* define canonical serialisation;
* define test vectors.

## Phase 1: Reference MORPH

Implement a minimal reference transformer capable of:

```text
QSOL IR
    ↓
C
```

C provides a conservative first backend with broad compiler availability and portability.

## Phase 2: Vector IR

Introduce:

* typed vectors;
* masks;
* reductions;
* dependency graphs;
* simple fusion;
* deterministic numerical rules.

## Phase 3: LLVM

Add LLVM lowering while retaining the reference C backend as an independently understandable implementation path.

## Phase 4: GPU

Introduce accelerator lowering.

Initial targets may include:

```text
CUDA
```

followed by additional GPU backends where useful.

## Phase 5: Formalisation

Formalise selected transformation rules and core invariants using Lean 4 or another appropriate proof environment.

---

# Non-Goals

QSOL-MORPH does **not** initially aim to:

* replace every compiler;
* replace CUDA;
* replace LLVM;
* replace Fortran;
* replace POSIX;
* invent a new operating system;
* hide all hardware characteristics;
* guarantee identical floating-point behaviour across fundamentally different machines without an explicit numerical contract;
* optimise arbitrary programs perfectly;
* become a universal programming-language kitchen sink.

QSOL-MORPH should reuse mature machinery whenever mature machinery already solves the lower-level problem well.

The wheel does not require reinvention.

It requires reliable bearings.

---

# Philosophy

QSOL-MORPH follows several guiding principles:

> **Describe meaning once.**

> **Keep the semantic core small.**

> **Make expensive behaviour visible.**

> **Move data as little as possible.**

> **Exploit vectors where vectors exist.**

> **Expose machinery when requested, not by default.**

> **Optimise without changing claims.**

> **Record enough information to reproduce what happened.**

> **Let old source survive new hardware.**

And above all:

> **QSOL describes intent. QSOL-CORE defines meaning. QSOL-MORPH chooses machinery.**

---

# License

Unless otherwise noted, QSOL-MORPH is intended to be released under the **Apache License 2.0**.

See `LICENSE` for the complete license text.

---

# Project

**QSOL-MORPH**

QSOL-IMC Research Architecture

Experimental research software for deterministic, human–AI collaborative scientific computing.
