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

QSOL-CORE implementation must not precede its normative operational specification.

Semantic IR → QSOL-CORE lowering must not be invented inside a backend. Its normative lowering specification and reference implementation must exist before MORPH code-generation backends are treated as end-to-end conforming.

## Semantic rules for agents

When proposing changes:

1. preserve the distinction between meaning and machinery;
2. preserve research/epistemic classes;
3. prefer one canonical concept over synonyms;
4. keep effects explicit;
5. keep backend-specific controls out of core unless explicitly justified;
6. treat determinism, numeric contracts, randomness, and provenance as first-class requirements;
7. do not call performance improvement an optimization unless the required semantics remain valid;
8. do not promote simulation/test/AI output into stronger evidence classes without an explicit rule;
9. do not silently weaken CARD, DECK, or JOB failure behavior;
10. require successful capability authorization before every protected external effect begins;
11. treat a potentially failing pure operation as ordering-relevant under fail-stop semantics unless it is proven total;
12. preserve all canonical enforcement fields across any serialization claiming semantic losslessness;
13. distinguish backend selection from optional vendor-control profiles (`CUDA` != `QX-CUDA`, POSIX execution != a compiler backend);
14. preserve the explicit Semantic IR → QSOL-CORE lowering boundary; do not let a backend reinterpret rich semantic CARDs privately;
15. record material numeric mode, automatic-backend selection policy/tuning identity, and identified per-effect-attempt states when relevant to provenance;
16. prefer small, inspectable transformations.

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
Semantic-to-Core Lowering
Vector/Dataflow IR
MORPH
backend
extension profile
capability
effect
numeric contract
randomness contract
effect attempt
trace
provenance
```

See `docs/GLOSSARY.md`.

## Illustrative syntax

Until a grammar is frozen, examples are architectural sketches.

Do not infer implementation support from examples in documentation.

## Semantic lowering work

Read `docs/SEMANTIC-TO-CORE-LOWERING.md` before changing the Semantic IR → QSOL-CORE boundary.

A legal lowering must preserve or explicitly validate before erasure:

- epistemic class and evidence boundaries;
- types and units;
- effects and required capabilities;
- result-determinism, numeric, and randomness contracts;
- extension identities/versions;
- source, effect, and failure ordering;
- CARD / DECK / JOB provenance.

Unsupported semantic constructs fail explicitly. Do not silently drop them, no-op them, or defer their meaning to a backend.

## Optimization work

Use the reference semantics first.

A valid optimization must preserve the active semantic/numeric/determinism/randomness/failure-order/authorization contract.

Only operations proven pure and total may be freely reordered solely from data dependencies. A pure operation that may fail can still change whether effects occur under fail-stop execution.

For CI and optimization evidence rules, read `docs/OPTIMIZATION-AND-CI.md` before changing performance-sensitive or validation-sensitive code.

## Backend work

Backend-specific behavior belongs behind explicit backend or extension boundaries.

Generated target code should remain inspectable where practical.

A backend implements frozen semantics. It does not define them.

A backend must consume the established lower pipeline; it must not become a second Semantic IR → QSOL-CORE compiler with private semantics.

Automatic backend selection must trace the selection policy and material tuning identity when those affect the choice.

## Serialization work

A format claiming semantic losslessness must round-trip all execution-relevant canonical fields, including:

- effects and required capabilities;
- result-determinism and numeric contracts;
- randomness contracts;
- extension/profile identities and versions;
- data, effect, and failure-order constraints.

Do not silently default a missing enforcement field during transport.

## Documentation hierarchy

Read in this order when context is limited:

1. `docs/SPECIFICATION-STATUS.md`
2. `docs/DESIGN-PRINCIPLES.md`
3. `docs/ARCHITECTURE.md`
4. `docs/LANGUAGE-MODEL.md`
5. `docs/SEMANTIC-IR.md`
6. `docs/SEMANTIC-TO-CORE-LOWERING.md`
7. the domain-specific document relevant to the task
8. `ROADMAP.md`

## Change discipline

Do not broaden scope merely because an adjacent improvement is attractive.

If a task targets one phase, leave later-phase work in `ROADMAP.md` unless it is required to make the current phase internally correct.

## Review discipline

For every substantive change, ask:

- Did meaning change?
- Did an effect become implicit?
- Did authorization move until after an effect began?
- Did determinism, numeric, or randomness guarantees weaken?
- Did provenance weaken?
- Did an extension leak into core?
- Did a serializer lose an enforcement field?
- Did reordering change failure/effect observability?
- Did a backend or implementation invent semantics not yet frozen?
- Did Semantic IR → QSOL-CORE lowering lose a contract or provenance edge?
- Did a trace collapse several effect attempts into one ambiguous state?
- Did an optimization alter a result contract?
- Did documentation claim functionality that does not exist?

If any answer is yes, make the change explicit or reject it.
