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
9. bind epistemic class and status to each identified output rather than one execution-wide result label;
10. do not silently weaken CARD, DECK, or JOB failure behavior;
11. require successful authorization of **every** capability required by a protected external effect before that effect begins;
12. preserve the explicit effect → complete capability-set association; do not replace it with an ambiguous CARD-level union;
13. preserve result bindings used by dependent CARDs across canonicalization, serialization, and lowering;
14. trace deterministic result-binding preservation/renaming at **both** mandatory lowering boundaries;
15. treat a potentially failing pure operation as ordering-relevant under fail-stop semantics unless it is proven total;
16. do not dead-eliminate a potentially failing operation merely because its result is unused;
17. preserve stable JOB/DECK/CARD identifiers plus all canonical semantic/enforcement fields, including semantic class, `result`, `qualifiers{}`, extension requirements, and explicit `failure_behavior`, across any serialization claiming semantic losslessness;
18. distinguish backend selection from optional vendor-control profiles (`CUDA` != `QX-CUDA`, POSIX execution != a compiler backend);
19. distinguish extension availability/functionality from runtime capability authorization; activating an extension never grants permission;
20. preserve the explicit Semantic IR → QSOL-CORE lowering boundary; do not let a backend reinterpret rich semantic CARDs privately;
21. preserve execution-relevant qualifiers through Semantic→Core lowering unless a frozen rule explicitly consumes them and records the resulting decision;
22. preserve the complete QSOL-CORE control/effect/contract surface through the mandatory Vector/Dataflow IR;
23. record both mandatory lowering identities/hashes **and their result-binding maps** in provenance: Semantic→Core and Core→Vector/Dataflow;
24. record result-determinism provenance at the CARD/region/kernel or other frozen scope where the requirement is actually valid; do not invent one execution-wide pair unless a frozen normalization proves it represents every source requirement;
25. record scoped numeric contract/mode provenance when different CARDs, regions, or kernels can use different legal numeric behavior;
26. record scoped randomness provenance when different CARDs, regions, or kernels can use different randomness modes, RNG identities, seeds, streams, or partitioning;
27. record automatic-backend selection policy/tuning identity and identified per-effect-attempt states when relevant to provenance;
28. record the complete required-capability set for each effect attempt;
29. distinguish canonical declared `effect_id` from runtime `effect_attempt_id` and trace both;
30. define effect-attempt completion independently from the enclosing CARD outcome;
31. apply completion-state precedence so known `COMPLETED` cannot also be `UNKNOWN`;
32. distinguish a cleanly aborted begun effect from `NOT_STARTED`, `PARTIAL`, and `UNKNOWN`;
33. do not satisfy an effectful CARD from cached prior output if that skips a declared effect or its authorization/ordering/failure/provenance boundary; effectful reuse requires an explicit frozen replay/cache semantic;
34. bind every material runtime input to a stable `input_id` plus the exact canonical value, content hash, immutable artifact/version identity, or equivalent frozen identity actually consumed; a mutable path/URL/name alone is not reproducibility evidence;
35. prefer small, inspectable transformations.

## Vocabulary

Use current project vocabulary consistently:

```text
JOB
DECK
CARD
stable JOB/DECK/CARD ID
VERB
NOUN
result binding
result binding map
identified input
identified output
result-determinism scope
QSOL-CORE
Semantic IR
Semantic-to-Core Lowering
Vector/Dataflow IR
Core-to-Vector/Dataflow Lowering
MORPH
backend
extension profile
extension requirement
capability
effect
effect requirement
declared effect ID
effect attempt ID
numeric contract
numeric execution scope
randomness contract
randomness execution scope
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
- result bindings;
- execution-relevant qualifiers;
- `effect_requirements[]` and each effect's stable `effect_id` plus complete `required_capabilities[]`;
- explicit `failure_behavior`;
- scoped result-determinism, scoped numeric, and scoped randomness contracts;
- extension identities/versions;
- source, effect, and failure ordering;
- CARD / DECK / JOB provenance.

If the lowering preserves or renames result bindings, its provenance must carry an explicit `result_binding_map[]` or use a frozen rule that deterministically reconstructs an identity mapping. Do not expect IR hashes alone to explain name correspondence.

Unsupported semantic constructs or qualifiers fail explicitly. Do not silently drop them, no-op them, default them, or defer their meaning to a backend.

## Vector/Dataflow IR work

Read `docs/VECTOR-AND-DATAFLOW.md` before changing the mandatory lower computational IR.

Because every backend path traverses this IR, it must represent or preserve the full supported QSOL-CORE surface, including:

- scalar and vector data operations;
- control flow;
- calls/returns and call state;
- explicit effects with declared effect identity;
- complete required-capability sets;
- result bindings and qualifiers where still material;
- explicit failure behavior carried from earlier stages where still material;
- failure/totality classification;
- source/effect/failure ordering;
- scoped result-determinism, scoped numeric, scoped randomness, and extension contracts;
- provenance and per-effect-attempt identity.

A non-vectorizable QSOL-CORE operation is not permission to bypass the IR. Use a defined scalar/control/effect/pass-through construct or fail conformance until the IR has one.

The Core→Vector/Dataflow stage is independently provenance-bearing. Trace at least the Core IR hash, Vector/Dataflow specification identity, lowering implementation identity, resulting Vector/Dataflow IR hash, and result-binding map when bindings are preserved or transformed.

## Result-determinism provenance work

Do not assume one requested/effective result-determinism pair governs an entire execution.

When requirements can differ by CARD, region, kernel, or another frozen scope, use scoped entries carrying at least:

```text
scope_kind
scope_id
source_card_ids[]
requested_result_determinism
effective_result_determinism
transition_authorized_by?
backend_unit_id?
```

A single execution-wide result-determinism scope is valid only when a frozen normalization rule proves that one requested/effective pair faithfully represents every source requirement.

A recorded downgrade is evidence, not authorization. If a scope cannot satisfy its requested guarantee and no pre-execution rule authorizes a weaker guarantee, fail closed.

## Numeric provenance work

Do not assume one numeric contract or one material numeric mode governs an entire execution.

When contracts or modes can differ by CARD, region, kernel, or another frozen scope, use scoped entries carrying at least:

```text
scope_kind
scope_id
source_card_ids[]
numeric_contract_id
numeric_contract_hash
material_numeric_mode
backend_unit_id?
```

A single execution-wide numeric scope is valid only when a frozen normalization rule proves that one contract/mode pair governs the whole execution.

## Randomness provenance work

Do not assume one randomness contract, RNG identity, seed, stream, or partitioning rule governs an entire execution.

When randomness requirements can differ by CARD, region, kernel, or another frozen scope, use scoped entries carrying at least:

```text
scope_kind
scope_id
source_card_ids[]
requested_randomness_mode
effective_randomness_mode
transition_authorized_by?
rng_algorithm?
rng_version?
seed?
stream_id?
parallel_partitioning?
backend_unit_id?
```

A single execution-wide randomness scope is valid only when a frozen normalization rule proves that one entry faithfully represents every source requirement. Separate seeded computations with different streams or RNG parameters remain separate scopes.

A recorded randomness transition is evidence, not authorization. If a scope cannot satisfy its requested randomness contract and no pre-execution rule authorizes another mode, fail closed.

## Input provenance work

Do not treat a mutable locator as the identity of a material input.

Each material `inputs[]` entry should conceptually carry at least:

```text
input_id
input_kind
canonical_value?          # inline scalar/record input
content_hash?             # external bytes/artifact content
artifact_id_or_version?
location?
media_or_schema_type?
```

A stable `input_id` plus either a canonical value or immutable content/artifact identity is required to distinguish exactly what was consumed. Paths, URLs, dataset names, model names, and similar locators may aid retrieval, but they do not replace content identity. If the implementation cannot establish the required material input identity, fail replay/provenance validation closed rather than guessing.

## Result provenance work

Do not represent several outputs as plural hashes plus one shared epistemic class or status.

Each output should be independently identified and bind its own provenance, conceptually including:

```text
output_id
result_binding?
artifact_hash
artifact_location?
semantic_class
status
producer_card_ids[]
result_determinism_scope_ids[]
numeric_scope_ids[]
randomness_scope_ids[]
```

TEST, VALIDATION, and PROOF status must remain attached only to the output whose explicit semantic transition supports that status. One validated output must not promote another simulation/test output produced by the same JOB.

## Optimization and cache work

Use the reference semantics first.

A valid optimization must preserve the active semantic/numeric/determinism/randomness/failure-order/authorization contract.

Only operations proven pure and total may be freely reordered solely from data dependencies. A pure operation that may fail can still change whether effects occur under fail-stop execution.

Dead-result elimination is legal only for operations proven pure and total under the active contract, unless the original failure is explicitly preserved at the same observable point. An unused `DIV 1 0` is still observable because its failure can prevent later effects.

Cached value/result substitution is legal only for computations proven safe for reuse under the active contract. Conservatively, ordinary substitution is effect-free by default.

Do not replace an effectful CARD with prior cached output if doing so skips a file write, process launch, network/AI call, clock read, or other declared effect. That would bypass the capability authorization boundary, effect/failure ordering, and per-effect-attempt provenance. Effectful reuse requires an explicit frozen cache/replay semantic that preserves or explicitly defines all of those boundaries. Without such a rule, execute the effect normally or fail closed.

A cached artifact may be used as an explicit declared input or reference when the semantic contract says so; that is not the same as silently satisfying an effectful CARD from cache. When used as input, the cached artifact itself must be bound by immutable input identity/content provenance.

For CI and optimization evidence rules, read `docs/OPTIMIZATION-AND-CI.md` before changing performance-sensitive or validation-sensitive code.

## Effect-attempt work

Completion state belongs to the effect attempt, not the enclosing CARD outcome.

Use this precedence:

```text
1. NOT_STARTED if the protected effect never began.
2. COMPLETED if the effect reached its defined completion boundary.
3. If begun and known incomplete:
   ABORTED_CLEAN if no external change occurred;
   PARTIAL if some incomplete portion became observable;
   UNKNOWN if clean-vs-partial cannot be established.
