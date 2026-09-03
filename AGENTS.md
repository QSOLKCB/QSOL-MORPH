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

The mandatory Vector/Dataflow IR stage must preserve the complete supported QSOL-CORE surface. Its normative specification must precede the reference Core→Vector/Dataflow lowering, and backends may not bypass that lowering for control, calls, effects, scalar operations, capabilities, or contracts merely because they are not vectorizable.

Human `.qsl` parsing/serialization must not be implemented from illustrative examples. A normative QSOL text profile must first freeze grammar and source-to-Semantic-IR mapping.

QX-POSIX implementation must not precede its normative profile contract.

Generic GPU backend work must not define accelerator semantics opportunistically; the generic GPU execution contract is frozen before vendor backends. QX-CUDA control implementation must not precede its own versioned normative control contract.

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
10. require successful authorization of **every** capability required by a protected external effect before that effect begins;
11. preserve the explicit effect → complete capability-set association; do not replace it with an ambiguous CARD-level union;
12. treat a potentially failing pure operation as ordering-relevant under fail-stop semantics unless it is proven total;
13. do not dead-eliminate a potentially failing operation merely because its result is unused;
14. preserve all canonical semantic/enforcement fields, including `qualifiers{}` and explicit `failure_behavior`, across any serialization claiming semantic losslessness;
15. distinguish backend selection from optional vendor-control profiles (`CUDA` != `QX-CUDA`, POSIX execution != a compiler backend);
16. distinguish extension availability/functionality from runtime capability authorization; activating an extension never grants permission;
17. preserve the explicit Semantic IR → QSOL-CORE lowering boundary; do not let a backend reinterpret rich semantic CARDs privately;
18. preserve execution-relevant qualifiers through Semantic→Core lowering unless a frozen rule explicitly consumes them and records the resulting decision;
19. preserve the complete QSOL-CORE control/effect/contract surface through the mandatory Vector/Dataflow IR;
20. record both mandatory lowering identities/hashes in provenance: Semantic→Core and Core→Vector/Dataflow;
21. record material numeric mode, automatic-backend selection policy/tuning identity, and identified per-effect-attempt states when relevant to provenance;
22. record the complete required-capability set for each effect attempt;
23. define effect-attempt completion independently from the enclosing CARD outcome;
24. distinguish a cleanly aborted begun effect from `NOT_STARTED`, `PARTIAL`, and `UNKNOWN`;
25. prefer small, inspectable transformations.

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
Core-to-Vector/Dataflow Lowering
MORPH
backend
extension profile
capability
effect
effect requirement
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

Do not implement `.qsl` parsing, formatting, or lossless text serialization until a normative QSOL text-profile specification freezes lexical grammar, syntax, shorthand/default reconstruction, canonical rendering, diagnostics, and source-to-Semantic-IR mapping.

## Semantic lowering work

Read `docs/SEMANTIC-TO-CORE-LOWERING.md` before changing the Semantic IR → QSOL-CORE boundary.

A legal lowering must preserve or explicitly validate before erasure:

- epistemic class and evidence boundaries;
- types and units;
- execution-relevant qualifiers;
- `effect_requirements[]` and each effect's complete `required_capabilities[]`;
- explicit `failure_behavior`;
- result-determinism, numeric, and randomness contracts;
- extension identities/versions;
- source, effect, and failure ordering;
- CARD / DECK / JOB provenance.

Unsupported semantic constructs or qualifiers fail explicitly. Do not silently drop them, no-op them, default them, or defer their meaning to a backend.

## Vector/Dataflow IR work

Read `docs/VECTOR-AND-DATAFLOW.md` before changing the mandatory lower computational IR.

Because every backend path traverses this IR, it must represent or preserve the full supported QSOL-CORE surface, including:

- scalar and vector data operations;
- control flow;
- calls/returns and call state;
- explicit effects;
- complete required-capability sets;
- qualifiers and explicit failure behavior carried from earlier stages where still material;
- failure/totality classification;
- source/effect/failure ordering;
- determinism, numeric, randomness, and extension contracts;
- provenance and per-effect-attempt identity.

A non-vectorizable QSOL-CORE operation is not permission to bypass the IR. Use a defined scalar/control/effect/pass-through construct or fail conformance until the IR has one.

The Core→Vector/Dataflow stage is independently provenance-bearing. Trace at least the Core IR hash, Vector/Dataflow specification identity, lowering implementation identity, and resulting Vector/Dataflow IR hash when material.

## Optimization work

Use the reference semantics first.

A valid optimization must preserve the active semantic/numeric/determinism/randomness/failure-order/authorization contract.

Only operations proven pure and total may be freely reordered solely from data dependencies. A pure operation that may fail can still change whether effects occur under fail-stop execution.

Dead-result elimination is legal only for operations proven pure and total under the active contract, unless the original failure is explicitly preserved at the same observable point. An unused `DIV 1 0` is still observable because its failure can prevent later effects.

For CI and optimization evidence rules, read `docs/OPTIMIZATION-AND-CI.md` before changing performance-sensitive or validation-sensitive code.

## Effect-attempt work

