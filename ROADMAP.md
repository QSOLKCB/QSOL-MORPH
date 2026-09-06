# QSOL-MORPH Roadmap

QSOL-MORPH is being developed specification-first. The project deliberately separates architectural agreement from executable implementation so that later code is judged against an explicit semantic contract rather than allowing implementation accidents to become the specification.

## Development rule

> Meaning is frozen before machinery is optimized.

No phase may silently weaken an invariant established by an earlier frozen phase. Backend-specific convenience does not override semantic preservation, determinism requirements, epistemic distinctions, numeric contracts, capability authorization, failure semantics, execution-path accounting, or traceability.

## PR #1 — Documentation Foundation

**Status:** current

Establish the non-normative architecture and vocabulary before implementation.

Deliverables:

- project architecture;
- human/AI language model;
- JOB → DECK → CARD → VERB/NOUN hierarchy;
- candidate semantic IR;
- candidate reduced core instruction families;
- semantic-to-core lowering boundary;
- vector and dataflow model;
- deterministic execution model;
- provenance and trace model;
- failure and partial-effect model;
- backend and code-morphing model;
- extension-profile model;
- effect-capability and machinery-capability authorization models;
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
- freeze hidden-effect rules and the distinction between external-effect authorization and protected-machinery authorization;
- freeze failure, fail-stop, JOB propagation, per-DECK/per-CARD execution accounting, and effect attempt/non-attempt disclosure rules;
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

- stable JOB/DECK/CARD identifiers;
- source locations;
- typed operands;
- result bindings naming values produced for dependent CARDs;
- values and units;
- qualifiers;
- semantic classes;
- `effect_requirements[]` with stable effect identity/kind and complete `required_capabilities[]` for each protected external effect;
- `machinery_requirements[]` with stable requirement identity, target selector/class, and complete `required_capabilities[]` for protected machinery use without reclassifying machinery selection as an effect;
- result-determinism requirements at JOB, DECK, CARD, or another explicitly frozen owning scope;
- numeric contract identity/parameters at the JOB, DECK, CARD, or other frozen scope where they govern `NUMERIC` execution;
- randomness/reproducibility requirements at their canonical owning scope;
- explicit scoped `failure_behavior` on CARD, DECK, or JOB where the frozen model permits non-default recovery/continuation/compensation behavior;
- dependencies;
- tagged `sequencing_constraints[]` preserving source-order, effect-order, failure-order, and any future frozen sequencing kind without parallel-schema ambiguity;
- `extension_requirements[]` binding each profile to its required version/range and contract identity where applicable;
- deterministic canonical ordering;
- schema validation;
- reference fixtures.

The normative data model must freeze how JOB/DECK/CARD execution contracts compose or refine one another before an executable phase can derive effective scopes. A child scope may not silently weaken a parent requirement.

The canonical model must carry enough information for later executable phases to preserve dependency/result identity and to enforce effect capability, machinery capability, numeric, randomness, failure-order, and determinism rules fail-closed. These fields are part of the semantic input to execution, not backend annotations added after execution begins.

A CARD-level or execution-wide capability union may be derived for preflight, but it must not replace the effect-to-capability-set or machinery-to-capability-set associations needed for correct authorization and traceability.

Only CARDs proven **pure and total** under the active contract may be freely reordered when dependencies permit. A CARD that may fail is semantically observable under fail-stop execution and must preserve ordering against externally observable effects unless an explicit frozen construct permits otherwise.

## PR #4 — Canonical Machine-Readable Serialization

Implement deterministic serialization for the complete canonical data model **without inventing the human QSOL grammar**.

Initial implementation targets:

- JSONL streaming profile;
- canonical JSON representation;
- XML interchange representation.

Every lossless format must round-trip all canonical semantic and enforcement fields, including stable JOB/DECK/CARD identifiers, scoped JOB/DECK/CARD determinism/numeric/randomness contracts, result bindings, qualifiers, effect requirements, machinery requirements and their per-requirement capability sets, explicit failure behavior, `extension_requirements[]`, dependencies, and the complete tagged `sequencing_constraints[]` field. Effect-order/failure-order views may be derived from tagged sequencing entries but must not replace or truncate the canonical field.

