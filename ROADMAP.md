# QSOL-MORPH Roadmap

QSOL-MORPH is being developed specification-first. The project deliberately separates architectural agreement from executable implementation so that later code is judged against an explicit semantic contract rather than allowing implementation accidents to become the specification.

## Development rule

> Meaning is frozen before machinery is optimized.

No phase may silently weaken an invariant established by an earlier frozen phase. Backend-specific convenience does not override semantic preservation, determinism requirements, epistemic distinctions, numeric contracts, capability authorization, failure semantics, concrete execution accounting, or traceability.

## PR #1 — Documentation Foundation

**Status:** current

Establish the non-normative architecture and vocabulary before implementation.

Deliverables:

- project architecture;
- human/AI language model;
- JOB → DECK → CARD → VERB/NOUN hierarchy;
- candidate Semantic IR;
- semantic-to-core lowering boundary;
- full semantics-preserving Vector/Dataflow model;
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
- freeze concrete execution identity as distinct from canonical JOB/DECK/CARD identity;
- add a machine-readable invariant registry;
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
- source locations and canonical containment/order;
- typed operands;
- result bindings naming values produced for dependent CARDs;
- values and units;
- qualifiers;
- semantic classes;
- `effect_requirements[]` with stable effect identity/kind and complete `required_capabilities[]` for each protected external effect;
- `machinery_requirements[]` with stable requirement identity, target selector/class, and complete `required_capabilities[]` for protected machinery use without reclassifying machinery selection as an effect;
- result-determinism requirements at JOB, DECK, CARD, or another explicitly frozen owning scope;
- numeric contract identity/parameters at the scope where they govern `NUMERIC` execution;
- randomness/reproducibility requirements at their canonical owning scope;
- explicit scoped `failure_behavior` on CARD, DECK, or JOB where the frozen model permits non-default recovery/continuation/compensation behavior;
- dependencies;
- tagged `sequencing_constraints[]` preserving source-order, effect-order, failure-order, and any future frozen sequencing kind;
- `extension_requirements[]` binding each profile to its required version/range and contract identity where applicable;
- deterministic canonical ordering;
- schema validation;
- reference fixtures.

The normative data model must freeze how JOB/DECK/CARD execution contracts compose or refine one another before an executable phase can derive effective scopes. A child scope may not silently weaken a parent requirement.

Only CARDs proven **pure and total** under the active contract may be freely reordered when dependencies permit. A CARD that may fail is semantically observable under fail-stop execution and must preserve ordering against externally observable effects unless an explicit frozen construct permits otherwise.

## PR #4 — Canonical Machine-Readable Serialization

Implement deterministic serialization for the complete canonical data model **without inventing the human QSOL grammar**.

Initial targets:

- JSONL streaming profile;
- canonical JSON representation;
- XML interchange representation.

Every lossless format must round-trip all canonical semantic and enforcement fields, including stable JOB/DECK/CARD identities and containment/order, scoped execution contracts, result bindings, qualifiers, effect requirements, machinery requirements, explicit failure behavior, extension requirements, dependencies, and complete tagged sequencing constraints.

The human-readable `.qsl` source profile is explicitly **deferred** until a separate normative text-profile specification freezes lexical grammar, syntax, shorthand/default reconstruction, diagnostics, canonical rendering, and source-to-Semantic-IR mapping.

## PR #5 — Execution Contract, Trace, Failure, and Provenance Foundation

Implement the minimum execution-contract schema required before any QSOL phase is permitted to execute research programs.

This phase is an explicit gate for PR #7 and every later executable implementation. Ledger definitions and conditional validation requirements follow [Trace and Provenance](docs/TRACE-AND-PROVENANCE.md); summaries below are not alternative weaker schemas.

### Aggregate execution identity

The trace contract must bind:

- stable aggregate `run_id`;
- explicit input representation kind plus its content-bound representation identity;
- source identity/hash and canonical Semantic IR identity/hash when that lineage actually exists;
- stable `job_id`, identified `deck_executions[]`, stable canonical CARD membership, and `card_executions[]` when Semantic execution structure exists;
- identified `operation_executions[]` for direct QSOL-CORE or another frozen lower-representation entry instead of fabricated Semantic CARD executions;
- `execution_status` and, when applicable, `job_status`;
- identified `control_decisions[]` and `failure_records[]`.

`card_id` identifies canonical Semantic meaning when that lineage exists. `card_execution_id` identifies one concrete Semantic CARD execution. `operation_execution_id` identifies one concrete execution of a lower-representation operation. Loops, retries, calls, repeated DECK execution, or repeated Core operation execution may create several concrete execution IDs for one canonical subject, and the execution contract must preserve that distinction. A lower-entry run must not synthesize JOB/DECK/CARD identities merely to satisfy this gate.

### Failure identity

Every `failure_records[]` entry must carry:

```text
failure_record_id
failing_scope_kind
failing_scope_id
failure_behavior_binding_ids[]
result_determinism_scope_ids[]
numeric_scope_ids[]
randomness_scope_ids[]
effect_accounting_failure_record_ids[]?
failure_class
failure_stage
failure_card_id?
failure_card_execution_id?
operation_execution_id?
deck_execution_id?
sequence_index?
backend_detail?
```

`failing_scope_kind` plus `failing_scope_id` is always present and is the authoritative typed identity of the failure location.

`failure_behavior_binding_ids[]` resolves to the exact stable policy bindings active for this failure and its propagation/handling, including the applicable frozen default fail-stop binding. A resulting retry/skip path or generic scope match cannot substitute for that relation. Rejected requested policies are not effective handling policies; pre-CARD/lower-entry rejections retain the actual setup/rejection-handling binding. Each failure record also carries the complete applicable `result_determinism_scope_ids[]`, `numeric_scope_ids[]`, and `randomness_scope_ids[]`, derived independently from its failing scope, concrete execution context where applicable, and validated lowering/contract mappings. Those IDs resolve to the retained execution-contract ledgers; an empty array means that no scope from that family applies, not that attribution was omitted. Selective omission or substitution with a generic scope ID fails the PR #5 gate.

When a CARD's unhandled failure caused the record, `failure_card_id` and `failure_card_execution_id` are required and must resolve consistently through `card_executions[]`.

When failure occurs before any CARD execution or in a legitimate lower-entry operation without Semantic lineage, such as JOB-scoped contract rejection, DECK setup failure, direct Core operation failure, lowering failure, or protected-machinery denial before CARD use, the trace must **not fabricate a CARD identity**. The typed failing scope and, where applicable, `operation_execution_id` remain authoritative and the CARD-specific fields are absent.

