# AGENTS.md

This file is guidance for AI coding/research agents working in QSOL-MORPH.

## Project mission

QSOL-MORPH is a deterministic code-morphing architecture for human–AI research computing.

Core mnemonic:

```text
QSOL describes intent.
QSOL-CORE defines meaning.
QSOL-MORPH chooses machinery.
```

## Current phase

The repository is specification-first and pre-alpha.

Do not implement compiler/runtime/backend code unless the active task explicitly belongs to an implementation phase in `ROADMAP.md`.

PR #1 is documentation foundation.

PR #2 is reserved for locking core invariants.

## Semantic rules for agents

When proposing changes:

1. preserve the distinction between meaning and machinery;
2. preserve research/epistemic classes;
3. prefer one canonical concept over synonyms;
4. keep effects explicit;
5. keep backend-specific controls out of core unless explicitly justified;
6. treat determinism and provenance as first-class requirements;
7. do not call performance improvement an optimization unless the required semantics remain valid;
8. do not promote simulation/test/AI output into stronger evidence classes without an explicit rule;
9. do not silently weaken failure behavior;
10. prefer small, inspectable transformations.

## Vocabulary

Use current project vocabulary consistently:

```text
JOB
DECK
CARD
VERB
NOUN
QSOL-CORE
Semantic IR
Vector/Dataflow IR
MORPH
backend
extension profile
capability
effect
trace
provenance
```

See `docs/GLOSSARY.md`.

## Illustrative syntax

Until a grammar is frozen, examples are architectural sketches.

Do not infer implementation support from examples in documentation.

## Optimization work

Use the reference semantics first.

A valid optimization must preserve the active semantic/numeric/determinism contract.

For CI and optimization evidence rules, read `docs/OPTIMIZATION-AND-CI.md` before changing performance-sensitive or validation-sensitive code.

## Backend work

Backend-specific behavior belongs behind explicit backend or extension boundaries.

Generated target code should remain inspectable where practical.

## Documentation hierarchy

Read in this order when context is limited:

1. `docs/SPECIFICATION-STATUS.md`
2. `docs/DESIGN-PRINCIPLES.md`
3. `docs/ARCHITECTURE.md`
4. `docs/LANGUAGE-MODEL.md`
5. `docs/SEMANTIC-IR.md`
6. the domain-specific document relevant to the task
7. `ROADMAP.md`

## Change discipline

Do not broaden scope merely because an adjacent improvement is attractive.

If a task targets one phase, leave later-phase work in `ROADMAP.md` unless it is required to make the current phase internally correct.

## Review discipline

For every substantive change, ask:

- Did meaning change?
- Did an effect become implicit?
- Did determinism weaken?
- Did provenance weaken?
- Did an extension leak into core?
- Did an optimization alter a result contract?
- Did documentation claim functionality that does not exist?

If any answer is yes, make the change explicit or reject it.