The human-readable `.qsl` source profile is explicitly **deferred**. It may not be implemented until a separate normative QSOL text-profile specification freezes lexical grammar, syntax, shorthand/default reconstruction, diagnostics, canonical text rendering, and the source-to-Semantic-IR mapping. Until that freeze, examples of QSOL text remain illustrative only.

A MIDI 2.0 mapping remains an extension profile and must not affect the language core.

## PR #5 — Execution Contract, Trace, Failure, and Provenance Foundation

Implement the minimum execution-contract schema required before any QSOL phase is permitted to execute research programs.

The initial trace contract should bind, where applicable:

- stable aggregate `run_id`, source identity/hash, and canonical Semantic IR identity/hash;
- stable `job_id`, identified `deck_executions[]` for every DECK selected by that JOB run, stable `card_ids[]`, and identified `card_executions[]` recording the actual path/outcome of every CARD in those selected DECKs;
- enclosing `execution_status` and `job_status`, plus per-DECK/per-CARD status/failure context and aggregate `failure_card_id`, failure class, and failure stage when applicable;
- active specification version;
- implementation/MORPH version;
- canonical `effect_requirements[]`, each carrying source CARD ID, declared `effect_id`, effect kind, and the complete `required_capabilities[]` set for that declared protected effect;
- canonical `machinery_requirements[]`, each carrying stable requirement identity, governing source scope, target selector/class, and complete required-capability set;
- `backend_selection_scopes[]`, each identifying a governed scope/source/backend unit plus ordered `selection_decision_ids[]` and the `final_selection_decision_id` when execution proceeds;
- identified `backend_selection_decisions[]`, each carrying its own decision ID, governing selection scope, order index, requested target, selected backend/version/architecture/device, automatic-selection policy/tuning identity where applicable, predecessor decision/fallback-rule identity where applicable, linked machinery-authorization records, and decision status;
- identified `machinery_authorization_records[]` binding the relevant backend selection decision/scope to applicable machinery requirement IDs, complete required/granted/denied capability sets, policy identity/version, and authorization outcome;
- `result_determinism_scopes[]`, each binding scope identity, source provenance, requested guarantee, effective guarantee, any pre-execution transition authority, and backend execution-unit identity where useful;
- `numeric_execution_scopes[]`, each binding scope identity, source provenance, numeric contract identity/hash, material numeric mode, and backend execution-unit identity where useful;
- `randomness_execution_scopes[]`, each binding scope identity, source provenance, requested/effective randomness mode, any pre-execution transition authority, and replay-relevant RNG algorithm/version/seed/stream/partitioning plus backend execution-unit identity where useful;
- scoped `failure_behavior_bindings[]` preserving the source and effective failure policy at each governing JOB/DECK/CARD or other frozen scope, including default fail-stop identity when material and any frozen mapping/transition rule;
- execution-wide required/granted/denied capability summaries plus capability-policy identity/version and capabilities actually used, without treating those summaries as replacements for per-effect or per-machinery authorization records;
- identified `inputs[]`, each binding a stable `input_id` to the exact canonical value, content hash, immutable artifact/version identity, or equivalent frozen identity actually consumed;
- identified `outputs[]`, each binding its own output/result identity, optional result binding, artifact hash/location, semantic class, generic artifact/execution status, class-discriminated `evidence_status?`, producer CARD IDs, governing backend-selection/result-determinism/numeric/randomness scope IDs, applicable exact `generated_artifact_ids[]`, concrete `effect_attempt_ids[]` when effects materially produced/exposed the output, material `external_tool_ids[]`, and any `cache_reuse_record_ids[]` that contributed to that output;
- where present, `evidence_status` must contain a compatible `evidence_class`, status, and any material evidence-transition/rule identity; generic output status must not silently promote TEST/VALIDATION/PROOF class;
- identified `cache_reuse_records[]`, each distinguishing cold execution, verified reuse, unverified cache hit, or frozen equivalent and binding source CARD IDs, material cache identity, reused computation/artifact identity, legality rule, and verification evidence;
- active extension profiles plus resolved extension versions/content identities;
- identified `external_tool_versions[]` for material external tools/services/models/provers/processes, with stable links to the applicable effect attempts and/or identified outputs when one source CARD can invoke more than one concrete tool/version;
- identified `effect_authorization_records[]`, each binding one effect attempt/declaration to its complete required/granted/denied capability sets, capability-policy identity/version, authorization outcome, and authorization decision/order identity before effect begin;
- identified `effect_attempts[]`, each carrying runtime `effect_attempt_id`, canonical `declared_effect_id`, initiating `card_id`, `effect_kind`, complete `required_capabilities[]`, its `effect_authorization_record_id` (or frozen equivalent), sequence identity/order where applicable, individual completion state, reciprocal `observable_output_ids[]` for outputs it materially produced/exposed, and material external-tool IDs where applicable;
- identified `effect_non_attempt_records[]` for declared effects that have no runtime attempt, each carrying `declared_effect_id`, `card_id`, `effect_kind`, an explicit non-attempt reason, and governing control/failure identity where applicable;
- structured execution-failure records where applicable.

