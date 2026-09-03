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
                     │ semantic-to-core lowering
                     ▼
┌──────────────────────────────────────────┐
│ QSOL-CORE / REDUCED SEMANTIC MACHINE    │
│ small orthogonal instruction families   │
└────────────────────┬─────────────────────┘
                     │ core-to-vector/dataflow lowering
                     ▼
┌──────────────────────────────────────────┐
│ VECTOR / DATAFLOW IR                     │
│ vectors • masks • dependency graph      │
│ control • effects • contracts • fusion  │
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

Each arrow is a contract boundary. In particular, canonical Semantic IR → QSOL-CORE and QSOL-CORE → Vector/Dataflow IR are specified and tested independently rather than being invented inside a backend.

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
           ├── RESULT BINDING
           ├── TYPE / UNIT
           ├── QUALIFIERS
           ├── SEMANTIC CLASS
           ├── EFFECT REQUIREMENTS[]
           │    ├── EFFECT ID
           │    ├── EFFECT KIND
           │    └── REQUIRED CAPABILITIES[]
           ├── DETERMINISM / RANDOMNESS CONTRACT
           ├── NUMERIC CONTRACT
           ├── EXTENSION REQUIREMENTS[]
           ├── FAILURE BEHAVIOR
           └── DEPENDENCIES / EFFECT ORDER
```

A `CARD` is intended to be the smallest independently addressable semantic statement.

The `RESULT BINDING` identifies the value produced by a CARD when one is named. It must survive canonicalization and serialization because dependent CARDs may reference it.

`SEMANTIC CLASS` carries the CARD's epistemic classification where applicable, such as observation, simulation, validation, or proof. It is canonical semantic state and must survive any representation boundary until a frozen rule explicitly validates how it is preserved or safely represented elsewhere.

`EFFECT REQUIREMENTS[]` is the canonical effect/authorization association. Each protected effect has its own stable effect identity and complete capability set. A CARD-level union of capabilities may be useful for preflight, but it does not replace the per-effect mapping and must not be used to guess which permissions govern which action.

`EXTENSION REQUIREMENTS[]` identifies any versioned profile/contract needed to interpret extension-owned syntax, qualifiers, effects, or lowering hooks. Extension availability remains separate from runtime capability authorization.

A `DECK` is a source-ordered collection of cards with explicit/derived dependency constraints representing one executable research workflow.

Only CARDs proven **pure and total** under the active contract may be freely scheduled from dependency edges. A pure CARD that may fail is still ordering-relevant under fail-stop semantics, because moving it across an observable effect can change which effects commit before failure. Effectful CARDs are source-ordered by default: the canonical model should derive sequencing constraints between observable effects so that two writes, external calls, process launches, or similar effects cannot be reordered merely because they lack a data dependency.

A future explicit construct may permit parallel or commutative effects, but only under frozen rules that define when the relaxation is semantically legal and what ordering remains observable.

A `JOB` coordinates one or more decks and their execution relationships.

The model is inspired by record-oriented computing, but QSOL is not intended to reproduce historical fixed-column limitations.

## 3. Semantic-to-QSOL-CORE lowering

The first lowering stage maps rich Semantic IR into the reduced operational machine.

This mapping is itself part of the language contract because Semantic IR contains information QSOL-CORE may represent more compactly or carry as preserved metadata:

- epistemic classes and evidence boundaries;
- units and types;
- result bindings;
- qualifiers;
- explicit effect requirements with stable effect IDs and complete per-effect capability sets;
- determinism, numeric, and randomness contracts;
- explicit failure behavior;
- extension identities;
- source/effect/failure ordering;
- CARD / DECK / JOB provenance.

The lowering must either encode a requirement into QSOL-CORE operations or preserve/validate it before safe metadata erasure. Unsupported semantic constructs fail explicitly rather than being silently dropped or delegated to a backend to reinterpret.

See [Semantic-to-QSOL-CORE Lowering](SEMANTIC-TO-CORE-LOWERING.md).

## 4. QSOL-CORE

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

## 5. Vector and dataflow layer

Scientific computation often contains bulk operations whose natural representation is not scalar source-code iteration.

QSOL-MORPH therefore treats vectors, masks, reductions, dependency graphs, control, effects, and contracts as first-class lower-IR concepts.

A sequence such as:

```text
DERIVE X = A * B
DERIVE Y = X + C
DERIVE Z = SQRT Y
```

may become a dependency graph that permits a backend to fuse operations while preserving the source contract.

The Vector/Dataflow IR is abstract. A vector operation need not correspond one-to-one with a physical register, and non-vector operations still require semantics-preserving representation through this mandatory stage.

## 6. MORPH layer

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

MORPH is not allowed to silently redefine the source program's scientific meaning, bypass either mandatory lowering contract, or bypass source effect/failure ordering constraints.

## 7. Backend layer

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

A backend may expose additional target-specific control through an explicit extension profile. For example, CUDA is a backend choice while `QX-CUDA` is an optional control profile. Backend-specific features should not leak into the core by default.

## Architectural separations

### Meaning is not machinery

`DERIVE C = A + B` describes a computation. It should not require the source to decide whether that addition occurs in a scalar loop, SIMD lane, GPU kernel, or future accelerator.

### Lowering is not backend invention

Semantic IR → QSOL-CORE and QSOL-CORE → Vector/Dataflow IR are defined transformation boundaries. A backend consumes the result of those boundaries; it does not decide how observations, assumptions, effects, units, contracts, or other semantic CARDs acquire lower-level meaning.

### Authorization belongs to each effect

An effect's permission requirements are part of the effect declaration itself. If one CARD declares a remote AI call requiring `AI_MODEL + NETWORK` and a separate file write requiring `FILESYSTEM_WRITE`, those capability sets remain associated with their respective effect IDs through lowering and trace provenance. Applying one ambiguous CARD-level capability union to every effect is not conforming behavior.

### Optimization is not epistemic promotion

A transformation may replace one implementation with an equivalent implementation. It may not turn a simulation into an observation, a test into a proof, or an assumption into evidence.

### Automatic is not invisible

QSOL-MORPH may automatically choose or optimize machinery, but material decisions should be inspectable and traceable.

### Extensions are not core growth

Networking, AI model calls, POSIX process behavior, MIDI, and vendor-specific control surfaces should be introduced through explicit profiles/capability boundaries unless a future core specification establishes otherwise.

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
semantic-to-core lowering
    ↓
QSOL-CORE operations + preserved metadata
    ↓
core-to-vector/dataflow lowering
    ↓
full Vector/Dataflow IR
    ↓
backend-selected implementation
    ↓
result + trace manifest
```

Every stage should be inspectable enough to answer: **what did the program mean, what transformation happened, and what machinery executed it?**