4. UNKNOWN if completion itself cannot be established.
```

Known `COMPLETED` takes precedence over uncertainty about broader external consequences. A completed process that exits with status `2` may have `completion_state = COMPLETED` while its enclosing CARD reports `PROCESS_FAILED`.

A buffered/atomic operation that begins but provably publishes no external change before aborting is `ABORTED_CLEAN`, not `NOT_STARTED`, `PARTIAL`, or `UNKNOWN`.

Every runtime effect attempt must record:

```text
effect_attempt_id
declared_effect_id
card_id
effect_kind
required_capabilities[]
completion_state
```

`declared_effect_id` references canonical `EffectRequirement.effect_id`; `effect_attempt_id` identifies this concrete attempt. Do not conflate them.

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

A format claiming semantic losslessness must round-trip all execution-, dependency-, and reference-relevant canonical fields, including:

- stable JOB/DECK/CARD identifiers;
- result bindings;
- semantic classes;
- qualifiers;
- effect requirements and complete per-effect required-capability sets;
- explicit failure behavior;
- scoped result-determinism and numeric contracts;
- randomness contracts;
- extension/profile identities and versions;
- data, effect, and failure-order constraints.

Do not silently default, discard, or renumber a stable identity or missing semantic/enforcement field during transport.

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
- Did a stable JOB/DECK/CARD identity disappear, change, or get renumbered without an explicit migration?
- Did a semantic class disappear or become detached from its CARD/output?
- Did an extension requirement/version disappear before an extension-owned construct was interpreted?
- Did a result binding disappear or change identity?
- Did either lowering lose the result-binding map needed to relate names across IRs?
- Did an effect become implicit?
- Did an effect lose its explicit capability-set association?
- Did a runtime attempt lose its link to the canonical declared effect ID?
- Did authorization move until after an effect began?
- Did an effect attempt omit one of several required capabilities?
- Did result determinism, numeric, or randomness guarantees weaken?
- Did scoped result-determinism provenance get collapsed into one false global requested/effective pair?
- Did scoped numeric provenance get collapsed into one false global contract/mode?
- Did scoped randomness provenance get collapsed into one false global RNG/mode/stream?
- Did an output lose the randomness-scope references that identify the RNG configuration which governed it?
- Did a material input retain only a mutable path/URL/name without the exact canonical value, content hash, or immutable artifact/version identity consumed?
- Did several outputs get collapsed under one semantic class or evidence status?
- Did provenance weaken or skip one of the mandatory lowering stages?
- Did an extension get mistaken for a capability grant?
- Did an extension leak into core?
- Did a serializer lose a stable JOB/DECK/CARD ID, `result`, semantic class, `qualifiers{}`, `failure_behavior`, extension requirements, effect requirements, or another semantic/enforcement field?
- Did a human text implementation invent grammar before a normative text-profile freeze?
- Did reordering change failure/effect observability?
- Did dead-result elimination erase a possible failure?
- Did cache reuse skip an effect, capability check, effect ordering edge, failure, or effect-attempt record?
- Did a backend or implementation invent semantics not yet frozen?
- Did Semantic IR → QSOL-CORE lowering lose a result binding, qualifier, contract, effect binding, failure behavior, or provenance edge?
- Did Core→Vector/Dataflow lowering lose a contract, binding map, or provenance edge?
- Did Vector/Dataflow IR drop or bypass control, calls, effects, capabilities, contracts, or scalar semantics?
- Did a trace collapse several effect attempts into one ambiguous state?
- Could the same known-completed attempt be labeled both `COMPLETED` and `UNKNOWN`?
- Was a cleanly aborted begun effect mislabeled as `NOT_STARTED`, `PARTIAL`, or `UNKNOWN`?
- Did QX-POSIX implementation precede its normative contract?
- Did generic GPU/CUDA implementation invent unfrozen accelerator semantics?
- Did QX-CUDA control implementation precede its normative contract?
- Did an optimization alter a result contract?
- Did documentation claim functionality that does not exist?

If any answer is yes, make the change explicit or reject it.