Every selected DECK must remain visible in `deck_executions[]`. A DECK prevented from starting by prior fail-stop behavior records an explicit non-started/skipped status or frozen equivalent rather than disappearing.

Every CARD in a selected DECK execution must remain visible in `card_executions[]`. Candidate outcomes include executed success/failure, untaken branch, prior fail-stop, CARD not reached, and explicit frozen skip. `card_ids[]` records identity/membership; it is not proof that a CARD executed.

Declared `effect_requirements[]` are required in addition to runtime attempt accounting. Every declared effect must be accounted for by either one or more `effect_attempts[]` or an explicit `effect_non_attempt_records[]` reason when no attempt object exists. Legitimate reasons include untaken branch, prior fail-stop, CARD not reached, or explicit frozen skip. `BACKEND_OMISSION_DETECTED` (or frozen equivalent) is not a successful non-attempt path: it is evidence that a reachable required effect was omitted and **must produce structured execution/conformance failure**. An effect declaration with neither an attempt nor an explicit non-attempt reason is incomplete provenance when declaration-completeness auditing is required.

Effect authorization is contextual and per attempt. Execution-wide granted/denied capability sets are summaries only. Every identified protected effect attempt must link to an authorization decision proving which policy evaluated that attempt and which complete capability set was granted or denied. A denied authorization may leave an already identified attempt in `NOT_STARTED`, but the effect itself must not begin.

Protected machinery selection and protected machinery authorization remain separate. An automatic target such as `ON BEST` may be resolved first, but all capabilities required by the applicable machinery requirement must be authorized **before protected machinery use begins**. A denied GPU authorization must not launch GPU work or create a fake external-effect attempt. Fallback to another target is legal only under a frozen pre-execution fallback/selection rule and must remain traceable as a new ordered backend-selection decision linked to its denied/predecessor decision rather than overwriting the first selection.

A mutable input locator such as a path, URL, dataset name, or model name is retrieval context, not sufficient provenance by itself. Every material input must have a stable input identity plus an immutable value/content/artifact identity that distinguishes exactly what was consumed.

A single execution-wide backend-selection, result-determinism, numeric, randomness, or failure-behavior scope is valid only when a frozen normalization rule proves that one entry faithfully represents every governed source decision or requirement. CARD-, region-, kernel-, or generated-unit-scoped machinery/contracts/modes/streams must not be collapsed into false global singletons.

Cache reuse must remain provenance-visible even when substitution is legal and effect-free. Cold execution and cache substitution must not produce indistinguishable execution records merely because they yield identical bytes.

Before PR #7 may execute a program, this phase must also define the reference failure contract:

