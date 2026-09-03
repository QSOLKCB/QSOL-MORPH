# Glossary

This glossary records current architectural vocabulary. Terms remain provisional until frozen by a normative specification.

## CARD

The smallest independently addressable semantic statement in the proposed model.

## DECK

A reproducible workflow composed of CARDs.

## JOB

An orchestration boundary that coordinates one or more DECKs.

## VERB

The operation performed by a CARD, such as `OBSERVE`, `RUN`, `TEST`, or `TRACE`.

## NOUN

The semantic target of a CARD, such as `TEMPERATURE`, `MODEL`, or `RESULT`.

## semantic anchor

A keyword chosen because its ordinary, research, and computational meanings align closely enough to reduce ambiguity for humans and AI.

## semantic class

The research/epistemic classification attached to a value or operation, such as observation, assumption, simulation, derivation, validation, or proof.

## QSOL-CORE

The proposed reduced semantic machine beneath the research-facing language.

## Semantic IR

The canonical typed representation that preserves research intent, units, qualifiers, effect requirements, explicit failure behavior, dependencies, numeric/reproducibility contracts, and semantic class before lower machine-oriented transformations.

## effect requirement

The canonical binding between one protected effect and the complete runtime capability set required before that effect may begin. Conceptually it contains an `effect_id`, `effect_kind`, and `required_capabilities[]`. A CARD-level union of capabilities may be useful for preflight but does not replace the per-effect association.

## Semantic-to-Core Lowering

The independently specified transformation from canonical Semantic IR into QSOL-CORE plus preserved metadata/provenance. It must preserve or validly consume qualifiers, effect requirements, explicit failure behavior, epistemic boundaries, contracts, ordering, and identity under frozen rules.

## Vector/Dataflow IR

The mandatory target-independent lower IR that preserves the complete supported QSOL-CORE surface while exposing vector and dataflow structure where applicable. It must represent or preserve scalar operations, vector operations, control flow, calls/returns, explicit effects and their complete capability sets, qualifiers/failure behavior still material at this stage, dependency/effect/failure ordering, determinism/numeric/randomness contracts, extension bindings, and provenance. Backends must not bypass this IR for non-vectorizable core operations.

## Core-to-Vector/Dataflow Lowering

The independently specified and provenance-bearing transformation from QSOL-CORE into the mandatory Vector/Dataflow IR. A conforming run identifies the input Core IR, active Vector/Dataflow specification, lowering implementation, and resulting Vector/Dataflow IR.

## MORPH

The transformation layer that maps stable QSOL semantics onto target-specific machinery after the mandatory lowerings.

## backend

A concrete code-generation or execution target such as C, LLVM, Fortran, CUDA, HIP, WebAssembly, or a native QSOL VM.

## extension profile

An optional, versioned syntax/adapter/execution surface such as `QX-POSIX`, `QX-GPU`, or `QX-NET` that adds functionality without redefining core meaning. Loading or using an extension profile does **not** grant runtime permission for protected effects; authorization remains a separate capability decision.

## QX-POSIX

The composable POSIX process/stream/filesystem execution profile. It is not a mutually exclusive compiler backend; generated C, LLVM, Fortran, or other targets may use the profile when explicitly enabled and when all required capabilities are separately authorized. Its operational semantics are frozen before its reference implementation.

## QX-CUDA

The optional versioned CUDA-specific control profile for explicit launch, memory, or tuning controls. It is distinct from selecting CUDA as a backend and does not itself grant GPU/runtime permission. Its control semantics must be frozen before implementation.

## capability

Runtime permission granted to an execution environment for a class of protected effects, such as network, filesystem, process, GPU, or AI-model access. Capability authorization is separate from extension-profile availability.

## effect

An operation with externally observable or stateful behavior, such as file I/O, network access, process execution, randomness, or an AI-model call.

## effect attempt

One identified attempt to perform a protected external effect. It records the originating CARD/effect identity, the complete required-capability set, ordering/provenance information, and a completion state.

## NOT_STARTED

An effect-attempt state meaning the protected effect never began.

## COMPLETED

An effect-attempt state meaning the effect reached its defined external completion boundary. This is independent of whether the enclosing CARD ultimately succeeds or fails.

## ABORTED_CLEAN

An effect-attempt state meaning the protected effect began, did not complete, and is proven to have produced no externally observable change.

## PARTIAL

An effect-attempt state meaning the protected effect began, did not complete, and some externally observable portion occurred.

## UNKNOWN

An effect-attempt state meaning completion or external observability cannot be established reliably.

## deterministic execution

Execution under a contract that constrains or eliminates relevant sources of nondeterminism.

## result-determinism contract

The requested or effective guarantee on observable results, such as strict byte identity, tolerance-bounded numeric equivalence, or explicitly declared nondeterminism.

## randomness contract

The independent contract describing whether randomness is absent, reproducibly seeded, externally entropic, or otherwise explicitly nondeterministic.

## numeric contract

Rules describing which numeric transformations and result differences are legal for a program or operation.

## trace

A structured record of semantic, lowering, transformation, execution, failure, or result information used to explain and reproduce a run.

## provenance

Evidence connecting a result or failure to its source, inputs, mandatory lowering stages, transformations, execution context, authorization decisions, and validation boundary.

## canonical form

A deterministic representation used for stable comparison, hashing, serialization, or frozen artifacts.

## semantic preservation

The requirement that a transformation retain the source meaning defined by the active contract.

## epistemic promotion

An increase in claimed knowledge status, for example treating a simulation as an observation or a test as a proof. Silent epistemic promotion is a design anti-goal.

## fusion

Combining multiple legal operations into a smaller number of target operations or kernels while preserving the required semantic/numeric/failure contract.

## vectorization

Mapping semantic bulk operations onto a parallel/vector execution strategy without requiring the source to encode the physical vector width.

## reference backend

A conservative implementation path used as an understandable correctness baseline for more aggressive backends.