Completion state belongs to the effect attempt, not the enclosing CARD outcome.

Use the candidate meanings consistently:

```text
NOT_STARTED   = protected effect never began
COMPLETED     = effect reached its defined external completion boundary
ABORTED_CLEAN = effect began, did not complete, and is proven to have produced no externally observable change
PARTIAL       = effect began, did not complete, and some portion became externally observable
UNKNOWN       = completion/observability cannot be established
```

A completed process that exits with status `2` may have `completion_state = COMPLETED` while its enclosing CARD reports `PROCESS_FAILED`.

A buffered/atomic operation that begins but provably publishes no external change before aborting is `ABORTED_CLEAN`, not `NOT_STARTED`, `PARTIAL`, or `UNKNOWN`.

Every effect attempt must record the full set of capabilities required for that attempt, not one representative capability. An attempt must not begin until all required capabilities are granted.

Do not collapse multiple effect attempts into one aggregate partial-effect flag.

## Extension and capability work

An extension profile supplies optional versioned syntax, adapters, effects, or lowering hooks. It does not itself grant execution permission.

For example, `USE QX-NET` and `ALLOW NETWORK`/`DENY NETWORK` operate at different boundaries. Likewise a remote QX-AI effect may require both `AI_MODEL` and `NETWORK` capabilities.

Before implementing an extension with material operational semantics, follow the roadmap's freeze-before-implementation rule. QX-POSIX requires a normative contract before its reference implementation. QX-CUDA requires a versioned normative control contract before launch/memory/tuning controls are implemented.

## Backend work

Backend-specific behavior belongs behind explicit backend or extension boundaries.

Generated target code should remain inspectable where practical.

A backend implements frozen semantics. It does not define them.

A backend must consume the established lower pipeline; it must not become a second Semantic IR → QSOL-CORE compiler with private semantics or bypass the mandatory Core→Vector/Dataflow lowering for scalar/control/effect operations.

Automatic backend selection must trace the selection policy and material tuning identity when those affect the choice.

CUDA backend implementation follows the frozen generic GPU contract. QX-CUDA vendor controls are a separate optional profile and may not be invented inside the CUDA backend phase.

## Serialization work

A format claiming semantic losslessness must round-trip all execution-relevant canonical fields, including:

- qualifiers;
- effect requirements and complete per-effect required-capability sets;
- explicit failure behavior;
- result-determinism and numeric contracts;
- randomness contracts;
- extension/profile identities and versions;
- data, effect, and failure-order constraints.

Do not silently default a missing semantic/enforcement field during transport.

Machine-readable canonical interchange may proceed before the human QSOL grammar is frozen. Human `.qsl` parsing/serialization may not.

## Documentation hierarchy

Read in this order when context is limited:

1. `docs/SPECIFICATION-STATUS.md`
2. `docs/DESIGN-PRINCIPLES.md`
3. `docs/ARCHITECTURE.md`
4. `docs/LANGUAGE-MODEL.md`
5. `docs/SEMANTIC-IR.md`
6. `docs/SEMANTIC-TO-CORE-LOWERING.md`
7. `docs/VECTOR-AND-DATAFLOW.md` when lower IR/backend/optimization work is involved
8. the domain-specific document relevant to the task
9. `ROADMAP.md`

## Change discipline

Do not broaden scope merely because an adjacent improvement is attractive.

If a task targets one phase, leave later-phase work in `ROADMAP.md` unless it is required to make the current phase internally correct.

## Review discipline

For every substantive change, ask:

- Did meaning change?
- Did an effect become implicit?
- Did an effect lose its explicit capability-set association?
- Did authorization move until after an effect began?
- Did an effect attempt omit one of several required capabilities?
- Did determinism, numeric, or randomness guarantees weaken?
- Did provenance weaken or skip one of the mandatory lowering stages?
- Did an extension get mistaken for a capability grant?
- Did an extension leak into core?
- Did a serializer lose `qualifiers{}`, `failure_behavior`, effect requirements, or another semantic/enforcement field?
- Did a human text implementation invent grammar before a normative text-profile freeze?
- Did reordering change failure/effect observability?
- Did dead-result elimination erase a possible failure?
- Did a backend or implementation invent semantics not yet frozen?
- Did Semantic IR → QSOL-CORE lowering lose a qualifier, contract, effect binding, failure behavior, or provenance edge?
- Did Core→Vector/Dataflow lowering lose a contract or provenance edge?
- Did Vector/Dataflow IR drop or bypass control, calls, effects, capabilities, contracts, or scalar semantics?
- Did a trace collapse several effect attempts into one ambiguous state?
- Was effect completion inferred incorrectly from CARD success/failure?
- Was a cleanly aborted begun effect mislabeled as `NOT_STARTED`, `PARTIAL`, or `UNKNOWN`?
- Did QX-POSIX implementation precede its normative contract?
- Did generic GPU/CUDA implementation invent unfrozen accelerator semantics?
- Did QX-CUDA control implementation precede its normative contract?
- Did an optimization alter a result contract?
- Did documentation claim functionality that does not exist?

If any answer is yes, make the change explicit or reject it.
