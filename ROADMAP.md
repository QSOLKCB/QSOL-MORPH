# QSOL-MORPH Roadmap

QSOL-MORPH is being developed specification-first. The project deliberately separates architectural agreement from executable implementation so that later code is judged against an explicit semantic contract rather than allowing implementation accidents to become the specification.

## Development rule

> Meaning is frozen before machinery is optimized.

No phase may silently weaken an invariant established by an earlier frozen phase. Backend-specific convenience does not override semantic preservation, determinism requirements, epistemic distinctions, numeric contracts, failure semantics, or traceability.

## PR #1 — Documentation Foundation

**Status:** current

Establish the non-normative architecture and vocabulary before implementation.

Deliverables:

- project architecture;
- human/AI language model;
- JOB → DECK → CARD → VERB/NOUN hierarchy;
- candidate semantic IR;
- candidate reduced core instruction families;
- vector and dataflow model;
- deterministic execution model;
- provenance and trace model;
- failure and partial-effect model;
- backend and code-morphing model;
- extension-profile model;
- capability/effect model;
- canonical serialization direction;
- contribution and AI-agent guidance;
- glossary and documentation index.

**Gate:** documentation must clearly distinguish illustrative syntax from frozen semantics.

## PR #2 — Lock in Core Invariants

Freeze the first normative QSOL-MORPH constitution.

Planned work:

- assign stable invariant identifiers;
- define MUST / MUST NOT / SHOULD interpretation;
- freeze semantic-preservation rules;
- freeze nondeterminism disclosure requirements;
- freeze numeric-contract preservation requirements;
- freeze epistemic non-promotion requirements;
- freeze backend-independence boundaries;
- freeze inspectability and traceability requirements;
- freeze the small-core / extension boundary;
- freeze capability and hidden-effect rules;
- freeze failure, fail-stop, and partial-effect disclosure rules;
- add machine-readable invariant registry;
- add validation that documentation and registry agree;
- define invariant change-control procedure.

No compiler or backend implementation is required for this PR.

## PR #3 — Canonical Data Model

Define and implement the first machine-readable representation of:

```text
JOB → DECK → CARD → VERB / NOUN
```

Planned scope:

- identifiers;
- source locations;
- typed operands;
- values and units;
- semantic classes;
- declared effects;
- required capabilities;
- result-determinism requirements;
- numeric contract identity and parameters required to interpret `NUMERIC` execution;
- randomness/reproducibility requirements;
- dependencies and effect-order constraints;
- extension declarations;
- deterministic canonical ordering;
- schema validation;
- reference fixtures.

The canonical model must carry enough information for later executable phases to enforce capability, numeric, and determinism rules fail-closed. These fields are part of the semantic input to execution, not backend annotations added after the fact.

## PR #4 — Canonical Serialization

Implement deterministic serialization for the canonical data model.

Initial targets:

- human-readable QSOL text profile;
- JSONL streaming profile;
- canonical JSON representation;
- XML interchange representation.

A MIDI 2.0 mapping remains an extension profile and must not affect the language core.

## PR #5 — Trace, Failure, and Provenance Foundation

Implement the minimum provenance and failure model required before any QSOL phase is permitted to execute research programs.

The initial trace contract should bind, where applicable:

- source identity/hash;
- canonical semantic IR identity/hash;
- active specification version;
- implementation/MORPH version;
- execution target or reference-machine identity;
- requested result-determinism contract;
- effective result-determinism contract;
- the rule/policy authorizing any permitted determinism transition;
- numeric contract identity/hash and material numeric mode;
- randomness mode/source;
- RNG algorithm and version;
- RNG stream identity and seed;
- parallel RNG partitioning/stream mapping where applicable;
- declared/used capabilities;
- inputs and output hashes;
- active extension profiles;
- structured execution-failure records and partial-effect status where applicable.

Before PR #6 may execute a program, this phase must also define the reference failure contract:

- evaluation yields a success or structured failure, never an implicit sentinel value;
- an unhandled failure stops the DECK by default;
- pure CARD failure commits no semantic state;
- capability/precondition rejection occurs before an external effect begins where practical;
- effects that were already externally observable before a later failure are not retroactively erased;
- an effect that begins and fails must be traceable as `NOT_STARTED`, `COMPLETED`, `PARTIAL`, or `UNKNOWN` (or frozen equivalents);
- division/modulo by zero and other defined arithmetic-domain errors produce structured failure rather than backend-chosen undefined behavior;
- failure traces identify the CARD, failure class/stage, prior committed effects, partial-effect state, and whether any output artifact became observable.

This phase is a gate for PR #6 and every later executable backend. No executable QSOL path should emit a research result without enough provenance to bind that result to the program, numeric contract, reproducibility contract, and execution/failure context that produced it.

## PR #6 — QSOL-CORE Reference Machine

Implement the first executable reduced semantic machine on top of the PR #5 trace/failure/provenance foundation.

Candidate families include:

- data movement;
- arithmetic;
- logic, including XOR;
- comparison;
- control;
- calls/returns;
- explicit effects.

The final instruction set is determined by the frozen specification, not by this roadmap.

Every reference-machine execution must emit the required PR #5 trace, obey the frozen success/failure and partial-effect contract, and fail closed when capability, numeric, or determinism requirements cannot be satisfied.

## PR #7 — Reference MORPH to C

Build the first deliberately boring backend:

```text
QSOL semantic representation
        ↓
QSOL-CORE / reference IR
        ↓
QSOL-MORPH
        ↓
portable C
```

Goals:

- semantic clarity;
- inspectable generated output;
- deterministic fixtures;
- no optimizer cleverness required for correctness;
- provenance-bound generated artifacts and results;
- failure behavior equivalent to the QSOL-CORE reference contract.

The C backend inherits the PR #5 trace/failure gate and must record backend/compiler identity and generated target hashes where material.

## PR #8 — Vector/Dataflow IR

Add target-independent vector computation.

Planned concepts:

- abstract vector registers;
- vector load/store;
- arithmetic and logic;
- masks;
- reductions;
- dependencies;
- fusion legality;
- alias rules;
- parallel partitioning;
- deterministic numeric-contract enforcement.

## PR #9 — Morph Optimization Passes

Introduce semantics-preserving transformations such as:

- constant folding;
- dead-result elimination;
- vectorization;
- dataflow fusion;
- temporary-elision;
- legal operation reordering under an explicit numeric contract.

Every optimization must be testable against the invariant set.

## PR #10 — POSIX Profile

Implement POSIX-oriented execution and composition:

- stdin/stdout/stderr;
- process execution;
- exit status;
- files;
- environment access;
- signals where appropriate;
- typed stream adapters.

External effects remain explicit capabilities. POSIX is a composable execution profile, not a mutually exclusive compiler backend: a C-, LLVM-, or other generated program may use the QX-POSIX contract when explicitly enabled.

## PR #11 — LLVM Backend

Add LLVM lowering while retaining the C backend as an independently understandable reference path.

## PR #12 — GPU Foundation

Define the generic accelerator execution model before binding it to one vendor.

Planned concepts:

- host/device residency;
- abstract work decomposition;
- memory classes;
- synchronization boundaries;
- deterministic execution declarations;
- kernel inspection.

## PR #13 — CUDA Profile

Implement direct CUDA morphing through the generic GPU model.

Target user experience:

```text
RUN GRAVITY ON CUDA
```

without requiring ordinary CUDA plumbing in research source, while preserving an expert escape hatch for explicit launch and memory controls.

## PR #14 — Additional Backends

Candidates include:

- Fortran;
- HIP;
- WebAssembly;
- Vulkan Compute;
- OpenCL;
- native QSOL VM.

Backends are added according to research value, not checklist pressure.

## PR #15 — Formalization

Formalize selected QSOL-CORE and QSOL-MORPH properties, potentially using Lean 4.

Targets may include:

- deterministic evaluation for a defined subset;
- semantic preservation for selected morph passes;
- invariant consistency;
- epistemic-class preservation;
- canonical serialization properties;
- failure-state and effect-order properties for a defined subset.

## Extension workstreams

Extension profiles may evolve independently once the core extension boundary is frozen:

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

An extension may add capability. It may not silently redefine frozen core meaning.

## Release philosophy

Early releases should favor frozen, auditable semantic milestones over feature volume.

A release should state exactly which specification, invariants, schemas, and backends it implements.