- evaluation yields a success or structured failure, never an implicit sentinel value;
- an unhandled CARD failure stops further CARD execution in the DECK by default;
- an unhandled DECK failure fails the enclosing JOB by default and no later DECK in that JOB starts;
- dependent JOB/DECK comparisons or consumers do not execute against missing or partial failed outputs;
- future continue/retry/recovery/parallel-JOB behavior requires explicit frozen JOB-level semantics;
- pure CARD failure commits no semantic state;
- capability authorization is completed successfully **before every protected external effect begins**;
- every capability required by that specific effect attempt must be granted by the attempt's identified authorization record before the effect begins;
- every capability required by protected machinery must be granted before protected machinery use begins;
- other static/precondition checks should occur before an external effect where practical;
- effects already externally observable before a later failure are not retroactively erased;
- every identified effect attempt must be traceable independently as `NOT_STARTED`, `COMPLETED`, `ABORTED_CLEAN`, `PARTIAL`, or `UNKNOWN` (or frozen equivalents);
- completion-state classification is mutually exclusive and ordered, with known completion taking precedence over broader uncertainty;
- a detected omission of a reachable declared effect is an execution/conformance failure and cannot coexist with a successful enclosing execution result;
- division/modulo by zero and other defined arithmetic-domain errors produce structured failure rather than backend-chosen undefined behavior;
- failure traces identify the run/JOB, every selected DECK, every CARD execution outcome, failure class/stage, per-effect declaration/authorization/attempt/non-attempt accounting, relevant machinery authorization/selection-decision history, and whether any output artifact became observable.

This phase is a gate for PR #7 and every later executable implementation. No executable QSOL path should emit a research result without enough provenance to bind each identified output to the selected stable run/JOB/per-DECK/per-CARD execution, immutable material inputs, epistemic class and compatible evidence status, exact generated target where applicable, scoped backend-selection/determinism/numeric/randomness/failure-behavior context, machinery authorization, cache-reuse path, extension set, concrete material external-tool identities, per-effect authorization/attempt identities, and execution/failure context that produced it.

## PR #6 — Normative QSOL-CORE Operational Specification

Freeze QSOL-CORE semantics **before** implementing the reference machine.

Planned work:

- freeze the initial instruction families and exact instruction inventory;
- define operand, result, type, and state-transition semantics;
- define arithmetic and numeric-contract interaction;
- define result-determinism execution semantics at each supported Core scope, including requested/effective guarantees, permitted transitions, fail-closed behavior, and how instruction evaluation contributes to the scoped guarantee;
- define randomness modes and Core-visible randomness behavior, including `NONE`, seeded execution, external entropy/declared nondeterminism where supported, RNG algorithm/version identity, seed/stream/partitioning semantics, and the failure/transition rules required by the PR #5 contract;
- define how determinism and randomness remain orthogonal and how their scopes compose with numeric contracts;
- define logic semantics, including XOR;
- define comparison semantics;
- define branch/jump/call/return/stop behavior;
- define stack/call-state behavior if present;
- define explicit effect operations and per-effect capability requirements;
- define success/failure propagation into DECK and JOB outcomes;
- define which operations are pure, total, potentially failing, or effectful;
- define sequencing and reordering observability;
- publish conformance fixtures/examples for each instruction, including determinism/randomness satisfaction and rejection cases.

This PR is normative specification work, not an executable machine. The reference implementation may not invent instruction, determinism, randomness, RNG, transition, or failure meaning that is absent from this specification.

## PR #7 — QSOL-CORE Reference Machine

Implement the first executable reduced semantic machine against the frozen PR #6 operational specification and the PR #5 execution-contract foundation.

The reference machine must:

- implement the frozen instruction semantics rather than define them;
- emit the required PR #5 trace including per-DECK/per-CARD execution outcomes;
- preserve result bindings and dependencies;
- obey frozen DECK/JOB failure propagation and per-effect-authorization/attempt/non-attempt behavior;
- require successful authorization of every capability required by each protected effect before that effect begins;
- require successful machinery authorization before any protected machinery used by the reference execution path begins use;
- fail closed when capability, numeric, randomness, or determinism requirements cannot be satisfied;
- pass the frozen QSOL-CORE conformance fixtures.

## PR #8 — Normative Semantic-to-QSOL-CORE Lowering Specification

Freeze the first lowering contract from canonical Semantic IR into QSOL-CORE before any backend implementation.

Planned work:

