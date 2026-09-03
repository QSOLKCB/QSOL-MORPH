# QSOL-MORPH Roadmap

QSOL-MORPH is being developed specification-first. The project deliberately separates architectural agreement from executable implementation so that later code is judged against an explicit semantic contract rather than allowing implementation accidents to become the specification.

## Development rule

> Meaning is frozen before machinery is optimized.

No phase may silently weaken an invariant established by an earlier frozen phase. Backend-specific convenience does not override semantic preservation, determinism requirements, epistemic distinctions, numeric contracts, capability authorization, failure semantics, or traceability.

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
- freeze failure, fail-stop, JOB propagation, and partial-effect disclosure rules;
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
- dependencies;
- source-order, effect-order, and failure-order constraints;
- extension declarations with required versions/contracts;
- deterministic canonical ordering;
- schema validation;
- reference fixtures.

The canonical model must carry enough information for later executable phases to enforce capability, numeric, randomness, failure-order, and determinism rules fail-closed. These fields are part of the semantic input to execution, not backend annotations added after the fact.

Only CARDs proven **pure and total** under the active contract may be freely reordered when dependencies permit. A CARD that may fail is semantically observable under fail-stop execution and must preserve ordering against externally observable effects unless an explicit frozen construct permits otherwise.

## PR #4 — Canonical Serialization

Implement deterministic serialization for the complete canonical data model.

Initial targets:

- human-readable QSOL text profile;
- JSONL streaming profile;
- canonical JSON representation;
- XML interchange representation.

Every lossless format must round-trip all canonical enforcement fields, including capabilities, determinism, numeric, randomness, extension/version, dependency, effect-order, and failure-order information.

A MIDI 2.0 mapping remains an extension profile and must not affect the language core.

## PR #5 — Execution Contract, Trace, Failure, and Provenance Foundation

Implement the minimum execution-contract schema required before any QSOL phase is permitted to execute research programs.

The initial trace contract should bind, where applicable:

- source identity/hash;
- canonical semantic IR identity/hash;
- active specification version;
- implementation/MORPH version;
- execution target or reference-machine identity;
- requested result-determinism contract;
- effective result-determinism contract;
- the rule/policy identity authorizing any permitted determinism transition;
- numeric contract identity/hash and material numeric mode;
- requested randomness contract/mode;
- effective randomness contract/mode;
- the rule/policy identity authorizing any permitted randomness transition;
- RNG algorithm and version;
- RNG stream identity and seed;
- parallel RNG partitioning/stream mapping where applicable;
- required capabilities;
- capabilities granted and denied for this execution;
- capability-policy identity/version responsible for authorization decisions;
- capabilities actually used;
- inputs and output hashes;
- active extension profiles plus resolved extension versions/content identities;
- structured execution-failure records and partial-effect status where applicable;
- fields for backend-selection policy/version and tuning-state identity when automatic target selection is later used.

Before PR #7 may execute a program, this phase must also define the reference failure contract:

- evaluation yields a success or structured failure, never an implicit sentinel value;
- an unhandled CARD failure stops further CARD execution in the DECK by default;
- an unhandled DECK failure fails the enclosing JOB by default and no later DECK in that JOB starts;
- dependent JOB/DECK comparisons or consumers do not execute against missing or partial failed outputs;
- future continue/retry/recovery/parallel-JOB behavior requires explicit frozen JOB-level semantics;
- pure CARD failure commits no semantic state;
- capability authorization is completed successfully **before every protected external effect begins**;
- other static/precondition checks should occur before an external effect where practical;
- effects already externally observable before a later failure are not retroactively erased;
- an effect that begins and fails must be traceable as `NOT_STARTED`, `COMPLETED`, `PARTIAL`, or `UNKNOWN` (or frozen equivalents);
- division/modulo by zero and other defined arithmetic-domain errors produce structured failure rather than backend-chosen undefined behavior;
- failure traces identify the CARD, DECK/JOB outcome, failure class/stage, prior committed effects, partial-effect state, and whether any output artifact became observable.

This phase is a gate for PR #7 and every later executable implementation. No executable QSOL path should emit a research result without enough provenance to bind that result to the program, execution policy, numeric contract, reproducibility contract, extension set, authorization decisions, and execution/failure context that produced it.

## PR #6 — Normative QSOL-CORE Operational Specification

Freeze QSOL-CORE semantics **before** implementing the reference machine.