Failure traces retain `failure_behavior_bindings[]`, `backend_selection_scopes[]`, and `backend_selection_decisions[]` alongside machinery authorization/use ledgers and `effect_accounting_failure_records[]`, including denied candidates, fallback predecessors, and exact declaration/subject accounting failures. Standalone failure manifests preserve the complete transitive reference closure, inline or through retrievable content-bound records. Dangling selection, policy, requirement, rule, evidence, effect-accounting, or output references fail provenance validation.

### Declared effects and protected machinery

The gate must include representation-qualified canonical `effect_requirements[]` using the shared trace shape:

```text
effect_requirements[]:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
    declared_effect_id
    card_id?
    operation_id?
    effect_kind
    required_capabilities[]
```

Semantic declarations resolve in the hash-bound Semantic IR and require the owning CARD identity. Direct QSOL-CORE declarations resolve in the hash-bound Core IR and use the actual Core operation identity without fabricating a CARD. Conditional CARD fields on a lower declaration are retained lineage only and must be independently verifiable through traversed provenance.

The gate also includes:

- canonical `machinery_requirements[]`, each carrying stable requirement identity, complete ordered absolute owning `owner_scope_path[]`, target selector/class, and complete required-capability set;
- execution-wide capability summaries only as summaries, never as replacements for contextual authorization records.

### Backend-selection and protected-machinery provenance

Require:

- `backend_selection_scopes[]`, each with stable `backend_selection_scope_id`, fully qualified `governed_scope_ref` carrying representation identity plus complete representation-relative `owner_scope_path[]`, source/backend-unit provenance, ordered decision IDs, and final decision ID when execution proceeds;
- `backend_selection_decisions[]`, each with stable decision ID, requested target, selected backend/version plus conditional content-bound `selected_backend_implementation_identity`, architecture/device, automatic-selection policy/tuning identity where applicable, predecessor/fallback-rule identity plus subject-bound `fallback_evidence_id` where fallback applies, linked machinery authorization, order, and status;
- `machinery_authorization_records[]` with stable authorization identity, governing selection scope/decision, absolute-owner-path-qualified machinery requirement references, complete required/granted/denied capability sets, policy identity/version, authorization outcome, and authorization sequence index;
- `machinery_use_records[]` with stable use identity, governing selection scope/decision/backend unit, nonempty representation-qualified `execution_subject_refs[]` for execution-governed work, conditional verified Semantic `source_card_ids[]` / `card_execution_ids[]` projections, exact `generated_artifact_ids[]` executed where applicable, authorization IDs, protected-use start index, exact output IDs, and optional stop index.

For every backend-selection decision whose status is final/executable, `selected_backend_implementation_identity` is mandatory whenever the backend implementation can affect execution semantics, numeric results, failure behavior, device interaction, or produced results. It must immutably content-bind the exact implementation that actually executes the governed work, including reference/interpreted runtimes, accelerator backends, drivers/runtime stacks, or another implementation with no generated artifact/toolchain invocation. A backend name, mutable tag/channel, device label, or ambiguous version is insufficient. `selected_backend_version` may satisfy this identity requirement only when the frozen backend contract proves that the recorded version is immutable and uniquely determines the executed implementation.

`execution_subject_refs[]` is the canonical concrete participant relation for protected machinery use and uses the shared `{ representation_kind, representation_identity, owner_scope_path[], subject_kind, subject_id, execution_id }` shape. A Semantic CARD use resolves through `card_executions[]`; a direct QSOL-CORE use resolves through `operation_executions[]` and the hash-bound Core operation. Repeated launches under one scope/decision must not collapse retries or iterations. CARD arrays are present only as verified Semantic-lineage projections of the CARD-backed subset and must never be invented for Core entry.

Genuine pre-execution RUN/DECK setup may have an empty `execution_subject_refs[]` only with `initiating_scope_ref`, a typed reference to the actual initiating RUN or DECK_EXECUTION resolving to `run_id` or `deck_execution_id`. This setup exception is not a substitute for a real Core operation execution subject.

Authorization and protected use share one frozen monotonic event-order domain. Every successful authorization required for a protected use must satisfy:

```text
authorization_sequence_index < protected_use_start_sequence_index
```

Denied machinery has no protected-use start record.

Fallback from a denied target is legal only under a frozen pre-execution rule plus passing subject-bound fallback evidence for the exact predecessor/fallback decision and evaluated context. `fallback_rule_id` resolves to the accepted frozen rule and `fallback_evidence_id` resolves to `validation_evidence[]`; both must be validated before the fallback selection is applied, with `validation_sequence_index < application_sequence_index` in the shared order domain. Missing, stale, wrong-kind, context-mismatched, unverifiable, or late fallback evidence fails closed. The fallback remains a new ordered selection decision rather than overwriting the denied decision.

### Execution-contract scopes and resolvable authority

Require stable type-specific record keys:

- `result_determinism_scopes[]` with `result_determinism_scope_id` and fully qualified `governed_scope_ref`;
- `numeric_execution_scopes[]` with `numeric_scope_id` and fully qualified `governed_scope_ref`;
- `randomness_execution_scopes[]` with `randomness_scope_id` and fully qualified `governed_scope_ref`;
- `failure_behavior_bindings[]` with stable `failure_behavior_binding_id`, fully qualified `governed_scope_ref`, source provenance, requested/effective failure policy, and material mapping/transition identity.

Every `governed_scope_ref` carries representation identity plus the complete representation-relative `owner_scope_path[]`, including every ancestor needed to distinguish reused JOB/DECK/CARD/region/kernel IDs. Stable ledger IDs and source CARD summaries do not establish canonical ownership. A single execution-wide scope is legal only when a frozen normalization proves it faithfully represents every governed source requirement.