- define how each supported semantic CARD category maps to QSOL-CORE operations or preserved metadata;
- define JOB / DECK / CARD identity preservation;
- define preservation of result bindings and dependency references;
- define preservation of epistemic classes and evidence boundaries;
- define type/unit validation and the conditions under which higher-level metadata may be erased;
- define preservation/consumption rules for execution-relevant `qualifiers{}`;
- define lowering of explicit `effect_requirements[]`, stable declared `effect_id`, and each effect's complete required-capability set;
- define preservation of `machinery_requirements[]` or their frozen transformation into later MORPH-facing metadata without turning them into effects;
- define preservation of explicit scoped `failure_behavior`;
- define preservation/composition of JOB/DECK/CARD result-determinism, numeric, randomness, extension, and tagged sequencing contracts;
- define deterministic cardinality-aware result-binding preservation/renaming/split/fusion rules and provenance mappings;
- define unsupported-construct/qualifier failure behavior;
- define extension-owned lowering hooks behind resolved versioned contracts;
- publish Semantic IR → QSOL-CORE conformance fixtures and rejection fixtures.

The lowering specification must make it impossible for a backend to invent the meaning of the first pipeline arrow.

## PR #9 — Reference Semantic-to-QSOL-CORE Lowering

Implement the PR #8 lowering specification as an independently testable reference stage.

The reference lowering must:

- consume canonical Semantic IR rather than hand-built QSOL-CORE only;
- produce QSOL-CORE plus preserved result bindings, qualifiers, scoped contracts, effect bindings/IDs, machinery requirements/metadata, failure behavior, metadata, and provenance required by later stages;
- fail closed for unsupported or contract-breaking semantic constructs/qualifiers;
- bind semantic IR identity, canonical `semantic_to_core_spec_version`, canonical `semantic_to_core_implementation_version`, resolved extension identities, resulting QSOL-CORE identity, and cardinality-aware `result_binding_map[]` whenever result identities are preserved or transformed; omission is allowed only under a frozen deterministic identity-map reconstruction rule;
- record `qualifier_lowering_decisions[]`, `result_determinism_lowering_decisions[]`, `numeric_contract_lowering_decisions[]`, `randomness_lowering_decisions[]`, `machinery_requirement_lowering_decisions[]`, and `failure_behavior_lowering_decisions[]` whenever lowering consumes, groups, remaps, normalizes, or otherwise materially transforms those source requirements/policies;
- pass all frozen lowering conformance and rejection fixtures.

No MORPH backend should be considered end-to-end conforming until this first lowering stage is present.

## PR #10 — Normative Full Vector/Dataflow IR Specification

Freeze the target-independent lower computational IR used by **every** MORPH backend path before implementing its reference lowering.

The name reflects its vector/dataflow optimization role, but the IR is not permitted to represent only vectorizable arithmetic. Because it is mandatory in the singular pipeline, it must preserve the full supported QSOL-CORE semantic and contract surface.

Planned concepts:

- abstract vector registers and scalar values;
- vector/scalar load/store, arithmetic, logic, comparison, and data movement;
- result bindings/data identities required by downstream dependencies;
- masks and reductions;
- dependencies and dataflow edges;
- explicit control-flow representation for branch/jump/stop semantics;
- call/return boundaries and frozen call-state semantics;
- explicit effect nodes/regions preserving canonical declared `effect_id`;
- complete required-capability sets and authorization boundaries for each protected effect;
- preserved protected-machinery requirements/metadata required by MORPH selection and authorization;
- tagged source/effect/failure sequencing constraints;
- per-effect-attempt identity/provenance hooks distinct from declared effect identity;
- result-determinism, scoped numeric, randomness, extension, qualifier, and failure-behavior preservation;
- deterministic cardinality-aware lower result-binding mapping rules;
- explicit scope identity needed to map Core execution contracts, machinery requirements, and failure behavior into lower regions/kernels/units;
- fusion legality;
- alias rules;
- parallel partitioning;
- totality/failure classification;
- deterministic numeric-contract enforcement;
- provenance links back to QSOL-CORE and originating semantic CARDs;
- versioned Vector/Dataflow IR schema and conformance fixtures.

