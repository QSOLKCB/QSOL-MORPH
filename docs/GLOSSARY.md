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

The canonical typed representation that preserves research intent, units, effects, dependencies, numeric/reproducibility contracts, and semantic class before lower machine-oriented transformations.

## Vector/Dataflow IR

A target-independent representation for vectors, masks, reductions, dependency graphs, and legal fusion opportunities.

## MORPH

The transformation layer that maps stable QSOL semantics onto target-specific machinery.

## backend

A concrete code-generation or execution target such as C, LLVM, Fortran, CUDA, HIP, WebAssembly, or a native QSOL VM.

## extension profile

An optional capability or execution surface such as `QX-POSIX`, `QX-GPU`, or `QX-NET` that adds functionality without redefining core meaning.

## QX-POSIX

The composable POSIX process/stream/filesystem execution profile. It is not a mutually exclusive compiler backend; generated C, LLVM, Fortran, or other targets may use the profile when explicitly enabled and authorized.

## capability

Permission granted to an execution environment for a class of effects, such as network or filesystem access.

## effect

An operation with externally observable or stateful behavior, such as file I/O, network access, process execution, randomness, or an AI-model call.

## deterministic execution

Execution under a contract that constrains or eliminates relevant sources of nondeterminism.

## result-determinism contract

The requested or effective guarantee on observable results, such as strict byte identity, tolerance-bounded numeric equivalence, or explicitly declared nondeterminism.

## randomness contract

The independent contract describing whether randomness is absent, reproducibly seeded, externally entropic, or otherwise explicitly nondeterministic.

## numeric contract

Rules describing which numeric transformations and result differences are legal for a program or operation.

## trace

A structured record of semantic, transformation, execution, failure, or result information used to explain and reproduce a run.

## provenance

Evidence connecting a result or failure to its source, inputs, transformations, execution context, and validation boundary.

## partial effect

An externally observable effect that began but did not complete normally. Its existence and known/unknown extent must not be hidden by a later execution failure.

## canonical form

A deterministic representation used for stable comparison, hashing, serialization, or frozen artifacts.

## semantic preservation

The requirement that a transformation retain the source meaning defined by the active contract.

## epistemic promotion

An increase in claimed knowledge status, for example treating a simulation as an observation or a test as a proof. Silent epistemic promotion is a design anti-goal.

## fusion

Combining multiple legal operations into a smaller number of target operations or kernels while preserving the required semantic/numeric contract.

## vectorization

Mapping semantic bulk operations onto a parallel/vector execution strategy without requiring the source to encode the physical vector width.

## reference backend

A conservative implementation path used as an understandable correctness baseline for more aggressive backends.