The gate includes `rule_records[]` and `validation_evidence[]` using the complete [shared reference schemas](docs/TRACE-AND-PROVENANCE.md#referenced-rules-and-validation-evidence). Rule records bind accepted source/specification or policy authority, version/content identity, rule kind, and verifiable definition. Evidence records bind the exact typed subject, rule, evaluated context, verifier identity, outcome, content, and validation/application ordering. Unknown references or producer success labels alone are not valid evidence.

Whenever requested and effective result-determinism or randomness contracts differ, `transition_authorized_by` must resolve to a `CONTRACT_TRANSITION` rule and `transition_evidence_id` to passing evidence for that exact execution-scope record and requested/effective pair. Whenever `failure_behavior_bindings[]` changes `requested_failure_behavior_id` to a different `effective_failure_behavior_id`, `mapping_or_transition_rule_id` must likewise resolve to an accepted `CONTRACT_TRANSITION` rule and `transition_evidence_id` to passing evidence for that exact `failure_behavior_binding_id` and requested/effective policy pair. Verify every applicable authority/evidence pair before effective-contract or failure-policy activation/use; the shared order domain requires `validation_sequence_index < application_sequence_index`. Missing, stale, wrong-kind, context-mismatched, unverifiable, or late authority/evidence fails closed. Optional fields may be absent only when no semantic transition occurs, not for an undocumented downgrade, continuation, retry, or compensation change.

For `randomness_execution_scopes[]`, replay/audit-relevant fields include requested/effective mode, transition authority/evidence, RNG algorithm/version, seed, stream identity, parallel partitioning, backend unit, and where applicable:

```text
entropy_effect_attempt_ids[]
entropy_input_ids[]
```

When `effective_randomness_mode = EXTERNAL-ENTROPY`, the scope must identify the exact authorized protected `RANDOM` acquisition attempt(s) that supplied entropy. Where the entropy value is a material runtime input, it must also identify the immutable entropy input record(s). A randomness mode or source CARD ID alone is not sufficient attribution.

### Inputs and outputs

Require identified immutable `inputs[]`, each binding stable `input_id` to the canonical value, content hash, immutable artifact/version identity, or frozen equivalent actually consumed. For any input consumed by a runtime CARD/Core/lower-operation invocation, `consumer_execution_refs[]` is nonempty and names every exact concrete consumer using the shared representation-qualified execution-subject shape; verified Semantic CARD projections may additionally appear in `consumer_card_execution_ids[]`. Effect-acquired values retain `effect_attempt_ids[]`, and concrete runtime consumers reciprocally list the input in `card_executions[].input_ids[]` or `operation_executions[].input_ids[]`. Genuine RUN/DECK setup may instead use typed `consumer_scope_refs[]` for that setup consumption.

Build-only inputs are different. A prebuilt library, header, startup file, sysroot, object, or other material dependency consumed only by compilation/linking may have an empty `consumer_execution_refs[]` because no runtime CARD/Core/lower operation consumed it. Such an input must instead be referenced by the actual consuming `toolchain_invocations[].input_ids[]` record(s), and it must not fabricate CARD/Core/lower-operation consumers merely to satisfy the runtime-consumer schema. If the same identified input is consumed both during build and at runtime, both relations are recorded. These direct consumption relations remain required for failed/output-free runtime invocations, repeated acquisitions, and build steps whose consumed bytes affect generated artifacts; canonical CARD summaries or output-level `input_ids[]` cannot replace them.

Require identified `outputs[]`, each carrying at least:

```text
output_id
result_binding_ref?:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
    binding_id
artifact_hash
artifact_location?
semantic_class
epistemic_class_binding_ids[]
status
evidence_status?
producer_execution_refs[]
producer_card_ids[]?
producer_card_execution_ids[]?
input_ids[]
effect_attempt_ids[]?
external_tool_ids[]
backend_selection_scope_ids[]
generated_artifact_ids[]?
machinery_use_record_ids[]
result_determinism_scope_ids[]
numeric_scope_ids[]
randomness_scope_ids[]
failure_behavior_binding_ids[]
cache_reuse_record_ids[]?
```

`result_binding_ref` is conditionally mandatory: whenever the output has a named result-binding identity in the entered, producer, Core, Vector/Dataflow, or another retained representation, the record must carry the representation kind/content identity, complete owner path, and local binding ID and resolve through every applicable cardinality-aware `result_binding_map[]` in its lineage. Omission is permitted only when independent inspection of the hash-bound producer/entered representations and mapping chain establishes that the output genuinely has no result-binding identity. A producer may not sever a real binding merely by omitting the field. A bare binding name is never an acceptable PR #5 result identity, including for fused producers or sibling scopes that reuse the same local name.

`producer_execution_refs[]` is the canonical nonempty concrete producer relation and uses the shared representation-qualified execution-subject shape. Semantic producers resolve through `card_executions[]`; direct QSOL-CORE producers resolve through `operation_executions[]` and the hash-bound Core representation. Local CARD/operation IDs or output-array position cannot substitute for this relation.

`producer_card_ids[]` and `producer_card_execution_ids[]` are conditional retained-lineage projections. When verified Semantic lineage exists they agree exactly with the Semantic CARD-backed subset of `producer_execution_refs[]` and resolve through `card_executions[]`. On a legitimate direct Core run without Semantic lineage they are absent rather than fabricated or used as empty stand-ins for the actual Core producer.

`epistemic_class_binding_ids[]` is always explicit. **Before interpreting the producer-supplied `semantic_class` label**, independently derive the complete applicable representation-qualified class-binding set from `producer_execution_refs[]`, the entered representation, and every traversed class-preservation/mapping relation. Require the recorded IDs to equal that complete duplicate-free set for every output, including an output labeled `UNCLASSIFIED`; the label never controls whether derivation runs. If the derived set is nonempty, `semantic_class` must be the exact class justified by that complete set under the frozen class-preservation/composition rules, with every binding resolvable to the producer/representation lineage. Only when the independently derived set is empty may the output be `UNCLASSIFIED` (or the frozen no-claim equivalent), record an empty binding array, and omit `evidence_status`. Clearing a retained TEST/VALIDATION/PROOF binding by asserting `UNCLASSIFIED` is invalid; no implicit declassification escape hatch exists.

`input_ids[]` identifies the exact immutable inputs materially contributing to that output. Execution-wide input availability is not a substitute for per-output attribution.

`external_tool_ids[]` is mandatory on every output. Use an explicit empty array only when no material external tool supplied or materially affected that output. Every listed tool must resolve to `external_tool_versions[]` and reciprocally list the output in its `output_ids[]`; when a material model, prover, process, service, or other external tool contributed, omission of that tool or of the array is incomplete provenance and fails the PR #5 gate. Producer execution identity alone cannot substitute for this concrete output/tool join.

`machinery_use_record_ids[]` identifies the exact protected-use occurrence(s) that produced or materially supplied the output and reciprocates `machinery_use_records[].output_ids[]`. A shared execution subject, backend-selection scope, generated artifact, or backend unit cannot replace this occurrence-level join when several protected launches occur.

`backend_selection_scope_ids[]` is a normative duplicate-free exact-set attribution. Independently derive every applicable backend-selection scope from the concrete `producer_execution_refs[]`, their representation-qualified governed scopes, the actual execution path (including interpreted/reference execution with no generated artifact or protected-machinery record), every final executable selection decision, and any validated lowering/selection relation needed to associate those producers with machinery. Then require:

```text
set(backend_selection_scope_ids[]) == applicable_backend_selection_scope_ids(output)
```

The array is empty only when the independently derived applicable set is empty. Extra unrelated scopes fail just as missing producer scopes do, and generated-artifact/machinery-use records are supporting attribution rather than the sole source of scope derivation.

The result-determinism, numeric, randomness, and failure-behavior arrays are likewise normative duplicate-free exact-set attributions. For each output, independently derive the complete materially governing record sets from `producer_execution_refs[]`, their representation-qualified containment, retained Semantic JOB/DECK containment where it exists, the canonical owner-qualified contracts, and every material lowering/mapping or frozen deterministic identity-scope reconstruction needed to reach the actual producer/backend units. Require:

```text
set(result_determinism_scope_ids[]) == applicable_result_determinism_scope_ids(output)
set(numeric_scope_ids[]) == applicable_numeric_scope_ids(output)
set(randomness_scope_ids[]) == applicable_randomness_scope_ids(output)
set(failure_behavior_binding_ids[]) == applicable_failure_behavior_binding_ids(output)
```

Each array is empty only when its independently derived applicable set is empty. Every supplied ID must resolve to the correct ledger record and actually govern a material producer path; omitted stricter parent/mapped scopes and unrelated extras both fail the PR #5 gate. Producer-supplied arrays never define their own applicability.

`failure_behavior_binding_ids[]` resolves to stable `failure_behavior_binding_id` records. A generic computation scope ID is not sufficient to identify which requested/effective failure policy governed the producer path.

For every evidence-bearing `semantic_class` (`TEST`, `VALIDATION`, `PROOF`, or a frozen equivalent requiring evidence verification), `evidence_status` is mandatory and both `evidence_rule_id` and `evidence_validation_id` are mandatory. Generic output status is only an execution/artifact state and can never stand in for research evidence.

For a class-preserving evidence-bearing output, `evidence_rule_id` must resolve to an accepted versioned/content-bound `EVIDENCE_STATUS` rule for that class, and `evidence_validation_id` must resolve to passing subject-bound `validation_evidence[]` for this exact output. Its evaluated context binds the artifact hash, exact `epistemic_class_binding_ids[]`, concrete producer executions, material inputs/tools/evidence identities, requested evidence status, applicable proposition/test/validation/proof subject, and publication event. The class-specific substantive evidence must be retrievable, hash-verifiable, checked by the accepted verifier, and validated before publication; preserving `PROOF` from an upstream binding plus reporting operational success is not sufficient.

For every non-class-preserving epistemic transition, both IDs remain mandatory: `evidence_rule_id` must resolve to accepted content-bound `EPISTEMIC_TRANSITION` authority, and `evidence_validation_id` must resolve to passing subject-bound evidence for this exact output, artifact hash, source binding/class-to-target-class transition, concrete producers, contributing evidence/inputs, requested evidence class/status, and claim-publication context. That evidence must be validated before the stronger or different claim is published; missing, stale, wrong-kind, failed, context-mismatched, unverifiable, or late evidence rejects the transition.

### Generated artifacts, optimization, tools, and cache reuse

Require:

- identified `generated_artifacts[]` linked to backend unit, backend-selection scope, and mandatory exact production `backend_selection_decision_id`, with optimization links, one `direct_producer_toolchain_invocation_id`, and ordered `toolchain_invocation_chain_ids[]` where generated bytes are involved;
- identified `toolchain_invocations[]` carrying stable invocation ID/order, invocation kind, immutable/versioned material tool identity, target/ABI context, exact flags/configuration, exact ordered duplicate-preserving typed `argument_vector[]`, explicit `input_ir_hashes[]`, immutable general `input_ids[]` for material non-generated dependencies, direct generated-artifact inputs/outputs, backend unit, and backend-selection scope where applicable;
- identified `optimization_provenance[]` recording reference/optimized IR identity, actual transformation sequence, legality evidence, target context, and reciprocal generated-artifact links;
- identified `external_tool_versions[]` with stable links to applicable effect attempts and/or outputs plus immutable/versioned material identity, or an explicit identity-unavailable status that weakens replay/evidence claims;
- identified `cache_reuse_records[]` distinguishing cold execution, verified reuse, unverified hit, or frozen equivalent, with nonempty representation-qualified current `execution_subject_refs[]`, material cache identity, legality rule, reused computation/artifact identity, verification evidence, and reciprocal cache-reuse record IDs on the applicable CARD/operation execution ledgers;
- per-output cache-reuse links where applicable.

A generated artifact's production decision must resolve in its recorded selection scope and match its target context. A rejected candidate's artifact must not be attributed to the final fallback decision merely because the two share one scope. Artifact existence does not authorize machinery use.

Toolchain `argument_vector[]` preserves the exact ordered, duplicate-preserving command-line occurrences with typed literal/input/output/generated-artifact references. Positional flags, repeated libraries or inputs, grouping delimiters, and options such as whole-archive placement must not be reconstructed from unordered summary arrays or deduplicated inventories.

Toolchain `input_ids[]` bind the immutable bytes of prebuilt objects, libraries, headers, startup files, sysroots, and implicit dependencies not generated in this run. Mutable locators or flags alone are insufficient. The array is empty only when no such material inputs were consumed; composite inputs content-bind the complete material dependency set under a frozen representation. Missing material dependency identity invalidates complete/reproducible build provenance. These build-input references are the direct consumer relation for build-only inputs and do not require or permit fabricated runtime `consumer_execution_refs[]`.

Toolchain `input_ir_hashes[]` is always explicit: it is nonempty with the exact direct content hash(es) whenever the invocation consumes IR, including ordinary non-optimized code generation, and empty only when that invocation consumes no IR. Tool identity, flags, target, backend unit, or output artifact cannot substitute for this content-bound direct IR edge.

Toolchain direct edges and ancestry have different meanings. `input_generated_artifact_ids[]` / `output_generated_artifact_ids[]` record what an invocation directly consumed/emitted. A generated artifact's `direct_producer_toolchain_invocation_id` must point to the invocation that directly emitted it. `toolchain_invocation_chain_ids[]` records ordered transitive build ancestry and must not force every ancestor to claim the final artifact as a direct output.

Run-wide compiler/tool version lists are summaries only. They cannot substitute for the exact direct producer plus ordered material toolchain ancestry of one generated artifact.

Every runtime `cache_reuse_records[]` entry must identify the exact current invocation(s) it governs through nonempty representation-qualified `execution_subject_refs[]`, including the concrete direct-Core `operation_execution_id` when Core is the entered representation. `card_ids[]` / `card_execution_ids[]`, when retained by the shared schema, are conditional verified Semantic projections only. The corresponding `card_executions[]` and `operation_executions[]` records reciprocally list their applicable cache-reuse record IDs, so repeated executions of one canonical CARD/operation cannot be conflated and direct Core reuse never requires fabricated CARD ancestry.

For `classification = VERIFIED_REUSE`, require `legality_rule_id` resolving to the applicable `CACHE_SUBSTITUTION` rule and `verification_evidence_id` resolving to passing evidence for the exact reuse record, checked cache identity/artifact, and current inputs/contracts/context before substitution. A label or matching hash alone is insufficient. `UNVERIFIED_HIT` cannot satisfy an execution subject: verify successfully before reuse, execute cold, or fail closed.

Ordinary cache substitution is effect-free by default. Effectful reuse requires that the referenced rule is the separately frozen replay/cache semantic preserving declared effects, contextual authorization, source/effect/failure ordering, attempt provenance, output attribution, and observable external state. A generic cache rule is not enough.

### Per-effect authorization and execution-instance accounting

Every protected effect attempt requires an identified authorization record using the shared declaration and execution-subject references:

```text
effect_authorization_records[]:
    effect_authorization_record_id
    effect_attempt_id
    effect_requirement_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        declared_effect_id
    execution_subject_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    card_id?
    card_execution_id?
    required_capabilities[]
    granted_capabilities[]
    denied_capabilities[]
    capability_policy_id
    capability_policy_version
    authorization_status
    authorization_sequence_index?
```

Every runtime attempt requires:

```text
effect_attempts[]:
    effect_attempt_id
    effect_requirement_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        declared_effect_id
    execution_subject_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    card_id?
    card_execution_id?
    effect_kind
    required_capabilities[]
    effect_authorization_record_id
    sequence_index
    effect_begin_sequence_index?
    effect_end_sequence_index?
    completion_state
    acquired_input_ids[]
    observable_output_ids[]
    external_tool_ids[]
```

`effect_requirement_ref` resolves to the exact declaration in the representation that owns it. `execution_subject_ref` resolves to the exact concrete CARD or lower-operation execution. For Semantic CARD-backed attempts, `card_id` / `card_execution_id` are required and agree with the subject ref. For direct QSOL-CORE attempts they are absent unless independently verified Semantic lineage exists; the Core `operation_execution_id` carried by the subject ref is the concrete execution identity.

`external_tool_ids[]` is mandatory on every effect attempt. Use an explicit empty array only when no material external tool participated in that concrete attempt. When material external tools participate, the IDs must resolve to `external_tool_versions[]` and the relation must be reciprocal through the tool record's `effect_attempt_ids[]`; broad CARD-only attribution is not sufficient.

Every non-attempt requires its own stable identity and concrete execution subject:

```text
effect_non_attempt_records[]:
    effect_non_attempt_record_id
    effect_requirement_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        declared_effect_id
    execution_subject_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    card_id?
    card_execution_id?
    effect_kind
    non_attempt_reason
    governing_control_decision_id?
    governing_failure_record_id?
    governing_skip_rule_id?
    skip_verification_evidence_id?
    backend_detail?
```

When complete effect accounting itself fails, the failure is also declaration/subject-specific rather than a broad untyped escape hatch:

```text
effect_accounting_failure_records[]:
    effect_accounting_failure_record_id
    failure_record_id
    effect_requirement_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        declared_effect_id
    execution_subject_ref:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        subject_kind
        subject_id
        execution_id
    accounting_failure_kind
    detected_sequence_index?
    backend_detail?
```

Each accounting-failure row resolves exactly one applicable declaration and one concrete execution subject and links them to the structured `failure_records[]` event that reports the conformance/execution failure. `failure_records[].effect_accounting_failure_record_ids[]`, when present, is the duplicate-free exact reciprocal set of accounting-failure rows that cite that failure. One broad failure may be referenced by several rows, but **one row is still required per missing declaration/subject pair**; the failure ID alone never discharges another declaration. A mismatched declaration, another retry/iteration, an owner-path guess, or a generic backend failure cannot satisfy this join.

This prevents separate runtime invocations of one Semantic CARD or lower operation from collapsing into one ambiguous attempt/non-attempt/accounting-failure fact. Conditional CARD fields are lineage projections, not the canonical runtime subject identity.

Explicit frozen skips require both `governing_skip_rule_id` and `skip_verification_evidence_id`, resolving to an applicable `EFFECT_SKIP` rule and passing evidence bound to this exact non-attempt record, declaration, execution subject, and active context before the skip is applied. Unknown, missing, stale, inapplicable, or unverifiable skip evidence forces conformance failure, not successful omission. Explicit execution-subject skips carry the same evidence requirements and cannot bypass accounting for their effects.

Authorization and effect-begin indices share one frozen monotonic event-order domain. Every protected effect known to begin must satisfy:

```text
authorization_sequence_index < effect_begin_sequence_index
```

Denied authorization has no effect-begin event. Generic attempt sequence numbering is not authorization-order proof.

For every `COMPLETED`, `ABORTED_CLEAN`, or `PARTIAL` attempt, `effect_end_sequence_index` is mandatory in that same frozen event-order domain and must satisfy:

```text
effect_begin_sequence_index < effect_end_sequence_index
```

For `UNKNOWN`, the end index is mandatory whenever definite termination is known and may be absent only when the termination/completion boundary itself cannot be established. `NOT_STARTED` has no begin or end event. A generic attempt sequence number, enclosing CARD/lower-operation outcome, later failure, or publication event cannot substitute for the explicit end boundary; missing or contradictory end evidence for a definitively terminated attempt fails the PR #5 gate.

Candidate mutually exclusive attempt states are:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

Known completion takes precedence over broader consequence uncertainty. Completion is a property of the effect attempt, not the enclosing CARD/lower-operation result.

### Unconditional declared-effect completeness

Effect declaration accounting is mandatory, not an optional audit profile.

For **every selected concrete `execution_subject_ref`**, every applicable canonical effect declaration owned by that subject or its governed scope must resolve to exactly one of these outcomes:

1. one or more identified `effect_attempts[]` records for that concrete execution subject when attempts occurred;
2. exactly one identified legitimate `effect_non_attempt_records[]` record for that concrete execution subject when no attempt occurred; or
3. exactly one identified `effect_accounting_failure_records[]` record for that exact declaration/concrete execution subject, linked to the structured execution/conformance `failure_record_id`, when complete accounting cannot be established or a reachable required effect was omitted.

Legitimate non-attempt reasons include untaken branch, prior fail-stop, subject not reached, or verified explicit frozen skip and must resolve to the applicable typed control/failure cause or governing skip-rule/evidence records.

`BACKEND_OMISSION_DETECTED` or frozen equivalent is **not** a successful non-attempt path. It means a reachable required effect was omitted and must produce the declaration/subject-specific accounting-failure record plus structured execution/conformance failure.

A declaration with neither attempt, legitimate non-attempt, nor exact accounting-failure record is always incomplete provenance. A generic failure not joined to the exact `effect_requirement_ref` and `execution_subject_ref` cannot account for it. No backend, profile, optimization mode, deployment setting, entry representation, or audit setting may disable this rule.

### Reference failure contract

Before PR #7 may execute a program, PR #5 must also freeze the execution-failure contract sufficiently for the reference machine to implement it:

- evaluation yields success or structured failure, never an implicit sentinel;
- an unhandled CARD/lower-operation failure follows the applicable frozen fail-stop/propagation contract;
- an unhandled DECK failure fails the enclosing JOB by default and later DECKs do not start where Semantic DECK/JOB structure exists;
- dependent consumers/comparisons do not execute against missing or partial failed output;
- future continue/retry/recovery/parallel-JOB behavior requires explicit frozen semantics;
- pure operation failure commits no semantic state;
- capability authorization succeeds before every protected external effect begins;
- protected machinery authorization succeeds before protected machinery use begins;
- effects already observable before a later failure are not retroactively erased;
- arithmetic-domain errors such as division/modulo by zero produce structured failure;
- failure traces preserve every applicable selected DECK/CARD execution outcome when Semantic structure exists, every lower-operation execution outcome when entry is lower, typed failure scope and exact failure-policy bindings, declaration-specific effect accounting including accounting failures, complete backend-selection/authorization/use history, and already-observable outputs/effects.

### Gate condition

No executable QSOL path may emit a research result without enough provenance to bind every identified output to:

- stable run identity and exact input representation;
- nonempty representation-qualified concrete producer execution subject(s);
- selected DECK/CARD execution(s) when verified Semantic execution lineage exists, without fabricating them for lower entry;
- exact immutable material inputs;
- semantic class plus the exact applicable representation-qualified `epistemic_class_binding_ids[]`, derived before interpreting the output label, and mandatory compatible output-bound evidence status for every evidence-bearing class;
- exact generated target and its production selection decision where applicable;
- exact direct producer invocation, immutable non-generated build dependencies, and ordered transitive material toolchain ancestry where generated target bytes are involved;
- the duplicate-free exact producer-derived backend-selection scope set and complete determinism/numeric/randomness/failure-behavior scope sets;
- protected-machinery authorization/use ordering and concrete execution-subject attribution where applicable;
- cache-reuse path, exact current execution subjects, reciprocal execution-ledger joins, and verified substitution rule/evidence where used;
- resolved extension set;
- concrete material external-tool identity, or explicit identity unavailability with a correspondingly weakened claim;
- concrete effect declaration, authorization, attempt/non-attempt/accounting-failure history, with verified skip authority where used;
- exact external-entropy acquisition attempt(s) where applicable;
- applicable pre-execution transition authority and context-bound verification evidence;
- execution/failure context that produced or prevented the result.

### Conformance cases to freeze before implementation

These are documentation-phase acceptance cases, not claims of implemented runtime tests:

| Case | Required result |
| --- | --- |
| Direct Core protected effect | Declaration resolves in the hash-bound Core IR; authorization/attempt use the same Core `execution_subject_ref` and `operation_execution_id`; Semantic CARD fields are absent unless independently verified lineage exists. |
| Direct Core output | Nonempty `producer_execution_refs[]` resolves to the actual Core operation execution; fabricated CARD producers fail. The complete applicable class-binding set is derived before reading the label; a classified output requires exact `epistemic_class_binding_ids[]`, and `UNCLASSIFIED` is legal only when the derived set is empty. |
| Final backend implementation identity | Every final/executable selection decision records a content-bound immutable `selected_backend_implementation_identity` adequate to distinguish the actual implementation, including reference/interpreted/accelerator execution with no generated artifact; a version alone counts only under a frozen unique-immutable version rule. |
| Output backend and execution-contract scopes | `backend_selection_scope_ids[]`, `result_determinism_scope_ids[]`, `numeric_scope_ids[]`, `randomness_scope_ids[]`, and `failure_behavior_binding_ids[]` each equal their independently derived complete duplicate-free producer-applicable sets; missing stricter scopes and unrelated extras fail. |
| Output named result binding | When a producer/entered/lower representation gives the output a named binding, qualified `result_binding_ref` is mandatory and resolves through the complete cardinality-aware map chain; omission is legal only when no result-binding identity exists. |
| Effect boundary termination | `COMPLETED`, `ABORTED_CLEAN`, and `PARTIAL` attempts have same-domain end indices after begin; known-terminated `UNKNOWN` does too. Missing/contradictory end evidence fails. |
| Effect-accounting failure | If one of several applicable effects for one execution subject cannot be accounted for or is omitted, an identified `effect_accounting_failure_record` names that exact declaration/subject and its structured failure. A broad failure with no declaration/subject join cannot discharge the missing effect, and separate missing effects require separate accounting-failure rows. |
| Class-preserving PROOF/VALIDATION/TEST output | `evidence_status`, `evidence_rule_id`, and `evidence_validation_id` are mandatory and resolve to passing output-bound class-specific evidence before publication; inherited class plus operational success alone fails. |
| Direct Core input consumer | `consumer_execution_refs[]` names the actual Core operation execution even if it fails or emits no output; invented `consumer_card_execution_ids[]` fail. |
| Build-only material input | When a prebuilt object/library/header/startup file/sysroot is consumed only by a toolchain invocation, `consumer_execution_refs[]` is explicitly empty and the exact consuming invocation references the input through `toolchain_invocations[].input_ids[]`; fabricating a runtime CARD/Core/lower-operation consumer fails. |
| Direct Core protected machinery use | `execution_subject_refs[]` names the actual Core operation execution; the pre-execution setup exception cannot replace it. |
| Two iterations of one CARD use the same backend scope/decision | Distinct use records resolve to their actual execution-subject refs and CARD projections; canonical IDs or event indices alone fail. |
| Protected setup occurs before any operation/CARD execution | The empty execution-subject array has a resolvable typed initiating RUN/DECK_EXECUTION; invented CARD/Core operation attribution fails. |
| A denied candidate and its fallback both have generated artifacts | Each artifact names its own exact production decision; a scope-only or final-decision guess fails. |
| A link consumes a prebuilt library or sysroot whose bytes change | Invocation `input_ids[]` identifies the actual immutable dependency set; unchanged paths/flags alone cannot establish identical build provenance. |
| Two link invocations differ only in repeated-input/library/grouping order | Their exact duplicate-preserving typed `argument_vector[]` differs; unordered input/output/flag summaries cannot claim the invocations are identical. |
| A requested guarantee is downgraded | Only applicable versioned authority and passing evidence for the exact requested/effective scope, established before application, permit it; unknown, stale, wrong-context, or late evidence fails. |
| A failure occurs under one of several scoped policies | `failure_behavior_binding_ids[]` selects the actual governing bindings, including defaults; inference from the resulting path fails. |
| Failure follows denied-target fallback or protected use | All referenced backend-selection and policy ledgers remain resolvable, including predecessor decisions; dangling references fail. |
| A reachable effect is labeled an explicit frozen skip | The exact execution subject has a resolvable permitted skip rule and passing applicability evidence; an unverifiable label is conformance failure. |
| A cache entry claims `VERIFIED_REUSE` | The applicable frozen rule and passing current-context verification evidence resolve; the exact current `execution_subject_refs[]` and reciprocal CARD/operation execution-ledger join also resolve. Absent evidence, ambiguous current invocation, fabricated CARD lineage, or effectful substitution under a generic cache rule fails. |

The first-lowering machinery requirement-ID cases are additionally frozen in PR #8 and exercised by PR #9.

## PR #6 — Normative QSOL-CORE Operational Specification

Freeze QSOL-CORE semantics **before** implementing the reference machine.

Planned work:

- freeze initial instruction families and exact instruction inventory;
- define operand, result, type, and state-transition semantics;
- define arithmetic and numeric-contract interaction;
- define result-determinism execution semantics at each supported Core scope;
- define requested/effective determinism transitions, resolvable pre-execution authority/evidence, and fail-closed behavior;
- define randomness modes and RNG algorithm/version/seed/stream/partitioning semantics;
- define interaction between randomness, numeric, and result-determinism contracts;
- define logic including XOR;
- define comparisons;
- define control flow, calls, returns, and STOP;
- define effect operations and their explicit protected boundaries;
- define sequencing/failure behavior and totality properties;
- define structured diagnostics and conformance fixtures.

## PR #7 — QSOL-CORE Reference Machine

Implement the frozen QSOL-CORE operational specification without inventing new semantics.

Requirements:

- deterministic reference execution under the active contract;
- fail-closed contract enforcement;
- full PR #5 provenance;
- complete structured failures;
- conformance against PR #6 fixtures.

## PR #8 — Normative Semantic-to-QSOL-CORE Lowering Specification

Freeze the first mandatory lowering before implementing it.

Specify:

- mapping of every supported Semantic-IR operation to Core;
- preservation of stable source identity/provenance;
- result-binding maps;
- type/unit preservation plus every permitted normalization/erasure rule, including exact source facts, resulting Core facts, and required pre-erasure validation evidence;
- extension requirement mapping;
- identified, verifiable qualifier-lowering decisions for every consumed execution-relevant qualifier, including the exact owner-qualified source qualifier/value, resulting Core scope/fact, frozen lowering rule, and required pre-application validation evidence;
- identified cardinality-aware machinery-requirement mappings using composite `source_machinery_requirement_refs[]` / `lower_machinery_requirement_refs[]`, where every entry pairs its local `machinery_requirement_id` with the complete ordered representation-relative `owner_scope_path[]`;
- result-determinism, numeric, randomness, and failure-behavior mapping;
- effect/capability preservation;
- complete tagged sequencing preservation;
- rejection rules and conformance fixtures, including several machinery requirements sharing a source scope but reaching different Core scopes, with missing/swapped/ambiguous associations rejected.

## PR #9 — Reference Semantic-to-QSOL-CORE Lowering

Implement PR #8.

Every material lowering decision must be provenance-bearing. Required decision families include type/unit facts, extension requirements, qualifiers, machinery requirements, result determinism, numerics, randomness, and failure behavior whenever consumed, grouped, normalized, erased, remapped, or otherwise transformed.

`type_unit_lowering_decisions[]` is mandatory whenever lowering normalizes, erases, combines, or otherwise changes a source type/unit fact rather than preserving it under a frozen deterministic reconstruction rule. Each decision identifies the exact owner-qualified source type/unit facts and resulting Core facts, resolves to the accepted frozen `TYPE_UNIT_LOWERING` rule for that transformation, and carries passing subject-bound pre-erasure validation evidence established before the changed/erased lower fact becomes operative. A bare Core type, implementation convenience, post-lowering success, or IR hash cannot prove that a higher-level unit/type fact was safely discarded.

`qualifier_lowering_decisions[]` must use the identified canonical record defined by `docs/TRACE-AND-PROVENANCE.md`: source qualifier ownership/value, resulting Core scope/facts, applicable frozen `QUALIFIER_LOWERING` rule, and passing subject-bound evidence are verifiable rather than opaque metadata. A qualifier affecting target, adapter, placement, tuning, extension controls, authorization, or behavior may not disappear behind a bare decision label.

`machinery_requirement_lowering_decisions[]` requires identified mapping groups, complete ordered absolute `source_scope_refs[]` / `core_scope_refs[]` containment paths, and nonempty deterministic composite `source_machinery_requirement_refs[]` / `lower_machinery_requirement_refs[]`. Every requirement reference pairs the local `machinery_requirement_id` with its complete representation-relative `owner_scope_path[]`; requirement IDs and scope arrays are never positionally paired. Resolve each composite source/lower reference in the hash-bound source Semantic IR and resulting Core IR. Separate unrelated requirements even when they share a local ID such as `gpu`; a frozen rule defines any split/fusion relation and the target selector/capability set reaching each lower requirement. Scope correspondence, bare requirement-ID arrays, or source CARD IDs alone are insufficient. Omission is legal only under a frozen rule reconstructing every owner-qualified requirement association.

`result_binding_map[]` is required whenever identities are preserved or transformed unless a frozen deterministic reconstruction rule applies.

## PR #10 — Normative Full Vector/Dataflow IR Specification

Freeze the mandatory lower IR before implementing its lowering.

The IR must preserve the complete supported QSOL-CORE surface, including:

- scalar and vector operations;
- control flow;
- calls/returns;
- representation-qualified epistemic class bindings and their retained source-binding lineage;
- explicit effects and complete effect-capability requirements;
- protected-machinery requirements;
- sequencing/failure constraints;
- result-determinism, numeric, randomness, extension, and failure-behavior contracts;
- provenance links.

Non-vectorizable operations use explicit scalar/control/effect/pass-through constructs or fail conformance. Backends do not bypass this IR.

## PR #11 — Reference QSOL-CORE-to-Vector/Dataflow Lowering

Implement PR #10 lowering.

Require:

- Vector/Dataflow IR identity/hash;
- cardinality-aware `result_binding_map[]`;
- representation-qualified `epistemic_class_bindings[]` preserving every applicable Core binding with complete `source_epistemic_class_binding_ids[]`; transformed subjects require the accepted frozen class-preservation/mapping rule rather than a copied output class or positional inference;
- owner-qualified `sequencing_constraint_mapping_decisions[]` for every Core sequencing edge whose endpoint identity/kind, owner, direction, cardinality, or lower encoding changes, with exact source/lower edge sets plus the applicable frozen `SEQUENCING_LOWERING` rule and passing subject-bound evidence before the lower edge becomes operative;
- typed Core → Vector/Dataflow scope mappings for extension, machinery, result-determinism, numeric, randomness, and failure-behavior contract families;
- for `machinery_requirement_mapping_decisions[]`, composite `source_machinery_requirement_refs[]` and `lower_machinery_requirement_refs[]`, each pairing a local `machinery_requirement_id` with its complete representation-relative `owner_scope_path[]` in addition to typed group-level scope mappings, so repeated local IDs across source/lower owners cannot be swapped, detached, or positionally inferred;
- lowering diagnostics and conformance/rejection fixtures.

Omission of a sequencing/class/scope mapping is allowed only under a frozen deterministic identity-scope/edge reconstruction rule covering that family. Renaming, splitting, fusion, relocation, retargeting, or endpoint-kind changes must not erase or reverse source/effect/failure ordering or detach a research-class binding from its transformed lower subject.

## PR #12 — Reference MORPH to C

Implement the first reference machinery/code-generation backend from the mandatory Vector/Dataflow IR.

Require:

- semantics-preserving C emission;
- stable backend-unit identity;
- identified `generated_artifacts[]` with artifact ID/kind/hash, backend unit, backend-selection scope and mandatory exact production `backend_selection_decision_id`, source provenance, optimization links where applicable, `direct_producer_toolchain_invocation_id`, and ordered `toolchain_invocation_chain_ids[]`;
- identified `toolchain_invocations[]` recording the exact material compiler/assembler/linker/code-generation identities, invocation order, target/ABI, deterministic build flags/configuration, exact ordered duplicate-preserving typed `argument_vector[]`, explicit exact `input_ir_hashes[]` whenever IR is directly consumed, immutable non-generated dependency `input_ids[]`, direct generated-artifact inputs/outputs, backend unit, and backend-selection scope;
- truthful direct-edge invariants: only the direct producer invocation lists an artifact in `output_generated_artifact_ids[]`, while transitive ancestors remain in the artifact's ordered chain and prebuilt dependencies resolve through `inputs[]`;
- reference/optimized equivalence evidence where optimization is used;
- no bypass around the Vector/Dataflow IR.

Each `argument_vector[]` is occurrence-ordered and duplicate-preserving with typed literal/input/output/generated-artifact references. Library order, repeated inputs, grouping delimiters, and option placement that can change symbol resolution or output bytes are therefore part of invocation identity; unordered flags/configuration or input/output inventories cannot substitute for exact argv.

A run-wide compiler/version inventory may remain as a summary, but it is not sufficient artifact provenance when several compilation/link stages or configurations are possible.

## PR #13 — Morph Optimization Passes

Introduce optimization only after the reference path exists.

Potential passes:

- vectorization;
- fusion;
- memory placement;
- deterministic parallelization;
- common-subexpression work;
- dead-result elimination only for operations proven pure and total unless original failure is explicitly preserved at the same observable point;
- verified cache reuse under the PR #5 rule/evidence validation contract.

Optimization correctness is more important than speed. Potentially failing pure operations remain observable under fail-stop semantics.

`VERIFIED_REUSE` requires its resolvable `legality_rule_id` and passing context-bound `verification_evidence_id` before substitution. Unverified hits cannot supply results. Cache substitution is effect-free by default; effectful reuse requires the specifically applicable separately frozen replay/cache semantics preserving effects, authorization, ordering, failure, provenance, and observable state.

## PR #14 — Normative QX-POSIX Contract

Freeze QX-POSIX before implementing it.

Specify process, stream, file, environment, signal, byte/text conversion, encoding, buffering, failure, effect-boundary, capability, ordering, and provenance semantics.

## PR #15 — QX-POSIX Reference Implementation

Implement PR #14 as a composable profile usable by generated targets. POSIX is not a compiler backend.

## PR #16 — LLVM Backend

Add an LLVM machinery backend after the C reference path and POSIX profile contract are established.

LLVM must preserve the same Vector/Dataflow, contract, provenance, effect, failure, and authorization semantics.

## PR #17 — Normative Generic GPU Execution Contract

Freeze vendor-neutral accelerator execution semantics before CUDA implementation.

Specify generic device selection, protected-machinery requirements, data movement, synchronization, determinism/numeric constraints, failure, authorization, and provenance.

## PR #18 — CUDA Backend

Implement CUDA as a machinery backend against PR #17.

CUDA selection is machinery. It does not itself imply or activate `QX-CUDA`.

## PR #19 — Normative QX-CUDA Control Contract

Freeze optional CUDA-specific language controls separately from CUDA machinery selection.

Specify launch/memory/tuning control validation, lowering, determinism, failure, provenance, and versioning.

## PR #20 — QX-CUDA Reference Control Implementation

Implement PR #19. Generic CUDA-targeted programs remain valid without QX-CUDA when they do not use QX-CUDA-owned controls.

## PR #21 — Additional Backends

Add additional actual machinery/code-generation targets only after their required contracts are frozen.

MIDI mapping remains a `QX-MIDI` adapter/extension workstream, not a backend. Formal-tool integration remains behind a proof/verification extension such as `QX-PROVE`, not a backend.

## PR #22 — Formalization

Formalize the frozen semantic core and critical invariants where useful.

Potential targets include:

- semantic preservation across lowerings;
- result-binding correspondence;
- effect/capability authorization invariants;
- protected-machinery authorization-before-use;
- fail-stop sequencing;
- determinism contracts;
- epistemic non-promotion;
- optimization equivalence.

## Deferred normative workstream — QSOL text profile

The human `.qsl` grammar remains deferred until a normative text-profile specification freezes:

- lexical grammar;
- source grammar;
- shorthand/default reconstruction;
- diagnostics;
- canonical text rendering;
- source-to-Semantic-IR mapping.

Examples before that freeze are illustrative and must not become accidental parser law.

## Principle

> Specify meaning. Preserve identity. Trace concrete execution. Authorize before effects or protected machinery begin. Bind generated bytes to truthful direct toolchain edges plus exact transitive ancestry. Optimize only after equivalence is demonstrated.