Every supported QSOL-CORE operation must either map to a defined IR construct or be preserved through a defined semantics-preserving scalar/control/effect/pass-through construct. Unsupported representation must fail closed.

This PR is normative specification work. The reference lowering and later backends may not invent lower-IR meaning absent from this contract.

## PR #11 — Reference QSOL-CORE-to-Vector/Dataflow Lowering

Implement the PR #10 specification as an independently testable mandatory lowering stage.

The reference lowering must:

- consume conforming QSOL-CORE plus preserved metadata/contracts;
- emit the full semantics-preserving Vector/Dataflow IR;
- preserve result bindings, control, calls, scalar operations, declared effect IDs, per-effect capability sets, machinery requirements/metadata, qualifiers, failure behavior, ordering, determinism, scoped numeric contracts/modes, randomness, extensions, and provenance;
- fail closed when a supported QSOL-CORE operation lacks a legal Vector/Dataflow representation;
- bind `core_ir_hash`, Vector/Dataflow specification identity, lowering implementation identity, `vector_dataflow_ir_hash`, and cardinality-aware `result_binding_map[]` whenever result identities are preserved or transformed; omission is allowed only under a frozen deterministic identity-map reconstruction rule;
- record `core_to_vector_result_determinism_mapping_decisions[]`, `core_to_vector_numeric_contract_mapping_decisions[]`, `core_to_vector_randomness_mapping_decisions[]`, `machinery_requirement_mapping_decisions[]`, and `failure_behavior_mapping_decisions[]` whenever the corresponding Core scopes/requirements/policies split, fuse, rename, group, or otherwise map to different Vector/Dataflow scopes/representations; omission is allowed only under a frozen deterministic identity-scope reconstruction rule that covers that contract family;
- pass scalar-only, result/dependency, control-flow, call, effect/capability, machinery-requirement, mixed vector/scalar, failure-order, and contract-preservation fixtures.

A backend may not bypass this stage for branches, calls, effects, or other non-vector operations merely because they are not optimization candidates.

## PR #12 — Reference MORPH to C

Build the first deliberately boring code-generation backend after both mandatory lowering stages exist:

