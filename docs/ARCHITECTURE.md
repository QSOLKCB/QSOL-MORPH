# Architecture

QSOL-MORPH separates **meaning**, **computation**, and **machinery**.

The project exists to let a researcher and an AI reason about one stable semantic program while allowing implementation strategies to change underneath it.

## Layer model

```text
┌──────────────────────────────────────────┐
│ QSOL SOURCE / HUMAN-AI SEMANTIC LAYER   │
│ intent, epistemic class, units, effects │
└────────────────────┬─────────────────────┘
                     │ parse / validate
                     ▼
┌──────────────────────────────────────────┐
│ CANONICAL SEMANTIC MODEL                 │
│ JOB → DECK → CARD → VERB / NOUN         │
│ typed • canonical • hashable            │
└────────────────────┬─────────────────────┘
                     │ lower
                     ▼
┌──────────────────────────────────────────┐
│ QSOL-CORE / REDUCED SEMANTIC MACHINE    │
│ small orthogonal instruction families   │
└────────────────────┬─────────────────────┘
                     │ analyze
                     ▼
┌──────────────────────────────────────────┐
│ VECTOR / DATAFLOW IR                     │
│ vectors • masks • dependency graph      │
│ reductions • fusion opportunities       │
└────────────────────┬─────────────────────┘
                     │ morph
                     ▼
┌──────────────────────────────────────────┐
│ QSOL-MORPH                               │
│ map • specialize • fuse • schedule      │
│ prove/check legality • emit trace       │
└─────────┬────────┬────────┬──────────────┘
          │        │        │
          ▼        ▼        ▼
          C       LLVM    Fortran      ...
          │        │        │
          └────────┴────────┴── may compose with QX-POSIX
                            │
                    ┌───────┴────────┐
                    ▼                ▼
                   CPU              GPU
                                      │
                                   CUDA etc.
```

## 1. Semantic source layer

The source language should optimize semantic bandwidth rather than punctuation density.

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

These terms are intended to carry recognizable meaning for both humans and language models. Their purpose is not decoration: the language should preserve meaningful distinctions such as observation versus assumption and validation versus proof.

## 2. Canonical semantic model

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
           ├── EFFECTS
           ├── CAPABILITIES
           ├── DETERMINISM / RANDOMNESS CONTRACT
           └── DEPENDENCIES / EFFECT ORDER
```

A `CARD` is intended to be the smallest independently addressable semantic statement.

A `DECK` is a source-ordered collection of cards with explicit/derived dependency constraints representing one executable research workflow.

Only CARDs proven **pure and total** under the active contract may be freely scheduled from dependency edges. A pure CARD that may fail is still ordering-relevant under fail-stop semantics, because moving it across an observable effect can change which effects commit before failure. Effectful CARDs are source-ordered by default: the canonical model should derive sequencing constraints between observable effects so that two writes, external calls, process launches, or similar effects cannot be reordered merely because they lack a data dependency.

A future explicit construct may permit parallel or commutative effects, but only under frozen rules that define when the relaxation is semantically legal and what ordering remains observable.

A `JOB` coordinates one or more decks and their execution relationships.

The model is inspired by record-oriented computing, but QSOL is not intended to reproduce historical fixed-column limitations.

## 3. QSOL-CORE

QSOL-CORE is the candidate reduced semantic machine beneath the research-facing language.

Its purpose is to give QSOL-MORPH a small, stable object to analyze, transform, test, and eventually formalize.

The core should avoid backend-specific operations when a generic semantic operation is sufficient.

Candidate families include:

```text
DATA       load, store, move
ARITH      add, subtract, multiply, divide, modulo
LOGIC      and, or, xor, not
COMPARE    equality and ordering
CONTROL    branch, jump, call, return, stop
EFFECT     explicit external/stateful operations
```

The exact instruction set is not frozen in the documentation phase.

## 4. Vector and dataflow layer

Scientific computation often contains bulk operations whose natural representation is not scalar source-code iteration.

QSOL-MORPH therefore treats vectors, masks, reductions, and dependency graphs as first-class IR concepts.

A sequence such as:

```text
DERIVE X = A * B
DERIVE Y = X + C
DERIVE Z = SQRT Y
```

may become a dependency graph that permits a backend to fuse operations while preserving the source contract.

The vector IR is abstract. A vector operation need not correspond one-to-one with a physical register.

## 5. MORPH layer

QSOL-MORPH is where target-specific implementation decisions are made.

Responsibilities may include:

- target selection;
- legality analysis;
- vectorization;
- fusion;
- scheduling;
- memory placement;
- backend lowering;
- generation of inspectable target code;
- recording material execution decisions.

MORPH is not allowed to silently redefine the source program's scientific meaning or bypass source effect-order constraints.

## 6. Backend layer

Backends translate validated intermediate representations into executable or consumable targets.

Possible backend families include:

- portable C;
- LLVM;
- Fortran;
- CUDA;
- HIP;
- WebAssembly;
- Vulkan Compute;
- OpenCL;
- a native QSOL VM;
- formal-verification adapters;
- MIDI 2.0 adapters.

POSIX process, stream, filesystem, environment, and signal semantics are modeled as the composable `QX-POSIX` profile rather than a mutually exclusive backend. A C-, LLVM-, Fortran-, or other generated program may use that profile when explicitly enabled and authorized.

A backend may expose additional target-specific control through an explicit extension profile. Backend-specific features should not leak into the core by default.

## Architectural separations

### Meaning is not machinery

`DERIVE C = A + B` describes a computation. It should not require the source to decide whether that addition occurs in a scalar loop, SIMD lane, GPU kernel, or future accelerator.

### Optimization is not epistemic promotion

A transformation may replace one implementation with an equivalent implementation. It may not turn a simulation into an observation, a test into a proof, or an assumption into evidence.

### Automatic is not invisible

QSOL-MORPH may automatically choose or optimize machinery, but material decisions should be inspectable and traceable.

### Extensions are not core growth

Capabilities such as CUDA, networking, AI model calls, POSIX process behavior, or MIDI should be introduced through explicit profiles/capability boundaries unless a future core specification establishes otherwise.

## Example path

```text
OBSERVE MASS 4.2 kg
DERIVE ENERGY = MASS * C * C
TRACE RESULT
```

might conceptually pass through:

```text
source cards
    ↓
typed semantic nodes
    ↓
reduced arithmetic/data operations
    ↓
dataflow graph
    ↓
backend-selected implementation
    ↓
result + trace manifest
```

Every stage should be inspectable enough to answer: **what did the program mean, what transformation happened, and what machinery executed it?**