Planned work:

- freeze the initial instruction families and exact instruction inventory;
- define operand, result, type, and state-transition semantics;
- define arithmetic and numeric-contract interaction;
- define logic semantics, including XOR;
- define comparison semantics;
- define branch/jump/call/return/stop behavior;
- define stack/call-state behavior if present;
- define explicit effect operations and capability requirements;
- define success/failure propagation into DECK and JOB outcomes;
- define which operations are pure, total, potentially failing, or effectful;
- define sequencing and reordering observability;
- publish conformance fixtures/examples for each instruction.

This PR is normative specification work, not an executable machine. The reference implementation may not invent instruction meaning that is absent from this specification.

## PR #7 — QSOL-CORE Reference Machine

Implement the first executable reduced semantic machine against the frozen PR #6 operational specification and the PR #5 execution-contract foundation.

The reference machine must:

- implement the frozen instruction semantics rather than define them;
- emit the required PR #5 trace;
- obey frozen DECK/JOB failure propagation and partial-effect behavior;
- require successful capability authorization before each protected effect;
- fail closed when capability, numeric, randomness, or determinism requirements cannot be satisfied;
- pass the frozen QSOL-CORE conformance fixtures.

## PR #8 — Vector/Dataflow IR

Define and implement the target-independent vector/dataflow layer used by MORPH backend lowering.

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
- totality/failure-order constraints;
- deterministic numeric-contract enforcement.

This phase occurs before the first MORPH code-generation backend so the documented pipeline remains singular:

```text
QSOL-CORE
    ↓
Vector/Dataflow IR
    ↓
MORPH
    ↓
backend
```

## PR #9 — Reference MORPH to C

Build the first deliberately boring backend after the Vector/Dataflow IR exists:

```text
QSOL semantic representation
        ↓
QSOL-CORE
        ↓
Vector/Dataflow IR
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

The C backend inherits the PR #5 trace/failure/authorization gate and must record backend/compiler identity and generated target hashes where material.

## PR #10 — Morph Optimization Passes

Introduce semantics-preserving transformations such as:

- constant folding;
- dead-result elimination;
- vectorization;
- dataflow fusion;
- temporary-elision;
- legal operation reordering under explicit totality, failure-order, and numeric contracts.

Every optimization must be testable against the invariant set and QSOL-CORE reference semantics.

## PR #11 — POSIX Profile

Implement POSIX-oriented execution and composition:

- stdin/stdout/stderr;
- process execution;
- exit status;
- files;
- environment access;
- signals where appropriate;
- typed stream adapters.

External effects remain explicit capabilities. POSIX is a composable execution profile, not a mutually exclusive compiler backend: a C-, LLVM-, or other generated program may use the QX-POSIX contract when explicitly enabled and authorized.

## PR #12 — LLVM Backend

Add LLVM lowering while retaining the C backend as an independently understandable reference path.

## PR #13 — GPU Foundation

Define the generic accelerator execution model before binding it to one vendor.

Planned concepts:

- host/device residency;
- abstract work decomposition;
- memory classes;
- synchronization boundaries;
- deterministic execution declarations;
- kernel inspection.

## PR #14 — CUDA Backend and QX-CUDA Control Profile

Implement CUDA lowering through the generic GPU model.

`CUDA` is a machinery/backend selection. `QX-CUDA` is the optional vendor-specific control profile for explicit launch, memory, or tuning controls. Selecting the CUDA backend does not by itself mean that source uses QX-CUDA-specific syntax.

Target user experience:

```text
RUN GRAVITY ON CUDA
```

without requiring ordinary CUDA plumbing in research source, while preserving an expert escape hatch through explicit QX-CUDA controls.

## PR #15 — Additional Backends

Candidates include:

- Fortran;
- HIP;
- WebAssembly;
- Vulkan Compute;
- OpenCL;
- native QSOL VM.

Backends are added according to research value, not checklist pressure.

## PR #16 — Formalization

Formalize selected QSOL-CORE and QSOL-MORPH properties, potentially using Lean 4.

Targets may include:

- deterministic evaluation for a defined subset;
- semantic preservation for selected morph passes;
- invariant consistency;
- epistemic-class preservation;
- canonical serialization properties;
- failure-state, JOB propagation, authorization, and ordering properties for a defined subset.

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

A release should state exactly which specification, invariants, schemas, extension versions, and backends it implements.