```text
Canonical Semantic IR
        ↓
Semantic-to-Core Lowering
        ↓
QSOL-CORE
        ↓
Core-to-Vector/Dataflow Lowering
        ↓
Full Vector/Dataflow IR
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
- failure behavior equivalent to the QSOL-CORE reference contract;
- end-to-end comparison from canonical Semantic IR through the reference machine and C result path;
- no backend bypass of the mandatory lower IR for control, calls, effects, or scalar operations.

The C backend inherits the PR #5 trace/failure/authorization gate and must record backend/compiler identity, scoped determinism/numeric/randomness execution information, selection-decision/fallback history where applicable, machinery authorization where applicable, and identified `generated_artifacts[]`. Each generated artifact must bind a stable artifact ID/kind/hash to its `backend_unit_id` and governing `backend_selection_scope_id`, plus the final `backend_selection_decision_id` where selection history has more than one decision, and source CARD/location provenance where material. Applicable outputs must also record the exact `generated_artifact_ids[]` that actually produced or supplied them.

## PR #13 — Morph Optimization Passes

Introduce semantics-preserving transformations such as:

- constant folding under the active type/numeric/failure contract;
- dead-result elimination **only** for operations proven pure and total, unless the original failure is preserved at the same observable point;
- vectorization;
- dataflow fusion;
- temporary-elision;
- legal operation reordering under explicit totality, failure-order, and numeric contracts;
- cache/result reuse only under an explicit legality rule that preserves the active semantic and execution contracts.

No optimization may erase or move an observable failure merely because a computed value is unused. Under fail-stop semantics, an unused potentially failing operation remains observable because its failure can prevent later effects or results.

Ordinary cached result substitution is permitted only for computations proven safe for reuse, conservatively effect-free by default. An effectful CARD may not be satisfied by returning a prior cached value if that would skip a declared effect, capability authorization, effect/failure ordering, or effect-attempt provenance. Effectful reuse requires a separately frozen replay/cache semantic that defines and preserves those boundaries; otherwise the effect executes normally or reuse fails closed.

Actual optimization decisions must be provenance-visible. An `optimization_profile` names requested/configured policy but does not prove which transformations ran. Where optimization is material, `optimization_provenance[]` or an equivalent stable content-bound MORPH-trace reference must bind reference/optimized IR identities, the actual transformation sequence, legality witnesses, relevant vectorization/fusion/memory-placement decisions, and target-context/resource assumptions where applicable.

Every optimization must be testable against the invariant set, both lowering fixture sets, full-IR fixtures, QSOL-CORE reference semantics, and cache/replay legality rules where reuse is involved.

## PR #14 — Normative QX-POSIX Contract

Freeze POSIX-profile semantics **before** implementing adapters or backend support.

Planned work:

- define stdin/stdout/stderr byte and text boundaries;
- define process launch, argument/environment, exit-status, and termination semantics;
- define file open/read/write/append/truncate and observable completion boundaries;
- define environment access and mutation rules;
- define signal semantics where supported;
- define typed-record ↔ byte/text stream conversion and encoding rules;
- define explicit effects, stable declared effect identities, and the complete capability sets required for each operation;
- define failure classes and mutually exclusive effect-attempt completion states, including clean aborts and known-completion precedence;
- define ordering, buffering, flushing, partial-write, and provenance requirements;
- define unsupported-platform behavior;
- publish normative conformance and rejection fixtures.

This PR is specification work. No POSIX implementation may invent behavior absent from this contract.

## PR #15 — QX-POSIX Reference Implementation

Implement POSIX-oriented execution and composition against the frozen PR #14 contract:

- stdin/stdout/stderr;
- process execution;
- exit status;
- files;
- environment access;
- signals where supported;
- typed stream adapters.

External operations remain explicit effects and require authorization of **all** corresponding capabilities before each protected effect begins. POSIX is a composable execution profile, not a mutually exclusive compiler backend: a C-, LLVM-, or other generated program may use the QX-POSIX contract when explicitly enabled and authorized.

The reference implementation must pass the frozen QX-POSIX conformance/rejection fixtures and emit required per-effect authorization and per-effect-attempt provenance linking each runtime attempt to its declared effect ID and any identified outputs.

## PR #16 — LLVM Backend

Add LLVM lowering while retaining the C backend as an independently understandable reference path.

## PR #17 — Normative Generic GPU Execution Contract

Freeze the generic accelerator execution model before binding it to CUDA or another vendor.

Planned concepts:

- host/device residency;
- abstract work decomposition;
- memory classes;
- synchronization boundaries;
- deterministic execution declarations;
- kernel inspection;
- explicit machinery requirements and capability authorization boundaries for protected accelerator use, distinct from external effects;
- external accelerator-related effects, if any, modeled separately through normal effect requirements;
- fail-closed behavior when accelerator authorization is denied;
- frozen rules and identified decision-chain provenance for any authorized fallback from an unavailable/denied selected target;
- failure and effect-attempt completion semantics for actual external effects;
- provenance requirements for device, kernel, launch, machinery authorization, backend-selection decision history, and **scoped** determinism/numeric/randomness behavior;
- conformance/rejection fixtures.

This PR is normative specification work. Vendor backends implement this contract rather than defining generic GPU meaning themselves.

## PR #18 — CUDA Backend

Implement CUDA lowering through the frozen generic GPU contract.

Target user experience:

```text
RUN GRAVITY ON CUDA
```

without requiring ordinary CUDA plumbing in research source.

This phase implements the CUDA machinery/backend only. It must enforce the frozen machinery-authorization boundary before protected CUDA use and emit corresponding scoped selection/authorization provenance. It does **not** invent or implement QX-CUDA vendor-control syntax unless the normative QX-CUDA contract is already frozen.

## PR #19 — Normative QX-CUDA Control Contract

Freeze the optional vendor-specific control profile before implementing explicit CUDA launch, memory, or tuning controls.

Planned work:

- version the QX-CUDA profile contract;
- define allowed launch-geometry controls;
- define memory/shared-memory placement controls;
- define tuning-control semantics and validation;
- define interaction with generic GPU semantics and target-selection qualifiers;
- define determinism/numeric restrictions for vendor controls;
- define failure and unsupported-control behavior;
- define provenance required for each material control, including scoped determinism/numeric/randomness and machinery-authorization consequences where applicable;
- publish conformance and rejection fixtures.

`QX-CUDA` remains an optional source/control extension. Activating the profile does not itself grant GPU or other runtime capabilities.

## PR #20 — QX-CUDA Reference Control Implementation

Implement the frozen PR #19 QX-CUDA control profile against the CUDA backend.

Explicit controls may include launch, memory, and tuning options only as defined by the frozen contract. The implementation must validate controls, preserve determinism/failure/provenance/machinery-authorization requirements, and pass the normative conformance/rejection fixtures.

## PR #21 — Additional Backends

Candidates include:

- Fortran;
- HIP;
- WebAssembly;
- Vulkan Compute;
- OpenCL;
- native QSOL VM.

Backends are added according to research value, not checklist pressure.

## PR #22 — Formalization

Formalize selected QSOL-CORE and QSOL-MORPH properties, potentially using Lean 4.

Targets may include:

- deterministic evaluation for a defined subset;
- semantic preservation for selected Semantic IR → QSOL-CORE lowering rules;
- semantic preservation for selected QSOL-CORE → Vector/Dataflow lowering rules;
- semantic preservation for selected morph passes;
- invariant consistency;
- epistemic-class preservation and class-discriminated evidence-status compatibility;
- canonical serialization properties including stable JOB/DECK/CARD, scoped contract, machinery-requirement, result-binding, and tagged sequencing-constraint preservation;
- immutable input-provenance binding properties for a defined subset;
- aggregate `run_id` plus per-DECK and per-CARD execution-record completeness for multi-DECK JOBs and untaken/skipped paths;
- scoped backend-selection decision-chain, machinery-authorization, result-determinism, numeric-contract/mode, randomness, and failure-behavior provenance properties;
- per-output epistemic/evidence status, execution-scope, exact generated-artifact, concrete effect-attempt, and external-tool binding properties;
- cardinality-aware result-binding-map preservation across both mandatory lowering boundaries;
- Core→Vector/Dataflow determinism/numeric/randomness/machinery/failure contract-scope mapping preservation for a defined subset;
- cache/replay legality and cache-reuse provenance for a defined effect-free subset;
- declared-effect completeness with explicit attempt-or-non-attempt accounting, per-attempt authorization, and declared-effect/runtime-attempt correspondence for a defined subset;
- detected reachable-effect omission implies execution/conformance failure;
- generated-artifact/backend-scope/selection-decision attribution properties;
- external-tool identity and optimization-provenance binding properties for a defined subset;
- QX-POSIX contract properties for a defined subset;
- generic GPU / QX-CUDA contract properties for a defined subset;
- failure-state, JOB propagation, effect authorization, machinery authorization, declared-effect/attempt identity, and ordering properties for a defined subset.

## Deferred normative workstream — QSOL text profile

The human `.qsl` authoring language is intentionally not implemented by PR #4.

Before source parsing or canonical QSOL-text serialization is implemented, a dedicated normative phase must freeze:

- lexical grammar and tokenization;
- source grammar;
- canonical formatting;
- source shorthand/default rules;
- source-to-Semantic-IR mapping;
- diagnostics and unsupported syntax behavior;
- versioning/migration rules;
- conformance and rejection fixtures.

Only after that specification is frozen may a reference parser/formatter/serializer be implemented. Machine-readable canonical interchange can proceed independently using the PR #3 semantic model and PR #4 schemas.

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

An extension may define new syntax, adapters, effects, or capability **requirements** under its versioned contract. Activating an extension never grants a runtime capability by itself, and an extension may not silently redefine frozen core meaning.

## Release philosophy

Early releases should favor frozen, auditable semantic milestones over feature volume.

A release should state exactly which specification, invariants, schemas, lowering contracts, extension versions, and backends it implements.