# Design Principles

QSOL-MORPH deliberately borrows successful ideas from older and newer computing traditions while keeping its own semantic contract.

This document records influences, not compatibility claims.

## 1. Meaning before machinery

The source program describes research intent and operational semantics. MORPH selects machinery.

## 2. Small semantic core

Prefer a small orthogonal instruction vocabulary over a growing collection of special cases.

Influence: RISC and simple machine architectures.

## 3. Stable interface, replaceable implementation

Keep the program-visible semantic model stable while allowing translation onto different physical architectures.

Influence: Transmeta Code Morphing.

## 4. Vector/dataflow first

Treat bulk scientific computation, masks, reductions, and chains as architectural concepts rather than accidental library patterns.

Influence: Cray vector systems.

## 5. Compose small operations

Use stream- and record-oriented composition instead of monolithic framework behavior.

Influence: Bell Labs / Unix / AWK traditions.

## 6. Memorable semantic vocabulary

Prefer common, semantically anchored words such as `OBSERVE`, `RUN`, `TEST`, `TRACE`, and `LOCK` over punctuation-heavy novelty.

Influence: Apollo VERB/NOUN interaction and command-oriented systems.

## 7. JOB → DECK → CARD

Use a memorable record-oriented hierarchy for research workflows.

Influence: mainframe batch systems and punch-card discipline, without fixed-column constraints.

## 8. Constraints as architecture

A constraint is useful when it reduces ambiguity or prevents accidental complexity.

Candidate examples:

- one preferred keyword per concept;
- explicit side effects;
- deterministic canonical forms;
- bounded semantic CARDs;
- small core plus extensions;
- no implicit epistemic promotion.

## 9. Reuse existing machinery

Do not recreate mature compilers, numerical libraries, formal tools, or accelerator stacks when a clean adapter/backend can reuse them.

Potential targets include C, Fortran, LLVM, POSIX, CUDA, Lean 4, and MIDI 2.0.

## 10. Optimization is conditional

A transformation is an optimization only if it satisfies the required semantic/evidence contract.

Correctness outranks speed.

## 11. Automatic is inspectable

Automatic vectorization, fusion, target selection, caching, or GPU placement should remain explainable and traceable.

## 12. AI is a collaborator, not a hidden runtime side effect

AI-assisted authoring should work against the same semantic model as human authoring. Calls to external AI models at program runtime are explicit effects with explicit provenance requirements.

## 13. Research claims retain class

The toolchain must preserve distinctions among observation, assumption, simulation, derivation, validation, and proof.

## 14. Portability does not mean pretending hardware is identical

A portable source program may have different legal implementations on different targets. The toolchain must state the actual numeric/determinism contract instead of overselling portability as universal byte identity.

## Design question

Every new feature should answer:

> Does this increase semantic power, or merely increase the number of ways to say the same thing?

If it is the latter, the default answer should be no.
